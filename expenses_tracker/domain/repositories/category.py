from abc import ABC, abstractmethod
from uuid import UUID

from expenses_tracker.domain.entities.category import Category


class ICategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None:
        pass

    @abstractmethod
    async def get_all_by_user_id(self, user_id: UUID) -> list[Category]:
        pass

    @abstractmethod
    async def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def delete(self, category: Category) -> None:
        pass
