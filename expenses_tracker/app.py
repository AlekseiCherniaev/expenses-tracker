from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import structlog
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from expenses_tracker.core.logger import prepare_logger
from expenses_tracker.core.settings import get_settings
from expenses_tracker.core.utils import use_handler_name_as_unique_id
from expenses_tracker.infrastructure.api.exception_handlers import (
    register_exception_handlers,
)
from expenses_tracker.infrastructure.api.main_router import get_routers
from expenses_tracker.infrastructure.database.db import (
    create_psycopg_dsn,
    create_sqlalchemy_engine,
)
from expenses_tracker.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from expenses_tracker.infrastructure.security.jwt_token_service import JWTTokenService

logger = structlog.get_logger(__name__)


def get_app_config(settings) -> dict:  # type: ignore
    return dict(
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    app.state.sqlalchemy_engine = create_sqlalchemy_engine()
    app.state.psycopg_dsn = create_psycopg_dsn()
    app.state.token_service = JWTTokenService()
    app.state.password_hasher = BcryptPasswordHasher()
    logger.info("Startup completed")
    yield
    logger.debug("Server stopped")


def init_app() -> FastAPI:
    settings = get_settings()
    prepare_logger(log_level=settings.log_level)
    logger.info("Initializing app")
    app = FastAPI(**get_app_config(settings))
    app.mount(
        "/internal/static",
        StaticFiles(directory=f"{settings.static_url_path}"),
        name="static",
    )
    register_exception_handlers(app)
    for router in get_routers(settings.environment):
        app.include_router(router=router)
    return app
