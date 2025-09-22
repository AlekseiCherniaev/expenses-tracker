from dataclasses import dataclass

from expenses_tracker.core.constants import TokenType


@dataclass
class TokenPayload:
    sub: str
    exp: float
    iat: float
    jti: str
    type: TokenType
