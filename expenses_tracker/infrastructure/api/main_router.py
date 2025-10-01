from fastapi import APIRouter

from expenses_tracker.core.constants import Environment
from expenses_tracker.infrastructure.api.endpoints.internal.budget import (
    router as internal_budget_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.category import (
    router as internal_category_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.docs import (
    router as docs_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.expense import (
    router as internal_expense_router,
)
from expenses_tracker.infrastructure.api.endpoints.internal.user import (
    router as internal_user_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.auth import (
    router as auth_user_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.budget import (
    router as budget_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.category import (
    router as category_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.expense import (
    router as expense_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.health import (
    router as health_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.oauth import (
    router as oauth_user_router,
)
from expenses_tracker.infrastructure.api.endpoints.public.user import (
    router as user_router,
)


def create_public_router() -> APIRouter:
    router = APIRouter(prefix="/api")
    router.include_router(auth_user_router)
    router.include_router(oauth_user_router)
    router.include_router(user_router)
    router.include_router(category_router)
    router.include_router(expense_router)
    router.include_router(budget_router)
    router.include_router(health_router)
    return router


def create_internal_router() -> APIRouter:
    router = APIRouter(prefix="/api/internal")
    router.include_router(internal_user_router)
    router.include_router(internal_category_router)
    router.include_router(internal_expense_router)
    router.include_router(internal_budget_router)
    router.include_router(docs_router)
    return router


def get_routers(environment: Environment) -> list[APIRouter]:
    routers = [create_public_router()]
    if environment != Environment.PROD:
        routers.append(create_internal_router())
    return routers
