from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.domain.entities.expense import Expense
from expenses_tracker.domain.repositories.expense import IExpenseRepository
from expenses_tracker.infrastructure.database.models.expense import ExpenseModel


class SQLAlchemyExpenseRepository(IExpenseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        stmt = select(ExpenseModel).where(ExpenseModel.id == expense_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Expense]:
        stmt = select(ExpenseModel).where(ExpenseModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_by_user_id_and_date_range(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Expense]:
        stmt = select(ExpenseModel).where(
            ExpenseModel.user_id == user_id,
            ExpenseModel.date >= start_date,
            ExpenseModel.date <= end_date,
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def get_by_user_id_and_category_id(
        self, user_id: UUID, category_id: UUID
    ) -> list[Expense]:
        stmt = select(ExpenseModel).where(
            ExpenseModel.user_id == user_id, ExpenseModel.category_id == category_id
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def create(self, expense: Expense) -> Expense:
        model = ExpenseModel.from_entity(expense)
        self._session.add(model)
        return model.to_entity()

    async def update(self, expense: Expense) -> Expense:
        model = ExpenseModel.from_entity(expense)
        await self._session.merge(model)
        return expense

    async def delete(self, expense: Expense) -> None:
        model = await self._session.get(ExpenseModel, expense.id)
        if model:
            await self._session.delete(model)
