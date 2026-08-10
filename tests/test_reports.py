# Tests for reports endpoints
import pytest
from datetime import date
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_employee_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_daily_attendance_report(client: AsyncClient):
    token = await get_admin_token(client)
    today = str(date.today())
    resp = await client.get(
        f"/api/v1/reports/daily-attendance?date={today}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "records" in data
    assert "total_employees" in data


@pytest.mark.asyncio
async def test_monthly_attendance_report(client: AsyncClient):
    token = await get_admin_token(client)
    today = date.today()
    resp = await client.get(
        f"/api/v1/reports/monthly-attendance?month={today.month}&year={today.year}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["month"] == today.month


@pytest.mark.asyncio
async def test_employee_time_card_report(client: AsyncClient):
    token = await get_admin_token(client)
    emp_payload = make_employee_payload()
    emp_resp = await client.post("/api/v1/employees", json=emp_payload, headers={"Authorization": f"Bearer {token}"})
    emp_id = emp_resp.json()["employee_id"]
    resp = await client.get(
        f"/api/v1/reports/time-card/{emp_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == emp_id


@pytest.mark.asyncio
async def test_department_attendance_report(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get(
        "/api/v1/reports/department-attendance?department=Engineering",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["department"] == "Engineering"


@pytest.mark.asyncio
async def test_export_attendance_csv(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get(
        "/api/v1/reports/export/attendance-csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_reports_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/reports/daily-attendance")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_reports_employee_role_forbidden(client: AsyncClient):
    payload = make_signup_payload(role="EMPLOYEE")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    token = resp.json()["access_token"]
    resp2 = await client.get("/api/v1/reports/daily-attendance", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 403
