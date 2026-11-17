from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.responses import ok
from app.repositories.taxonomy import list_categories
from app.schemas.archive import CategoryOut

router = APIRouter(tags=["archive"])


@router.get("/categories")
async def categories(session: SessionDep) -> dict:
    rows = await list_categories(session)
    data = [
        CategoryOut(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            cover_image=category.cover_image,
            display_order=category.display_order,
            artwork_count=count,
        )
        for category, count in rows
    ]
    return ok([item.model_dump(mode="json") for item in data])
