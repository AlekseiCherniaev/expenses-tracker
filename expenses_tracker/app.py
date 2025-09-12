from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import structlog
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from expenses_tracker.core.logger import prepare_logger
from expenses_tracker.core.settings import settings
from expenses_tracker.core.utils import use_handler_name_as_unique_id
from expenses_tracker.infrastructure.api.main_router import (
    public_router,
    internal_router,
)
from expenses_tracker.infrastructure.di import get_user_use_cases

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[dict[str, Any], None]:
    user_use_cases = await get_user_use_cases()
    logger.info("Startup completed")
    yield {"user_use_cases": user_use_cases}
    logger.debug("Server stopped")


def init_app() -> FastAPI:
    prepare_logger(log_level=settings.log_level)
    logger.info("Initializing app")
    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
        docs_url=None,
        redoc_url=None,
        debug=settings.fast_api_debug,
        openapi_url="/internal/openapi.json",
        swagger_ui_oauth2_redirect_url="/internal/docs/oauth2-redirect",
        generate_unique_id_function=use_handler_name_as_unique_id,
        lifespan=lifespan,
    )
    app.mount("/internal/static", StaticFiles(directory="static"), name="static")
    app.include_router(router=public_router)
    app.include_router(router=internal_router)
    return app
