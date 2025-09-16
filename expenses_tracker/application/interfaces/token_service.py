from abc import ABC, abstractmethod
from datetime import timedelta

from expenses_tracker.domain.entities.token_payload import TokenPayload


class ITokenService(ABC):
    @abstractmethod
    def create_token(self, subject: str, expires_delta: timedelta | None = None) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        pass
