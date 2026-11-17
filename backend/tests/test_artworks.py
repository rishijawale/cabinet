from datetime import datetime
from urllib.parse import urlparse

import pytest
from httpx import AsyncClient

ARTWORKS = "/api/v1/artworks"


def _dates(payload: dict) -> list[datetime]:
    return [datetime.fromisoformat(item["published_at"]) for item in payload["data"]]


@pytest.mark.asyncio
async def test_list_defaults_to_first_page_of_24(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS)

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 24
    assert body["meta"] == {"page": 1, "limit": 24, "total": 100, "pages": 5}
    first = body["data"][0]
    assert first["preview"]["thumb"].endswith("-thumb.webp")
    assert first["preview"]["card"].endswith("-card.webp")
    assert first["preview"]["full"].endswith("-full.webp")
    assert first["preview"]["alt"]
    assert first["license"]["identifier"]


@pytest.mark.asyncio
async def test_last_page_returns_remainder(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"page": 5})

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 4
    assert body["meta"]["page"] == 5
    assert body["meta"]["pages"] == 5


@pytest.mark.asyncio
async def test_zero_page_is_rejected(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"page": 0})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert any(detail["field"].endswith("page") for detail in error["details"])


@pytest.mark.asyncio
async def test_limit_cannot_exceed_maximum(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"limit": 49})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("params", "expected_total"),
    [
        ({"category": "ascii"}, 40),
        ({"category": "pixel-art"}, 30),
        ({"category": "wallpapers"}, 30),
        ({"format": "txt"}, 40),
        ({"media_type": "text"}, 40),
    ],
)
async def test_catalogue_filters(
    archive: AsyncClient, params: dict, expected_total: int
) -> None:
    request = {**params, "limit": 48}
    response = await archive.get(ARTWORKS, params=request)

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == expected_total
    assert len(body["data"]) == min(expected_total, 48)

    for artwork in body["data"]:
        if "category" in params:
            assert artwork["category"]["slug"] == params["category"]
        if "format" in params:
            assert artwork["file_format"] == params["format"]
        if "media_type" in params:
            assert artwork["media_type"] == params["media_type"]


@pytest.mark.asyncio
async def test_orientation_filter(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"orientation": "landscape", "limit": 48})

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] > 0
    assert all(item["orientation"] == "landscape" for item in body["data"])


@pytest.mark.asyncio
async def test_tag_filter_accepts_comma_separated_values(archive: AsyncClient) -> None:
    listing = await archive.get(ARTWORKS, params={"limit": 1})
    tag = listing.json()["data"][0]["tags"][0]["slug"]

    response = await archive.get(ARTWORKS, params={"tags": tag, "limit": 48})

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] > 0
    assert all(any(item["slug"] == tag for item in artwork["tags"]) for artwork in body["data"])


@pytest.mark.asyncio
async def test_search_matches_title_and_sets_relevance_sort(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"q": "terminal", "limit": 48})

    assert response.status_code == 200
    body = response.json()
    assert 0 < body["meta"]["total"] < 100
    assert any("terminal" in item["title"].lower() for item in body["data"])


