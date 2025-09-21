from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class ICacheService(ABC, Generic[T]):
    @abstractmethod
    def get(self, key: str) -> T | None:
        pass

    @abstractmethod
    def set(self, key: str, value: T, ttl: int | None = None) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass
