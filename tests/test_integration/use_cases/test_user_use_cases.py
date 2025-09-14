from datetime import datetime, timezone
from uuid import uuid4, UUID

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserCreateDTO, UserDTO, UserUpdateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions import UserNotFound, UserAlreadyExists
from expenses_tracker.infrastructure.database.repositories.dummy_uow import (
    DummyUnitOfWork,
)
from expenses_tracker.infrastructure.database.repositories.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from expenses_tracker.infrastructure.security.password_hasher import (
    BcryptPasswordHasher,
)


@fixture(autouse=True)
def random_uuid() -> UUID:
    return uuid4()


@fixture
def unique_user_create_dto(random_uuid):
    uid = random_uuid.hex[:6]
    return UserCreateDTO(
        username=f"user_{uid}",
        password="password123",
        email=f"user_{uid}@test.com",
    )


@fixture
def unique_user_entity_with_times(random_uuid) -> (User, datetime, datetime):
    before_create = datetime.now(timezone.utc)
    uid = random_uuid.hex[:6]
    user = User(
        username=f"user_{uid}",
        hashed_password="hashed_password123",
        email=f"user_{uid}@test.com",
    )
    after_create = datetime.now(timezone.utc)
    return user, before_create, after_create


@fixture
def unique_user_entity(unique_user_entity_with_times):
    user, _, _ = unique_user_entity_with_times
    return user


@fixture
def unique_user_dto(unique_user_entity):
    return UserDTO(
        id=unique_user_entity.id,
        username=unique_user_entity.username,
        email=unique_user_entity.email,
        is_active=unique_user_entity.is_active,
        created_at=unique_user_entity.created_at,
        updated_at=unique_user_entity.updated_at,
    )


@fixture
def unique_user_update_dto(unique_user_entity):
    return UserUpdateDTO(
        id=unique_user_entity.id,
        password="new_password",
        email="new_email@test.com",
        is_active=True,
    )


@fixture(params=["bcrypt_hasher"])
def password_hasher(request):
    match request.param:
        case "bcrypt_hasher":
            return BcryptPasswordHasher()
        case _:
            raise ValueError(f"Unknown password_hasher {request.param}")


@fixture(params=["dummy", "sqlalchemy"])
def unit_of_work(request, async_session_factory):
    match request.param:
        case "dummy":
            return DummyUnitOfWork()
        case "sqlalchemy":
            return SqlAlchemyUnitOfWork(session_factory=async_session_factory)
        case _:
            raise ValueError(f"Unknown repo {request.param}")


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work, password_hasher):
        self.user_use_cases = UserUseCases(
            unit_of_work=unit_of_work, password_hasher=password_hasher
        )
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher

    async def _create_user(self, unique_user_entity):
        async with self.unit_of_work as uow:
            return await uow.user_repository.create(unique_user_entity)

    async def test_get_user_success(self, unique_user_entity, unique_user_dto):
        new_user = await self._create_user(unique_user_entity)
        user = await self.user_use_cases.get_user(user_id=new_user.id)

        assert isinstance(user, UserDTO)
        assert user == unique_user_dto

    async def test_get_user_not_found(self, random_uuid):
        with pytest.raises(UserNotFound):
            await self.user_use_cases.get_user(user_id=random_uuid)

    async def test_create_user_success(self, unique_user_create_dto, unique_user_dto):
        before_create = datetime.now(timezone.utc)
        user = await self.user_use_cases.create_user(user_data=unique_user_create_dto)
        after_create = datetime.now(timezone.utc)

        assert isinstance(user, UserDTO)
        assert user.username == unique_user_dto.username
        assert user.email == unique_user_dto.email
        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create

    @pytest.mark.parametrize(
        "change_field, value, error_message",
        [
            (
                "email",
                "newemail@gmail.com",
                "User with username",
            ),
            (
                "username",
                "new_test",
                "User with email",
            ),
        ],
    )
    async def test_create_user_conflicts(
        self,
        change_field,
        value,
        error_message,
        unique_user_create_dto,
        unique_user_entity,
    ):
        setattr(unique_user_entity, change_field, value)
        await self._create_user(unique_user_entity)

        with pytest.raises(UserAlreadyExists, match=error_message):
            await self.user_use_cases.create_user(
                UserCreateDTO(
                    username=unique_user_create_dto.username,
                    email=unique_user_create_dto.email,
                    password=unique_user_create_dto.password,
                )
            )

    async def test__validate_user_uniqueness(
        self, unique_user_entity, unique_user_create_dto
    ):
        async with self.unit_of_work as uow:
            assert (
                await self.user_use_cases._validate_user_uniqueness(
                    uow=uow,
                    new_username=unique_user_create_dto.username,
                    new_email=unique_user_create_dto.email,
                )
                is None
            )

        await self._create_user(unique_user_entity)

        async with self.unit_of_work as uow:
            with pytest.raises(
                UserAlreadyExists,
                match=f"User with username {unique_user_create_dto.username} already exists",
            ):
                await self.user_use_cases._validate_user_uniqueness(
                    uow=uow, new_username=unique_user_create_dto.username
                )

    async def test_update_user_success(
        self, unique_user_entity_with_times, unique_user_update_dto
    ):
        user, before_create, after_create = unique_user_entity_with_times
        await self._create_user(user)
        before_update = datetime.now(timezone.utc)
        updated_user = await self.user_use_cases.update_user(unique_user_update_dto)
        after_update = datetime.now(timezone.utc)

        assert isinstance(updated_user, UserDTO)
        assert updated_user.email == unique_user_update_dto.email
        assert updated_user.is_active == unique_user_update_dto.is_active
        assert before_create <= updated_user.created_at <= after_create
        assert before_update <= updated_user.updated_at <= after_update

    async def test_update_user_not_found(self, unique_user_update_dto, random_uuid):
        unique_user_update_dto.id = random_uuid
        with pytest.raises(UserNotFound):
            await self.user_use_cases.update_user(unique_user_update_dto)

    async def test_delete_user_success(self, unique_user_entity):
        new_user = await self._create_user(unique_user_entity)
        result = await self.user_use_cases.delete_user(user_id=new_user.id)

        assert result is None

    async def test_delete_user_not_found(self, random_uuid):
        with pytest.raises(UserNotFound):
            await self.user_use_cases.delete_user(user_id=random_uuid)
