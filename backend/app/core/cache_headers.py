"""Explicit response cache policy.

Development serves everything with `no-store` (API) or `no-cache` (media, where
ETag revalidation keeps it fast) so counter changes and re-seeded previews are
seen immediately. Production marks browsable archive GETs cacheable for a short
window while keeping auth surfaces, mutations, errors and downloads uncached.

Media previews and originals are deterministic outputs of the seed pipeline,
so they are safe to cache for a week; the window is configurable via
`MEDIA_CACHE_MAX_AGE`.
"""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

# Archive browsing: list, detail, random and collection reads.
_BROWSABLE = re.compile(r"^/api/v1/(artworks|categories|collections)(/|$)")
# Per-visitor or mutating surfaces, plus the download endpoint (counter writes
# and signed URLs): never cached.
_FRESH = re.compile(
    r"^/api/v1/(auth|favorites)(/|$)|^/api/v1/artworks/[^/]+/download$"
)


def _cache_control_for(path: str, method: str, status: int) -> str | None:
    if path.startswith("/media"):
        if status == 200:
            if settings.is_development:
                return "no-cache"
            return f"public, max-age={settings.media_cache_max_age}"
        return "no-store"

    if method not in {"GET", "HEAD"}:
        return "no-store"
    if status != 200:
        return "no-store"
    if path in {"/", "/health"} or path.startswith("/api/v1/health"):
        return "no-store"
    if _FRESH.search(path):
        return "no-store"
    if _BROWSABLE.match(path):
        if settings.is_development:
            return "no-store"
        return f"public, max-age={settings.api_cache_max_age}"
    return "no-store"


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Applies the cache policy to every response unless one was set already."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        if "cache-control" not in response.headers:
            header = _cache_control_for(
                request.scope["path"], request.method, response.status_code
            )
            if header:
                response.headers["cache-control"] = header
        return response
