"""Supabase JWT verification against the project's published JWKS.

Supabase issues RS256/ES256 access tokens signed with asymmetric keys
published at `{project}/auth/v1/.well-known/jwks.json`. Tokens carry
`aud: "authenticated"`, `iss: {project}/auth/v1` and a `sub` claim (the
Supabase user id) which becomes the local `users.supabase_sub` key.

Verification failures raise `AppError` subclasses rendered in the standard
error envelope. The JWKS cache refreshes on expiry and whenever an unknown
key id is seen, so Supabase key rotation is picked up without a restart.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import jwt
from jwt import PyJWK, PyJWTError

from app.core.config import settings
from app.core.errors import AppError

ALLOWED_ALGORITHMS = ("ES256", "RS256")


def auth_required_error() -> AppError:
    return AppError(
        "AUTH_REQUIRED",
        "Sign in to use this endpoint.",
        status_code=401,
    )


def invalid_token_error() -> AppError:
    return AppError(
        "TOKEN_INVALID",
        "The session token is missing, malformed or expired.",
        status_code=401,
    )


class UnknownKeyError(Exception):
    """The token's `kid` is not present in the published JWKS."""


class JWKSCache:
    """In-memory cache of the identity provider's signing keys."""

    def __init__(self, ttl_seconds: float = 600.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._keys: dict[str, PyJWK] = {}
        self._fetched_at = 0.0

    async def get_key(self, jwks_url: str, kid: str | None) -> PyJWK:
        stale = (time.monotonic() - self._fetched_at) > self.ttl_seconds
        if kid is None or stale or kid not in self._keys:
            await self._refresh(jwks_url)
        try:
            return self._keys[kid]
        except KeyError:
            raise UnknownKeyError(kid) from None

    async def _refresh(self, jwks_url: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AppError(
                "AUTH_UNAVAILABLE",
                "The identity provider could not be reached.",
                status_code=503,
            ) from exc
        try:
            entries = response.json().get("keys", [])
        except ValueError as exc:
            raise AppError(
                "AUTH_UNAVAILABLE",
                "The identity provider returned malformed keys.",
                status_code=503,
            ) from exc

        keys: dict[str, PyJWK] = {}
        for entry in entries:
            try:
                jwk = PyJWK.from_dict(entry)
            except PyJWTError:
                continue
            if jwk.key_id and jwk.algorithm_name in ALLOWED_ALGORITHMS:
                keys[jwk.key_id] = jwk
        self._keys = keys
        self._fetched_at = time.monotonic()


# Module-level cache so tests can substitute a stub instead of the network.
_cache = JWKSCache()


def bearer_token(request: Any) -> str | None:
    header = request.headers.get("Authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


async def verify_token(token: str) -> dict[str, Any]:
    if not settings.auth_enabled:
        raise auth_required_error()
    try:
        header = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        raise invalid_token_error() from exc

    try:
        jwk = await _cache.get_key(settings.auth_jwks_url, header.get("kid"))
    except UnknownKeyError as exc:
        raise invalid_token_error() from exc

    try:
        return jwt.decode(
            token,
            key=jwk.key,
            algorithms=list(ALLOWED_ALGORITHMS),
            audience=settings.supabase_audience or None,
            issuer=settings.auth_issuer,
            leeway=settings.supabase_leeway_seconds,
            options={"require": ["exp", "iat", "sub"]},
        )
    except PyJWTError as exc:
        raise invalid_token_error() from exc
