from abc import ABC, abstractmethod


class IOAuthStateStorage(ABC):
    @abstractmethod
    async def save(self, key: str, data: dict[str, str], ttl: int = 300) -> None:
        pass

    @abstractmethod
    async def load(self, key: str) -> dict[str, str] | None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
