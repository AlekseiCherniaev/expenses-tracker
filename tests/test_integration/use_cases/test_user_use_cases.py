from datetime import datetime, timezone

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.user import UserCreateDTO, UserDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.exceptions.user import UserNotFound, UserAlreadyExists


class TestUserUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work, password_hasher, cache_service):
        self.user_use_cases = UserUseCases(
            unit_of_work=unit_of_work,
            password_hasher=password_hasher,
            cache_service=cache_service,
        )
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher
        self.cache_service = cache_service

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
