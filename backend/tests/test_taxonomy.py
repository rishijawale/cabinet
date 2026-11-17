import pytest
from httpx import AsyncClient

API = "/api/v1"


@pytest.mark.asyncio
async def test_categories_are_ordered_with_counts(archive: AsyncClient) -> None:
    response = await archive.get(f"{API}/categories")

    assert response.status_code == 200
    categories = response.json()["data"]
    assert [item["slug"] for item in categories] == ["ascii", "wallpapers", "pixel-art"]
    assert all(item["artwork_count"] > 0 for item in categories)
    assert {item["slug"]: item["artwork_count"] for item in categories} == {
        "ascii": 40,
        "wallpapers": 30,
        "pixel-art": 30,
    }
    assert all(item["cover_image"].endswith("-card.webp") for item in categories)


@pytest.mark.asyncio
async def test_collections_list_features_exhibitions(archive: AsyncClient) -> None:
    response = await archive.get(f"{API}/collections")

    assert response.status_code == 200
    collections = response.json()["data"]
    assert len(collections) == 5
    assert collections[0]["is_featured"] is True
    assert all(item["artwork_count"] > 0 for item in collections)
    assert all(item["cover"]["card"].endswith("-card.webp") for item in collections)
    assert all(item["curator"]["display_name"] for item in collections)


@pytest.mark.asyncio
async def test_collection_detail_lists_published_artworks(archive: AsyncClient) -> None:
    response = await archive.get(f"{API}/collections/tiny-worlds")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["slug"] == "tiny-worlds"
    assert body["artwork_count"] == len(body["artworks"])
    assert body["artworks"]
    assert all(item["category"]["slug"] == "pixel-art" for item in body["artworks"])
    assert all(item["preview"]["card"] for item in body["artworks"])
    assert body["created_at"]


@pytest.mark.asyncio
async def test_missing_collection_returns_404(archive: AsyncClient) -> None:
    response = await archive.get(f"{API}/collections/no-such-exhibition")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COLLECTION_NOT_FOUND"
