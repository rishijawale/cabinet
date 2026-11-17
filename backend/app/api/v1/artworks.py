from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from fastapi import APIRouter, Query, Request

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.errors import AppError, NotFoundError
from app.core.pagination import PageDep
from app.core.rate_limit import limiter
from app.core.responses import ok, paginated
from app.models.enums import MediaType, Orientation
from app.repositories.artworks import (
    SORT_OPTIONS,
    ArtworkFilters,
    get_by_slug,
    get_random,
    get_related,
    list_artworks,
    record_download,
    record_view,
)
from app.schemas.archive import LicenseOut
from app.services.serializers import artwork_card
from app.services.serializers import artwork_detail as serialize_artwork_detail
from app.storage import get_storage

router = APIRouter(tags=["artworks"])


def _split(values: list[str] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for value in values:
        out.extend(part.strip() for part in value.split(",") if part.strip())
    return out


def _validate(values: list[str], allowed: set[str], field: str) -> None:
    invalid = sorted(set(values) - allowed)
    if invalid:
        raise AppError(
            "INVALID_FILTER",
            f"Unsupported {field}: {', '.join(invalid)}.",
            status_code=400,
        )


@router.get("/artworks/random")
async def random_artwork(session: SessionDep) -> dict:
    artwork = await get_random(session)
    if artwork is None:
        raise NotFoundError("NO_ARTWORKS", "The archive is empty.")
    return ok(artwork_card(artwork).model_dump(mode="json"))


@router.get("/artworks")
async def artworks(
    session: SessionDep,
    page: PageDep,
    q: str | None = Query(None, max_length=140),
    category: str | None = Query(None, max_length=80),
    tags: list[str] | None = Query(None),
    format: list[str] | None = Query(None),
    media_type: list[str] | None = Query(None),
    orientation: list[str] | None = Query(None),
    sort: str | None = Query(None),
) -> dict:
    formats = [value.lower() for value in _split(format)]
    media_types = _split(media_type)
    orientations = _split(orientation)
    tag_slugs = _split(tags)

    _validate(media_types, {member.value for member in MediaType}, "media type")
    _validate(orientations, {member.value for member in Orientation}, "orientation")
    effective_sort = sort or ("relevance" if q else "recent")
    if effective_sort not in SORT_OPTIONS:
        raise AppError(
            "INVALID_SORT",
            f"Unsupported sort '{effective_sort}'. Use one of: {', '.join(sorted(SORT_OPTIONS))}.",
            status_code=400,
        )

    filters = ArtworkFilters(
        q=q,
        category=category,
        tags=tag_slugs,
        file_formats=formats,
        media_types=media_types,
        orientations=orientations,
        sort=effective_sort,
        page=page.page,
        limit=page.limit,
    )
    items, total = await list_artworks(session, filters)
    return paginated(
        [artwork_card(item).model_dump(mode="json") for item in items],
        page=page.page,
        limit=page.limit,
        total=total,
    )


@router.get("/artworks/{slug}")
async def artwork_detail(slug: str, session: SessionDep) -> dict:
    artwork = await get_by_slug(session, slug)
    if artwork is None:
        raise NotFoundError(
            "ARTWORK_NOT_FOUND", "The requested artwork could not be found."
        )
    related = await get_related(session, artwork)
    payload = serialize_artwork_detail(artwork, related).model_dump(mode="json")
    await record_view(session, artwork)
    payload["view_count"] = artwork.view_count
    return ok(payload)


@router.get("/artworks/{slug}/download")
@limiter.limit("30/minute")
async def download(slug: str, request: Request, session: SessionDep) -> dict:
    artwork = await get_by_slug(session, slug)
    if artwork is None:
        raise NotFoundError(
            "ARTWORK_NOT_FOUND", "The requested artwork could not be found."
        )

    if not artwork.redistribution_allowed or not artwork.original_key:
        return ok(
            {
                "downloadable": False,
                "external_url": artwork.original_source_url,
                "reason": "Cabinet can preview this object but is not permitted to redistribute the original file.",
                "license": LicenseOut.model_validate(artwork.license).model_dump(mode="json")
                if artwork.license
                else None,
            }
        )

    storage = get_storage()
    if not storage.exists(artwork.original_key):
        raise NotFoundError(
            "ASSET_MISSING", "The original file is not available. Please report this object."
        )

    if artwork.original_source_url:
        parsed = urlparse(artwork.original_source_url)
        if parsed.scheme not in {"http", "https"}:
            raise NotFoundError("ASSET_MISSING", "The original source is invalid.")

    url = storage.signed_url(artwork.original_key, settings.download_url_ttl_seconds)
    expires_at = datetime.now(UTC) + timedelta(
        seconds=settings.download_url_ttl_seconds
    )
    await record_download(session, artwork)

    return ok(
        {
            "downloadable": True,
            "url": url,
            "expires_at": expires_at.isoformat(),
            "file_format": artwork.file_format,
            "file_size": artwork.file_size,
            "license": LicenseOut.model_validate(artwork.license).model_dump(mode="json")
            if artwork.license
            else None,
        }
    )
