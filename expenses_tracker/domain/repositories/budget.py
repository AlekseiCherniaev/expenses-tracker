from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget


class IBudgetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, budget_id: UUID) -> Optional[Budget]:
        pass

    @abstractmethod
    async def get_all_by_user_id(self, user_id: UUID) -> list[Budget]:
        pass

    @abstractmethod
    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Budget]:
        pass

    @abstractmethod
    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Budget]:
        pass

    @abstractmethod
    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[Budget]:
        pass

    @abstractmethod
    async def get_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[Budget]:
        pass

    @abstractmethod
    async def create(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    async def update(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    async def delete(self, budget: Budget) -> None:
        pass

    @abstractmethod
    async def get_total_budget_amount_for_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        pass
