"""Submissions: creator proposals for new objects, reviewed by moderators.

A submission carries intent and metadata only — media files arrive in the
storage milestone, so approval does not yet create an artwork. Every review
decision is recorded in the moderation log.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ModerationAction, Submission
from app.models.enums import SubmissionStatus
from app.schemas.engagement import SubmissionCreate


async def create_submission(
    session: AsyncSession, user_id, payload: SubmissionCreate
) -> Submission:
    submission = Submission(
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        source_url=payload.source_url,
        license_confirmation=True,
        permission_confirmation=True,
        status=SubmissionStatus.SUBMITTED,
    )
    session.add(submission)
    await session.flush()
    await session.refresh(submission)
    return submission


async def list_submissions_for_user(
    session: AsyncSession, user_id, offset: int = 0, limit: int = 24
) -> tuple[list[Submission], int]:
    query = (
        select(Submission)
        .where(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc(), Submission.id.desc())
    )
    count_query = select(func.count()).select_from(Submission).where(
        Submission.user_id == user_id
    )
    items = (await session.execute(query.offset(offset).limit(limit))).scalars().all()
    total = (await session.execute(count_query)).scalar_one()
    return list(items), total


async def list_submissions(
    session: AsyncSession,
    status: SubmissionStatus | None = None,
    offset: int = 0,
    limit: int = 24,
) -> tuple[list[Submission], int]:
    query = select(Submission).order_by(Submission.created_at.desc(), Submission.id.desc())
    count_query = select(func.count()).select_from(Submission)
    if status is not None:
        query = query.where(Submission.status == status)
        count_query = count_query.where(Submission.status == status)
    items = (await session.execute(query.offset(offset).limit(limit))).scalars().all()
    total = (await session.execute(count_query)).scalar_one()
    return list(items), total


async def get_submission(session: AsyncSession, submission_id) -> Submission | None:
    return (
        (await session.execute(select(Submission).where(Submission.id == submission_id)))
        .scalars()
        .first()
    )


async def review_submission(
    session: AsyncSession,
    submission: Submission,
    *,
    reviewer_id,
    decision: str,
    notes: str | None,
) -> Submission:
    """Apply the decision and record it in the moderation log."""
    submission.status = SubmissionStatus(decision)
    submission.reviewer_id = reviewer_id
    submission.review_notes = notes
    submission.reviewed_at = datetime.now(UTC)
    session.add(submission)
    session.add(
        ModerationAction(
            actor_id=reviewer_id,
            entity_type="submission",
            entity_id=submission.id,
            action=decision,
            notes=notes,
        )
    )
    await session.flush()
    await session.refresh(submission)
    return submission
