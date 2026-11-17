from fastapi import APIRouter

from app.api.v1 import (
    artworks,
    auth,
    categories,
    collections,
    favorites,
    health,
    moderation,
    reports,
    submissions,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(categories.router)
api_router.include_router(artworks.router)
api_router.include_router(collections.router)
api_router.include_router(auth.router)
api_router.include_router(favorites.router)
api_router.include_router(submissions.router)
api_router.include_router(reports.router)
api_router.include_router(moderation.router)
