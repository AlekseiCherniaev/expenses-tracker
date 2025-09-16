from datetime import timedelta
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.token import TokenPairDTO
from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.auth import InvalidCredentials
from expenses_tracker.domain.exceptions.user import UserAlreadyExists, UserNotFound


class TestAuthUserUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work, password_hasher, token_service):
        self.auth_user_use_cases = AuthUserUseCases(
            unit_of_work=unit_of_work,
            password_hasher=password_hasher,
            token_service=token_service,
        )
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def _create_user_with_hashed_password(
        self, user_create_dto: UserCreateDTO
    ) -> User:
        hashed_password = self.password_hasher.hash(password=user_create_dto.password)
        user = User(
            username=user_create_dto.username,
            hashed_password=hashed_password,
            email=user_create_dto.email,
        )
        async with self.unit_of_work as uow:
            return await uow.user_repository.create(user)
        assert False, "Unreachable"

    async def test_register_user_success(self, unique_user_create_dto):
        token_pair = await self.auth_user_use_cases.register(
            user_data=unique_user_create_dto
        )

        assert isinstance(token_pair, TokenPairDTO)
        assert token_pair.access_token is not None
        assert token_pair.refresh_token is not None
        self.token_service.decode_token(token_pair.access_token)
        self.token_service.decode_token(token_pair.refresh_token)

        async with self.unit_of_work as uow:
            user = await uow.user_repository.get_by_username(
                unique_user_create_dto.username
            )

            assert user is not None
            assert user.username == unique_user_create_dto.username
            assert user.email == unique_user_create_dto.email
            assert self.password_hasher.verify(
                unique_user_create_dto.password, user.hashed_password
            )

    async def test_register_user_already_exists(self, unique_user_create_dto):
        await self._create_user_with_hashed_password(unique_user_create_dto)

        with pytest.raises(UserAlreadyExists):
            await self.auth_user_use_cases.register(user_data=unique_user_create_dto)

    async def test_login_success(self, unique_user_create_dto):
        await self._create_user_with_hashed_password(unique_user_create_dto)
        token_pair = await self.auth_user_use_cases.login(
            username=unique_user_create_dto.username,
            password=unique_user_create_dto.password,
        )

        assert isinstance(token_pair, TokenPairDTO)
        assert token_pair.access_token is not None
        assert token_pair.refresh_token is not None
        self.token_service.decode_token(token_pair.access_token)
        self.token_service.decode_token(token_pair.refresh_token)

    async def test_login_user_not_found(self):
        with pytest.raises(UserNotFound):
            await self.auth_user_use_cases.login(
                username="nonexistent_user", password="password123"
            )

    async def test_login_invalid_password(self, unique_user_create_dto):
        await self._create_user_with_hashed_password(unique_user_create_dto)

        with pytest.raises(InvalidCredentials):
            await self.auth_user_use_cases.login(
                username=unique_user_create_dto.username, password="wrong_password"
            )

    async def test_refresh_success(self, unique_user_create_dto):
        user = await self._create_user_with_hashed_password(unique_user_create_dto)
        refresh_token = self.token_service.create_token(
            subject=str(user.id), expires_delta=timedelta(days=7)
        )
        new_token_pair = await self.auth_user_use_cases.refresh(refresh_token)

        assert isinstance(new_token_pair, TokenPairDTO)
        assert new_token_pair.access_token is not None
        assert new_token_pair.refresh_token is not None
        access_payload = self.token_service.decode_token(new_token_pair.access_token)
        refresh_payload = self.token_service.decode_token(new_token_pair.refresh_token)
        assert access_payload.sub == str(user.id)
        assert refresh_payload.sub == str(user.id)

    async def test_refresh_user_not_found(self):
        non_existent_user_id = uuid4()
        refresh_token = self.token_service.create_token(
            subject=str(non_existent_user_id), expires_delta=timedelta(days=7)
        )

        with pytest.raises(UserNotFound):
            await self.auth_user_use_cases.refresh(refresh_token)

    async def test_refresh_invalid_token(self):
        with pytest.raises(Exception):
            await self.auth_user_use_cases.refresh("invalid_token")

    async def test_refresh_expired_token(self, unique_user_create_dto):
        user = await self._create_user_with_hashed_password(unique_user_create_dto)
        expired_refresh_token = self.token_service.create_token(
            subject=str(user.id), expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(Exception):
            await self.auth_user_use_cases.refresh(expired_refresh_token)

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
    async def test_register_user_conflicts(
        self,
        change_field,
        value,
        error_message,
        unique_user_create_dto,
        unique_user_entity,
    ):
        await self._create_user_with_hashed_password(unique_user_create_dto)
        conflicting_user_data = UserCreateDTO(
            username=value
            if change_field == "username"
            else unique_user_create_dto.username,
            email=value if change_field == "email" else unique_user_create_dto.email,
            password="password123",
        )

        with pytest.raises(UserAlreadyExists, match=error_message):
            await self.auth_user_use_cases.register(user_data=conflicting_user_data)
