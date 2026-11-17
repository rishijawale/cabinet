"""Reports: per-artwork problem flags written to the `reports` table.

Anonymous reports are allowed; the `reporter_id` column records the account
when the request is authenticated.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Artwork, Report
from app.models.enums import ReportStatus


async def create_report(
    session: AsyncSession,
    artwork: Artwork,
    reason: str,
    details: str | None,
    reporter_id=None,
) -> Report:
    report = Report(
        artwork_id=artwork.id,
        reporter_id=reporter_id,
        reason=reason,
        details=details,
        status=ReportStatus.OPEN,
    )
    session.add(report)
    await session.flush()
    await session.refresh(report)
    return report


async def list_reports(
    session: AsyncSession,
    status: ReportStatus | None = None,
    offset: int = 0,
    limit: int = 24,
) -> tuple[list[Report], int]:
    query = (
        select(Report)
        .options(joinedload(Report.artwork))
        .order_by(Report.created_at.desc(), Report.id.desc())
    )
    count_query = select(func.count()).select_from(Report)
    if status is not None:
        query = query.where(Report.status == status)
        count_query = count_query.where(Report.status == status)
    items = (
        (await session.execute(query.offset(offset).limit(limit))).scalars().unique().all()
    )
    total = (await session.execute(count_query)).scalar_one()
    return list(items), total


async def get_report(session: AsyncSession, report_id) -> Report | None:
    return (
        (
            await session.execute(
                select(Report)
                .options(joinedload(Report.artwork))
                .where(Report.id == report_id)
            )
        )
        .scalars()
        .unique()
        .first()
    )


async def review_report(
    session: AsyncSession,
    report: Report,
    *,
    moderator_id,
    decision: str,
    notes: str | None,
) -> Report:
    """Apply the decision, log it, and return the report with its artwork."""
    from app.models import ModerationAction
    from app.models.enums import ReportStatus

    report.status = ReportStatus(decision)
    session.add(report)
    session.add(
        ModerationAction(
            actor_id=moderator_id,
            entity_type="report",
            entity_id=report.id,
            action=decision,
            notes=notes,
        )
    )
    await session.flush()
    return (
        (
            await session.execute(
                select(Report)
                .options(joinedload(Report.artwork))
                .where(Report.id == report.id)
            )
        )
        .scalars()
        .unique()
        .one()
    )
