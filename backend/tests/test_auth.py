"""Supabase auth: token verification and account provisioning."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient
from sqlalchemy import select

from app.models import User
from app.models.enums import UserStatus
from tests.conftest import ENABLED_AUTH, bearer, mint_token


@ENABLED_AUTH
async def test_me_requires_bearer_token(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    token = mint_token(private_key)

    missing = await client.get("/api/v1/auth/me")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTH_REQUIRED"

    wrong_scheme = await client.get("/api/v1/auth/me", headers={"Authorization": token})
    assert wrong_scheme.status_code == 401

    accepted = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert accepted.status_code == 200
    assert accepted.json()["data"]["email"] == "collector@example.com"


@ENABLED_AUTH
async def test_me_provisions_user_once(client: AsyncClient, session, es256) -> None:
    private_key, _ = es256
    sub = str(uuid.uuid4())
    token = mint_token(
        private_key, sub=sub, overrides={"email": "new-member@example.com"}
    )

    first = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert first.status_code == 200
    account = first.json()["data"]
    assert account["username"] == "collector-example"
    assert account["display_name"] == "Collector Example"
    assert account["status"] == "active"

    row = (
        (await session.execute(select(User).where(User.supabase_sub == sub)))
        .scalars()
        .first()
    )
    assert row is not None and row.email == "new-member@example.com"

    # A repeat request resolves the same account instead of creating another.
    again = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert again.status_code == 200
    assert again.json()["data"]["id"] == account["id"]

    matches = (
        (await session.execute(select(User).where(User.supabase_sub == sub)))
        .scalars()
        .all()
    )
    assert len(matches) == 1


@ENABLED_AUTH
async def test_me_links_account_by_email(client: AsyncClient, session, es256) -> None:
    private_key, _ = es256
    seeded = User(
        username="seeded-member",
        display_name="Seeded Member",
        email="seeded-member@cabinet.local",
    )
    session.add(seeded)
    await session.flush()

    token = mint_token(
        private_key,
        overrides={"email": "seeded-member@cabinet.local", "user_metadata": {}},
    )
    response = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(seeded.id)
    assert data["username"] == "seeded-member"

    claims = jwt.decode(token, options={"verify_signature": False}, algorithms=["ES256"])
    await session.refresh(seeded)
    assert seeded.supabase_sub == claims["sub"]


@ENABLED_AUTH
async def test_invalid_signature_rejected(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    impostor = ec.generate_private_key(ec.SECP256R1())
    token = jwt.encode(
        {
            "iss": "https://cabinet-test.supabase.co/auth/v1",
            "sub": str(uuid.uuid4()),
            "aud": "authenticated",
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
        },
        impostor,
        algorithm="ES256",
        headers={"kid": "cabinet-test-key"},
    )
    response = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_INVALID"


@ENABLED_AUTH
async def test_expired_token_rejected(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    token = mint_token(
        private_key,
        overrides={"exp": datetime.now(UTC) - timedelta(hours=2)},
    )
    response = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_INVALID"


@ENABLED_AUTH
async def test_wrong_audience_rejected(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    token = mint_token(private_key, overrides={"aud": "service_role"})
    response = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert response.status_code == 401


@ENABLED_AUTH
async def test_wrong_issuer_rejected(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    token = mint_token(private_key, overrides={"iss": "https://attacker.example/auth/v1"})
    response = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert response.status_code == 401


@ENABLED_AUTH
async def test_unknown_key_id_rejected(client: AsyncClient, es256) -> None:
    private_key, _ = es256
    rotated = jwt.encode(
        {
            "iss": "https://cabinet-test.supabase.co/auth/v1",
            "sub": str(uuid.uuid4()),
            "aud": "authenticated",
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "rotated-key"},
    )
    response = await client.get("/api/v1/auth/me", headers=bearer(rotated))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_INVALID"


@ENABLED_AUTH
async def test_suspended_user_forbidden(client: AsyncClient, session, es256) -> None:
    private_key, _ = es256
    sub = str(uuid.uuid4())
    token = mint_token(private_key, sub=sub)

    first = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert first.status_code == 200

    row = (
        (await session.execute(select(User).where(User.supabase_sub == sub)))
        .scalars()
        .one()
    )
    row.status = UserStatus.SUSPENDED
    await session.commit()

    second = await client.get("/api/v1/auth/me", headers=bearer(token))
    assert second.status_code == 403
    assert second.json()["error"]["code"] == "ACCOUNT_SUSPENDED"


async def test_auth_disabled_returns_auth_required(client: AsyncClient) -> None:
    """Without SUPABASE_URL configured every auth endpoint is closed."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
