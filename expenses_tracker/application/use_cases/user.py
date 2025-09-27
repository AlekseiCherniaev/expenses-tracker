from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions.user import UserAlreadyExists, UserNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class UserUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        cache_service: ICacheService[UserDTO],
    ):
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._cache_service = cache_service

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        return UserDTO(
            username=user.username,
            email=user.email,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_refresh_jti=user.last_refresh_jti,
            avatar_url=user.avatar_url,
            id=user.id,
        )

    @staticmethod
    def _user_cache_key(user_id: UUID) -> str:
        return f"user:{user_id}"

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

    async def get_user(self, user_id: UUID) -> UserDTO:
        cache_key = self._user_cache_key(user_id)
        cached_user = await self._cache_service.get(key=cache_key, serializer=UserDTO)
        if cached_user:
            logger.bind(user_id=cached_user.id).debug("Retrieved user from cache")
            return cached_user

        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            user_dto = self._to_dto(user)
            await self._cache_service.set(
                key=cache_key, value=user_dto, ttl=get_settings().user_dto_ttl_seconds
            )
            logger.bind(user_id=user_dto.id).debug(
                "Retrieved user from repo and cached"
            )
            return user_dto
        assert False, "unreachable"

    async def get_all_users(self) -> list[UserDTO]:
        async with self._unit_of_work as uow:
            users = await uow.user_repository.get_all()
            logger.bind(count=len(users)).debug("Retrieved users from repo")
            return [self._to_dto(user) for user in users]
        assert False, "unreachable"

    async def create_user(self, user_data: UserCreateDTO) -> UserDTO:
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
            logger.bind(user=user).debug("Created user in repo")

            user_dto = self._to_dto(user)
            await self._cache_service.set(
                key=self._user_cache_key(user_dto.id),
                value=user_dto,
                ttl=get_settings().user_dto_ttl_seconds,
            )
            return user_dto
        assert False, "unreachable"

    async def update_user(self, user_data: UserUpdateDTO) -> UserDTO | None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id=user_data.id)
            if not user:
                raise UserNotFound(f"User with id {user_data.id} not found")

            if user_data.email and user_data.email != user.email:
                await self._validate_user_uniqueness(uow=uow, new_email=user_data.email)
                user.email = user_data.email
            if user_data.email_verified is not None:
                user.email_verified = user_data.email_verified
            if user_data.password is not None:
                user.hashed_password = self._password_hasher.hash(
                    password=user_data.password
                )
            user.updated_at = datetime.now(timezone.utc)

            updated_user = await uow.user_repository.update(user=user)
            logger.bind(user=updated_user).debug("Updated user in repo")

            user_dto = self._to_dto(updated_user)
            await self._cache_service.set(
                key=self._user_cache_key(user_dto.id),
                value=user_dto,
                ttl=get_settings().user_dto_ttl_seconds,
            )
            return user_dto
        assert False, "unreachable"

    async def delete_user(self, user_id: UUID) -> None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")
            await uow.user_repository.delete(user=user)
            logger.bind(user=user).debug("Deleted user in repo")

        await self._cache_service.delete(key=self._user_cache_key(user_id))
        return None
