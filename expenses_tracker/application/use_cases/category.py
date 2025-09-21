from datetime import datetime, timezone
from uuid import UUID

import structlog

from expenses_tracker.application.dto.category import (
    CategoryDTO,
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.exceptions.category import CategoryNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork

logger = structlog.get_logger(__name__)


class CategoryUseCases:
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        cache_service: ICacheService[CategoryDTO | list[CategoryDTO]],
    ):
        self._unit_of_work = unit_of_work
        self._cache_service = cache_service

    @staticmethod
    def _to_dto(category: Category) -> CategoryDTO:
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

    @staticmethod
    def _category_cache_key(category_id: UUID) -> str:
        return f"category:{category_id}"

    @staticmethod
    def _user_categories_cache_key(user_id: UUID) -> str:
        return f"category:user:{user_id}"

    async def get_category(self, category_id: UUID) -> CategoryDTO | None:
        cache_key = self._category_cache_key(category_id)
        cached_category = await self._cache_service.get(
            key=cache_key, serializer=CategoryDTO
        )
        if cached_category:
            logger.bind(category_id=category_id).debug("Retrieved category from cache")
            return cached_category  # type: ignore

        async with self._unit_of_work as uow:
            category = await uow.category_repository.get_by_id(category_id=category_id)
            if not category:
                raise CategoryNotFound(f"Category with id {category_id} not found")

            dto = self._to_dto(category)
            await self._cache_service.set(
                key=cache_key, value=dto, ttl=get_settings().category_dto_ttl_seconds
            )
            logger.bind(category_id=category_id).debug(
                "Retrieved category from repo and cached"
            )
            return dto
        assert False, "unreachable"

    async def get_categories_by_user_id(self, user_id: UUID) -> list[CategoryDTO]:
        cache_key = self._user_categories_cache_key(user_id)
        cached_categories = await self._cache_service.get(
            key=cache_key, serializer=list[CategoryDTO]
        )
        if cached_categories:
            logger.bind(user_id=user_id, count=len(cached_categories)).debug(  # type: ignore
                "Retrieved categories from cache"
            )
            return cached_categories  # type: ignore

        async with self._unit_of_work as uow:
            categories = await uow.category_repository.get_all_by_user_id(
                user_id=user_id
            )
            dtos = [self._to_dto(c) for c in categories]
            await self._cache_service.set(
                key=cache_key,
                value=dtos,
                ttl=get_settings().categories_list_ttl_seconds,
            )
            logger.bind(user_id=user_id, count=len(dtos)).debug(
                "Retrieved categories from repo and cached"
            )
            return dtos
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
            logger.bind(category=category).debug("Created category in repo")

            dto = self._to_dto(category)
            await self._cache_service.set(
                key=self._category_cache_key(dto.id),
                value=dto,
                ttl=get_settings().category_dto_ttl_seconds,
            )
            # invalidate user categories cache
            await self._cache_service.delete(
                key=self._user_categories_cache_key(category.user_id)
            )
            return dto
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
                "Updated category in repo"
            )

            dto = self._to_dto(updated_category)
            await self._cache_service.set(
                key=self._category_cache_key(dto.id),
                value=dto,
                ttl=get_settings().category_dto_ttl_seconds,
            )
            # invalidate user categories cache
            await self._cache_service.delete(
                key=self._user_categories_cache_key(dto.user_id)
            )
            return dto
        assert False, "unreachable"

    async def delete_category(self, category_id: UUID) -> None:
        async with self._unit_of_work as uow:
            category = await uow.category_repository.get_by_id(category_id=category_id)
            if not category:
                raise CategoryNotFound(f"Category with id {category_id} not found")

            await uow.category_repository.delete(category=category)
            logger.bind(category=category).debug("Deleted category in repo")

            await self._cache_service.delete(key=self._category_cache_key(category_id))
            await self._cache_service.delete(
                key=self._user_categories_cache_key(category.user_id)
            )
            return None
        assert False, "unreachable"
