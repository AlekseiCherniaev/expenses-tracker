import asyncio
from dataclasses import dataclass

from pytest_asyncio import fixture

from expenses_tracker.infrastructure.cache.redis_cache_service import RedisService


@dataclass
class DummyDTO:
    id: int
    name: str


@fixture
async def redis_service(redis_container):
    service = RedisService[DummyDTO](url=redis_container["dsn"])
    yield service
    await service.close()


class TestRedisService:
    async def test_set_and_get_value(self, redis_service: RedisService[DummyDTO]):
        dto = DummyDTO(id=1, name="test")
        await redis_service.set("dummy:1", dto, ttl=10)

        cached = await redis_service.get("dummy:1", DummyDTO)

        assert cached is not None
        assert cached.id == dto.id
        assert cached.name == dto.name

    async def test_get_missing_key_returns_none(
        self, redis_service: RedisService[DummyDTO]
    ):
        cached = await redis_service.get("missing:key", DummyDTO)
        assert cached is None

    async def test_delete_key(self, redis_service: RedisService[DummyDTO]):
        dto = DummyDTO(id=2, name="to_delete")
        await redis_service.set("dummy:2", dto, ttl=10)

        await redis_service.delete("dummy:2")
        cached = await redis_service.get("dummy:2", DummyDTO)

        assert cached is None

    async def test_delete_keys_by_pattern(self, redis_service: RedisService[DummyDTO]):
        dto1 = DummyDTO(id=3, name="a")
        dto2 = DummyDTO(id=4, name="b")
        await redis_service.set("pattern:3", dto1)
        await redis_service.set("pattern:4", dto2)

        await redis_service.delete_keys_by_pattern("pattern")

        assert await redis_service.get("pattern:3", DummyDTO) is None
        assert await redis_service.get("pattern:4", DummyDTO) is None

    async def test_set_with_ttl_expires(self, redis_service: RedisService[DummyDTO]):
        dto = DummyDTO(id=5, name="temp")
        await redis_service.set("temp:5", dto, ttl=1)

        await asyncio.sleep(1.2)
        cached = await redis_service.get("temp:5", DummyDTO)

        assert cached is None
