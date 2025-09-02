from fastapi import APIRouter

router = APIRouter(tags=["status"])

@router.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    return {"status": "OK"}
