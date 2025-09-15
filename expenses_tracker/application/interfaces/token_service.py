from abc import ABC, abstractmethod

from expenses_tracker.domain.entities.token_payload import TokenPayload
from expenses_tracker.domain.entities.user import User


class ITokenService(ABC):
    @abstractmethod
    def create_token(self, user: User) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        pass
