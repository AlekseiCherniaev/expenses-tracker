from typing import Generic, TypeVar

from expenses_tracker.application.interfaces.cache_service import ICacheService

T = TypeVar("T")


class DummyCacheService(ICacheService[T], Generic[T]):
    async def get(self, key: str, serializer: type[T]) -> T | None:
        return None

    async def get_keys_by_pattern(self, pattern: str) -> list[str]:
        return []

    async def delete_keys_by_pattern(self, pattern: str) -> None:
        return None

    async def set(self, key: str, value: T, ttl: int | None = 300) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass
