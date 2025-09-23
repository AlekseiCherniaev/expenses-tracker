from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Response, status

from expenses_tracker.application.dto.category import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
)
from expenses_tracker.application.use_cases.category import CategoryUseCases
from expenses_tracker.infrastructure.api.schemas.category import (
    InternalCategoryCreateRequest,
    InternalCategoryResponse,
    InternalCategoryUpdateRequest,
)
from expenses_tracker.infrastructure.di import get_category_use_cases

router = APIRouter(prefix="/categories", tags=["internal categories"])

logger = structlog.get_logger(__name__)


@router.get("/get/{category_id}")
async def get_internal_category(
    category_id: UUID,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> InternalCategoryResponse:
    logger.bind(category_id=category_id).debug("Getting category...")
    category_dto = await category_use_cases.get_category(category_id=category_id)
    logger.bind(category=category_dto).debug("Got category")
    return InternalCategoryResponse(**category_dto.__dict__)


@router.get("/get-by-user/{user_id}")
async def get_internal_categories_by_user(
    user_id: UUID,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> list[InternalCategoryResponse]:
    logger.bind(user_id=user_id).debug("Getting categories for user...")
    category_dtos = await category_use_cases.get_categories_by_user_id(user_id=user_id)
    logger.bind(categories=category_dtos).debug("Got categories")
    return [InternalCategoryResponse(**dto.__dict__) for dto in category_dtos]


@router.post("/create")
async def create_internal_category(
    category_data: InternalCategoryCreateRequest,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> InternalCategoryResponse:
    logger.bind(category_data=category_data).debug("Creating category...")
    create_dto = CategoryCreateDTO(
        user_id=category_data.user_id,
        name=category_data.name,
        description=category_data.description,
        is_default=category_data.is_default,
        color=category_data.color,
    )
    category_dto = await category_use_cases.create_category(category_data=create_dto)
    logger.bind(category=category_dto).debug("Created category")
    return InternalCategoryResponse(**category_dto.__dict__)


@router.put("/update")
async def update_internal_category(
    category_data: InternalCategoryUpdateRequest,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> InternalCategoryResponse:
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
    return InternalCategoryResponse(**category_dto.__dict__)


@router.delete("/delete/{category_id}")
async def delete_internal_category(
    category_id: UUID,
    category_use_cases: CategoryUseCases = Depends(get_category_use_cases),
) -> Response:
    logger.bind(category_id=category_id).debug("Deleting category...")
    await category_use_cases.delete_category(category_id=category_id)
    logger.bind(category_id=category_id).debug("Deleted category")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
