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
