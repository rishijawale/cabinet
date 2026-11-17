"""Shared pytest fixtures.

The archive tests run against the development database that has been seeded with
`scripts/seed_archive.py`. Every test is wrapped in a transaction that is rolled
back afterwards, so view/download counters and other writes never leak between
tests.

Auth tests verify Supabase tokens for real against locally generated ES256
keys; only the JWKS transport is replaced by a stub cache.
"""

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import ASGITransport, AsyncClient
from jwt import PyJWK
from jwt.algorithms import ECAlgorithm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core import auth as auth_module
from app.core.config import settings
from app.core.db import get_session
from app.main import app

# The application engine pools connections across event loops, which breaks under
# pytest-asyncio (one loop per test). Tests get a dedicated NullPool engine so
# every connection belongs to the loop that created it.
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)

AUTH_KID = "cabinet-test-key"
AUTH_ISSUER = "https://cabinet-test.supabase.co/auth/v1"


@pytest.fixture
async def archive(client: AsyncClient) -> AsyncClient:
    """Skip the test when the development archive has not been seeded."""
    response = await client.get("/api/v1/artworks", params={"limit": 1})
    total = response.json()["meta"]["total"] if response.status_code == 200 else 0
    if total != 100:
        pytest.skip(
            f"Development database has {total} artworks; run scripts/seed_archive.py first."
        )
    return client


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://cabinet.test") as http:
            yield http
    finally:
        app.dependency_overrides.clear()


class StubJWKSCache:
    """Serves one fixed key instead of fetching the JWKS endpoint."""

    def __init__(self, jwk: PyJWK) -> None:
        self._key = jwk
        self.calls = 0

    async def get_key(self, jwks_url: str, kid: str | None) -> PyJWK:
        self.calls += 1
        if kid != self._key.key_id:
            raise auth_module.UnknownKeyError(kid)
        return self._key


@pytest.fixture
def es256():
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = ECAlgorithm("ES256").to_jwk(private_key, as_dict=True)
    jwk.update({"kid": AUTH_KID, "alg": "ES256", "use": "sig"})
    return private_key, PyJWK.from_dict(jwk)


@pytest.fixture
def auth_settings(monkeypatch):
    """Point auth at a fake Supabase project; auth is disabled by default."""
    monkeypatch.setattr(settings, "supabase_url", "https://cabinet-test.supabase.co")
    monkeypatch.setattr(settings, "supabase_jwks_url", "")
    monkeypatch.setattr(settings, "supabase_audience", "authenticated")
    monkeypatch.setattr(settings, "supabase_issuer", "")
    monkeypatch.setattr(settings, "supabase_leeway_seconds", 30)
    return settings


@pytest.fixture
def stub_cache(monkeypatch, es256) -> StubJWKSCache:
    _, jwk = es256
    stub = StubJWKSCache(jwk)
    monkeypatch.setattr(auth_module, "_cache", stub)
    return stub


def mint_token(
    private_key, sub: str | None = None, overrides: dict | None = None
) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "iss": AUTH_ISSUER,
        "sub": sub or str(uuid.uuid4()),
        "aud": "authenticated",
        "exp": now + timedelta(hours=1),
        "iat": now,
        "email": "collector@example.com",
        "user_metadata": {"name": "Collector Example"},
    }
    payload.update(overrides or {})
    return jwt.encode(
        payload, private_key, algorithm="ES256", headers={"kid": AUTH_KID}
    )


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# Apply to any test that should run with auth enabled; tests that must prove
# the disabled default stay unmarked.
ENABLED_AUTH = pytest.mark.usefixtures("auth_settings", "stub_cache")
