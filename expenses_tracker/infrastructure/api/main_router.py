from fastapi import APIRouter

from expenses_tracker.infrastructure.api.endpoints.internal.docs import (
    router as docs_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.status import (
    router as status_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.auth import (
    router as auth_user_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.user import (
    router as user_router,
)

public_router = APIRouter()
public_router.include_router(user_router)
public_router.include_router(auth_user_router)

internal_router = APIRouter(prefix="/internal")

internal_router.include_router(docs_router)
internal_router.include_router(status_router)
