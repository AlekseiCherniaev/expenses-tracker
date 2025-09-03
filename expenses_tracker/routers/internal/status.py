import structlog
from fastapi import APIRouter

router = APIRouter(tags=["status"])

logger = structlog.getLogger(__name__)


@router.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    logger.debug("Health check")
    return {"status": "OK"}
