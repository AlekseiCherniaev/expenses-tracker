from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.domain.entities.user import User
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email, UserModel.email_verified.is_(True)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_all(self) -> list[User]:
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def create(self, user: User) -> User:
        model = UserModel.from_entity(user)
        self._session.add(model)
        return model.to_entity()

    async def update(self, user: User) -> User:
        model = UserModel.from_entity(user)
        await self._session.merge(model)
        return user

    async def update_last_refresh_jti(self, user_id: UUID, jti: str | None) -> None:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                last_refresh_jti=jti,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def update_avatar_url(self, user_id: UUID, avatar_url: str | None) -> None:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                avatar_url=avatar_url,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def get_for_update(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id).with_for_update()
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def delete(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model:
            await self._session.delete(model)
