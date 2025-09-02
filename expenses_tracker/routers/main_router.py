from fastapi import APIRouter

from expenses_tracker.routers.internal.docs import router as docs_router

router = APIRouter()

router.include_router(docs_router)
