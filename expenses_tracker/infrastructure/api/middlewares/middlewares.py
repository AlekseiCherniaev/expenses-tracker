import structlog
from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from expenses_tracker.core.settings import get_settings
from expenses_tracker.infrastructure.api.middlewares.prometheus import (
    PrometheusMiddleware,
    setup_metrics_route,
)
from expenses_tracker.infrastructure.api.middlewares.pyinstrument import (
    PyInstrumentMiddleware,
    setup_pyinstrument_routes,
)

logger = structlog.getLogger(__name__)


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key)
    setup_metrics_route(app)
    if get_settings().enable_profiling:
        app.add_middleware(PyInstrumentMiddleware)
        setup_pyinstrument_routes(app)
    logger.debug("Middlewares added to the app")
