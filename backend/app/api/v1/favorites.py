from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import NotFoundError
from app.core.responses import ok
from app.repositories.artworks import get_by_slug
from app.repositories.favorites import (
    add_favorite,
    list_favorites,
    remove_favorite,
)
from app.services.serializers import artwork_card

router = APIRouter(tags=["favorites"])


@router.get("/favorites")
async def favorites_index(session: SessionDep, user: CurrentUser) -> dict:
    items = await list_favorites(session, user.id)
    cards = [artwork_card(item).model_dump(mode="json") for item in items]
    return ok(cards, {"total": len(cards)})


@router.post("/favorites/{slug}")
async def favorite_create(session: SessionDep, user: CurrentUser, slug: str) -> dict:
    artwork = await get_by_slug(session, slug)
    if artwork is None:
        raise NotFoundError(
            "ARTWORK_NOT_FOUND", "The requested artwork could not be found."
        )
    created, count = await add_favorite(session, user.id, artwork)
    return ok({"saved": True, "already_saved": not created, "favorite_count": count})


@router.delete("/favorites/{slug}")
async def favorite_delete(session: SessionDep, user: CurrentUser, slug: str) -> dict:
    artwork = await get_by_slug(session, slug)
    if artwork is None:
        raise NotFoundError(
            "ARTWORK_NOT_FOUND", "The requested artwork could not be found."
        )
    removed, count = await remove_favorite(session, user.id, artwork)
    return ok({"saved": False, "favorite_count": count})
