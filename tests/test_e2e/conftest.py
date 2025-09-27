from typing import AsyncGenerator

import redis.asyncio as redis
from asgi_lifespan import LifespanManager
from asgi_lifespan._types import ASGIApp
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.datastructures import State
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from expenses_tracker.app import init_app
from expenses_tracker.core import settings as settings_module
from expenses_tracker.core.constants import Environment
from expenses_tracker.core.settings import Settings
from expenses_tracker.infrastructure.database.models import Base


@fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as container:
        yield container


@fixture(scope="session")
def redis_container():
    with RedisContainer() as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        yield {"host": host, "port": port, "dsn": f"redis://{host}:{port}/0"}


@fixture(scope="session")
def minio_container():
    with MinioContainer("minio/minio:latest") as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(9000)
        endpoint = f"http://{host}:{port}"
        yield {
            "endpoint": endpoint,
            "access_key": container.access_key,
            "secret_key": container.secret_key,
        }


@fixture(scope="function")
async def redis_client(redis_container):
    client = redis.Redis.from_url(
        redis_container["dsn"], encoding="utf-8", decode_responses=True
    )
    yield client
    await client.close()


@fixture(scope="session")
def postgres_container_sync_url(postgres_container):
    return postgres_container.get_connection_url().replace("+psycopg2", "")


@fixture(scope="session")
def postgres_container_async_url(postgres_container):
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@fixture
async def async_engine(postgres_container_async_url):
    engine = create_async_engine(postgres_container_async_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@fixture
def override_settings(
    postgres_container, redis_container, monkeypatch, minio_container
):
    test_settings = Settings(
        environment=Environment.TEST,
        postgres_host=postgres_container.get_container_host_ip(),
        postgres_port=postgres_container.get_exposed_port(5432),
        postgres_user="test",
        postgres_password="test",
        postgres_db="test",
        redis_host=redis_container["host"],
        redis_port=redis_container["port"],
        redis_db=0,
        minio_endpoint=minio_container["endpoint"],
        minio_access_key=minio_container["access_key"],
        minio_secret_key=minio_container["secret_key"],
    )
    monkeypatch.setattr(settings_module, "Settings", lambda: test_settings)


@fixture
def configured_app(override_settings, async_engine) -> FastAPI:
    settings_module.get_settings.cache_clear()
    app = init_app()
    return app


@fixture
async def lifespan_manager(
    configured_app: FastAPI,
) -> AsyncGenerator[LifespanManager, None]:
    async with LifespanManager(configured_app) as m:
        yield m


@fixture
def lifespan_state(lifespan_manager: LifespanManager) -> State:
    return State(lifespan_manager._state)


@fixture
def initialized_app(lifespan_manager: LifespanManager) -> ASGIApp:
    return lifespan_manager.app


@fixture
async def async_client(initialized_app: ASGIApp) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=initialized_app), base_url="http://test"
    ) as c:
        yield c


@fixture(autouse=True)
def disable_limiter(monkeypatch):
    from expenses_tracker.infrastructure.api import rate_limiter

    rate_limiter.limiter.enabled = False
