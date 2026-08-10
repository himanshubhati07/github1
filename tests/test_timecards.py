# Tests for time card endpoint
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_employee_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_get_time_card_success(client: AsyncClient):
    token = await get_admin_token(client)
    # Create employee
    emp_payload = make_employee_payload()
    emp_resp = await client.post("/api/v1/employees", json=emp_payload, headers={"Authorization": f"Bearer {token}"})
    emp_id = emp_resp.json()["employee_id"]
    # Get time card
    resp = await client.get(f"/api/v1/time-cards/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == emp_id
    assert "total_working_days" in data
    assert "total_working_hours" in data


@pytest.mark.asyncio
async def test_get_time_card_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get("/api/v1/time-cards/NONEXISTENT", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_time_card_with_date_range(client: AsyncClient):
    token = await get_admin_token(client)
    emp_payload = make_employee_payload()
    emp_resp = await client.post("/api/v1/employees", json=emp_payload, headers={"Authorization": f"Bearer {token}"})
    emp_id = emp_resp.json()["employee_id"]
    resp = await client.get(
        f"/api/v1/time-cards/{emp_id}?start_date=2024-01-01&end_date=2024-12-31",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_working_days"] == 0  # no records in that range


@pytest.mark.asyncio
async def test_time_card_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/time-cards/EMP001")
    assert resp.status_code in (401, 403)
