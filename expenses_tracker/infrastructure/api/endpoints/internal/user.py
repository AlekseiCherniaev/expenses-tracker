from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Response, status

from expenses_tracker.application.dto.user import UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.api.schemas.user import (
    InternalUserResponse,
    InternalUserCreateRequest,
    InternalUserUpdateRequest,
)
from expenses_tracker.infrastructure.di import get_user_use_cases

router = APIRouter(prefix="/users", tags=["internal users"])

logger = structlog.get_logger(__name__)


@router.get("/get/{user_id}")
async def get_internal_user(
    user_id: UUID,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> InternalUserResponse:
    logger.bind(user_id=user_id).debug("Getting user...")
    user_dto = await user_use_cases.get_user(user_id=user_id)
    logger.bind(user=user_dto).debug("Got user")
    return InternalUserResponse(**user_dto.__dict__)


@router.get("/get-all")
async def get_internal_all_users(
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> list[InternalUserResponse]:
    logger.debug("Getting all users...")
    user_dtos = await user_use_cases.get_all_users()
    logger.bind(user=user_dtos).debug("Got users")
    return [InternalUserResponse(**user_dto.__dict__) for user_dto in user_dtos]


@router.post("/create")
async def create_internal_user(
    user_data: InternalUserCreateRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> InternalUserResponse:
    logger.bind(user_data=user_data).debug("Creating user...")
    create_user_dto = UserCreateDTO(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    user_dto = await user_use_cases.create_user(user_data=create_user_dto)
    logger.bind(user=user_dto).debug("Created user")
    return InternalUserResponse(**user_dto.__dict__)


@router.put("/update")
async def update_internal_user(
    user_data: InternalUserUpdateRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> InternalUserResponse:
    logger.bind(user_data=user_data).debug("Updating user...")
    update_user_dto = UserUpdateDTO(
        id=user_data.id,
        is_active=user_data.is_active,
        email=user_data.email,
        password=user_data.password,
    )
    user_dto = await user_use_cases.update_user(user_data=update_user_dto)
    logger.bind(user=user_dto).debug("Updated user")
    return InternalUserResponse(**user_dto.__dict__)


@router.delete("/delete/{user_id}")
async def delete_internal_user(
    user_id: UUID,
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> Response:
    logger.bind(user_id=user_id).debug("Deleting user...")
    await user_use_cases.delete_user(user_id=user_id)
    logger.bind(user_id=user_id).debug("Deleted user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
