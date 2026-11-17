"""Shared pytest fixtures.

The archive tests run against the development database that has been seeded with
`scripts/seed_archive.py`. Every test is wrapped in a transaction that is rolled
back afterwards, so view/download counters and other writes never leak between
tests.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.db import get_session
from app.main import app

# The application engine pools connections across event loops, which breaks under
# pytest-asyncio (one loop per test). Tests get a dedicated NullPool engine so
# every connection belongs to the loop that created it.
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)


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
