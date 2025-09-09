from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserCreateDTO, UserDTO, UserUpdateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.exceptions import UserNotFound, UserAlreadyExists
from expenses_tracker.infrastructure.database.repositories.dummy_repo import (
    create_dummy_user,
    DummyUserRepository,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


@fixture
def dummy_user():
    return create_dummy_user()


@fixture
def dummy_user_dto(dummy_user):
    return UserDTO(
        id=dummy_user.id,
        username=dummy_user.username,
        email=dummy_user.email,
        is_active=dummy_user.is_active,
        created_at=dummy_user.created_at,
        updated_at=dummy_user.updated_at,
    )


@fixture
def dummy_repo(dummy_user):
    return DummyUserRepository(initial_user=dummy_user)


@fixture
def bcrypt_hasher(dummy_repo):
    return BcryptPasswordHasher()


@fixture
def user_use_cases(dummy_repo, bcrypt_hasher) -> UserUseCases:
    return UserUseCases(user_repository=dummy_repo, password_hasher=bcrypt_hasher)


class TestUserUseCasesWithDummyRepo:
    async def test_get_user(self, user_use_cases, dummy_user, dummy_user_dto):
        user = await user_use_cases.get_user(user_id=dummy_user.id)

        assert isinstance(user, UserDTO)
        assert user == dummy_user_dto

    async def test_get_user_not_found(self, user_use_cases):
        with pytest.raises(UserNotFound):
            await user_use_cases.get_user(user_id=uuid4())

    async def test_create_user(self, user_use_cases):
        username = "new_user"
        email = "new@test.com"
        password = "password123"

        user = await user_use_cases.create_user(
            user_data=UserCreateDTO(username=username, email=email, password=password)
        )

        assert isinstance(user, UserDTO)
        assert user.username == username
        assert user.email == email

    async def test_create_user_with_existing_username(self, user_use_cases, dummy_user):
        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {dummy_user.username} already exists",
        ):
            await user_use_cases.create_user(
                user_data=UserCreateDTO(
                    username=dummy_user.username,
                    email="new@test.com",
                    password="password123",
                )
            )

    async def test_create_user_with_existing_email(self, user_use_cases, dummy_user):
        with pytest.raises(
            UserAlreadyExists,
            match=f"User with email {dummy_user.email} already exists",
        ):
            await user_use_cases.create_user(
                user_data=UserCreateDTO(
                    username="new_user",
                    email=dummy_user.email,
                    password="password123",
                )
            )

    async def test__validate_user_uniqueness(self, user_use_cases, dummy_user):
        username = "new_user"
        email = "new@test.com"
        assert (
            await user_use_cases._validate_user_uniqueness(
                new_username=username, new_email=email
            )
            is None
        )

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {dummy_user.username} already exists",
        ):
            await user_use_cases._validate_user_uniqueness(
                new_username=dummy_user.username
            )

    async def test_update_user(self, user_use_cases, dummy_user):
        new_email = "new_email@test.com"

        user = await user_use_cases.update_user(
            UserUpdateDTO(id=dummy_user.id, email=new_email)
        )

        assert isinstance(user, UserDTO)
        assert user.email == new_email

    async def test_update_user_not_found(self, user_use_cases):
        with pytest.raises(UserNotFound):
            await user_use_cases.update_user(
                UserUpdateDTO(id=uuid4(), email="new_email@test.com")
            )

    async def test_delete_user(self, user_use_cases, dummy_user):
        await user_use_cases.delete_user(user_id=dummy_user.id)

        assert user_use_cases.user_repository.users == {}

    async def test_delete_user_not_found(self, user_use_cases):
        with pytest.raises(UserNotFound):
            await user_use_cases.delete_user(user_id=uuid4())