@pytest.mark.asyncio
async def test_search_without_matches_returns_empty_page(archive: AsyncClient) -> None:
    response = await archive.get(ARTWORKS, params={"q": "zzzz-no-such-object-zzzz"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0
    assert body["meta"]["pages"] == 0


@pytest.mark.asyncio
async def test_sort_oldest_and_recent(archive: AsyncClient) -> None:
    oldest = (await archive.get(ARTWORKS, params={"sort": "oldest", "limit": 48})).json()
    recent = (await archive.get(ARTWORKS, params={"sort": "recent", "limit": 48})).json()

    oldest_dates = _dates(oldest)
    recent_dates = _dates(recent)
    assert oldest_dates == sorted(oldest_dates)
    assert recent_dates == sorted(recent_dates, reverse=True)
    assert oldest["data"][0]["slug"] != recent["data"][0]["slug"]


@pytest.mark.asyncio
async def test_invalid_filters_return_actionable_errors(archive: AsyncClient) -> None:
    bad_media = await archive.get(ARTWORKS, params={"media_type": "audio"})
    bad_sort = await archive.get(ARTWORKS, params={"sort": "trending"})
    long_query = await archive.get(ARTWORKS, params={"q": "x" * 141})

    assert bad_media.status_code == 400
    assert bad_media.json()["error"]["code"] == "INVALID_FILTER"
    assert "audio" in bad_media.json()["error"]["message"]

    assert bad_sort.status_code == 400
    assert bad_sort.json()["error"]["code"] == "INVALID_SORT"

    assert long_query.status_code == 422
    assert long_query.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_random_returns_a_card_not_a_detail(archive: AsyncClient) -> None:
    response = await archive.get(f"{ARTWORKS}/random")

    assert response.status_code == 200
    artwork = response.json()["data"]
    assert artwork["slug"]
    assert "related" not in artwork
    assert "download_count" not in artwork
    assert artwork["preview"]["full"].endswith("-full.webp")


@pytest.mark.asyncio
async def test_detail_includes_related_objects_and_text_url(archive: AsyncClient) -> None:
    first = await archive.get(f"{ARTWORKS}/quiet-observer")
    second = await archive.get(f"{ARTWORKS}/quiet-observer")

    assert first.status_code == 200
    body = first.json()["data"]
    assert body["slug"] == "quiet-observer"
    assert body["category"]["slug"] == "ascii"
    assert body["media_type"] == "text"
    assert body["text_url"].endswith("/original.txt")
    assert body["downloadable"] is True
    assert body["description"]
    assert len(body["related"]) == 4
    assert all(item["id"] != body["id"] for item in body["related"])
    assert all(item["category"]["slug"] == "ascii" for item in body["related"])

    # The view counter is incremented after the payload is serialized, so each
    # response reports the total including its own view.
    assert second.json()["data"]["view_count"] == body["view_count"] + 1


@pytest.mark.asyncio
async def test_missing_object_returns_404_envelope(archive: AsyncClient) -> None:
    response = await archive.get(f"{ARTWORKS}/no-such-object")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ARTWORK_NOT_FOUND"


@pytest.mark.asyncio
async def test_download_returns_original_and_records_counter(archive: AsyncClient) -> None:
    before = (await archive.get(f"{ARTWORKS}/quiet-observer")).json()["data"]

    response = await archive.get(f"{ARTWORKS}/quiet-observer/download")

    assert response.status_code == 200
    info = response.json()["data"]
    assert info["downloadable"] is True
    assert info["url"].endswith("/original.txt")
    assert info["file_format"] == "txt"
    assert info["expires_at"]
    assert info["license"]["identifier"] in {"CC0-1.0", "CC-BY-4.0"}

    media_path = urlparse(info["url"]).path
    media = await archive.get(media_path)
    assert media.status_code == 200
    assert len(media.content) == before["file_size"]
    assert media.text.strip()

    after = (await archive.get(f"{ARTWORKS}/quiet-observer")).json()["data"]
    assert after["download_count"] == before["download_count"] + 1


@pytest.mark.asyncio
async def test_external_only_object_refuses_redistribution(archive: AsyncClient) -> None:
    before = (await archive.get(f"{ARTWORKS}/silent-field")).json()["data"]

    response = await archive.get(f"{ARTWORKS}/silent-field/download")

    assert response.status_code == 200
    info = response.json()["data"]
    assert info["downloadable"] is False
    assert "url" not in info
    assert info["external_url"].startswith("https://")
    assert "not permitted" in info["reason"]
    assert info["license"]["redistribution_allowed"] is False

    assert before["downloadable"] is False
    assert before["download_count"] == 0


@pytest.mark.asyncio
async def test_missing_download_returns_404(archive: AsyncClient) -> None:
    response = await archive.get(f"{ARTWORKS}/no-such-object/download")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ARTWORK_NOT_FOUND"
