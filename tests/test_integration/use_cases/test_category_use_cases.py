from datetime import datetime, timezone

import pytest
from pytest import fixture

from expenses_tracker.application.dto.category import (
    CategoryDTO,
)
from expenses_tracker.application.use_cases.category import CategoryUseCases
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.exceptions.category import CategoryNotFound


class TestCategoryUseCases:
    @fixture(autouse=True)
    def setup(self, unit_of_work):
        self.category_use_cases = CategoryUseCases(unit_of_work=unit_of_work)
        self.unit_of_work = unit_of_work

    async def _create_category(self, category_entity: Category) -> Category:
        async with self.unit_of_work as uow:
            return await uow.category_repository.create(category_entity)

    async def test_get_category_success(
        self, unique_category_entity, unique_category_dto
    ):
        new_category = await self._create_category(unique_category_entity)
        category = await self.category_use_cases.get_category(
            category_id=new_category.id
        )

        assert isinstance(category, CategoryDTO)
        assert category == unique_category_dto

    async def test_get_category_not_found(self, random_uuid):
        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.get_category(category_id=random_uuid)

    async def test_get_categories_by_user_id_success(
        self, unique_category_entity, unique_category_dto
    ):
        await self._create_category(unique_category_entity)
        categories = await self.category_use_cases.get_categories_by_user_id(
            user_id=unique_category_entity.user_id
        )

        assert len(categories) == 1
        assert isinstance(categories[0], CategoryDTO)
        assert categories[0] == unique_category_dto

    async def test_create_category_success(
        self, unique_category_create_dto, unique_category_dto
    ):
        before_create = datetime.now(timezone.utc)
        category = await self.category_use_cases.create_category(
            category_data=unique_category_create_dto
        )
        after_create = datetime.now(timezone.utc)

        assert isinstance(category, CategoryDTO)
        assert category.name == unique_category_dto.name
        assert category.user_id == unique_category_dto.user_id
        assert before_create <= category.created_at <= after_create
        assert before_create <= category.updated_at <= after_create

    async def test_update_category_success(
        self, unique_category_entity_with_times, unique_category_update_dto
    ):
        category, before_create, after_create = unique_category_entity_with_times
        await self._create_category(category)

        before_update = datetime.now(timezone.utc)
        updated_category = await self.category_use_cases.update_category(
            unique_category_update_dto
        )
        after_update = datetime.now(timezone.utc)

        assert isinstance(updated_category, CategoryDTO)
        assert updated_category.name == unique_category_update_dto.name
        assert updated_category.color == unique_category_update_dto.color
        assert updated_category.is_default == unique_category_update_dto.is_default
        assert before_create <= updated_category.created_at <= after_create
        assert before_update <= updated_category.updated_at <= after_update

    async def test_update_category_not_found(
        self, unique_category_update_dto, random_uuid
    ):
        unique_category_update_dto.id = random_uuid
        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.update_category(unique_category_update_dto)

    async def test_delete_category_success(self, unique_category_entity):
        new_category = await self._create_category(unique_category_entity)
        result = await self.category_use_cases.delete_category(
            category_id=new_category.id
        )

        assert result is None

    async def test_delete_category_not_found(self, random_uuid):
        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.delete_category(category_id=random_uuid)
