"""Object reports: anonymous allowed, authed reports attach the account."""

from httpx import AsyncClient
from sqlalchemy import select

from app.models import ModerationAction, Report, User
from tests.conftest import ENABLED_AUTH, bearer, mint_token

REPORTS = "/api/v1/artworks/quiet-observer/report"


async def test_anonymous_report_is_queued(
    archive: AsyncClient, session
) -> None:
    response = await archive.post(
        REPORTS, json={"reason": "Wrong attribution", "details": "Creator is someone else."}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "open"
    assert data["artwork_slug"] == "quiet-observer"
    assert response.json()["meta"]["message"]

    row = (
        (await session.execute(select(Report).where(Report.id == data["report_id"])))
        .scalars()
        .first()
    )
    assert row is not None
    assert row.reporter_id is None
    assert row.details == "Creator is someone else."


@ENABLED_AUTH
async def test_signed_in_report_links_account(
    archive: AsyncClient, session, es256
) -> None:
    private_key, _ = es256
    token = mint_token(private_key)
    response = await archive.post(
        REPORTS, headers=bearer(token), json={"reason": "License violation"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "open"

    row = (
        (await session.execute(select(Report).order_by(Report.created_at.desc())))
        .scalars()
        .first()
    )
    assert row is not None and row.reporter_id is not None
    assert row.details is None


async def test_report_validation_and_missing_artwork(
    archive: AsyncClient,
) -> None:
    empty = await archive.post(REPORTS, json={"reason": "   "})
    assert empty.status_code == 422

    too_long = await archive.post(REPORTS, json={"reason": "x" * 121})
    assert too_long.status_code == 422

    missing = await archive.post(
        "/api/v1/artworks/does-not-exist/report", json={"reason": "Anything"}
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "ARTWORK_NOT_FOUND"


async def test_moderation_requires_auth(archive: AsyncClient) -> None:
    queue = await archive.get("/api/v1/moderation/reports")
    assert queue.status_code == 401
    assert queue.json()["error"]["code"] == "AUTH_REQUIRED"


@ENABLED_AUTH
async def test_moderation_requires_moderator_role(
    archive: AsyncClient, es256
) -> None:
    private_key, _ = es256
    token = mint_token(private_key)
    await archive.get("/api/v1/auth/me", headers=bearer(token))  # provision as USER

    queue = await archive.get("/api/v1/moderation/reports", headers=bearer(token))
    assert queue.status_code == 403
    assert queue.json()["error"]["code"] == "MODERATOR_REQUIRED"


@ENABLED_AUTH
async def test_moderator_resolves_report(
    archive: AsyncClient, session, es256
) -> None:
    from app.models.enums import UserRole

    private_key, _ = es256
    token = mint_token(private_key)
    await archive.get("/api/v1/auth/me", headers=bearer(token))
    row = (
        (await session.execute(select(User).where(User.email == "collector@example.com")))
        .scalars()
        .first()
    )
    row.role = UserRole.MODERATOR

    filed = await archive.post(REPORTS, json={"reason": "Wrong attribution"})
    report_id = filed.json()["data"]["report_id"]

    closed = await archive.post(
        f"/api/v1/moderation/reports/{report_id}/review",
        headers=bearer(token),
        json={"decision": "resolved", "notes": "Attribution corrected."},
    )
    assert closed.status_code == 200
    assert closed.json()["data"]["status"] == "resolved"

    action = (
        (
            await session.execute(
                select(ModerationAction).where(ModerationAction.entity_id == report_id)
            )
        )
        .scalars()
        .first()
    )
    assert action is not None
    assert action.action == "resolved"
    assert action.notes == "Attribution corrected."

    bad_decision = await archive.post(
        f"/api/v1/moderation/reports/{report_id}/review",
        headers=bearer(token),
        json={"decision": "approved"},
    )
    assert bad_decision.status_code == 400

    queue = await archive.get(
        "/api/v1/moderation/reports",
        headers=bearer(token),
        params={"status": "open"},
    )
    assert queue.json()["meta"]["total"] == 0
