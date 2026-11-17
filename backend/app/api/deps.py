from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import auth_required_error, bearer_token, verify_token
from app.core.db import get_session
from app.models import User
from app.models.enums import UserStatus
from app.repositories.users import get_or_provision

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_claims(request: Request) -> dict:
    """Verified Supabase token claims, or a 401 rendered in the envelope."""
    token = bearer_token(request)
    if token is None:
        raise auth_required_error()
    return await verify_token(token)


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    claims: Annotated[dict, Depends(get_current_claims)],
) -> User:
    user = await get_or_provision(session, claims)
    if user.status == UserStatus.SUSPENDED:
        from app.core.errors import AppError

        raise AppError(
            "ACCOUNT_SUSPENDED",
            "This account can no longer use the archive.",
            status_code=403,
        )
    return user


AuthClaims = Annotated[dict, Depends(get_current_claims)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    """The account behind the request, or None for anonymous visitors.

    A missing bearer header stays anonymous without touching the network;
    a present one must verify, so forged tokens are rejected even on
    optional-auth endpoints.
    """
    if bearer_token(request) is None:
        return None
    return await get_current_user(session, await get_current_claims(request))


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


async def get_moderator_user(user: CurrentUser) -> User:
    """Current user restricted to moderator and admin roles."""
    from app.core.errors import ForbiddenError
    from app.models.enums import UserRole

    if user.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
        raise ForbiddenError(
            "MODERATOR_REQUIRED",
            "This endpoint is reserved for archive moderators.",
        )
    return user


ModeratorUser = Annotated[User, Depends(get_moderator_user)]
