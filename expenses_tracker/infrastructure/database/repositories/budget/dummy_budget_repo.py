from datetime import datetime
from typing import Optional
from uuid import UUID

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.repositories.budget import IBudgetRepository


class DummyBudgetRepository(IBudgetRepository):
    def __init__(self) -> None:
        self.budgets: dict[UUID, Budget] = {}

    async def get_by_id(self, budget_id: UUID) -> Optional[Budget]:
        return self.budgets.get(budget_id)

    async def get_all_by_user_id(self, user_id: UUID) -> list[Budget]:
        return [budget for budget in self.budgets.values() if budget.user_id == user_id]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Budget]:
        return [
            budget
            for budget in self.budgets.values()
            if (
                budget.user_id == user_id
                and budget.start_date >= start_date
                and budget.end_date <= end_date
            )
        ]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Budget]:
        return [
            budget
            for budget in self.budgets.values()
            if (budget.user_id == user_id and budget.category_id == category_id)
        ]

    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[Budget]:
        return [
            budget
            for budget in self.budgets.values()
            if (
                budget.user_id == user_id
                and budget.start_date <= current_date <= budget.end_date
            )
        ]

    async def get_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[Budget]:
        return [
            budget
            for budget in self.budgets.values()
            if (budget.user_id == user_id and budget.period == period)
        ]

    async def create(self, budget: Budget) -> Budget:
        self.budgets[budget.id] = budget
        return budget

    async def update(self, budget: Budget) -> Budget:
        self.budgets[budget.id] = budget
        return budget

    async def delete(self, budget: Budget) -> None:
        self.budgets.pop(budget.id, None)

    async def get_total_budget_amount_for_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        user_budgets = [
            budget
            for budget in self.budgets.values()
            if (
                budget.user_id == user_id
                and budget.start_date >= start_date
                and budget.end_date <= end_date
            )
        ]
        return sum(budget.amount for budget in user_budgets)
