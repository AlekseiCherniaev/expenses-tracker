from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class ICacheService(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: str) -> T | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
