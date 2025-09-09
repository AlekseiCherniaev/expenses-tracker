from datetime import datetime
from uuid import UUID

from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.user import IUserRepository


class DummyUserRepository(IUserRepository):
    async def get_by_id(self, user_id: UUID) -> User | None:
        return User(
            id=user_id,
            username="test",
            hashed_password="hashed_test",
            email="testemail@gmail.com",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    async def get_by_email(self, email: str) -> User | None:
        return None

    async def get_by_username(self, username: str) -> User | None:
        return None

    async def get_all(self) -> list[User]:
        return [
            User(
                username="test",
                hashed_password="hashed_test",
                email="testemail@gmail.com",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            User(
                username="test2",
                hashed_password="hashed_test2",
                email="testemail2@gmail.com",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

    async def create(self, user: User) -> User:
        return User(
            username=user.username,
            hashed_password=user.hashed_password,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def update(self, user: User) -> User:
        return User(
            username=user.username,
            hashed_password=user.hashed_password,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def delete(self, user_id: UUID) -> None:
        return None
