"""Submissions: auth-gated proposals, moderator review, audit logging."""

import uuid

from httpx import AsyncClient
from sqlalchemy import select

from app.models import Submission, User
from app.models.enums import UserRole
from tests.conftest import ENABLED_AUTH, bearer, mint_token

SUBMISSIONS = "/api/v1/submissions"
VALID = {
    "title": "Terminal Garden",
    "description": "A slow ASCII garden for the command line.",
    "source_url": "https://example.org/garden",
    "license_confirmation": True,
    "permission_confirmation": True,
}


async def test_submission_requires_auth(archive: AsyncClient) -> None:
    created = await archive.post(SUBMISSIONS, json=VALID)
    assert created.status_code == 401
    assert created.json()["error"]["code"] == "AUTH_REQUIRED"

    listed = await archive.get(SUBMISSIONS)
    assert listed.status_code == 401


@ENABLED_AUTH
async def test_submission_confirmations_are_enforced(
    archive: AsyncClient, es256
) -> None:
    private_key, _ = es256
    token = mint_token(private_key)

    for field in ("license_confirmation", "permission_confirmation"):
        broken = {**VALID, field: False}
        response = await archive.post(
            SUBMISSIONS, headers=bearer(token), json=broken
        )
        assert response.status_code == 422

    bad_url = await archive.post(
        SUBMISSIONS, headers=bearer(token), json={**VALID, "source_url": "not-a-url"}
    )
    assert bad_url.status_code == 422


@ENABLED_AUTH
async def test_submission_round_trip(
    archive: AsyncClient, session, es256
) -> None:
    private_key, _ = es256
    token = mint_token(private_key)

    created = await archive.post(SUBMISSIONS, headers=bearer(token), json=VALID)
    assert created.status_code == 200
    data = created.json()["data"]
    assert data["status"] == "submitted"
    assert data["title"] == "Terminal Garden"
    assert data["reviewed_at"] is None

    listed = await archive.get(SUBMISSIONS, headers=bearer(token))
    assert listed.status_code == 200
    assert listed.json()["meta"]["total"] == 1
    assert listed.json()["data"][0]["id"] == data["id"]


@ENABLED_AUTH
async def test_moderator_reviews_submission(
    archive: AsyncClient, session, es256
) -> None:
    private_key, _ = es256
    creator_token = mint_token(private_key, sub=str(uuid.uuid4()))
    await archive.post(SUBMISSIONS, headers=bearer(creator_token), json=VALID)

    moderator_token = mint_token(
        private_key,
        sub=str(uuid.uuid4()),
        overrides={"email": "curator@example.com", "user_metadata": {"name": "Curator"}},
    )
    await archive.get("/api/v1/auth/me", headers=bearer(moderator_token))
    moderator = (
        (await session.execute(select(User).where(User.email == "curator@example.com")))
        .scalars()
        .first()
    )
    moderator.role = UserRole.MODERATOR

    queue = await archive.get(
        "/api/v1/moderation/submissions", headers=bearer(moderator_token)
    )
    assert queue.status_code == 200
    assert queue.json()["meta"]["total"] == 1
    submission_id = queue.json()["data"][0]["id"]

    reviewed = await archive.post(
        f"/api/v1/moderation/submissions/{submission_id}/review",
        headers=bearer(moderator_token),
        json={"decision": "rejected", "notes": "Needs a better original file."},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["data"]["status"] == "rejected"
    assert reviewed.json()["data"]["review_notes"] == "Needs a better original file."

    row = (
        (await session.execute(select(Submission).where(Submission.id == submission_id)))
        .scalars()
        .first()
    )
    assert row is not None and row.reviewer_id == moderator.id

    log = await archive.get("/api/v1/moderation/log", headers=bearer(moderator_token))
    assert log.status_code == 200
    assert log.json()["meta"]["total"] == 1
    assert log.json()["data"][0]["action"] == "rejected"

    unknown = await archive.post(
        f"/api/v1/moderation/submissions/{uuid.uuid4()}/review",
        headers=bearer(moderator_token),
        json={"decision": "approved"},
    )
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "SUBMISSION_NOT_FOUND"
