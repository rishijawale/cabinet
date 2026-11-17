import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Uuid,
    false,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ArtworkStatus, MediaType, Orientation, enum_column

if TYPE_CHECKING:
    from app.models.taxonomy import Category, License, Tag
    from app.models.user import User

artwork_tags = Table(
    "artwork_tags",
    Base.metadata,
    Column(
        "artwork_id",
        Uuid(as_uuid=True),
        ForeignKey("artworks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Uuid(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_artwork_tags_tag_id", "tag_id"),
)


class Artwork(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "artworks"
    __table_args__ = (
        CheckConstraint(
            "NOT redistribution_allowed OR original_key IS NOT NULL",
            name="ck_artworks_redistribution_requires_file",
        ),
        CheckConstraint(
            "status <> 'published' OR published_at IS NOT NULL",
            name="ck_artworks_published_requires_date",
        ),
        CheckConstraint(
            "status <> 'published' OR creator_id IS NOT NULL "
            "OR external_creator_name IS NOT NULL OR creator_anonymous",
            name="ck_artworks_published_requires_attribution",
        ),
        CheckConstraint("file_size >= 0", name="ck_artworks_file_size_non_negative"),
        Index("ix_artworks_status_published_at", "status", "published_at"),
        Index("ix_artworks_category_status", "category_id", "status"),
        Index("ix_artworks_media_type_status", "media_type", "status"),
        Index("ix_artworks_featured", "featured"),
        Index("ix_artworks_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "ix_artworks_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
    )

    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    creator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    external_creator_name: Mapped[str | None] = mapped_column(String(160))
    creator_anonymous: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    original_source_url: Mapped[str | None] = mapped_column(Text)
    preview_key: Mapped[str | None] = mapped_column(Text)
    original_key: Mapped[str | None] = mapped_column(Text)
    media_type: Mapped[MediaType] = mapped_column(
        enum_column(MediaType, "media_type"), nullable=False
    )
    file_format: Mapped[str] = mapped_column(String(16), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    orientation: Mapped[Orientation] = mapped_column(
        enum_column(Orientation, "orientation"), nullable=False, default=Orientation.LANDSCAPE
    )
    license_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("licenses.id", ondelete="RESTRICT"), nullable=False
    )
    redistribution_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    rights_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ArtworkStatus] = mapped_column(
        enum_column(ArtworkStatus, "artwork_status"),
        nullable=False,
        default=ArtworkStatus.DRAFT,
    )
    featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)
    view_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    download_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    favorite_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    category: Mapped["Category"] = relationship(back_populates="artworks")
    creator: Mapped["User | None"] = relationship(back_populates="artworks")
    license: Mapped["License"] = relationship(back_populates="artworks")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=artwork_tags, back_populates="artworks", order_by="Tag.name"
    )
