from uuid import UUID, uuid4

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import Response, JSONResponse, RedirectResponse

from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.constants import TokenType, Environment
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.exceptions.auth import InvalidCredentials
from expenses_tracker.infrastructure.di import get_token_service

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    token_service: ITokenService = Depends(get_token_service),
) -> UUID:
    payload = token_service.decode_token(token=token.credentials)
    if payload.type != TokenType.ACCESS:
        raise InvalidCredentials("Provided token is not an access token")
    return UUID(payload.sub)


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    is_production = get_settings().environment == Environment.PROD

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        path="/api/auth",
        max_age=60 * 60 * 24 * get_settings().refresh_token_expire_days,
    )


def set_csrf_cookie(response: Response, csrf_token: str | None = None) -> None:
    is_production = get_settings().environment == Environment.PROD
    csrf_token = csrf_token or str(uuid4())

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=is_production,
        samesite="lax",
        path="/",
    )


def auth_response(
    access_token: str, refresh_token: str, status_code: int = 200
) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content={
            "access_token": access_token,
            "token_type": "bearer",
        },
    )
    set_refresh_cookie(response, refresh_token)
    set_csrf_cookie(response)
    return response


def oauth_response(
    access_token: str | None = None,
    refresh_token: str | None = None,
    error_message: str | None = None,
) -> RedirectResponse:
    if error_message or access_token is None or refresh_token is None:
        frontend_url = f"https://{get_settings().domain}/login?error={error_message}"
        return RedirectResponse(url=frontend_url)

    frontend_url = f"https://{get_settings().domain}/oauth/callback"
    response = RedirectResponse(url=frontend_url)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=get_settings().access_token_expire_minutes * 60,
    )

    set_refresh_cookie(response, refresh_token)
    set_csrf_cookie(response)
    return response
