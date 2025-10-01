from uuid import UUID

import structlog
from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    Request,
    Cookie,
    HTTPException,
    Header,
)
from starlette.responses import JSONResponse

from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.auth import AuthUserUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import (
    get_current_user_id,
    auth_response,
)
from expenses_tracker.infrastructure.api.rate_limiter import limiter
from expenses_tracker.infrastructure.api.schemas.auth import (
    LoginRequest,
    PasswordResetRequest,
    NewPasswordRequest,
)
from expenses_tracker.infrastructure.api.schemas.user import (
    UserCreateRequest,
)
from expenses_tracker.infrastructure.di import get_auth_user_use_cases

router = APIRouter(prefix="/auth", tags=["auth"])

logger = structlog.get_logger(__name__)


@router.post("/register")
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: UserCreateRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> JSONResponse:
    logger.bind(user_username=user_data.username).debug("Registering user")
    create_user_dto = UserCreateDTO(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    token_pair = await auth_use_cases.register(user_data=create_user_dto)
    logger.bind(user_username=user_data.username).debug("Registered user")
    return auth_response(token_pair.access_token, token_pair.refresh_token)


@router.post("/login")
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    login_data: LoginRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> JSONResponse:
    logger.bind(username=login_data.username).debug("Logging in user")
    token_pair = await auth_use_cases.login(
        username=login_data.username, password=login_data.password
    )
    logger.bind(username=login_data.username).debug("Logged in user")
    return auth_response(token_pair.access_token, token_pair.refresh_token)


@router.post("/refresh")
@limiter.limit("15/minute")
async def refresh_user_token(
    request: Request,
    refresh_token: str | None = Cookie(default=None),
    csrf_token_header: str | None = Header(default=None, alias="X-CSRF-Token"),
    csrf_token_cookie: str | None = Cookie(default=None, alias="csrf_token"),
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> JSONResponse:
    logger.bind(refresh_data=refresh_token).debug("Refreshing token")

    if not csrf_token_header or not csrf_token_cookie:
        raise HTTPException(status_code=403, detail="Missing CSRF tokens")
    if csrf_token_header != csrf_token_cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token_pair = await auth_use_cases.refresh(refresh_token=refresh_token)
    logger.bind(refresh_data=refresh_token).debug("Refreshed token")
    return auth_response(token_pair.access_token, token_pair.refresh_token)


@router.post("/logout")
@limiter.limit("5/minute")
async def logout_user(
    request: Request,
    refresh_token: str | None = Cookie(default=None),
    csrf_token_header: str | None = Header(default=None, alias="X-CSRF-Token"),
    csrf_token_cookie: str | None = Cookie(default=None, alias="csrf_token"),
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.bind(logout_data=refresh_token).debug("Logging out user")

    if not csrf_token_header or not csrf_token_cookie:
        raise HTTPException(status_code=403, detail="Missing CSRF tokens")
    if csrf_token_header != csrf_token_cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    await auth_use_cases.logout(refresh_token=refresh_token)
    logger.bind(logout_data=refresh_token).debug("Logged out user")

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("refresh_token", path="/api/auth")
    response.delete_cookie("csrf_token", path="/api/auth")
    request.session.pop("user", None)
    return response


@router.post("/request-verify-email")
@limiter.limit("3/minute")
async def request_verify_email(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.debug("Requesting verify email")
    await auth_use_cases.request_verify_email(user_id=user_id)
    logger.debug("Requested verify email")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/verify-email")
async def verify_email(
    email_token: str,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.debug("Verifying email")
    await auth_use_cases.verify_email(email_token=email_token)
    logger.debug("Verified email")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/request-reset-password")
@limiter.limit("3/minute")
async def request_reset_password(
    request: Request,
    password_reset_request_data: PasswordResetRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.bind(email=password_reset_request_data.email).debug(
        "Requesting password reset"
    )
    await auth_use_cases.request_password_reset(email=password_reset_request_data.email)
    logger.bind(email=password_reset_request_data.email).debug(
        "Requested password reset"
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/reset-password")
async def reset_password(
    password_token: str,
    new_password_data: NewPasswordRequest,
    auth_use_cases: AuthUserUseCases = Depends(get_auth_user_use_cases),
) -> Response:
    logger.debug("Resetting password")
    await auth_use_cases.reset_password(
        password_reset_token=password_token, new_password=new_password_data.new_password
    )
    logger.debug("Reset password")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
