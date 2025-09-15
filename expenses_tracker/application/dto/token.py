from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenPairDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
