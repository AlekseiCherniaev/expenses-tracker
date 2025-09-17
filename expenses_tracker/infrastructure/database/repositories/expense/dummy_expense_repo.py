from datetime import datetime
from uuid import UUID

from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.repositories.expense import IExpenseRepository


class DummyExpenseRepository(IExpenseRepository):
    def __init__(self) -> None:
        self.expenses: dict[UUID, Expense] = {}

    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        return self.expenses.get(expense_id)

    async def get_all_by_user_id(self, user_id: UUID) -> list[Expense]:
        return [
            expense for expense in self.expenses.values() if expense.user_id == user_id
        ]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Expense]:
        return [
            expense
            for expense in self.expenses.values()
            if expense.user_id == user_id and start_date <= expense.date <= end_date
        ]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Expense]:
        return [
            expense
            for expense in self.expenses.values()
            if expense.user_id == user_id and expense.category_id == category_id
        ]

    async def create(self, expense: Expense) -> Expense:
        self.expenses[expense.id] = expense
        return expense

    async def update(self, expense: Expense) -> Expense:
        self.expenses[expense.id] = expense
        return expense

    async def delete(self, expense: Expense) -> None:
        self.expenses.pop(expense.id, None)
