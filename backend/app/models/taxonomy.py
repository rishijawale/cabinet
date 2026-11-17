from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.artwork import Artwork


class Category(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())

    artworks: Mapped[list["Artwork"]] = relationship(back_populates="category")


class Tag(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    artworks: Mapped[list["Artwork"]] = relationship(
        secondary="artwork_tags", back_populates="tags"
    )


class License(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "licenses"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    identifier: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    license_url: Mapped[str | None] = mapped_column(Text)
    attribution_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    commercial_use_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    modification_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    redistribution_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    artworks: Mapped[list["Artwork"]] = relationship(back_populates="license")
