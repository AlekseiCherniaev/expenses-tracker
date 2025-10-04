from typing import Any
from uuid import uuid4

import structlog
from fastapi import Request, Response, FastAPI, HTTPException, Depends
from pyinstrument import Profiler
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import HTMLResponse
from starlette.types import ASGIApp

from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.infrastructure.di import get_cache_service

logger = structlog.getLogger(__name__)


class RedisProfilingStorage:
    def __init__(self, cache_service: ICacheService[str], ttl_hours: int = 24) -> None:
        self.ttl_seconds = ttl_hours * 3600
        self.cache_service = cache_service

    @staticmethod
    def _profile_cache_key(profile_id: str) -> str:
        return f"profile:{profile_id}"

    async def add_profile(self, profile_id: str, html_content: str) -> None:
        await self.cache_service.set(
            key=self._profile_cache_key(profile_id),
            value=html_content,
            ttl=self.ttl_seconds,
        )
        logger.bind(profile_id=profile_id).debug("Added profile to Redis")

    async def get_profile(self, profile_id: str) -> str | None:
        return await self.cache_service.get(
            key=self._profile_cache_key(profile_id), serializer=str
        )

    async def delete_profile(self, profile_id: str) -> None:
        await self.cache_service.delete(key=self._profile_cache_key(profile_id))

    async def get_stats(self) -> dict[str, int | list[str]]:
        keys = await self.cache_service.get_keys_by_pattern("profile:*")
        return {
            "keys": [key.split("profile:")[1] for key in keys],
            "total_profiles": len(keys),
            "ttl_hours": self.ttl_seconds // 3600,
        }

    async def clear_all_profiles(self) -> None:
        await self.cache_service.delete_keys_by_pattern(pattern="profile:*")
        return None


def get_profiling_storage(
    cache_service: ICacheService[Any] = Depends(get_cache_service),
) -> RedisProfilingStorage:
    return RedisProfilingStorage(cache_service=cache_service)


class PyInstrumentMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/api/internal/static",
            "/api/health",
            "/api/profiling",
            "/api/metrics",
            "/api/internal/docs",
            "/api/internal/openapi.json",
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self._should_profile(request):
            return await call_next(request)

        profiler = Profiler(interval=0.001, async_mode="enabled")
        profiler.start()
        response = await call_next(request)
        profiler.stop()

        try:
            html_content = profiler.output_html()
            profile_id = str(uuid4())
            cache_service = request.app.state.cache_service
            storage = RedisProfilingStorage(cache_service=cache_service)
            await storage.add_profile(profile_id, html_content)
            response.headers["X-Profiling-ID"] = profile_id
            logger.bind(profile_id=profile_id, url_path=request.url.path).info(
                "Profiled request completed"
            )
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")

        return response

    def _should_profile(self, request: Request) -> bool:
        path = request.url.path
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return False
        return True


def setup_pyinstrument_routes(app: FastAPI) -> None:
    @app.get("/api/profiling/{profile_id}", response_class=HTMLResponse)
    async def get_profile(
        profile_id: str, storage: RedisProfilingStorage = Depends(get_profiling_storage)
    ) -> HTMLResponse:
        html = await storage.get_profile(profile_id)
        if html is None:
            raise HTTPException(status_code=404, detail="Profile not found or expired")
        return HTMLResponse(content=html)

    @app.get("/api/profiling")
    async def get_profiling_stats(
        storage: RedisProfilingStorage = Depends(get_profiling_storage),
    ) -> dict[str, int | list[str]]:
        return await storage.get_stats()

    @app.delete("/api/profiling/{profile_id}")
    async def delete_profile(
        profile_id: str, storage: RedisProfilingStorage = Depends(get_profiling_storage)
    ) -> dict[str, str]:
        await storage.delete_profile(profile_id)
        return {"message": "Profile deleted"}

    @app.delete("/api/profiling-delete-all")
    async def delete_all_profiles(
        storage: RedisProfilingStorage = Depends(get_profiling_storage),
    ) -> dict[str, str]:
        await storage.clear_all_profiles()
        return {"message": "All profiles deleted"}
