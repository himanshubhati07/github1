# Tests for dashboard endpoint
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_dashboard_success(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "total_employees" in data
    assert "present_today" in data
    assert "absent_today" in data
    assert "currently_checked_in" in data
    assert "late_today" in data
    assert "today_summary" in data


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code in (401, 403)
