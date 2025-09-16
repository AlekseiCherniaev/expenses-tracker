from types import TracebackType
from typing import Type

from psycopg import AsyncConnection

from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.repositories.dummy_category_repo import (
    DummyCategoryRepository,
)
from expenses_tracker.infrastructure.database.repositories.psycopg_user_repo import (
    PsycopgUserRepository,
)


class PsycopgUnitOfWork(IUnitOfWork):
    def __init__(self, dns: str) -> None:
        self.dns: str = dns
        self._user_repository: PsycopgUserRepository | None = None
        self._category_repository = DummyCategoryRepository()

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

    async def __aenter__(self) -> "PsycopgUnitOfWork":
        self._conn = await AsyncConnection.connect(self.dns)
        self._user_repository = PsycopgUserRepository(conn=self._conn)
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        try:
            if exc_type is None:
                await self._conn.commit()
            else:
                await self._conn.rollback()
        finally:
            await self._conn.close()
        return False
