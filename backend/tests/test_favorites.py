"""Favorites endpoints: auth gating, idempotency and atomic counters."""

import uuid

from httpx import AsyncClient
from sqlalchemy import select

from app.models import Artwork
from tests.conftest import ENABLED_AUTH, bearer, mint_token


async def test_favorites_require_auth(archive: AsyncClient) -> None:
    """With auth disabled the favorites surface is closed, not open."""
    listing = await archive.get("/api/v1/favorites")
    assert listing.status_code == 401
    assert listing.json()["error"]["code"] == "AUTH_REQUIRED"

    saving = await archive.post("/api/v1/favorites/quiet-observer")
    assert saving.status_code == 401


@ENABLED_AUTH
async def test_favorite_add_idempotent_remove_cycle(
    archive: AsyncClient, session, es256
) -> None:
    private_key, _ = es256
    token = mint_token(
        private_key,
        sub=str(uuid.uuid4()),
        overrides={"email": "saver@example.com", "user_metadata": {"name": "Saver"}},
    )
    headers = bearer(token)
    artwork_row = (
        (await session.execute(select(Artwork).where(Artwork.slug == "quiet-observer")))
        .scalars()
        .one()
    )
    baseline = int(artwork_row.favorite_count)

    first = await archive.post("/api/v1/favorites/quiet-observer", headers=headers)
    assert first.status_code == 200
    body = first.json()["data"]
    assert body == {"saved": True, "already_saved": False, "favorite_count": baseline + 1}

    listing = await archive.get("/api/v1/favorites", headers=headers)
    assert listing.status_code == 200
    slugs = [card["slug"] for card in listing.json()["data"]]
    assert "quiet-observer" in slugs
    assert listing.json()["meta"]["total"] == 1

    repeat = await archive.post("/api/v1/favorites/quiet-observer", headers=headers)
    assert repeat.status_code == 200
    assert repeat.json()["data"]["already_saved"] is True
    assert repeat.json()["data"]["favorite_count"] == baseline + 1

    await session.refresh(artwork_row)
    assert int(artwork_row.favorite_count) == baseline + 1

    removed = await archive.delete("/api/v1/favorites/quiet-observer", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["data"]["favorite_count"] == baseline

    await session.refresh(artwork_row)
    assert int(artwork_row.favorite_count) == baseline

    # Deleting again must not drive the counter negative.
    repeat_remove = await archive.delete(
        "/api/v1/favorites/quiet-observer", headers=headers
    )
    assert repeat_remove.status_code == 200
    assert repeat_remove.json()["data"]["favorite_count"] == baseline

    empty = await archive.get("/api/v1/favorites", headers=headers)
    assert empty.json()["data"] == []


@ENABLED_AUTH
async def test_favorite_unknown_artwork(archive: AsyncClient, es256) -> None:
    private_key, _ = es256
    token = mint_token(private_key)
    response = await archive.post(
        "/api/v1/favorites/does-not-exist", headers=bearer(token)
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ARTWORK_NOT_FOUND"
