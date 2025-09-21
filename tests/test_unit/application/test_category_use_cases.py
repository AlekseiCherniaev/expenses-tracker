from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pytest_asyncio import fixture

from expenses_tracker.application.dto.category import (
    CategoryDTO,
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.use_cases.category import CategoryUseCases
from expenses_tracker.domain.entities.category import Category
from expenses_tracker.domain.exceptions.category import CategoryNotFound


@fixture
def category_entity():
    return Category(
        id=uuid4(),
        user_id=uuid4(),
        name="Food",
        description="Food expenses",
        is_default=False,
        color="#FF0000",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@fixture
def category_dto(category_entity):
    return CategoryDTO(
        id=category_entity.id,
        user_id=category_entity.user_id,
        name=category_entity.name,
        description=category_entity.description,
        is_default=category_entity.is_default,
        color=category_entity.color,
        created_at=category_entity.created_at,
        updated_at=category_entity.updated_at,
    )


@fixture
def category_create_dto(category_entity):
    return CategoryCreateDTO(
        user_id=category_entity.user_id,
        name=category_entity.name,
        description=category_entity.description,
        is_default=category_entity.is_default,
        color=category_entity.color,
    )


@fixture
def category_update_dto(category_entity):
    return CategoryUpdateDTO(
        id=category_entity.id,
        name="Updated Food",
        description="Updated food expenses",
        is_default=True,
        color="#00FF00",
    )


class TestCategoryUseCases:
    @fixture(autouse=True)
    def setup(self, mock_unit_of_work, cache_service_mock):
        self.category_use_cases = CategoryUseCases(
            unit_of_work=mock_unit_of_work, cache_service=cache_service_mock
        )
        self.mock_unit_of_work = mock_unit_of_work

    async def test_get_category_success(
        self, mock_unit_of_work, category_entity, category_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = category_entity
        category = await self.category_use_cases.get_category(
            category_id=category_entity.id
        )

        assert isinstance(category, CategoryDTO)
        assert category.id == category_dto.id
        assert category.name == category_dto.name
        assert category.description == category_dto.description
        mock_repo.get_by_id.assert_called_once_with(category_id=category_entity.id)

    async def test_get_category_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.get_category(category_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(category_id=random_uuid)

    async def test_get_categories_by_user_id_success(
        self, mock_unit_of_work, category_entity, category_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_all_by_user_id.return_value = [category_entity]
        categories = await self.category_use_cases.get_categories_by_user_id(
            user_id=category_entity.user_id
        )

        assert len(categories) == 1
        assert isinstance(categories[0], CategoryDTO)
        assert categories[0].id == category_dto.id
        assert categories[0].name == category_dto.name
        mock_repo.get_all_by_user_id.assert_called_once_with(
            user_id=category_entity.user_id
        )

    async def test_get_categories_by_user_id_empty(
        self, mock_unit_of_work, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_all_by_user_id.return_value = []
        categories = await self.category_use_cases.get_categories_by_user_id(
            user_id=random_uuid
        )

        assert len(categories) == 0
        mock_repo.get_all_by_user_id.assert_called_once_with(user_id=random_uuid)

    async def test_create_category_success(
        self, mock_unit_of_work, category_entity, category_create_dto, category_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.create.return_value = category_entity
        category = await self.category_use_cases.create_category(
            category_data=category_create_dto
        )

        assert isinstance(category, CategoryDTO)
        assert category.id == category_dto.id
        assert category.name == category_dto.name
        assert category.description == category_dto.description
        mock_repo.create.assert_called_once()
        created_category = mock_repo.create.call_args[1]["category"]
        assert created_category.user_id == category_create_dto.user_id
        assert created_category.name == category_create_dto.name

    async def test_update_category_success(
        self, mock_unit_of_work, category_entity, category_update_dto
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = category_entity
        mock_repo.update.return_value = category_entity
        category = await self.category_use_cases.update_category(
            category_data=category_update_dto
        )

        assert isinstance(category, CategoryDTO)
        assert category.id == category_entity.id
        assert category.name == category_update_dto.name
        assert category.description == category_update_dto.description
        assert category.is_default == category_update_dto.is_default
        assert category.color == category_update_dto.color
        mock_repo.get_by_id.assert_called_once_with(category_id=category_entity.id)
        mock_repo.update.assert_called_once_with(category=category_entity)

    async def test_update_category_partial_data(
        self, mock_unit_of_work, category_entity
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = category_entity
        mock_repo.update.return_value = category_entity
        partial_update_dto = CategoryUpdateDTO(
            id=category_entity.id,
            name="New Name Only",
            description=None,
            is_default=None,
            color=None,
        )

        category = await self.category_use_cases.update_category(
            category_data=partial_update_dto
        )

        assert category.name == "New Name Only"
        assert category.description == category_entity.description
        assert category.is_default == category_entity.is_default
        assert category.color == category_entity.color

    async def test_update_category_not_found(
        self, mock_unit_of_work, category_update_dto, random_uuid
    ):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = None
        category_update_dto.id = random_uuid

        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.update_category(
                category_data=category_update_dto
            )
        mock_repo.get_by_id.assert_called_once_with(category_id=random_uuid)

    async def test_delete_category_success(self, mock_unit_of_work, category_entity):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = category_entity
        mock_repo.delete.return_value = None
        await self.category_use_cases.delete_category(category_id=category_entity.id)

        mock_repo.get_by_id.assert_called_once_with(category_id=category_entity.id)
        mock_repo.delete.assert_called_once_with(category=category_entity)

    async def test_delete_category_not_found(self, mock_unit_of_work, random_uuid):
        mock_repo = mock_unit_of_work.__aenter__.return_value.category_repository
        mock_repo.get_by_id.return_value = None

        with pytest.raises(CategoryNotFound):
            await self.category_use_cases.delete_category(category_id=random_uuid)
        mock_repo.get_by_id.assert_called_once_with(category_id=random_uuid)
