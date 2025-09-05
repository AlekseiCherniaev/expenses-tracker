from fastapi import APIRouter

from expenses_tracker.infrastructure.api.endpoints.internal.docs import (
    router as docs_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.status import (
    router as status_router,
)

public_router = APIRouter()
internal_router = APIRouter(prefix="/internal")

internal_router.include_router(docs_router)
internal_router.include_router(status_router)
