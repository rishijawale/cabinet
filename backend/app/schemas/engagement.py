"""Request and response models for reports, submissions and moderation."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Preset reasons the interface offers; the API accepts any short free text so
# new reasons do not require a migration.
REPORT_REASON_MAX = 120
REPORT_DETAILS_MAX = 2000
SUBMISSION_TITLE_MAX = 200
SUBMISSION_DESCRIPTION_MAX = 4000
REVIEW_NOTES_MAX = 2000

_URL = re.compile(r"^https?://\S+$")


class ReportCreate(BaseModel):
    reason: str = Field(min_length=1, max_length=REPORT_REASON_MAX)
    details: str | None = Field(default=None, max_length=REPORT_DETAILS_MAX)

    @field_validator("reason")
    @classmethod
    def _strip_reason(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("reason must not be empty")
        return stripped

    @field_validator("details")
    @classmethod
    def _strip_details(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ReportOut(BaseModel):
    id: UUID
    artwork_slug: str
    artwork_title: str
    reason: str
    details: str | None
    status: str
    reported_by_account: bool
    created_at: datetime


class SubmissionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=SUBMISSION_TITLE_MAX)
    description: str | None = Field(default=None, max_length=SUBMISSION_DESCRIPTION_MAX)
    source_url: str | None = Field(default=None, max_length=2000)
    license_confirmation: Literal[True]
    permission_confirmation: Literal[True]

    @field_validator("title", "description")
    @classmethod
    def _strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("source_url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not _URL.match(value):
            raise ValueError("source_url must be an http(s) URL")
        return value


class SubmissionOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    source_url: str | None
    license_confirmation: bool
    permission_confirmation: bool
    status: str
    created_at: datetime
    reviewed_at: datetime | None
    review_notes: str | None


class ReviewCreate(BaseModel):
    """Moderator decision. `decision` drives the target status transition."""

    decision: Literal["approved", "rejected", "resolved", "dismissed"]
    notes: str | None = Field(default=None, max_length=REVIEW_NOTES_MAX)

    @field_validator("notes")
    @classmethod
    def _strip(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
