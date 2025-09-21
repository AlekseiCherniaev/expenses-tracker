import structlog
from fastapi import APIRouter, Depends

from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.infrastructure.api.schemas.auth import (
    TokenResponse,
    LoginRequest,
    RefreshRequest,
)
from expenses_tracker.infrastructure.api.schemas.user import (
    UserCreateRequest,
)
from expenses_tracker.infrastructure.di import get_auth_user_use_cases

router = APIRouter(prefix="/auth", tags=["auth"])

logger = structlog.get_logger(__name__)


@router.post("/register")
async def register_user(
    user_data: UserCreateRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> TokenResponse:
    logger.bind(user_username=user_data.username).debug("Registering user")
    create_user_dto = UserCreateDTO(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    token_pair = await auth_use_cases.register(user_data=create_user_dto)
    logger.bind(user_username=user_data.username).debug("Registered user")
    return TokenResponse(
        refresh_token=token_pair.refresh_token,
        access_token=token_pair.access_token,
        token_type=token_pair.token_type,
    )


@router.post("/login")
async def login_user(
    login_data: LoginRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> TokenResponse:
    logger.bind(username=login_data.username).debug("Logging in user")
    token_pair = await auth_use_cases.login(
        username=login_data.username, password=login_data.password
    )
    logger.bind(username=login_data.username).debug("Logged in user")
    return TokenResponse(
        refresh_token=token_pair.refresh_token,
        access_token=token_pair.access_token,
        token_type=token_pair.token_type,
    )


@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> TokenResponse:
    logger.bind(refresh_data=refresh_data).debug("Refreshing token")
    token_pair = await auth_use_cases.refresh(refresh_token=refresh_data.refresh_token)
    logger.bind(refresh_data=refresh_data).debug("Refreshed token")
    return TokenResponse(
        refresh_token=token_pair.refresh_token,
        access_token=token_pair.access_token,
        token_type=token_pair.token_type,
    )
