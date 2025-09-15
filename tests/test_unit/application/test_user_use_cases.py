from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.user import UserNotFound, UserAlreadyExists
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository


@fixture
def user_entity():
    return User(
        id=uuid4(),
        username="test",
        email="test@test.com",
        hashed_password="hashed_password",
    )


@fixture
def user_dto(user_entity):
    return UserDTO(
        id=user_entity.id,
        username=user_entity.username,
        email=user_entity.email,
        is_active=user_entity.is_active,
        created_at=user_entity.created_at,
        updated_at=user_entity.updated_at,
    )


@fixture
def user_create_dto(user_entity):
    return UserCreateDTO(
        username=user_entity.username, email=user_entity.email, password="new_password"
    )


@fixture
def user_update_dto(user_entity):
    return UserUpdateDTO(id=user_entity.id, email="new_email", password="new_password")


@fixture
def mock_unit_of_work():
    mock_uow = AsyncMock(spec=IUnitOfWork)
    mock_uow.__aenter__ = AsyncMock()
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    mock_user_repo = AsyncMock(spec=IUserRepository)
    mock_uow.__aenter__.return_value.user_repository = mock_user_repo
    return mock_uow


@fixture
def mock_password_hasher(user_entity):
    mock_hasher = Mock(spec=IPasswordHasher)
    mock_hasher.hash.return_value = user_entity.hashed_password
    mock_hasher.verify.return_value = True
    return mock_hasher


@fixture()
def random_uuid():
    return uuid4()


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work, mock_password_hasher):
        self.user_use_cases = UserUseCases(
            unit_of_work=mock_unit_of_work, password_hasher=mock_password_hasher
        )
        self.mock_unit_of_work = mock_unit_of_work
        self.mock_hasher = mock_password_hasher

    async def test_get_user_success(self, mock_unit_of_work, user_entity, user_dto):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = user_entity
        user = await self.user_use_cases.get_user(user_id=user_entity.id)

        assert isinstance(user, UserDTO)
        assert user == user_dto
        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)

    async def test_get_user_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.get_user(user_id=random_uuid)
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
        assert user.is_active == user_dto.is_active
        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        mock_password_hasher.hash.assert_called_once_with(
            password=user_update_dto.password
        )
        mock_repo.update.assert_called_once_with(user=user_entity)

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

    async def test_delete_user_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.delete_user(user_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(user_id=random_uuid)
