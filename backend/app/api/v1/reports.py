"""Per-artwork problem reports. Anonymous visitors may file them."""

from fastapi import APIRouter, Request

from app.api.deps import OptionalUser, SessionDep
from app.core.errors import NotFoundError
from app.core.rate_limit import limiter
from app.core.responses import ok
from app.repositories.artworks import get_by_slug
from app.repositories.reports import create_report
from app.schemas.engagement import ReportCreate

router = APIRouter(tags=["reports"])


@router.post("/artworks/{slug}/report")
@limiter.limit("10/minute")
async def report_artwork(
    slug: str,
    request: Request,
    session: SessionDep,
    user: OptionalUser,
    payload: ReportCreate,
) -> dict:
    """Flag an object for curator review; the report is queued as open."""
    artwork = await get_by_slug(session, slug)
    if artwork is None:
        raise NotFoundError(
            "ARTWORK_NOT_FOUND", "The requested artwork could not be found."
        )
    report = await create_report(
        session,
        artwork,
        reason=payload.reason,
        details=payload.details,
        reporter_id=user.id if user else None,
    )
    return ok(
        {
            "report_id": str(report.id),
            "status": report.status.value,
            "artwork_slug": artwork.slug,
        },
        {"message": "Thanks. A curator will take a look."},
    )
