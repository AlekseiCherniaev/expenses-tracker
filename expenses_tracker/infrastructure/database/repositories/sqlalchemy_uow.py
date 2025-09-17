from types import TracebackType
from typing import Callable, Type

from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.domain.repositories.budget import IBudgetRepository
from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.domain.repositories.expense import IExpenseRepository
from expenses_tracker.domain.repositories.uow import IUnitOfWork
from expenses_tracker.domain.repositories.user import IUserRepository
from expenses_tracker.infrastructure.database.repositories.budget.sqlalchemy_budget_repo import (
    SQLAlchemyBudgetRepository,
)
from expenses_tracker.infrastructure.database.repositories.category.sqlalchemy_category_repo import (
    SQLAlchemyCategoryRepository,
)
from expenses_tracker.infrastructure.database.repositories.expense.sqlalchemy_expense_repo import (
    SQLAlchemyExpenseRepository,
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
        self._expense_repository: SQLAlchemyExpenseRepository | None = None
        self._budget_repository: SQLAlchemyBudgetRepository | None = None

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

    @property
    def expense_repository(self) -> IExpenseRepository:
        if not self._expense_repository:
            raise RuntimeError("Repository accessed outside of UnitOfWork context")
        return self._expense_repository

    @property
    def budget_repository(self) -> IBudgetRepository:
        if not self._budget_repository:
            raise RuntimeError("Repository accessed outside of UnitOfWork context")
        return self._budget_repository

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._user_repository = SQLAlchemyUserRepository(self._session)
        self._category_repository = SQLAlchemyCategoryRepository(self._session)
        self._expense_repository = SQLAlchemyExpenseRepository(self._session)
        self._budget_repository = SQLAlchemyBudgetRepository(self._session)
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
