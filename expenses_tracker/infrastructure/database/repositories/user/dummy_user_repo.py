from uuid import UUID

from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.user import IUserRepository


class DummyUserRepository(IUserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    async def get_by_email(self, email: str) -> User | None:
        return next(
            (
                u
                for u in self.users.values()
                if u.email == email and u.email_verified is True
            ),
            None,
        )

    async def get_all(self) -> list[User]:
        return list(self.users.values())

    async def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def update_last_refresh_jti(self, user_id: UUID, jti: str | None) -> None:
        user = self.users.get(user_id)
        if user:
            user.last_refresh_jti = jti
            self.users[user_id] = user

    async def update_avatar_url(self, user_id: UUID, avatar_url: str | None) -> None:
        user = self.users.get(user_id)
        if user:
            user.avatar_url = avatar_url
            self.users[user_id] = user

    async def get_for_update(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def delete(self, user: User) -> None:
        self.users.pop(user.id, None)
