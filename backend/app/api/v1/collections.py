from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.errors import NotFoundError
from app.core.responses import ok
from app.repositories.taxonomy import get_collection, get_collection_artworks, list_collections
from app.services.serializers import collection_card, collection_detail

router = APIRouter(tags=["collections"])


@router.get("/collections")
async def collections(session: SessionDep) -> dict:
    rows = await list_collections(session)
    data = [
        collection_card(collection, count).model_dump(mode="json")
        for collection, count in rows
    ]
    return ok(data)


@router.get("/collections/{slug}")
async def collection_detail_endpoint(slug: str, session: SessionDep) -> dict:
    collection = await get_collection(session, slug)
    if collection is None:
        raise NotFoundError(
            "COLLECTION_NOT_FOUND", "The requested collection could not be found."
        )
    artworks = await get_collection_artworks(session, collection.id)
    return ok(
        collection_detail(collection, artworks, len(artworks)).model_dump(mode="json")
    )
