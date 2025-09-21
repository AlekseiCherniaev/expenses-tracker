from dataclasses import is_dataclass, asdict
from typing import TypeVar, Generic, get_origin, get_args, cast, Any

import orjson
import redis.asyncio as redis
import structlog

from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.settings import get_settings

T = TypeVar("T")
logger = structlog.get_logger(__name__)


class RedisService(Generic[T], ICacheService[T]):
    def __init__(self, url: str | None = None) -> None:
        self._redis = redis.Redis.from_url(
            url=url or get_settings().redis_dsn, encoding="utf-8", decode_responses=True
        )

    def _serialize(self, value: T) -> bytes:
        """Serialize an object (DTO, dataclass, dict, list) to JSON bytes."""
        if isinstance(value, list):
            data = [self._model_dump(v) for v in value]
        else:
            data = self._model_dump(value)  # type: ignore
        return orjson.dumps(data)

    @staticmethod
    def _deserialize(value: str, serializer: type[T]) -> T | None:
        """Deserialize JSON from Redis to an object/list."""
        try:
            obj = orjson.loads(value)
            if get_origin(serializer) is list:
                model = get_args(serializer)[0]
                return cast(T, [model(**item) for item in obj])

            return serializer(**obj)
        except Exception as e:
            logger.bind(error=str(e)).warning("Redis DESERIALIZE failed")
            return None

    @staticmethod
    def _model_dump(value: object) -> dict[str, Any]:
        """Convert supported object types into a plain dict."""
        if hasattr(value, "model_dump"):
            return value.model_dump()  # type: ignore
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        if hasattr(value, "__dict__"):
            return dict(value.__dict__)
        if isinstance(value, dict):
            return dict(value)
        raise TypeError(f"Unsupported type for serialization: {type(value)}")

    async def get(self, key: str, serializer: type[T]) -> T | None:
        try:
            value = await self._redis.get(key)
            if value is None:
                return None
            logger.bind(key=key).debug("Hit cache")
            return self._deserialize(value, serializer)
        except Exception as e:
            logger.bind(key=key, error=str(e)).warning("Redis GET failed")
            return None

    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        try:
            data = self._serialize(value)
            await self._redis.set(key, data, ex=ttl)
            logger.bind(key=key).debug("Set cache")
        except Exception as e:
            logger.bind(key=key, error=str(e)).warning("Redis SET failed")

    async def delete(self, key: str) -> None:
        try:
            await self._redis.delete(key)
            logger.bind(key=key).debug("Delete cache")
        except Exception as e:
            logger.bind(key=key, error=str(e)).warning("Redis DELETE failed")

    async def delete_keys_by_pattern(self, pattern: str) -> None:
        """
        Delete all keys by pattern
        """
        try:
            cursor = "0"
            while cursor != 0:  # type: ignore
                cursor, keys = await self._redis.scan(
                    cursor=cursor, match=f"*{pattern}*", count=5000
                )
                if keys:
                    await self._redis.delete(*keys)
            logger.bind(pattern=pattern).debug("Deleted keys by pattern")
        except Exception as e:
            logger.bind(pattern=pattern, error=str(e)).warning(
                "Redis DELETE BY PATTERN failed"
            )

    async def close(self) -> None:
        try:
            await self._redis.aclose()
        except Exception as e:
            logger.bind(error=str(e)).warning("Redis CLOSE failed")
