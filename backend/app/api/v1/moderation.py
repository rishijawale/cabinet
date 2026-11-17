"""Moderation queue: review submissions and reports, audit to the log.

Every route requires the moderator or admin role; with auth disabled the
token check fails first and the response is 401.
"""

from fastapi import APIRouter, Query

from app.api.deps import ModeratorUser, SessionDep
from app.core.errors import AppError, NotFoundError
from app.core.pagination import PageDep
from app.core.responses import ok, paginated
from app.models import ModerationAction
from app.models.enums import ReportStatus, SubmissionStatus
from app.repositories.reports import get_report, list_reports, review_report
from app.repositories.submissions import (
    get_submission,
    list_submissions,
    review_submission,
)
from app.schemas.engagement import ReviewCreate, SubmissionOut
from app.services.serializers import report_out

router = APIRouter(tags=["moderation"])


def _status_or_none(value: str | None, enum_cls, code: str):
    if value is None:
        return None
    try:
        return enum_cls(value.lower())
    except ValueError:
        raise AppError(
            code,
            f"Unsupported status filter: {value}.",
            status_code=400,
        ) from None


@router.get("/moderation/submissions")
async def moderation_submissions(
    session: SessionDep,
    moderator: ModeratorUser,
    page: PageDep,
    status: str | None = Query(default=None),
) -> dict:
    filtered = _status_or_none(status, SubmissionStatus, "INVALID_FILTER")
    items, total = await list_submissions(
        session, status=filtered, offset=page.offset, limit=page.limit
    )
    data = [
        SubmissionOut.model_validate(item, from_attributes=True).model_dump(mode="json")
        for item in items
    ]
    return paginated(data, page.page, page.limit, total)


@router.post("/moderation/submissions/{submission_id}/review")
async def review_moderation_submission(
    submission_id: str,
    session: SessionDep,
    moderator: ModeratorUser,
    payload: ReviewCreate,
) -> dict:
    if payload.decision not in {"approved", "rejected"}:
        raise AppError(
            "INVALID_DECISION",
            "Submission review decisions are approved or rejected.",
            status_code=400,
        )
    submission = await get_submission(session, submission_id)
    if submission is None:
        raise NotFoundError(
            "SUBMISSION_NOT_FOUND", "The requested submission could not be found."
        )
    reviewed = await review_submission(
        session,
        submission,
        reviewer_id=moderator.id,
        decision=payload.decision,
        notes=payload.notes,
    )
    return ok(
        SubmissionOut.model_validate(reviewed, from_attributes=True).model_dump(mode="json")
    )


@router.get("/moderation/reports")
async def moderation_reports(
    session: SessionDep,
    moderator: ModeratorUser,
    page: PageDep,
    status: str | None = Query(default=None),
) -> dict:
    filtered = _status_or_none(status, ReportStatus, "INVALID_FILTER")
    items, total = await list_reports(
        session, status=filtered, offset=page.offset, limit=page.limit
    )
    data = [report_out(item).model_dump(mode="json") for item in items]
    return paginated(data, page.page, page.limit, total)


@router.post("/moderation/reports/{report_id}/review")
async def review_moderation_report(
    report_id: str,
    session: SessionDep,
    moderator: ModeratorUser,
    payload: ReviewCreate,
) -> dict:
    if payload.decision not in {"resolved", "dismissed"}:
        raise AppError(
            "INVALID_DECISION",
            "Report review decisions are resolved or dismissed.",
            status_code=400,
        )
    report = await get_report(session, report_id)
    if report is None:
        raise NotFoundError("REPORT_NOT_FOUND", "The requested report could not be found.")
    reviewed = await review_report(
        session,
        report,
        moderator_id=moderator.id,
        decision=payload.decision,
        notes=payload.notes,
    )
    return ok(report_out(reviewed).model_dump(mode="json"))


@router.get("/moderation/log")
async def moderation_log(
    session: SessionDep, moderator: ModeratorUser, page: PageDep
) -> dict:
    """The moderation audit trail, newest first."""
    from sqlalchemy import func, select

    query = select(ModerationAction).order_by(
        ModerationAction.created_at.desc(), ModerationAction.id.desc()
    )
    items = (
        (await session.execute(query.offset(page.offset).limit(page.limit))).scalars().all()
    )
    total = (
        (await session.execute(select(func.count()).select_from(ModerationAction)))
        .scalar_one()
    )
    data = [
        {
            "id": str(item.id),
            "entity_type": item.entity_type,
            "entity_id": str(item.entity_id),
            "action": item.action,
            "notes": item.notes,
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]
    return paginated(data, page.page, page.limit, total)
