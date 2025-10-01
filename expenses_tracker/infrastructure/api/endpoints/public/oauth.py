import structlog
from authlib.integrations.base_client import OAuthError
from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from starlette.responses import RedirectResponse

from expenses_tracker.application.dto.user import UserCreateDTO
from expenses_tracker.application.use_cases.oauth import OAuthUserUseCases
from expenses_tracker.infrastructure.api.dependencies.auth import oauth_response
from expenses_tracker.infrastructure.di import get_oauth_user_use_cases
from expenses_tracker.infrastructure.security.oauth_providers import oauth

router = APIRouter(prefix="/oauth", tags=["oauth"])

logger = structlog.get_logger(__name__)


@router.get("/login-google")
async def login_via_google(request: Request) -> RedirectResponse:
    logger.debug("Logging in via Google")
    redirect_uri = "http://127.0.0.1:8000/api/oauth/auth-via-google"
    result = await oauth.google.authorize_redirect(request, redirect_uri)
    logger.debug("Logged in via Google")
    return result  # type: ignore


@router.get("/auth-via-google")
async def auth_via_google(
    request: Request,
    oauth_use_cases: OAuthUserUseCases = Depends(get_oauth_user_use_cases),
) -> RedirectResponse:
    logger.debug("Authorizing via Google")
    try:
        user_info = (await oauth.google.authorize_access_token(request)).get("userinfo")
        create_user_dto = UserCreateDTO(
            username=user_info.get("email").split("@")[0],
            email=user_info.get("email"),
            password="9DuMmY_PaSsWoRd0",
            avatar_url=user_info.get("picture"),
        )
        token_pair = await oauth_use_cases.third_party_auth(user_data=create_user_dto)
        logger.debug("Authorized via Google")
        return oauth_response(
            access_token=token_pair.access_token, refresh_token=token_pair.refresh_token
        )
    except OAuthError as e:
        logger.bind(e=e).warning("OAuth error")
        return oauth_response(error_message="oauth_cancelled")
    except Exception as e:
        logger.error(f"Unexpected error during OAuth: {e}")
        return oauth_response(error_message="oauth_failed")
