from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.core.constants import BudgetPeriod
from expenses_tracker.domain.entities.budget import Budget
from expenses_tracker.domain.repositories.budget import IBudgetRepository
from expenses_tracker.infrastructure.database.models import BudgetModel


class SQLAlchemyBudgetRepository(IBudgetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, budget_id: UUID) -> Budget | None:
        stmt = select(BudgetModel).where(BudgetModel.id == budget_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Budget]:
        stmt = select(BudgetModel).where(BudgetModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Budget]:
        stmt = select(BudgetModel).where(
            and_(
                BudgetModel.user_id == user_id,
                BudgetModel.start_date >= start_date,
                BudgetModel.end_date <= end_date,
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Budget]:
        stmt = select(BudgetModel).where(
            and_(BudgetModel.user_id == user_id, BudgetModel.category_id == category_id)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_active_budgets_by_user_id(
        self, user_id: UUID, current_date: datetime
    ) -> list[Budget]:
        stmt = select(BudgetModel).where(
            and_(
                BudgetModel.user_id == user_id,
                BudgetModel.start_date <= current_date,
                BudgetModel.end_date >= current_date,
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_by_user_id_and_period(
        self, user_id: UUID, period: BudgetPeriod
    ) -> list[Budget]:
        stmt = select(BudgetModel).where(
            and_(BudgetModel.user_id == user_id, BudgetModel.period == period)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def create(self, budget: Budget) -> Budget:
        model = BudgetModel.from_entity(budget)
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def update(self, budget: Budget) -> Budget:
        model = BudgetModel.from_entity(budget)
        model = await self._session.merge(model)
        await self._session.flush()
        return model.to_entity()

    async def delete(self, budget: Budget) -> None:
        model = await self._session.get(BudgetModel, budget.id)
        if model:
            await self._session.delete(model)

    async def get_total_budget_amount_for_period(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        stmt = select(BudgetModel.amount).where(
            and_(
                BudgetModel.user_id == user_id,
                BudgetModel.start_date >= start_date,
                BudgetModel.end_date <= end_date,
            )
        )
        result = await self._session.execute(stmt)
        amounts = result.scalars().all()
        return sum(amounts) if amounts else 0.0
