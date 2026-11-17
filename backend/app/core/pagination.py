from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query

from app.core.config import settings


@dataclass
class PageParams:
    page: int
    limit: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


def page_params(
    page: Annotated[int, Query(ge=1, description="1-based page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=settings.max_page_size)] = settings.default_page_size,
) -> PageParams:
    return PageParams(page=page, limit=limit)


PageDep = Annotated[PageParams, Depends(page_params)]
