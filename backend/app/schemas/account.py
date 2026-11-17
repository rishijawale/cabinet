from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountOut(BaseModel):
    id: UUID
    username: str
    display_name: str
    email: str | None
    avatar_url: str | None
    status: str
    created_at: datetime
