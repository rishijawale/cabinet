"""Submissions: signed-in creators propose new objects for the archive."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.core.pagination import PageDep
from app.core.responses import ok, paginated
from app.repositories.submissions import create_submission, list_submissions_for_user
from app.schemas.engagement import SubmissionCreate, SubmissionOut

router = APIRouter(tags=["submissions"])


@router.post("/submissions")
async def submit(session: SessionDep, user: CurrentUser, payload: SubmissionCreate) -> dict:
    """Record a submission proposal. Media files arrive in a later milestone."""
    submission = await create_submission(session, user.id, payload)
    return ok(
        SubmissionOut.model_validate(submission, from_attributes=True).model_dump(
            mode="json"
        ),
        {
            "message": "Submission received. A moderator will review it.",
        },
    )


@router.get("/submissions")
async def my_submissions(
    session: SessionDep, user: CurrentUser, page: PageDep
) -> dict:
    """The signed-in member's own submissions, newest first."""
    items, total = await list_submissions_for_user(
        session, user.id, offset=page.offset, limit=page.limit
    )
    data = [
        SubmissionOut.model_validate(item, from_attributes=True).model_dump(mode="json")
        for item in items
    ]
    return paginated(data, page.page, page.limit, total)
