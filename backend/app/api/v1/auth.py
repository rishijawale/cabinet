from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.core.responses import ok
from app.schemas.account import AccountOut

router = APIRouter(tags=["auth"])


@router.get("/auth/me")
async def me(session: SessionDep, user: CurrentUser) -> dict:
    """Return the account behind the presented Supabase token.

    The dependency chain verifies the JWT, provisions or links the local
    account and rejects suspended users, so this handler only serialises.
    """
    account = AccountOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        avatar_url=user.avatar_url,
        status=user.status.value,
        created_at=user.created_at,
    )
    return ok(account.model_dump(mode="json"))
