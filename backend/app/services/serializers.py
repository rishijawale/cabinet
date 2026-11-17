from app.models import Artwork, Collection, User
from app.models.enums import MediaType
from app.schemas.archive import (
    ArtworkCard,
    ArtworkDetail,
    CategoryBrief,
    CollectionCard,
    CollectionDetail,
    CreatorOut,
    LicenseOut,
    PreviewSet,
    TagOut,
)
from app.schemas.engagement import ReportOut
from app.storage import get_storage


def preview_set(artwork: Artwork) -> PreviewSet:
    storage = get_storage()
    name = creator_name(artwork)
    alt = f"{artwork.title} — {artwork.category.name} artwork by {name}"
    base = artwork.preview_key
    if not base:
        return PreviewSet(thumb="", card="", full="", alt=alt)
    return PreviewSet(
        thumb=storage.public_url(f"{base}-thumb.webp"),
        card=storage.public_url(f"{base}-card.webp"),
        full=storage.public_url(f"{base}-full.webp"),
        alt=alt,
    )


def creator_name(artwork: Artwork) -> str:
    if artwork.creator_anonymous:
        return "Anonymous"
    if artwork.creator:
        return artwork.creator.display_name
    return artwork.external_creator_name or "Unknown maker"


def creator_out(artwork: Artwork) -> CreatorOut:
    if artwork.creator_anonymous:
        return CreatorOut(display_name="Anonymous", anonymous=True)
    if artwork.creator:
        return CreatorOut(
            id=artwork.creator.id,
            username=artwork.creator.username,
            display_name=artwork.creator.display_name,
            avatar_url=artwork.creator.avatar_url,
        )
    return CreatorOut(
        display_name=artwork.external_creator_name or "Unknown maker",
        external_name=artwork.external_creator_name,
    )


def user_out(user: User | None) -> CreatorOut | None:
    if user is None:
        return None
    return CreatorOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


def artwork_card(artwork: Artwork) -> ArtworkCard:
    downloadable = bool(artwork.redistribution_allowed and artwork.original_key)
    return ArtworkCard(
        id=artwork.id,
        slug=artwork.slug,
        title=artwork.title,
        category=CategoryBrief.model_validate(artwork.category),
        creator=creator_out(artwork),
        media_type=artwork.media_type.value if isinstance(artwork.media_type, MediaType) else str(artwork.media_type),
        file_format=artwork.file_format,
        width=artwork.width,
        height=artwork.height,
        orientation=artwork.orientation.value
        if hasattr(artwork.orientation, "value")
        else str(artwork.orientation),
        preview=preview_set(artwork),
        license=LicenseOut.model_validate(artwork.license) if artwork.license else None,
        redistributable=artwork.redistribution_allowed,
        downloadable=downloadable,
        featured=artwork.featured,
        published_at=artwork.published_at,
        tags=[TagOut.model_validate(tag) for tag in artwork.tags],
    )


def artwork_detail(artwork: Artwork, related: list[Artwork]) -> ArtworkDetail:
    storage = get_storage()
    text_url = None
    if (
        artwork.media_type in {MediaType.TEXT, "text"}
        and artwork.redistribution_allowed
        and artwork.original_key
    ):
        text_url = storage.public_url(artwork.original_key)

    card = artwork_card(artwork)
    return ArtworkDetail(
        **card.model_dump(),
        description=artwork.description,
        original_source_url=artwork.original_source_url,
        rights_notes=artwork.rights_notes,
        file_size=artwork.file_size,
        text_url=text_url,
        view_count=artwork.view_count,
        download_count=artwork.download_count,
        created_at=artwork.created_at,
        updated_at=artwork.updated_at,
        related=[artwork_card(item) for item in related],
    )


def collection_card(collection: Collection, artwork_count: int) -> CollectionCard:
    cover = preview_set(collection.cover_artwork) if collection.cover_artwork else None
    return CollectionCard(
        id=collection.id,
        slug=collection.slug,
        title=collection.title,
        description=collection.description,
        cover=cover,
        cover_artwork_slug=collection.cover_artwork.slug if collection.cover_artwork else None,
        curator=user_out(collection.curator),
        artwork_count=artwork_count,
        is_featured=collection.is_featured,
    )


def collection_detail(
    collection: Collection, artworks: list[Artwork], artwork_count: int
) -> CollectionDetail:
    base = collection_card(collection, artwork_count)
    return CollectionDetail(
        **base.model_dump(),
        artworks=[artwork_card(item) for item in artworks],
        created_at=collection.created_at,
    )


def report_out(report) -> ReportOut:
    """Serialise a report row. The artwork relationship must be loaded."""
    return ReportOut(
        id=report.id,
        artwork_slug=report.artwork.slug,
        artwork_title=report.artwork.title,
        reason=report.reason,
        details=report.details,
        status=report.status.value if hasattr(report.status, "value") else str(report.status),
        reported_by_account=report.reporter_id is not None,
        created_at=report.created_at,
    )
