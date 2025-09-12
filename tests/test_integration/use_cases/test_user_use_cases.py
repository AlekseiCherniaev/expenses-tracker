from datetime import datetime
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserCreateDTO, UserDTO, UserUpdateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions import UserNotFound, UserAlreadyExists
from expenses_tracker.infrastructure.database.repositories.dummy_uow import (
    DummyUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


@fixture
def user_entity_with_times() -> (User, datetime, datetime):
    before_create = datetime.now()
    user = User(
        username="test",
        hashed_password="hashed_test",
        email="testemail@gmail.com",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    after_create = datetime.now()
    return user, before_create, after_create


@fixture
def user_entity(user_entity_with_times):
    user, _, _ = user_entity_with_times
    return user


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
        username=user_entity.username,
        email=user_entity.email,
        password="new_password",
    )


@fixture
def user_update_dto(user_entity):
    return UserUpdateDTO(id=user_entity.id, email="new_email")


@fixture(params=["bcrypt_hasher"])
def password_hasher(request):
    match request.param:
        case "bcrypt_hasher":
            return BcryptPasswordHasher()
        case _:
            raise ValueError(f"Unknown password_hasher {request.param}")


@fixture(params=["dummy"])
def unit_of_work(request):
    match request.param:
        case "dummy":
            return DummyUnitOfWork()
        case _:
            raise ValueError(f"Unknown repo {request.param}")


@fixture(autouse=True)
def random_uuid():
    return uuid4()


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work, password_hasher):
        self.user_use_cases = UserUseCases(
            unit_of_work=unit_of_work, password_hasher=password_hasher
        )
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher

    async def _create_user(self, user_entity):
        return await self.unit_of_work.user_repository.create(user_entity)

    async def test_get_user_success(self, user_entity, user_dto):
        new_user = await self._create_user(user_entity)
        user = await self.user_use_cases.get_user(user_id=new_user.id)

        assert isinstance(user, UserDTO)
        assert user == user_dto

    async def test_get_user_not_found(self):
        with pytest.raises(UserNotFound):
            await self.user_use_cases.get_user(user_id=random_uuid)

    async def test_create_user_success(self, user_create_dto, user_dto):
        before_create = datetime.now()
        user = await self.user_use_cases.create_user(user_data=user_create_dto)
        after_create = datetime.now()

        assert isinstance(user, UserDTO)
        assert user.username == user_dto.username
        assert user.email == user_dto.email
        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create

    @pytest.mark.parametrize(
        "change_field, value, error_message",
        [
            (
                "email",
                "newemail@gmail.com",
                "User with username test already exists",
            ),
            (
                "username",
                "new_test",
                "User with email testemail@gmail.com already exists",
            ),
        ],
    )
    async def test_create_user_conflicts(
        self, change_field, value, error_message, user_create_dto, user_entity
    ):
        setattr(user_entity, change_field, value)
        await self._create_user(user_entity)

        with pytest.raises(UserAlreadyExists, match=error_message):
            await self.user_use_cases.create_user(
                UserCreateDTO(
                    username=user_create_dto.username,
                    email=user_create_dto.email,
                    password=user_create_dto.password,
                )
            )

    async def test__validate_user_uniqueness(self, user_entity, user_create_dto):
        assert (
            await self.user_use_cases._validate_user_uniqueness(
                uow=self.unit_of_work,
                new_username=user_create_dto.username,
                new_email=user_create_dto.email,
            )
            is None
        )

        await self._create_user(user_entity)

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {user_create_dto.username} already exists",
        ):
            await self.user_use_cases._validate_user_uniqueness(
                uow=self.unit_of_work, new_username=user_create_dto.username
            )

    async def test_update_user_success(self, user_entity_with_times, user_update_dto):
        user, before_create, after_create = user_entity_with_times
        new_user = await self._create_user(user)
        before_update = datetime.now()
        updated_user = await self.user_use_cases.update_user(user_update_dto)
        after_update = datetime.now()

        assert isinstance(updated_user, UserDTO)
        assert updated_user.email == user_update_dto.email
        assert updated_user.is_active == new_user.is_active
        assert before_create <= updated_user.created_at <= after_create
        assert before_update <= updated_user.updated_at <= after_update

    async def test_update_user_not_found(self, user_update_dto):
        user_update_dto.id = random_uuid
        with pytest.raises(UserNotFound):
            await self.user_use_cases.update_user(user_update_dto)

    async def test_delete_user_success(self, user_entity):
        new_user = await self._create_user(user_entity)
        result = await self.user_use_cases.delete_user(user_id=new_user.id)

        assert result is None

    async def test_delete_user_not_found(self):
        with pytest.raises(UserNotFound):
            await self.user_use_cases.delete_user(user_id=random_uuid)
