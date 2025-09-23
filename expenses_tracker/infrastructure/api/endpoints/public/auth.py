from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Response, status

from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import get_current_user_id
from expenses_tracker.infrastructure.api.schemas.auth import (
    TokenResponse,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
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


@router.post("/logout")
async def logout_user(
    logout_data: LogoutRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.bind(logout_data=logout_data).debug("Logging out user")
    await auth_use_cases.logout(refresh_token=logout_data.refresh_token)
    logger.bind(logout_data=logout_data).debug("Logged out user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/request-verify-email")
async def request_verify_email(
    user_id: UUID = Depends(get_current_user_id),
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.debug("Requesting verify email")
    await auth_use_cases.request_verify_email(user_id=user_id)
    logger.debug("Requested verify email")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/verify-email")
async def verify_email(
    email_token: str,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.debug("Verifying email")
    await auth_use_cases.verify_email(email_token=email_token)
    logger.debug("Verified email")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
