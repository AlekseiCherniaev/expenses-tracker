import secrets
from datetime import timedelta
from uuid import uuid4

import structlog
from authlib.integrations.base_client import OAuthError

from expenses_tracker.application.dto.token import TokenPairDTO
from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.constants import TokenType
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class OAuthUserUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ):
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._token_service = token_service

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

    async def third_party_auth(self, user_data: UserCreateDTO) -> TokenPairDTO:
        async with self._unit_of_work as uow:
            if not user_data.email:
                raise OAuthError("Email is required for third-party authentication")

            user = await uow.user_repository.get_by_email(email=user_data.email)

            refresh_jti = str(uuid4())
            if not user:
                same_user = await uow.user_repository.get_by_username(
                    username=user_data.username
                )
                if same_user:
                    secrets.token_urlsafe(8)
                    user_data.username = (
                        f"{user_data.username}_{secrets.token_urlsafe(8)}"
                    )
                    logger.bind(username=user_data.username).debug(
                        "Username already taken, modified username for new user"
                    )

                hashed_password = self._password_hasher.hash(
                    password=user_data.password
                )
                new_user = User(
                    username=user_data.username,
                    hashed_password=hashed_password,
                    email=user_data.email,
                    avatar_url=user_data.avatar_url,
                    last_refresh_jti=refresh_jti,
                )
                user = await uow.user_repository.create(user=new_user)
                logger.bind(username=user_data.username).debug("Created user in repo")
            else:
                refresh_jti = str(uuid4())
                await uow.user_repository.update_last_refresh_jti(
                    user_id=user.id, jti=refresh_jti
                )
            return self._create_tokens_for_user(user=user, refresh_jti=refresh_jti)
        assert False, "unreachable"
