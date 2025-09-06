from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request

from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.exceptions import UserAlreadyExists, UserNotFound
from expenses_tracker.infrastructure.api.schemas.user import (
    UserResponse,
    UserCreateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])

logger = structlog.get_logger(__name__)


@router.get("/get/{user_id}")
async def get_user(user_id: UUID, request: Request) -> UserResponse:
    logger.bind(user_id=user_id).debug("Getting user...")
    try:
        user_use_case: UserUseCases = request.state.user_use_case
        user_dto = await user_use_case.get_user(user_id=user_id)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    logger.bind(user=user_dto).debug("Got user")
    return UserResponse(**user_dto.__dict__)


@router.post("/create")
async def create_user(user_data: UserCreateRequest, request: Request) -> UserResponse:
    logger.bind(user_data=user_data).debug("Creating user...")
    try:
        user_use_case: UserUseCases = request.state.user_use_case
        create_user_dto = UserCreateDTO(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        user_dto = await user_use_case.create_user(user_data=create_user_dto)
    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    logger.bind(user=user_dto).debug("Created user")
    return UserResponse(**user_dto.__dict__)
