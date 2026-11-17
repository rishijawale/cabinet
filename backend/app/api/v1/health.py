from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.responses import ok

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(session: SessionDep) -> dict:
    await session.execute(text("SELECT 1"))
    return ok({"status": "ok", "environment": settings.environment, "version": "0.1.0"})
