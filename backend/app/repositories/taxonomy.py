from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Artwork, Category, Collection, CollectionItem
from app.models.enums import ArtworkStatus


async def list_categories(session: AsyncSession) -> list[tuple[Category, int]]:
    stmt = (
        select(Category, func.count(Artwork.id))
        .outerjoin(
            Artwork,
            and_(
                Artwork.category_id == Category.id,
                Artwork.status == ArtworkStatus.PUBLISHED,
            ),
        )
        .where(Category.active.is_(True))
        .group_by(Category.id)
        .order_by(Category.display_order.asc(), Category.name.asc())
    )
    rows = await session.execute(stmt)
    return [(row[0], int(row[1])) for row in rows.all()]


async def list_collections(session: AsyncSession) -> list[tuple[Collection, int]]:
    counts = (
        select(
            CollectionItem.collection_id.label("collection_id"),
            func.count(CollectionItem.artwork_id).label("item_count"),
        )
        .group_by(CollectionItem.collection_id)
        .subquery()
    )
    stmt = (
        select(Collection, func.coalesce(counts.c.item_count, 0))
        .outerjoin(counts, counts.c.collection_id == Collection.id)
        .where(Collection.is_public.is_(True))
        .options(
            joinedload(Collection.cover_artwork).joinedload(Artwork.category),
            joinedload(Collection.cover_artwork).joinedload(Artwork.creator),
            joinedload(Collection.curator),
        )
        .order_by(Collection.is_featured.desc(), Collection.created_at.desc())
    )
    rows = await session.execute(stmt)
    return [(row[0], int(row[1])) for row in rows.unique().all()]


async def get_collection(session: AsyncSession, slug: str) -> Collection | None:
    stmt = (
        select(Collection)
        .where(Collection.slug == slug, Collection.is_public.is_(True))
        .options(
            joinedload(Collection.cover_artwork).joinedload(Artwork.category),
            joinedload(Collection.cover_artwork).joinedload(Artwork.creator),
            joinedload(Collection.curator),
        )
    )
    return (await session.execute(stmt)).unique().scalars().first()


async def get_collection_artworks(
    session: AsyncSession, collection_id, *, limit: int | None = None
):
    from app.repositories.artworks import ARTWORK_LOADS

    stmt = (
        select(Artwork)
        .join(CollectionItem, CollectionItem.artwork_id == Artwork.id)
        .where(
            CollectionItem.collection_id == collection_id,
            Artwork.status == ArtworkStatus.PUBLISHED,
        )
        .options(*ARTWORK_LOADS)
        .order_by(CollectionItem.display_order.asc(), Artwork.published_at.desc())
    )
    if limit:
        stmt = stmt.limit(limit)
    return list((await session.execute(stmt)).scalars().all())
