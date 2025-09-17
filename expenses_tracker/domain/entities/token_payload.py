from dataclasses import dataclass


@dataclass
class TokenPayload:
    sub: str
    exp: float
    iat: float
    jti: str
