import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.artwork import Artwork
    from app.models.user import User


class Collection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collections"

    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_artwork_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("artworks.id", ondelete="SET NULL")
    )
    curator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    cover_artwork: Mapped["Artwork | None"] = relationship(foreign_keys=[cover_artwork_id])
    curator: Mapped["User | None"] = relationship(back_populates="curated_collections")
    items: Mapped[list["CollectionItem"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionItem.display_order",
    )


class CollectionItem(Base):
    __tablename__ = "collection_items"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    artwork_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("artworks.id", ondelete="CASCADE"), primary_key=True
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    collection: Mapped["Collection"] = relationship(back_populates="items")
    artwork: Mapped["Artwork"] = relationship()
