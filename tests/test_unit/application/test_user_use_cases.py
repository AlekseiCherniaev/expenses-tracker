from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions import UserNotFound, UserAlreadyExists
from expenses_tracker.domain.repositories.user import IUserRepository


@fixture
def user_entity():
    return User(
        id=uuid4(),
        username="test",
        email="test@test.com",
        hashed_password="hashed_password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
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
def mock_user_repo():
    return AsyncMock(spec=IUserRepository)


@fixture
def mock_password_hasher(user_entity):
    mock_hasher = Mock(spec=IPasswordHasher)
    mock_hasher.hash.return_value = user_entity.hashed_password
    mock_hasher.verify.return_value = True
    return mock_hasher


@fixture(autouse=True)
def random_uuid():
    return uuid4()


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, mock_user_repo, mock_password_hasher):
        self.user_use_cases = UserUseCases(
            user_repository=mock_user_repo, password_hasher=mock_password_hasher
        )
        self.mock_repo = mock_user_repo
        self.mock_hasher = mock_password_hasher

    async def test_get_user_success(self, mock_user_repo, user_entity, user_dto):
        mock_user_repo.get_by_id.return_value = user_entity
        user = await self.user_use_cases.get_user(user_id=user_entity.id)

        assert isinstance(user, UserDTO)
        assert user == user_dto
        mock_user_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)

    async def test_get_user_not_found(self, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.get_user(user_id=random_uuid)
        mock_user_repo.get_by_id.assert_called_once_with(user_id=random_uuid)

    async def test__validate_user_uniqueness(self, mock_user_repo, user_entity):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = None

        assert (
            await self.user_use_cases._validate_user_uniqueness(
                new_username=user_entity.username, new_email=user_entity.email
            )
            is None
        )
        mock_user_repo.get_by_email.assert_called_once_with(user_entity.email)

        mock_user_repo.get_by_username.return_value = user_entity

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {user_entity.username} already exists",
        ):
            await self.user_use_cases._validate_user_uniqueness(
                new_username=user_entity.username
            )
        mock_user_repo.get_by_email.assert_called_once_with(user_entity.email)
        mock_user_repo.get_by_username.assert_called_with(user_entity.username)

    async def test_create_user_success(
        self,
        mock_user_repo,
        mock_password_hasher,
        user_entity,
        user_create_dto,
        user_dto,
    ):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.create.return_value = user_entity
        user = await self.user_use_cases.create_user(user_data=user_create_dto)

        assert isinstance(user, UserDTO)
        assert user == user_dto
        mock_user_repo.create.assert_called_once()
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
        mock_user_repo,
        user_entity,
        user_create_dto,
        existing_field,
        none_field,
        error_message,
    ):
        getattr(mock_user_repo, existing_field).return_value = user_entity
        getattr(mock_user_repo, none_field).return_value = None

        with pytest.raises(UserAlreadyExists, match=error_message):
            await self.user_use_cases.create_user(user_create_dto)

    async def test_update_user_success(
        self,
        mock_user_repo,
        mock_password_hasher,
        user_entity,
        user_dto,
    ):
        mock_user_repo.get_by_id.return_value = user_entity
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.update.return_value = user_entity
        new_email = "new_email"
        user_update_dto = UserUpdateDTO(
            id=user_entity.id, email=new_email, password="new_password"
        )

        user = await self.user_use_cases.update_user(user_data=user_update_dto)

        assert isinstance(user, UserDTO)
        assert user.id == user_dto.id
        assert user.email == new_email
        assert user.is_active == user_dto.is_active
        mock_user_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        mock_password_hasher.hash.assert_called_once_with(
            password=user_update_dto.password
        )
        mock_user_repo.update.assert_called_once_with(user=user_entity)

    async def test_update_user_not_found(self, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.update_user(
                UserUpdateDTO(id=random_uuid, email="new_email@test.com")
            )
        mock_user_repo.get_by_id.assert_called_once_with(user_id=random_uuid)

    async def test_delete_user(self, mock_user_repo, user_entity):
        mock_user_repo.get_by_id.return_value = user_entity
        mock_user_repo.delete.return_value = None
        await self.user_use_cases.delete_user(user_id=user_entity.id)

        mock_user_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        mock_user_repo.delete.assert_called_once_with(user_id=user_entity.id)

    async def test_delete_user_not_found(self, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await self.user_use_cases.delete_user(user_id=random_uuid)
        mock_user_repo.get_by_id.assert_called_once_with(user_id=random_uuid)
