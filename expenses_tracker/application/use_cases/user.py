from datetime import datetime
from uuid import UUID

import structlog

from expenses_tracker.application.dto.user import UserDTO, UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.interfaces.password_hasher import IPasswordHasher
from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.exceptions import UserAlreadyExists, UserNotFound
from expenses_tracker.domain.repositories.user import IUserRepository

logger = structlog.get_logger(__name__)


class UserUseCases:
    def __init__(
        self, user_repository: IUserRepository, password_hasher: IPasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def get_user(self, user_id: UUID) -> UserDTO | None:
        user = await self.user_repository.get_by_id(user_id=user_id)
        if not user:
            raise UserNotFound(f"User with id {user_id} not found")
        logger.bind(user=user).debug("Retrieved user from repo")
        return UserDTO(
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            id=user.id,
        )

    async def create_user(self, user_data: UserCreateDTO) -> UserDTO:
        await self._validate_user_uniqueness(
            new_email=user_data.email, new_username=user_data.username
        )
        hashed_password = self.password_hasher.hash(password=user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            email=user_data.email,
        )
        user = await self.user_repository.create(user=new_user)
        logger.bind(user=user).debug("Created user from repo")
        return UserDTO(
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            id=user.id,
        )

    async def _validate_user_uniqueness(
        self, new_email: str | None = None, new_username: str | None = None
    ) -> None:
        """Checks if user with given email or username already exists"""
        if new_email and await self.user_repository.get_by_email(new_email):
            raise UserAlreadyExists(f"User with email {new_email} already exists")

        if new_username and await self.user_repository.get_by_username(new_username):
            raise UserAlreadyExists(f"User with username {new_username} already exists")

    async def update_user(self, user_data: UserUpdateDTO) -> UserDTO:
        user = await self.user_repository.get_by_id(user_id=user_data.id)
        if not user:
            raise UserNotFound(f"User with id {user_data.id} not found")
        if user_data.email and user_data.email != user.email:
            await self._validate_user_uniqueness(new_email=user_data.email)
            user.email = user_data.email
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.password is not None:
            user.hashed_password = self.password_hasher.hash(
                password=user_data.password
            )
        user.updated_at = datetime.now()
        updated_user = await self.user_repository.update(user=user)
        logger.bind(user=updated_user).debug("Updated user from repo")
        return UserDTO(
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            id=user.id,
        )

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.user_repository.get_by_id(user_id=user_id)
        if not user:
            raise UserNotFound(f"User with id {user_id} not found")
        await self.user_repository.delete(user_id=user_id)
        logger.bind(user=user).debug("Deleted user from repo")
        return None
