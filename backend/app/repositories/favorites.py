"""Favorites with atomic artwork counters.

`artworks.favorite_count` feeds the popularity score, so it is kept in step
with the join table inside the same transaction: bumped only when a row is
actually created, floored at zero when rows are removed.
"""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artwork, Favorite
from app.repositories.artworks import ARTWORK_LOADS


async def list_favorites(session: AsyncSession, user_id: uuid.UUID) -> list[Artwork]:
    stmt = (
        select(Artwork)
        .join(Favorite, Favorite.artwork_id == Artwork.id)
        .where(Favorite.user_id == user_id)
        .options(*ARTWORK_LOADS)
        .order_by(Favorite.created_at.desc(), Artwork.id.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def add_favorite(
    session: AsyncSession, user_id: uuid.UUID, artwork: Artwork
) -> tuple[bool, int]:
    """Insert the favorite idempotently; returns (created?, favorite_count)."""
    result = await session.execute(
        pg_insert(Favorite)
        .values(user_id=user_id, artwork_id=artwork.id)
        .on_conflict_do_nothing()
    )
    created = bool(result.rowcount)
    if not created:
        return False, int(artwork.favorite_count)

    count = (
        await session.execute(
            update(Artwork)
            .where(Artwork.id == artwork.id)
            .values(favorite_count=Artwork.favorite_count + 1)
            .returning(Artwork.favorite_count)
            .execution_options(synchronize_session=False)
        )
    ).scalar_one()
    await session.commit()
    artwork.favorite_count = int(count)
    return True, int(count)


async def remove_favorite(
    session: AsyncSession, user_id: uuid.UUID, artwork: Artwork
) -> tuple[bool, int]:
    """Delete the favorite if present; returns (removed?, favorite_count)."""
    result = await session.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.artwork_id == artwork.id,
        )
    )
    removed = bool(result.rowcount)
    if not removed:
        return False, int(artwork.favorite_count)

    count = (
        await session.execute(
            update(Artwork)
            .where(Artwork.id == artwork.id)
            .values(favorite_count=func.greatest(Artwork.favorite_count - 1, 0))
            .returning(Artwork.favorite_count)
            .execution_options(synchronize_session=False)
        )
    ).scalar_one()
    await session.commit()
    artwork.favorite_count = int(count)
    return True, int(count)
