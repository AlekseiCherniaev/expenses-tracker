import time
from typing import Callable, Awaitable

from fastapi import Response, FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from expenses_tracker.infrastructure.monitoring.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        response: Response = await call_next(request)

        process_time = time.time() - start_time
        endpoint = request.url.path

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(process_time)

        return response


def setup_metrics_route(app: FastAPI) -> None:
    @app.get("/api/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
