from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions import UserNotFound, UserAlreadyExists
from expenses_tracker.domain.repositories.user import IUserRepository


@fixture
def test_user_data():
    return {
        "id": UUID("a050493d-ed7a-4316-8f2a-77a2edc0a0c2"),
        "username": "test_username",
        "email": "test_email@test.com",
        "password": "test",
        "hashed_password": "hash_test",
        "is_active": True,
        "created_at": datetime(year=2001, month=4, day=23, second=23),
        "updated_at": datetime(year=2001, month=4, day=24, second=23),
    }


@fixture
def test_user(test_user_data):
    return User(
        id=test_user_data["id"],
        username=test_user_data["username"],
        hashed_password=test_user_data["hashed_password"],
        email=test_user_data["email"],
        is_active=test_user_data["is_active"],
        created_at=test_user_data["created_at"],
        updated_at=test_user_data["updated_at"],
    )


@fixture
def test_user_dto(test_user_data):
    return UserDTO(
        id=test_user_data["id"],
        username=test_user_data["username"],
        email=test_user_data["email"],
        is_active=test_user_data["is_active"],
        created_at=test_user_data["created_at"],
        updated_at=test_user_data["updated_at"],
    )


@fixture
def fake_user_repo(test_user):
    class FakeUserRepo(IUserRepository):
        def __init__(self, initial_user=None):
            self.users = {}
            if initial_user:
                self.users[initial_user.id] = initial_user

        async def get_by_id(self, user_id: UUID) -> User | None:
            return self.users.get(user_id)

        async def get_by_username(self, username: str) -> User | None:
            return next(
                (u for u in self.users.values() if u.username == username), None
            )

        async def get_by_email(self, email: str) -> User | None:
            return next((u for u in self.users.values() if u.email == email), None)

        async def create(self, user: User) -> User:
            self.users[user.id] = user
            return user

        async def get_all(self) -> list[User]:
            return list(self.users.values())

        async def update(self, user: User) -> User:
            self.users[user.id] = user
            return user

        async def delete(self, user_id: UUID) -> None:
            self.users.pop(user_id, None)

    return FakeUserRepo(initial_user=test_user)


@fixture
def fake_password_hasher():
    class FakePasswordHasher(IPasswordHasher):
        def hash(self, password: str) -> str:
            return f"hash_{password}"

        def verify(self, password: str, hashed: str) -> bool:
            return password == hashed.removeprefix("hash_")

    return FakePasswordHasher()


@fixture
def user_use_cases(fake_user_repo, fake_password_hasher) -> UserUseCases:
    return UserUseCases(
        user_repository=fake_user_repo, password_hasher=fake_password_hasher
    )


class TestUserUseCases:
    async def test_get_user(self, user_use_cases, test_user, test_user_dto):
        user = await user_use_cases.get_user(user_id=test_user.id)

        assert isinstance(user, UserDTO)
        assert user == test_user_dto

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

    async def test_create_user_with_existing_username(
        self, user_use_cases, test_user_data
    ):
        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {test_user_data['username']} already exists",
        ):
            await user_use_cases.create_user(
                user_data=UserCreateDTO(
                    username=test_user_data["username"],
                    email="new@test.com",
                    password="password123",
                )
            )

    async def test_create_user_with_existing_email(
        self, user_use_cases, test_user_data
    ):
        with pytest.raises(
            UserAlreadyExists,
            match=f"User with email {test_user_data['email']} already exists",
        ):
            await user_use_cases.create_user(
                user_data=UserCreateDTO(
                    username="new_user",
                    email=test_user_data["email"],
                    password="password123",
                )
            )

    async def test__validate_user_uniqueness(self, user_use_cases, test_user_data):
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
            match=f"User with username {test_user_data['username']} already exists",
        ):
            await user_use_cases._validate_user_uniqueness(
                new_username=test_user_data["username"]
            )

    async def test_update_user(self, user_use_cases, test_user_dto, test_user_data):
        new_email = "new_email@test.com"

        user = await user_use_cases.update_user(
            UserUpdateDTO(id=test_user_data["id"], email=new_email)
        )

        assert isinstance(user, UserDTO)
        assert user.email == new_email

    async def test_update_user_not_found(self, user_use_cases):
        with pytest.raises(UserNotFound):
            await user_use_cases.update_user(
                UserUpdateDTO(id=uuid4(), email="new_email@test.com")
            )

    async def test_delete_user(self, user_use_cases, test_user_data):
        await user_use_cases.delete_user(user_id=test_user_data["id"])

        assert user_use_cases.user_repository.users == {}

    async def test_delete_user_not_found(self, user_use_cases):
        with pytest.raises(UserNotFound):
            await user_use_cases.delete_user(user_id=uuid4())
