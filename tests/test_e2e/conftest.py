from typing import AsyncGenerator

from asgi_lifespan import LifespanManager
from asgi_lifespan._types import ASGIApp
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.datastructures import State
from testcontainers.postgres import PostgresContainer

from expenses_tracker.app import init_app
from expenses_tracker.core import settings as settings_module
from expenses_tracker.core.constants import Environment
from expenses_tracker.core.settings import Settings
from expenses_tracker.infrastructure.database.models import Base


@fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


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
def override_settings(postgres_container, monkeypatch):
    test_settings = Settings(
        environment=Environment.TEST,
        postgres_host=postgres_container.get_container_host_ip(),
        postgres_port=postgres_container.get_exposed_port(5432),
        postgres_user="test",
        postgres_password="test",
        postgres_db="test",
    )
    monkeypatch.setattr(settings_module, "Settings", lambda: test_settings)
    return test_settings


@fixture
def configured_app(override_settings, async_engine) -> FastAPI:
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
