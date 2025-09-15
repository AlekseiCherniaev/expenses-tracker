from types import TracebackType
from typing import Type

from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.repositories.dummy_user_repo import (
    DummyUserRepository,
)


class DummyUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._user_repository = DummyUserRepository()

    @property
    def user_repository(self) -> IUserRepository:
        return self._user_repository

    async def __aenter__(self) -> "DummyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        return False
