from types import TracebackType
from typing import Type

from expenses_tracker.domain.repositories.budget import IBudgetRepository
from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.expense import IExpenseRepository
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.repositories.budget.dummy_budget_repo import (
    DummyBudgetRepository,
)
from expenses_tracker.infrastructure.database.repositories.category.dummy_category_repo import (
    DummyCategoryRepository,
)
from expenses_tracker.infrastructure.database.repositories.expense.dummy_expense_repo import (
    DummyExpenseRepository,
)
from expenses_tracker.infrastructure.database.repositories.user.dummy_user_repo import (
    DummyUserRepository,
)


class DummyUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._user_repository = DummyUserRepository()
        self._category_repository = DummyCategoryRepository()
        self._expense_repository = DummyExpenseRepository()
        self._budget_repository = DummyBudgetRepository()

    @property
    def user_repository(self) -> IUserRepository:
        return self._user_repository

    @property
    def category_repository(self) -> ICategoryRepository:
        return self._category_repository

    @property
    def expense_repository(self) -> IExpenseRepository:
        return self._expense_repository

    @property
    def budget_repository(self) -> IBudgetRepository:
        return self._budget_repository

    async def __aenter__(self) -> "DummyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        return False
