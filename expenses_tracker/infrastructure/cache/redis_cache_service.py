from typing import TypeVar, Generic

import orjson
import redis.asyncio as redis
import structlog

from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.settings import get_settings

T = TypeVar("T")
logger = structlog.get_logger(__name__)


class RedisService(Generic[T], ICacheService[T]):
    def __init__(self) -> None:
        self._redis = redis.Redis.from_url(
            get_settings().redis_dsn, encoding="utf-8", decode_responses=True
        )

    async def get(self, key: str, serializer: type[T]) -> T | None:
        value = await self._redis.get(key)
        if value is None:
            return None
        logger.bind(key=key).debug("Hit cache")
        data = orjson.loads(value)
        return serializer(**data)

    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        data = value.model_dump() if hasattr(value, "model_dump") else value.__dict__
        await self._redis.set(key, orjson.dumps(data), ex=ttl)
        logger.bind(key=key).debug("Set cache")

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
        logger.bind(key=key).debug("Delete cache")

    async def delete_keys_by_pattern(self, pattern: str) -> None:
        """
        Delete all keys by pattern
        """
        cursor = "0"
        while cursor != 0:  # type: ignore
            cursor, keys = await self._redis.scan(
                cursor=cursor, match=f"*{pattern}*", count=5000
            )
            if keys:
                await self._redis.delete(*keys)

    async def close(self) -> None:
        await self._redis.aclose()
