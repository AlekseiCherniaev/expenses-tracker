from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.repositories.category import ICategoryRepository
from expenses_tracker.infrastructure.database.models import CategoryModel


class SQLAlchemyCategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_all_by_user_id(self, user_id: UUID) -> list[Category]:
        stmt = select(CategoryModel).where(CategoryModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def create(self, category: Category) -> Category:
        model = CategoryModel.from_entity(category)
        self._session.add(model)
        return model.to_entity()

    async def update(self, category: Category) -> Category:
        model = CategoryModel.from_entity(category)
        await self._session.merge(model)
        return category

    async def delete(self, category: Category) -> None:
        model = await self._session.get(CategoryModel, category.id)
        if model:
            await self._session.delete(model)
