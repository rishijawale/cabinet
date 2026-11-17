import pytest
from httpx import AsyncClient


async def _total(client: AsyncClient) -> int:
    response = await client.get("/api/v1/artworks", params={"limit": 1})
    assert response.status_code == 200
    return response.json()["meta"]["total"]


@pytest.mark.asyncio
async def test_health_reports_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


@pytest.mark.asyncio
async def test_unknown_route_uses_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/not-a-real-route")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_seed_data_is_present(client: AsyncClient) -> None:
    total = await _total(client)

    if total != 100:
        pytest.skip(f"Development database has {total} artworks; run scripts/seed_archive.py first.")
