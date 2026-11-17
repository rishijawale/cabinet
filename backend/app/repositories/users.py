"""Provision local accounts from verified Supabase token claims.

The first time a token is seen we either link the existing account by email
(lets seeded curators sign in to their profile) or create a new one with a
unique username derived from the profile name. `supabase_sub` is the stable
join key afterwards.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import auth_required_error
from app.models import User
from app.models.enums import UserRole, UserStatus

USERNAME_MAX = 40
# The slug must leave room for collision suffixes appended by _unique_username.
_BASE_MAX = 30
_UNSAFE = re.compile(r"[^a-z0-9-]+")


def _slugify(value: str) -> str:
    slug = _UNSAFE.sub("-", value.lower().strip()).strip("-")
    return slug[:_BASE_MAX].strip("-") or "member"


async def _username_taken(session: AsyncSession, username: str) -> bool:
    existing = await session.execute(
        select(User.id).where(User.username == username)
    )
    return existing.scalar_one_or_none() is not None


async def _unique_username(session: AsyncSession, base: str, sub: str) -> str:
    base = _slugify(base)
    if not await _username_taken(session, base):
        return base
    suffix = sub.replace("-", "").lower()[:6] or "user"
    candidate = f"{base}-{suffix}"
    if not await _username_taken(session, candidate):
        return candidate
    for attempt in range(2, 40):
        candidate = f"{base}-{suffix}{attempt}"
        if not await _username_taken(session, candidate):
            return candidate
    raise auth_required_error()  # pragma: no cover - practically unreachable


def _profile(claims: dict) -> dict:
    metadata = claims.get("user_metadata")
    return metadata if isinstance(metadata, dict) else {}


def _display_name(claims: dict) -> str:
    metadata = _profile(claims)
    name = str(metadata.get("name") or "").strip()
    if name:
        return name[:120]
    email = str(claims.get("email") or "").strip()
    if email:
        return email.split("@", 1)[0][:120]
    return "New member"


def _avatar_url(claims: dict) -> str | None:
    metadata = _profile(claims)
    value = metadata.get("avatar_url") or metadata.get("picture")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


async def get_or_provision(session: AsyncSession, claims: dict) -> User:
    sub = str(claims.get("sub") or "").strip()
    if not sub:
        raise auth_required_error()

    email_value = str(claims.get("email") or "").strip().lower()
    email = email_value or None
    provisioned = False

    user = (
        (await session.execute(select(User).where(User.supabase_sub == sub)))
        .scalars()
        .first()
    )
    if user is None and email is not None:
        user = (
            (await session.execute(select(User).where(User.email == email)))
            .scalars()
            .first()
        )
        if user is not None:
            user.supabase_sub = sub
            provisioned = True

    if user is None:
        user = User(
            username=await _unique_username(session, _display_name(claims), sub),
            display_name=_display_name(claims),
            email=email,
            avatar_url=_avatar_url(claims),
            supabase_sub=sub,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        await session.flush()
        provisioned = True

    # get_session never commits implicitly; persist the new or linked account
    # so repeat requests resolve through the supabase_sub lookup.
    if provisioned:
        await session.commit()

    return user
