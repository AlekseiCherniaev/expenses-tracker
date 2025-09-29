import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.exceptions.user import UserNotFound, UserAlreadyExists


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work, mock_password_hasher, cache_service_mock):
        self.user_use_cases = UserUseCases(
            unit_of_work=mock_unit_of_work,
            password_hasher=mock_password_hasher,
            cache_service=cache_service_mock,
        )
        self.mock_unit_of_work = mock_unit_of_work
        self.mock_hasher = mock_password_hasher
        self.cache_service_mock = cache_service_mock

    async def test_get_user_success(self, mock_unit_of_work, user_entity, user_dto):
        self.cache_service_mock.get.return_value = None
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = user_entity
        user = await self.user_use_cases.get_user(user_id=user_entity.id)

        assert isinstance(user, UserDTO)
        assert user == user_dto
        self.cache_service_mock.get.assert_awaited_once_with(
            key=f"user:{user_entity.id}", serializer=UserDTO
        )
        self.cache_service_mock.set.assert_awaited_once()
        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)

    async def test_get_user_not_found(self, mock_unit_of_work, random_uuid):
        self.cache_service_mock.get.return_value = None
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.get_user(user_id=random_uuid)
        self.cache_service_mock.get.assert_awaited_once_with(
            key=f"user:{random_uuid}", serializer=UserDTO
        )
        mock_repo.get_by_id.assert_called_once_with(user_id=random_uuid)

    async def test__validate_user_uniqueness(self, mock_unit_of_work, user_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None

        assert (
            await self.user_use_cases._validate_user_uniqueness(
                uow=mock_unit_of_work.__aenter__.return_value,
                new_username=user_entity.username,
                new_email=user_entity.email,
            )
            is None
        )
        mock_repo.get_by_email.assert_called_once_with(user_entity.email)

        mock_repo.get_by_username.return_value = user_entity

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {user_entity.username} already exists",
        ):
            await self.user_use_cases._validate_user_uniqueness(
                uow=mock_unit_of_work.__aenter__.return_value,
                new_username=user_entity.username,
            )
        mock_repo.get_by_email.assert_called_once_with(user_entity.email)
        mock_repo.get_by_username.assert_called_with(user_entity.username)

    async def test_create_user_success(
        self,
        mock_unit_of_work,
        mock_password_hasher,
        user_entity,
        user_create_dto,
        user_dto,
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        mock_repo.create.return_value = user_entity
        user = await self.user_use_cases.create_user(user_data=user_create_dto)

        assert isinstance(user, UserDTO)
        assert user == user_dto
        mock_repo.create.assert_called_once()
        mock_password_hasher.hash.assert_called_once_with(password="new_password")
        self.cache_service_mock.set.assert_awaited_once_with(
            key=f"user:{user_entity.id}",
            value=user,
            ttl=get_settings().user_dto_ttl_seconds,
        )

    @pytest.mark.parametrize(
        "existing_field, none_field, error_message",
        [
            (
                "get_by_username",
                "get_by_email",
                "User with username test already exists",
            ),
            (
                "get_by_email",
                "get_by_username",
                "User with email test@test.com already exists",
            ),
        ],
    )
    async def test_create_user_conflicts(
        self,
        mock_unit_of_work,
        user_entity,
        user_create_dto,
        existing_field,
        none_field,
        error_message,
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        user_entity.email_verified = True
        getattr(mock_repo, existing_field).return_value = user_entity
        getattr(mock_repo, none_field).return_value = None

        with pytest.raises(UserAlreadyExists, match=error_message):
            await self.user_use_cases.create_user(user_create_dto)

    async def test_update_user_success(
        self,
        mock_unit_of_work,
        mock_password_hasher,
        user_entity,
        user_dto,
        user_update_dto,
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = user_entity
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        mock_repo.update.return_value = user_entity
        user = await self.user_use_cases.update_user(user_data=user_update_dto)

        assert isinstance(user, UserDTO)
        assert user.id == user_dto.id
        assert user.email == user_update_dto.email
        assert user.email_verified == user_dto.email_verified
        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        mock_password_hasher.hash.assert_called_once_with(
            password=user_update_dto.password
        )
        mock_repo.update.assert_called_once_with(user=user_entity)
        self.cache_service_mock.set.assert_awaited_once_with(
            key=f"user:{user_entity.id}",
            value=user,
            ttl=get_settings().user_dto_ttl_seconds,
        )

    async def test_update_user_not_found(
        self, mock_unit_of_work, user_update_dto, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = None
        user_update_dto.id = random_uuid

        with pytest.raises(UserNotFound):
            await self.user_use_cases.update_user(user_update_dto)
        mock_repo.get_by_id.assert_called_once_with(user_id=random_uuid)

    async def test_delete_user_success(self, mock_unit_of_work, user_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = user_entity
        mock_repo.delete.return_value = None
        await self.user_use_cases.delete_user(user_id=user_entity.id)

        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        mock_repo.delete.assert_called_once_with(user=user_entity)
        self.cache_service_mock.delete.assert_awaited_once_with(
            key=f"user:{user_entity.id}"
        )

    async def test_delete_user_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.delete_user(user_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(user_id=random_uuid)
