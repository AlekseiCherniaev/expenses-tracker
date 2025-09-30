from expenses_tracker.application.interfaces.oauth_state_storage import (
    IOAuthStateStorage,
)
from expenses_tracker.infrastructure.cache.redis_cache_service import RedisService


class RedisOAuthStateStorage(IOAuthStateStorage):
    def __init__(self, redis_service: RedisService[dict[str, str]]):
        self.redis_service = redis_service

    async def save(self, key: str, data: dict[str, str], ttl: int = 300) -> None:
        await self.redis_service.set(f"oauth_state:{key}", data, ttl)

    async def load(self, key: str) -> dict[str, str] | None:
        return await self.redis_service.get(f"oauth_state:{key}", dict[str, str])

    async def delete(self, key: str) -> None:
        await self.redis_service.delete(f"oauth_state:{key}")
