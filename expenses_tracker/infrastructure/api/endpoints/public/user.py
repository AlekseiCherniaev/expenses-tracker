from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Response, status

from expenses_tracker.application.dto.user import UserUpdateDTO
from expenses_tracker.application.use_cases.upload_avatar_use_cases import (
    UserAvatarUseCase,
)
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import get_current_user_id
from expenses_tracker.infrastructure.api.schemas.user import (
    UserUpdateRequest,
    UserResponse,
    UserAvatarUploadResponse,
)
from expenses_tracker.infrastructure.di import (
    get_user_use_cases,
    get_upload_avatar_use_cases,
)

router = APIRouter(prefix="/users", tags=["users"])

logger = structlog.get_logger(__name__)


@router.get("/me")
async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserResponse:
    logger.bind(user_id=user_id).debug("Getting current user...")
    user_dto = await user_use_cases.get_user(user_id=user_id)
    logger.bind(user_id=user_id).debug("Got current user")
    return UserResponse(**user_dto.__dict__)


@router.put("/update")
async def update_current_user(
    user_data: UserUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserResponse:
    logger.bind(user_id=user_id).debug("Updating current user...")
    update_user_dto = UserUpdateDTO(
        id=user_id,
        email=user_data.email,
        password=user_data.password,
    )
    user_dto = await user_use_cases.update_user(user_data=update_user_dto)
    logger.bind(user_id=user_id).debug("Updated current user")
    return UserResponse(**user_dto.__dict__)


@router.put("/upload-avatar")
async def upload_avatar_for_current_user(
    user_id: UUID = Depends(get_current_user_id),
    upload_avatar_use_cases: UserAvatarUseCase = Depends(get_upload_avatar_use_cases),
) -> UserAvatarUploadResponse:
    logger.bind(user_id=user_id).debug("Avatar upload for current user...")
    upload_url, public_url = await upload_avatar_use_cases.generate_presigned_urls(
        user_id=user_id
    )
    logger.bind(user_id=user_id).debug("Avatar uploaded for current user")
    return UserAvatarUploadResponse(upload_url=upload_url, public_url=public_url)


@router.put("/delete-avatar")
async def delete_avatar_for_current_user(
    user_id: UUID = Depends(get_current_user_id),
    upload_avatar_use_cases: UserAvatarUseCase = Depends(get_upload_avatar_use_cases),
) -> Response:
    logger.bind(user_id=user_id).debug("Avatar delete for current user...")
    await upload_avatar_use_cases.delete_avatar(user_id=user_id)
    logger.bind(user_id=user_id).debug("Avatar deleted for current user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/delete")
async def delete_current_user(
    user_id: UUID = Depends(get_current_user_id),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
) -> Response:
    logger.bind(user_id=user_id).debug("Deleting current user...")
    await user_use_cases.delete_user(user_id=user_id)
    logger.bind(user_id=user_id).debug("Deleted current user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
