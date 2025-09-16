from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from expenses_tracker.application.dto.category import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.use_cases.categories import CategoryUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import get_current_user_id
from expenses_tracker.infrastructure.api.schemas.category import (
    CategoryResponse,
    CategoryUpdateRequest,
    CategoryCreateRequest,
)
from expenses_tracker.infrastructure.di import get_category_use_cases

router = APIRouter(prefix="/categories", tags=["categories"])

logger = structlog.get_logger(__name__)


@router.get("/get/{category_id}")
async def get_category(
    category_id: UUID,
    _: UUID = Depends(get_current_user_id),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponse:
    logger.bind(category_id=category_id).debug("Getting category...")
    category_dto = await category_use_cases.get_category(category_id=category_id)
    logger.bind(category=category_dto).debug("Got category")
    return CategoryResponse(**category_dto.__dict__)


@router.get("/get-by-user")
async def get_categories_by_user(
    user_id: UUID = Depends(get_current_user_id),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> list[CategoryResponse]:
    logger.bind(user_id=user_id).debug("Getting categories for user...")
    category_dtos = await category_use_cases.get_categories_by_user_id(user_id=user_id)
    logger.bind(categories=category_dtos).debug("Got categories")
    return [CategoryResponse(**dto.__dict__) for dto in category_dtos]


@router.post("/create")
async def create_category(
    category_data: CategoryCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponse:
    logger.bind(category_data=category_data).debug("Creating category...")
    create_dto = CategoryCreateDTO(
        user_id=user_id,
        name=category_data.name,
        description=category_data.description,
        is_default=category_data.is_default,
        color=category_data.color,
    )
    category_dto = await category_use_cases.create_category(category_data=create_dto)
    logger.bind(category=category_dto).debug("Created category")
    return CategoryResponse(**category_dto.__dict__)


@router.put("/update")
async def update_category(
    category_data: CategoryUpdateRequest,
    _: UUID = Depends(get_current_user_id),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponse:
    logger.bind(category_data=category_data).debug("Updating category...")
    update_dto = CategoryUpdateDTO(
        id=category_data.id,
        name=category_data.name,
        description=category_data.description,
        is_default=category_data.is_default,
        color=category_data.color,
    )
    category_dto = await category_use_cases.update_category(category_data=update_dto)
    logger.bind(category=category_dto).debug("Updated category")
    return CategoryResponse(**category_dto.__dict__)


@router.delete("/delete/{category_id}")
async def delete_category(
    category_id: UUID,
    _: UUID = Depends(get_current_user_id),
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> None:
    logger.bind(category_id=category_id).debug("Deleting category...")
    await category_use_cases.delete_category(category_id=category_id)
    logger.bind(category_id=category_id).debug("Deleted category")
    return None
