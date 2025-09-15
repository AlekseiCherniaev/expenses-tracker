from datetime import datetime, timedelta, timezone

import jwt

from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.token_payload import TokenPayload


class JWTTokenService(ITokenService):
    def create_token(self, subject: str, expires_delta: timedelta | None = None) -> str:
        expire = datetime.now(timezone.utc) + (
            expires_delta
            or timedelta(minutes=get_settings().access_token_expire_minutes)
        )
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(
            payload,
            get_settings().secret_key,
            algorithm=get_settings().algorithm,
        )

    def decode_token(self, token: str) -> TokenPayload:
        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=[get_settings().algorithm]
        )
        return TokenPayload(**payload)
