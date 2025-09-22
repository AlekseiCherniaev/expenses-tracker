from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from expenses_tracker.application.interfaces.token_service import ITokenService
from expenses_tracker.core.constants import TokenType
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.entities.token_payload import TokenPayload
from expenses_tracker.domain.exceptions.auth import TokenExpired, InvalidToken


class JWTTokenService(ITokenService):
    def create_token(
        self,
        subject: str,
        jti: str | None = None,
        expires_delta: timedelta | None = None,
        token_type: TokenType = TokenType.ACCESS,
    ) -> str:
        now = datetime.now(timezone.utc)
        expire = now + (
            expires_delta
            or timedelta(minutes=get_settings().access_token_expire_minutes)
        )
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": now,
            "jti": jti or str(uuid4()),
            "type": token_type.value,
        }
        return jwt.encode(
            payload,
            get_settings().secret_key,
            algorithm=get_settings().algorithm,
        )

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                get_settings().secret_key,
                algorithms=[get_settings().algorithm],
            )
            payload["type"] = TokenType(payload["type"])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError as e:
            raise TokenExpired("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise InvalidToken("Invalid token") from e
