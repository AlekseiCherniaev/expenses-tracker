from types import TracebackType
from typing import Callable, Type

from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.repositories.category.sqlalchemy_category_repo import (
    SQLAlchemyCategoryRepository,
)
from expenses_tracker.infrastructure.database.repositories.user.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._user_repository: SQLAlchemyUserRepository | None = None
        self._category_repository: SQLAlchemyCategoryRepository | None = None

    @property
    def user_repository(self) -> IUserRepository:
        if not self._user_repository:
            raise RuntimeError("Repository accessed outside of UnitOfWork context")
        return self._user_repository

    @property
    def category_repository(self) -> ICategoryRepository:
        if not self._category_repository:
            raise RuntimeError("Repository accessed outside of UnitOfWork context")
        return self._category_repository

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._user_repository = SQLAlchemyUserRepository(self._session)
        self._category_repository = SQLAlchemyCategoryRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if not self._session:
            return False
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
        return False
