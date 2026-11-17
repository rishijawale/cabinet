from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CategoryOut(CategoryBrief):
    description: str | None = None
    cover_image: str | None = None
    display_order: int = 0
    artwork_count: int = 0


class LicenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    identifier: str
    license_url: str | None = None
    attribution_required: bool
    commercial_use_allowed: bool
    modification_allowed: bool
    redistribution_allowed: bool


class CreatorOut(BaseModel):
    id: UUID | None = None
    username: str | None = None
    display_name: str
    avatar_url: str | None = None
    external_name: str | None = None
    anonymous: bool = False


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str


class PreviewSet(BaseModel):
    thumb: str
    card: str
    full: str
    alt: str


class ArtworkCard(BaseModel):
    id: UUID
    slug: str
    title: str
    category: CategoryBrief
    creator: CreatorOut
    media_type: str
    file_format: str
    width: int | None
    height: int | None
    orientation: str
    preview: PreviewSet
    license: LicenseOut | None
    redistributable: bool
    downloadable: bool
    featured: bool
    published_at: datetime | None
    tags: list[TagOut]


class ArtworkDetail(ArtworkCard):
    description: str | None
    original_source_url: str | None
    rights_notes: str | None
    file_size: int
    text_url: str | None
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    related: list[ArtworkCard]


class CollectionCard(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str | None
    cover: PreviewSet | None
    cover_artwork_slug: str | None
    curator: CreatorOut | None
    artwork_count: int
    is_featured: bool


class CollectionDetail(CollectionCard):
    artworks: list[ArtworkCard]
    created_at: datetime
