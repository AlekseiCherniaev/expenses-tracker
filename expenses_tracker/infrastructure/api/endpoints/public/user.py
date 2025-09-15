from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request

from expenses_tracker.application.dto.user import UserCreateDTO, UserUpdateDTO
from expenses_tracker.application.use_cases.user import UserUseCases
from expenses_tracker.domain.exceptions.user import UserAlreadyExists, UserNotFound
from expenses_tracker.infrastructure.api.schemas.user import (
    UserResponse,
    UserCreateRequest,
    UserUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["users"])

logger = structlog.get_logger(__name__)


@router.get("/get/{user_id}")
async def get_user(user_id: UUID, request: Request) -> UserResponse:
    logger.bind(user_id=user_id).debug("Getting user...")
    try:
        user_use_cases: UserUseCases = request.state.user_use_cases
        user_dto = await user_use_cases.get_user(user_id=user_id)
    except UserNotFound as e:
        logger.bind(user_id=user_id).exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    logger.bind(user=user_dto).debug("Got user")
    return UserResponse(**user_dto.__dict__)


@router.get("/get-all")
async def get_all_users(request: Request) -> list[UserResponse]:
    logger.debug("Getting all users...")
    user_use_cases: UserUseCases = request.state.user_use_cases
    user_dtos = await user_use_cases.get_all_users()
    logger.bind(user=user_dtos).debug("Got users")
    return [UserResponse(**user_dto.__dict__) for user_dto in user_dtos]


@router.post("/create")
async def create_user(user_data: UserCreateRequest, request: Request) -> UserResponse:
    logger.bind(user_data=user_data).debug("Creating user...")
    try:
        user_use_cases: UserUseCases = request.state.user_use_cases
        create_user_dto = UserCreateDTO(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        user_dto = await user_use_cases.create_user(user_data=create_user_dto)
    except UserAlreadyExists as e:
        logger.bind(user_data=user_data).exception("User already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    logger.bind(user=user_dto).debug("Created user")
    return UserResponse(**user_dto.__dict__)


@router.put("/update")
async def update_user(user_data: UserUpdateRequest, request: Request) -> UserResponse:
    logger.bind(user_data=user_data).debug("Updating user...")
    try:
        user_use_cases: UserUseCases = request.state.user_use_cases
        update_user_dto = UserUpdateDTO(
            id=user_data.id,
            is_active=user_data.is_active,
            email=user_data.email,
            password=user_data.password,
        )
        user_dto = await user_use_cases.update_user(user_data=update_user_dto)
    except UserNotFound as e:
        logger.bind(user_id=user_data.id).exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExists as e:
        logger.bind(user_id=user_data.id).exception("User already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    logger.bind(user=user_dto).debug("Updated user")
    return UserResponse(**user_dto.__dict__)


@router.delete("/delete/{user_id}")
async def delete_user(user_id: UUID, request: Request) -> None:
    logger.bind(user_id=user_id).debug("Deleting user...")
    try:
        user_use_cases: UserUseCases = request.state.user_use_cases
        await user_use_cases.delete_user(user_id=user_id)
    except UserNotFound as e:
        logger.bind(user_id=user_id).exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    logger.bind(user_id=user_id).debug("Deleted user")
    return None
