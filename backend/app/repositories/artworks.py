from dataclasses import dataclass, field

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models import Artwork, Category, Tag
from app.models.engagement import Download as DownloadModel
from app.models.enums import ArtworkStatus, MediaType, Orientation

ARTWORK_LOADS = (
    selectinload(Artwork.category),
    joinedload(Artwork.creator),
    joinedload(Artwork.license),
    selectinload(Artwork.tags),
)

SORT_OPTIONS = {"recent", "oldest", "popular", "relevance"}


@dataclass
class ArtworkFilters:
    q: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    file_formats: list[str] = field(default_factory=list)
    media_types: list[str] = field(default_factory=list)
    orientations: list[str] = field(default_factory=list)
    sort: str = "recent"
    page: int = 1
    limit: int = 24

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


def _conditions(filters: ArtworkFilters) -> list:
    conditions = [
        Artwork.status == ArtworkStatus.PUBLISHED,
        Artwork.published_at.is_not(None),
    ]
    if filters.category:
        conditions.append(Artwork.category.has(Category.slug == filters.category))
    for tag in filters.tags:
        conditions.append(Artwork.tags.any(Tag.slug == tag))
    if filters.file_formats:
        conditions.append(Artwork.file_format.in_([f.lower() for f in filters.file_formats]))
    if filters.media_types:
        types = [MediaType(value) for value in filters.media_types]
        conditions.append(Artwork.media_type.in_(types))
    if filters.orientations:
        orientations = [Orientation(value) for value in filters.orientations]
        conditions.append(Artwork.orientation.in_(orientations))
    if filters.q:
        query = filters.q.strip()
        if query:
            tsquery = func.websearch_to_tsquery("simple", query)
            conditions.append(
                or_(
                    Artwork.search_vector.op("@@")(tsquery),
                    Artwork.title.ilike(f"%{query}%"),
                )
            )
    return conditions


def _tsquery(filters: ArtworkFilters):
    if not filters.q or not filters.q.strip():
        return None
    return func.websearch_to_tsquery("simple", filters.q.strip())


def _apply_sort(stmt: Select, filters: ArtworkFilters) -> Select:
    tsquery = _tsquery(filters)
    if filters.sort == "oldest":
        return stmt.order_by(Artwork.published_at.asc(), Artwork.id.asc())
    if filters.sort == "popular":
        popularity = (
            Artwork.download_count * 3 + Artwork.favorite_count * 2 + Artwork.view_count
        )
        return stmt.order_by(popularity.desc(), Artwork.published_at.desc())
    if filters.sort == "relevance" and tsquery is not None:
        rank = func.ts_rank_cd(Artwork.search_vector, tsquery)
        return stmt.order_by(rank.desc(), Artwork.published_at.desc(), Artwork.id.desc())
    return stmt.order_by(Artwork.published_at.desc(), Artwork.id.desc())


async def list_artworks(
    session: AsyncSession, filters: ArtworkFilters
) -> tuple[list[Artwork], int]:
    conditions = _conditions(filters)
    stmt = select(Artwork).where(*conditions).options(*ARTWORK_LOADS)
    stmt = _apply_sort(stmt, filters).offset(filters.offset).limit(filters.limit)
    result = await session.execute(stmt)
    artworks = list(result.scalars().all())

    count_stmt = select(func.count(Artwork.id)).where(*conditions)
    total = int((await session.execute(count_stmt)).scalar_one())
    return artworks, total


async def get_by_slug(session: AsyncSession, slug: str) -> Artwork | None:
    stmt = (
        select(Artwork)
        .where(Artwork.slug == slug, Artwork.status == ArtworkStatus.PUBLISHED)
        .options(*ARTWORK_LOADS)
    )
    return (await session.execute(stmt)).scalars().first()


async def get_related(
    session: AsyncSession, artwork: Artwork, limit: int = 4
) -> list[Artwork]:
    stmt = (
        select(Artwork)
        .where(
            Artwork.status == ArtworkStatus.PUBLISHED,
            Artwork.category_id == artwork.category_id,
            Artwork.id != artwork.id,
        )
        .options(*ARTWORK_LOADS)
        .order_by(func.random())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def get_random(session: AsyncSession) -> Artwork | None:
    stmt = (
        select(Artwork)
        .where(
            Artwork.status == ArtworkStatus.PUBLISHED,
            Artwork.published_at.is_not(None),
        )
        .options(*ARTWORK_LOADS)
        .order_by(func.random())
        .limit(1)
    )
    return (await session.execute(stmt)).scalars().first()


async def record_view(session: AsyncSession, artwork: Artwork) -> None:
    count = (
        await session.execute(
            update(Artwork)
            .where(Artwork.id == artwork.id)
            .values(view_count=Artwork.view_count + 1)
            .returning(Artwork.view_count)
            .execution_options(synchronize_session=False)
        )
    ).scalar_one()
    await session.commit()
    artwork.view_count = int(count)


async def record_download(
    session: AsyncSession, artwork: Artwork, user_id=None
) -> None:
    session.add(DownloadModel(artwork_id=artwork.id, user_id=user_id))
    count = (
        await session.execute(
            update(Artwork)
            .where(Artwork.id == artwork.id)
            .values(download_count=Artwork.download_count + 1)
            .returning(Artwork.download_count)
            .execution_options(synchronize_session=False)
        )
    ).scalar_one()
    await session.commit()
    artwork.download_count = int(count)


__all__ = [
    "ArtworkFilters",
    "SORT_OPTIONS",
    "get_by_slug",
    "get_random",
    "get_related",
    "list_artworks",
    "record_download",
    "record_view",
]
