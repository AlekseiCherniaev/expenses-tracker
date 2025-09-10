from typing import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from asgi_lifespan._types import ASGIApp
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from starlette.datastructures import State

from expenses_tracker.app import init_app


@pytest.fixture(scope="session")
async def configured_app() -> FastAPI:
    app = init_app()
    return app


@pytest.fixture(scope="session")
async def lifespan_manager(
    configured_app: FastAPI,
) -> AsyncGenerator[LifespanManager, None]:
    async with LifespanManager(configured_app) as m:
        yield m


@pytest.fixture(scope="session")
async def lifespan_state(lifespan_manager: LifespanManager) -> State:
    return State(lifespan_manager._state)


@pytest.fixture(scope="session")
async def initialized_app(lifespan_manager: LifespanManager) -> ASGIApp:
    return lifespan_manager.app


@pytest.fixture(scope="session")
async def async_client(initialized_app: ASGIApp) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=initialized_app), base_url="http://test"
    ) as c:
        yield c
