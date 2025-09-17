from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.category import (
    CategoryDTO,
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.exceptions.category import CategoryNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class CategoryUseCases:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work

    async def get_category(self, category_id: UUID) -> CategoryDTO | None:
        async with self._unit_of_work as uow:
            category = await uow.category_repository.get_by_id(category_id=category_id)
            if not category:
                raise CategoryNotFound(f"Category with id {category_id} not found")
            logger.bind(category=category).debug("Retrieved category from repo")
            return CategoryDTO(
                id=category.id,
                name=category.name,
                user_id=category.user_id,
                description=category.description,
                is_default=category.is_default,
                color=category.color,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
        assert False, "unreachable"

    async def get_categories_by_user_id(self, user_id: UUID) -> list[CategoryDTO]:
        async with self._unit_of_work as uow:
            categories = await uow.category_repository.get_all_by_user_id(
                user_id=user_id
            )
            logger.bind(categories=categories).debug("Retrieved categories from repo")
            return [
                CategoryDTO(
                    id=category.id,
                    name=category.name,
                    user_id=category.user_id,
                    description=category.description,
                    is_default=category.is_default,
                    color=category.color,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                )
                for category in categories
            ]
        assert False, "unreachable"

    async def create_category(self, category_data: CategoryCreateDTO) -> CategoryDTO:
        async with self._unit_of_work as uow:
            new_category = Category(
                user_id=category_data.user_id,
                name=category_data.name,
                description=category_data.description,
                is_default=category_data.is_default,
                color=category_data.color,
            )
            category = await uow.category_repository.create(category=new_category)
            logger.bind(category=category).debug("Created category from repo")
            return CategoryDTO(
                id=category.id,
                name=category.name,
                user_id=category.user_id,
                description=category.description,
                is_default=category.is_default,
                color=category.color,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
        assert False, "unreachable"

    async def update_category(
        self, category_data: CategoryUpdateDTO
    ) -> CategoryDTO | None:
        async with self._unit_of_work as uow:
            category = await uow.category_repository.get_by_id(
                category_id=category_data.id
            )
            if not category:
                raise CategoryNotFound(f"Category with id {category_data.id} not found")
            if category_data.name is not None:
                category.name = category_data.name
            if category_data.color is not None:
                category.color = category_data.color
            if category_data.is_default is not None:
                category.is_default = category_data.is_default
            if category_data.description is not None:
                category.description = category_data.description
            category.updated_at = datetime.now(timezone.utc)
            updated_category = await uow.category_repository.update(category=category)
            logger.bind(updated_category=updated_category).debug(
                "Updated updated_category from repo"
            )
            return CategoryDTO(
                id=category.id,
                name=category.name,
                user_id=category.user_id,
                description=category.description,
                is_default=category.is_default,
                color=category.color,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
        assert False, "unreachable"

    async def delete_category(self, category_id: UUID) -> None:
        async with self._unit_of_work as uow:
            category = await uow.category_repository.get_by_id(category_id=category_id)
            if not category:
                raise CategoryNotFound(f"Category with id {category_id} not found")
            await uow.category_repository.delete(category=category)
            logger.bind(category=category).debug("Deleted category from repo")
            return None
        assert False, "unreachable"
