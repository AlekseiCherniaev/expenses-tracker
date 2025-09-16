from uuid import UUID

from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.repositories.category import ICategoryRepository


class DummyCategoryRepository(ICategoryRepository):
    def __init__(self) -> None:
        self.categories: dict[UUID, Category] = {}

    async def get_by_id(self, category_id: UUID) -> Category | None:
        return self.categories.get(category_id)

    async def get_all_by_user_id(self, user_id: UUID) -> list[Category]:
        return [
            category
            for category in self.categories.values()
            if category.user_id == user_id
        ]

    async def create(self, category: Category) -> Category:
        self.categories[category.id] = category
        return category

    async def update(self, category: Category) -> Category:
        self.categories[category.id] = category
        return category

    async def delete(self, category: Category) -> None:
        self.categories.pop(category.id, None)
