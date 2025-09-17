from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.token import TokenPairDTO
from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.auth import (
    InvalidCredentials,
    TokenExpired,
    InvalidToken,
)
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
def user_create_dto(user_entity):
    return UserCreateDTO(
        username=user_entity.username, email=user_entity.email, password="password123"
    )


@fixture
def token_pair_dto():
    return TokenPairDTO(
        access_token="access_token", refresh_token="refresh_token", token_type="bearer"
    )


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


@fixture
def mock_token_service(token_pair_dto):
    mock_service = Mock(spec=ITokenService)
    mock_service.create_token.return_value = "test_token"
    mock_service.decode_token.return_value = Mock(sub=str(uuid4()))
    return mock_service


@fixture()
def random_uuid():
    return uuid4()


class TestAuthUserUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work, mock_password_hasher, mock_token_service):
        self.auth_use_cases = AuthUserUseCases(
            unit_of_work=mock_unit_of_work,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
        )
        self.mock_unit_of_work = mock_unit_of_work
        self.mock_hasher = mock_password_hasher
        self.mock_token_service = mock_token_service

    async def test_create_tokens_for_user_success(
        self, user_entity, mock_token_service
    ):
        expected_access_token = "access_token"
        expected_refresh_token = "refresh_token"
        mock_token_service.create_token.side_effect = [
            expected_access_token,
            expected_refresh_token,
        ]
        result = self.auth_use_cases._create_tokens_for_user(user_entity)

        assert isinstance(result, TokenPairDTO)
        assert result.access_token == expected_access_token
        assert result.refresh_token == expected_refresh_token
        assert result.token_type == "bearer"
        assert mock_token_service.create_token.call_count == 2
        calls = mock_token_service.create_token.call_args_list
        assert calls[0][1]["subject"] == str(user_entity.id)
        assert calls[1][1]["subject"] == str(user_entity.id)

    async def test_validate_user_uniqueness_success(
        self, mock_unit_of_work, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        result = await self.auth_use_cases._validate_user_uniqueness(
            uow=mock_unit_of_work.__aenter__.return_value,
            new_username=user_entity.username,
            new_email=user_entity.email,
        )

        assert result is None
        mock_repo.get_by_email.assert_called_once_with(user_entity.email)
        mock_repo.get_by_username.assert_called_once_with(user_entity.username)

    async def test_validate_user_uniqueness_email_conflict(
        self, mock_unit_of_work, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = user_entity

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with email {user_entity.email} already exists",
        ):
            await self.auth_use_cases._validate_user_uniqueness(
                uow=mock_unit_of_work.__aenter__.return_value,
                new_email=user_entity.email,
            )

    async def test_validate_user_uniqueness_username_conflict(
        self, mock_unit_of_work, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_username.return_value = user_entity

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with username {user_entity.username} already exists",
        ):
            await self.auth_use_cases._validate_user_uniqueness(
                uow=mock_unit_of_work.__aenter__.return_value,
                new_username=user_entity.username,
            )

    async def test_register_success(
        self,
        mock_unit_of_work,
        mock_password_hasher,
        mock_token_service,
        user_entity,
        user_create_dto,
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        mock_repo.create.return_value = user_entity
        mock_token_service.create_token.return_value = "test_token"
        result = await self.auth_use_cases.register(user_create_dto)

        assert isinstance(result, TokenPairDTO)
        mock_repo.get_by_email.assert_called_once_with(user_create_dto.email)
        mock_repo.get_by_username.assert_called_once_with(user_create_dto.username)
        mock_password_hasher.hash.assert_called_once_with(
            password=user_create_dto.password
        )
        mock_repo.create.assert_called_once()
        assert mock_token_service.create_token.call_count == 2

    async def test_register_user_already_exists(
        self, mock_unit_of_work, user_entity, user_create_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_email.return_value = user_entity

        with pytest.raises(
            UserAlreadyExists,
            match=f"User with email {user_entity.email} already exists",
        ):
            await self.auth_use_cases.register(user_create_dto)

    async def test_login_success(
        self, mock_unit_of_work, mock_password_hasher, mock_token_service, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_username.return_value = user_entity
        mock_token_service.create_token.return_value = "test_token"
        result = await self.auth_use_cases.login(
            username=user_entity.username, password="password123"
        )

        assert isinstance(result, TokenPairDTO)
        mock_repo.get_by_username.assert_called_once_with(user_entity.username)
        mock_password_hasher.verify.assert_called_once_with(
            password="password123", hashed=user_entity.hashed_password
        )
        assert mock_token_service.create_token.call_count == 2

    async def test_login_user_not_found(self, mock_unit_of_work):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_username.return_value = None

        with pytest.raises(
            UserNotFound, match="User with username nonexistent not found"
        ):
            await self.auth_use_cases.login(
                username="nonexistent", password="password123"
            )

    async def test_login_invalid_credentials(
        self, mock_unit_of_work, mock_password_hasher, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_repo.get_by_username.return_value = user_entity
        mock_password_hasher.verify.return_value = False

        with pytest.raises(
            InvalidCredentials,
            match=f"Invalid credentials for user {user_entity.username}",
        ):
            await self.auth_use_cases.login(
                username=user_entity.username, password="wrong_password"
            )

    async def test_refresh_success(
        self, mock_unit_of_work, mock_token_service, user_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_payload = Mock(sub=str(user_entity.id))
        mock_token_service.decode_token.return_value = mock_payload
        mock_repo.get_by_id.return_value = user_entity
        mock_token_service.create_token.return_value = "test_token"
        result = await self.auth_use_cases.refresh("valid_refresh_token")

        assert isinstance(result, TokenPairDTO)
        mock_token_service.decode_token.assert_called_once_with("valid_refresh_token")
        mock_repo.get_by_id.assert_called_once_with(user_id=user_entity.id)
        assert mock_token_service.create_token.call_count == 2

    async def test_refresh_user_not_found(
        self, mock_unit_of_work, mock_token_service, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.user_repository
        mock_payload = Mock(sub=str(random_uuid))
        mock_token_service.decode_token.return_value = mock_payload
        mock_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFound, match=f"User with id {random_uuid} not found"):
            await self.auth_use_cases.refresh("valid_refresh_token")

    async def test_refresh_invalid_token(self, mock_token_service):
        mock_token_service.decode_token.side_effect = InvalidToken("Invalid token")

        with pytest.raises(InvalidToken, match="Invalid token"):
            await self.auth_use_cases.refresh("invalid_token")

    async def test_refresh_expired_token(self, mock_token_service):
        mock_token_service.decode_token.side_effect = TokenExpired("Token has expired")

        with pytest.raises(TokenExpired, match="Token has expired"):
            await self.auth_use_cases.refresh("expired_token")
