from abc import ABC, abstractmethod
from types import TracebackType
from typing import Type

from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.expense import IExpenseRepository
from expenses_tracker.domain.repositories.user import IUserRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def user_repository(self) -> IUserRepository:
        pass

    @property
    @abstractmethod
    def category_repository(self) -> ICategoryRepository:
        pass

    @property
    @abstractmethod
    def expense_repository(self) -> IExpenseRepository:
        pass

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        pass
