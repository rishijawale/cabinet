from typing import TYPE_CHECKING

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole, UserStatus, enum_column

if TYPE_CHECKING:
    from app.models.artwork import Artwork
    from app.models.collection import Collection


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("supabase_sub", name="uq_users_supabase_sub"),)

    supabase_sub: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(
        enum_column(UserRole, "user_role"), nullable=False, default=UserRole.USER
    )
    status: Mapped[UserStatus] = mapped_column(
        enum_column(UserStatus, "user_status"), nullable=False, default=UserStatus.ACTIVE
    )

    artworks: Mapped[list["Artwork"]] = relationship(back_populates="creator")
    curated_collections: Mapped[list["Collection"]] = relationship(back_populates="curator")
