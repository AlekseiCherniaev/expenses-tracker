from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send_verification_email(self, to: str, token: str) -> None:
        pass
