# Tests for authentication endpoints: signup, login, me, logout
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_login_payload


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    payload = make_signup_payload()
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == payload["email"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = make_signup_payload()
    r1 = await client.post("/api/v1/auth/signup", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/auth/signup", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_signup_password_mismatch(client: AsyncClient):
    payload = make_signup_payload(confirm_password="WrongPassword")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient):
    payload = make_signup_payload(email="not-an-email")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # First signup
    payload = make_signup_payload()
    await client.post("/api/v1/auth/signup", json=payload)
    # Then login
    login_payload = make_login_payload(payload["email"], payload["password"])
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    payload = make_signup_payload()
    await client.post("/api/v1/auth/signup", json=payload)
    login_payload = make_login_payload(payload["email"], "WrongPassword!")
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"email": "noone@example.com", "password": "Test123"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    payload = make_signup_payload()
    signup_resp = await client.post("/api/v1/auth/signup", json=payload)
    token = signup_resp.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    # HTTPBearer returns 403 when no Authorization header is provided
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    payload = make_signup_payload()
    signup_resp = await client.post("/api/v1/auth/signup", json=payload)
    token = signup_resp.json()["access_token"]
    resp = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
