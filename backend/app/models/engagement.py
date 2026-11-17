import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import UUIDPrimaryKeyMixin
from app.models.enums import ReportStatus, SubmissionStatus, enum_column

if TYPE_CHECKING:
    from app.models.artwork import Artwork
    from app.models.user import User


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    artwork_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("artworks.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    artwork: Mapped["Artwork"] = relationship()


class Download(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "downloads"
    __table_args__ = (Index("ix_downloads_artwork_created", "artwork_id", "created_at"),)

    artwork_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("artworks.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Submission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "submissions"
    __table_args__ = (Index("ix_submissions_status_created", "status", "created_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    artwork_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("artworks.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    license_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permission_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        enum_column(SubmissionStatus, "submission_status"),
        nullable=False,
        default=SubmissionStatus.SUBMITTED,
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    review_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    submitter: Mapped["User"] = relationship(foreign_keys=[user_id])


class Report(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "reports"

    artwork_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("artworks.id", ondelete="CASCADE"), nullable=False
    )
    reporter_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(
        enum_column(ReportStatus, "report_status"),
        nullable=False,
        default=ReportStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    artwork: Mapped["Artwork"] = relationship()


class ModerationAction(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "moderation_actions"
    __table_args__ = (Index("ix_moderation_actions_entity", "entity_type", "entity_id"),)

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
