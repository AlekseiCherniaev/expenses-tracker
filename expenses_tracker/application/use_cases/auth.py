from datetime import timedelta
from uuid import UUID

import structlog

from expenses_tracker.application.dto.token import TokenPairDTO
from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.auth import InvalidCredentials
from expenses_tracker.domain.exceptions.user import UserAlreadyExists, UserNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class AuthUserUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ):
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._token_service = token_service

    def _create_tokens_for_user(self, user: User) -> TokenPairDTO:
        access_token = self._token_service.create_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=get_settings().access_token_expire_minutes),
        )
        refresh_token = self._token_service.create_token(
            subject=str(user.id),
            expires_delta=timedelta(days=get_settings().refresh_token_expire_days),
        )
        return TokenPairDTO(access_token=access_token, refresh_token=refresh_token)

    async def _validate_user_uniqueness(
        self,
        uow: IUnitOfWork,
        new_email: str | None = None,
        new_username: str | None = None,
    ) -> None:
        """Checks if user with given email or username already exists"""
        if new_email and await uow.user_repository.get_by_email(new_email):
            raise UserAlreadyExists(f"User with email {new_email} already exists")

        if new_username and await uow.user_repository.get_by_username(new_username):
            raise UserAlreadyExists(f"User with username {new_username} already exists")

    async def register(self, user_data: UserCreateDTO) -> TokenPairDTO:
        async with self._unit_of_work as uow:
            await self._validate_user_uniqueness(
                uow=uow, new_email=user_data.email, new_username=user_data.username
            )
            hashed_password = self._password_hasher.hash(password=user_data.password)
            new_user = User(
                username=user_data.username,
                hashed_password=hashed_password,
                email=user_data.email,
            )
            user = await uow.user_repository.create(user=new_user)
            logger.bind(user=user).debug("Created user from repo")
            return self._create_tokens_for_user(user=user)
        assert False, "unreachable"

    async def login(self, username: str, password: str) -> TokenPairDTO:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_username(username)
            if not user:
                raise UserNotFound(f"User with username {username} not found")
            if not self._password_hasher.verify(
                password=password, hashed=user.hashed_password
            ):
                raise InvalidCredentials(f"Invalid credentials for user {username}")
            return self._create_tokens_for_user(user)
        assert False, "unreachable"

    async def refresh(self, refresh_token: str) -> TokenPairDTO:
        async with self._unit_of_work as uow:
            payload = self._token_service.decode_token(refresh_token)
            user_id = UUID(payload.sub)
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")
            return self._create_tokens_for_user(user)
        assert False, "unreachable"
