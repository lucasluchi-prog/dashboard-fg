"""Health + readiness probes."""

from datetime import datetime, timezone

from fastapi import APIRouter, status
from sqlalchemy import text

from app.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready(db: SessionDep) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}
