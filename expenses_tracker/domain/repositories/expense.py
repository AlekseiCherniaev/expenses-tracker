from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from expenses_tracker.domain.entities.expense import Expense


class IExpenseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        pass

    @abstractmethod
    async def get_all_by_user_id(self, user_id: UUID) -> list[Expense]:
        pass

    @abstractmethod
    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Expense]:
        pass

    @abstractmethod
    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Expense]:
        pass

    @abstractmethod
    async def create(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def update(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def delete(self, expense: Expense) -> None:
        pass
