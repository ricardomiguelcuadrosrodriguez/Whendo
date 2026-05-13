"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe. Used by docker healthcheck."""
    return {"status": "ok"}
