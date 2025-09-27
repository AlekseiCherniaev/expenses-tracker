from datetime import timedelta, datetime
from uuid import UUID, uuid4

import structlog

from expenses_tracker.application.dto.token import TokenPairDTO
from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.application.interfaces.email_service import IEmailService
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.constants import TokenType
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.token_payload import TokenPayload
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.auth import (
    InvalidCredentials,
    EmailAlreadyVerified,
)
from expenses_tracker.domain.exceptions.user import UserAlreadyExists, UserNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class AuthUserUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        email_service: IEmailService,
        cache_service: ICacheService[TokenPayload],
    ):
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._token_service = token_service
        self.email_service = email_service
        self._cache_service = cache_service

    @staticmethod
    def _refresh_token_cache_key(jti: str) -> str:
        return f"blacklist:refresh:{jti}"

    @staticmethod
    def _user_cache_key(user_id: UUID) -> str:
        return f"user:{user_id}"

    def _create_tokens_for_user(self, user: User, refresh_jti: str) -> TokenPairDTO:
        access_token = self._token_service.create_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=get_settings().access_token_expire_minutes),
            token_type=TokenType.ACCESS,
        )
        refresh_token = self._token_service.create_token(
            subject=str(user.id),
            jti=refresh_jti,
            expires_delta=timedelta(days=get_settings().refresh_token_expire_days),
            token_type=TokenType.REFRESH,
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
            refresh_jti = str(uuid4())
            new_user = User(
                username=user_data.username,
                hashed_password=hashed_password,
                email=user_data.email,
                last_refresh_jti=refresh_jti,
            )
            user = await uow.user_repository.create(user=new_user)
            logger.bind(username=user_data.username).debug("Created user in repo")
            return self._create_tokens_for_user(user=user, refresh_jti=refresh_jti)
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

            refresh_jti = str(uuid4())
            await uow.user_repository.update_last_refresh_jti(
                user_id=user.id, jti=refresh_jti
            )
            return self._create_tokens_for_user(user=user, refresh_jti=refresh_jti)
        assert False, "unreachable"

    async def refresh(self, refresh_token: str) -> TokenPairDTO:
        payload = self._token_service.decode_token(refresh_token)

        if payload.type != TokenType.REFRESH:
            raise InvalidCredentials("Provided token is not a refresh token")

        key = self._refresh_token_cache_key(payload.jti)
        blacklisted = await self._cache_service.get(key=key, serializer=TokenPayload)
        if blacklisted:
            raise InvalidCredentials("Refresh token is revoked")

        async with self._unit_of_work as uow:
            user_id = UUID(payload.sub)
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            if user.last_refresh_jti != payload.jti:
                raise InvalidCredentials("Refresh token is no longer valid")

            ttl = (
                int(payload.exp - datetime.now().timestamp())
                + get_settings().clock_skew_seconds
            )
            if ttl > 0:
                await self._cache_service.set(key=key, value=payload, ttl=ttl)

            refresh_jti = str(uuid4())
            await uow.user_repository.update_last_refresh_jti(
                user_id=user.id, jti=refresh_jti
            )

            return self._create_tokens_for_user(user=user, refresh_jti=refresh_jti)
        assert False, "unreachable"

    async def logout(self, refresh_token: str) -> None:
        payload = self._token_service.decode_token(refresh_token)
        jti = payload.jti
        ttl = (
            int(payload.exp - datetime.now().timestamp())
            + get_settings().clock_skew_seconds
        )
        if ttl > 0:
            await self._cache_service.set(
                key=self._refresh_token_cache_key(jti),
                value=payload,
                ttl=ttl,
            )
            logger.bind(jti=jti).debug("Refresh token revoked")

        async with self._unit_of_work as uow:
            user_id = UUID(payload.sub)
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            await uow.user_repository.update_last_refresh_jti(user_id=user.id, jti=None)
        return None

    async def request_verify_email(self, user_id: UUID) -> None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            if user.email is None:
                raise InvalidCredentials("User does not have an email to verify")

            if user.email_verified:
                raise EmailAlreadyVerified("Email is already verified")

            email_token = self._token_service.create_token(
                subject=str(user.id),
                expires_delta=timedelta(
                    hours=get_settings().email_verification_token_expire_hours
                ),
                token_type=TokenType.EMAIL_VERIFICATION,
            )

            await self.email_service.send_verification_email(
                to=user.email, token=email_token
            )
            logger.bind(user_id=user.id).debug("Sent email verification email")
        return None

    async def verify_email(self, email_token: str) -> None:
        payload = self._token_service.decode_token(email_token)

        if payload.type != TokenType.EMAIL_VERIFICATION:
            raise InvalidCredentials(
                "Provided token is not an email verification token"
            )

        async with self._unit_of_work as uow:
            user_id = UUID(payload.sub)
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            if user.email_verified:
                raise EmailAlreadyVerified("Email is already verified")

            user.email_verified = True
            await uow.user_repository.update(user=user)
            await self._cache_service.delete(key=self._user_cache_key(user_id))
            logger.bind(user_id=user.id).debug("Verified user email")
        return None

    async def request_password_reset(self, email: str) -> None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_email(email)
            if not user:
                raise UserNotFound(f"User with email {email} not found")

            if user.email is None or user.email_verified is False:
                raise InvalidCredentials(
                    "User does not have an verified email to reset password"
                )

            password_reset_token = self._token_service.create_token(
                subject=str(user.id),
                expires_delta=timedelta(
                    hours=get_settings().password_reset_token_expire_hours
                ),
                token_type=TokenType.RESET_PASSWORD,
            )

            await self.email_service.send_password_reset_email(
                to=user.email, token=password_reset_token
            )
            logger.bind(user_id=user.id).debug("Sent password reset email")
        return None

    async def reset_password(
        self, password_reset_token: str, new_password: str
    ) -> None:
        payload = self._token_service.decode_token(password_reset_token)

        if payload.type != TokenType.RESET_PASSWORD:
            raise InvalidCredentials("Provided token is not a password reset token")

        async with self._unit_of_work as uow:
            user_id = UUID(payload.sub)
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            hashed_password = self._password_hasher.hash(password=new_password)
            user.hashed_password = hashed_password
            user.last_refresh_jti = None  # Invalidate all existing refresh tokens
            await uow.user_repository.update(user=user)
            logger.bind(user_id=user.id).debug("Reset user password")
        return None
