"""Response cache policy: browsable GETs cache in production, never in dev.

Media, downloads, auth surfaces, mutations, errors and health always stay
uncacheable regardless of environment.
"""

import pytest
from httpx import AsyncClient

from app.core.config import settings

MEDIA_CARD = "/media/artworks/quiet-observer/preview-card.webp"


@pytest.fixture
def production(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    return settings


async def test_development_serves_no_store(archive: AsyncClient) -> None:
    response = await archive.get("/api/v1/artworks", params={"limit": 1})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"

    health = await archive.get("/health")
    assert health.headers["cache-control"] == "no-store"


async def test_development_media_revalidates(archive: AsyncClient) -> None:
    response = await archive.get(MEDIA_CARD)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"


async def test_production_caches_browsable_gets(archive: AsyncClient, production) -> None:
    listing = await archive.get("/api/v1/artworks", params={"limit": 1})
    assert listing.headers["cache-control"] == "public, max-age=60"

    detail = await archive.get("/api/v1/artworks/quiet-observer")
    assert detail.headers["cache-control"] == "public, max-age=60"

    categories = await archive.get("/api/v1/categories")
    assert categories.headers["cache-control"] == "public, max-age=60"


async def test_production_caches_media_long(archive: AsyncClient, production) -> None:
    response = await archive.get(MEDIA_CARD)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=604800"


async def test_auth_and_favorites_never_cached(
    archive: AsyncClient, production
) -> None:
    me = await archive.get("/api/v1/auth/me")
    assert me.status_code == 401
    assert me.headers["cache-control"] == "no-store"

    favorites = await archive.get("/api/v1/favorites")
    assert favorites.status_code == 401
    assert favorites.headers["cache-control"] == "no-store"


async def test_download_and_errors_never_cached(
    archive: AsyncClient, production
) -> None:
    download = await archive.get("/api/v1/artworks/quiet-observer/download")
    assert download.headers["cache-control"] == "no-store"

    missing = await archive.get("/api/v1/artworks/does-not-exist")
    assert missing.status_code == 404
    assert missing.headers["cache-control"] == "no-store"


async def test_mutations_never_cached(archive: AsyncClient, production) -> None:
    response = await archive.post("/api/v1/favorites/quiet-observer")
    assert response.status_code == 401  # auth disabled in the base environment
    assert response.headers["cache-control"] == "no-store"
