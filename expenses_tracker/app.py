from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

import structlog
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from expenses_tracker.core.logger import prepare_logger
from expenses_tracker.core.settings import get_settings, Settings
from expenses_tracker.core.utils import use_handler_name_as_unique_id
from expenses_tracker.infrastructure.api.exception_handlers import (
    register_exception_handlers,
)
from expenses_tracker.infrastructure.api.main_router import get_routers
from expenses_tracker.infrastructure.api.middlewares.middlewares import add_middlewares
from expenses_tracker.infrastructure.api.rate_limiter import init_rate_limiter
from expenses_tracker.infrastructure.cache.redis_cache_service import RedisService
from expenses_tracker.infrastructure.database.avatar_storages.minio_storage import (
    MinioAvatarStorage,
)
from expenses_tracker.infrastructure.database.db import (
    create_sqlalchemy_engine,
)
from expenses_tracker.infrastructure.monitoring.opentelemetry import setup_opentelemetry
from expenses_tracker.infrastructure.monitoring.sentry import init_sentry
from expenses_tracker.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from expenses_tracker.infrastructure.security.fastapi_email_service import (
    FastapiEmailService,
)
from expenses_tracker.infrastructure.security.jwt_token_service import JWTTokenService

logger = structlog.get_logger(__name__)


def get_app_config(settings: Settings) -> dict[Any, Any]:
    return dict(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version,
        docs_url=None,
        redoc_url=None,
        debug=settings.fast_api_debug,
        openapi_url="/api/internal/openapi.json",
        swagger_ui_oauth2_redirect_url="/api/internal/docs/oauth2-redirect",
        generate_unique_id_function=use_handler_name_as_unique_id,
        lifespan=lifespan,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    app.state.sqlalchemy_engine = create_sqlalchemy_engine()
    app.state.psycopg_dsn = get_settings().sync_postgres_url
    app.state.token_service = JWTTokenService()
    app.state.password_hasher = BcryptPasswordHasher()
    app.state.cache_service = RedisService()
    app.state.email_service = FastapiEmailService()
    app.state.avatar_storage = MinioAvatarStorage()
    app.state.limiter = init_rate_limiter(get_settings().redis_dsn)
    setup_opentelemetry(app=app, engine=app.state.sqlalchemy_engine)
    logger.info("Startup completed")
    yield
    await app.state.sqlalchemy_engine.dispose()
    await app.state.cache_service.close()
    app.state.avatar_storage.close()
    logger.debug("Server stopped")


def init_app() -> FastAPI:
    settings = get_settings()
    init_sentry(settings)
    prepare_logger(log_level=settings.log_level)

    logger.info("Initializing app")
    app = FastAPI(**get_app_config(settings))
    app.mount(
        "/api/internal/static",
        StaticFiles(directory=f"{settings.static_url_path}"),
        name="static",
    )
    register_exception_handlers(app)
    add_middlewares(app)
    for router in get_routers(settings.environment):
        app.include_router(router=router)

    return app
