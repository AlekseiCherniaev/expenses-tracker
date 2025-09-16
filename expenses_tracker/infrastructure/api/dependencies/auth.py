from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.infrastructure.di import get_token_service

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    token_service: ITokenService = Depends(get_token_service),
) -> UUID:
    payload = token_service.decode_token(token=token.credentials)
    return UUID(payload.sub)
