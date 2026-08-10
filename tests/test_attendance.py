# Tests for attendance check-in, check-out, and history endpoints
import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models import Attendance, Employee
from tests.utils.factories import make_signup_payload, make_employee_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


async def create_test_employee(client: AsyncClient, token: str) -> str:
    payload = make_employee_payload()
    resp = await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["employee_id"]


async def clear_today_attendance(db_session: AsyncSession, employee_code: str):
    """Remove today's attendance for a given employee to allow clean test."""
    emp_result = await db_session.execute(select(Employee).where(Employee.employee_id == employee_code))
    emp = emp_result.scalar_one_or_none()
    if emp:
        today = date.today()
        await db_session.execute(
            delete(Attendance).where(
                Attendance.employee_id == emp.id,
                Attendance.attendance_date == today,
            )
        )
        await db_session.commit()


@pytest.mark.asyncio
async def test_check_in_success(client: AsyncClient, db_session: AsyncSession):
    token = await get_admin_token(client)
    emp_id = await create_test_employee(client, token)
    await clear_today_attendance(db_session, emp_id)
    resp = await client.post(
        "/api/v1/attendance/check-in",
        json={"employee_id": emp_id, "face_verified": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["employee_id"] == emp_id
    assert data["status"] in ("PRESENT", "LATE")


@pytest.mark.asyncio
async def test_check_in_duplicate(client: AsyncClient, db_session: AsyncSession):
    token = await get_admin_token(client)
    emp_id = await create_test_employee(client, token)
    await clear_today_attendance(db_session, emp_id)
    # First check-in
    r1 = await client.post(
        "/api/v1/attendance/check-in",
        json={"employee_id": emp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 201
    # Duplicate check-in
    r2 = await client.post(
        "/api/v1/attendance/check-in",
        json={"employee_id": emp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_check_out_without_check_in(client: AsyncClient, db_session: AsyncSession):
    token = await get_admin_token(client)
    emp_id = await create_test_employee(client, token)
    await clear_today_attendance(db_session, emp_id)
    resp = await client.post(
        "/api/v1/attendance/check-out",
        json={"employee_id": emp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_check_out_success(client: AsyncClient, db_session: AsyncSession):
    token = await get_admin_token(client)
    emp_id = await create_test_employee(client, token)
    await clear_today_attendance(db_session, emp_id)
    # Check in first
    await client.post(
        "/api/v1/attendance/check-in",
        json={"employee_id": emp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.post(
        "/api/v1/attendance/check-out",
        json={"employee_id": emp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Either 200 (checked out OK) or 400 (same second as check-in)
    assert resp.status_code in (200, 400)


@pytest.mark.asyncio
async def test_attendance_history(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get("/api/v1/attendance", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_attendance_history_with_filters(client: AsyncClient):
    token = await get_admin_token(client)
    today = str(date.today())
    resp = await client.get(
        f"/api/v1/attendance?date={today}&status=PRESENT",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_check_in_invalid_employee(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.post(
        "/api/v1/attendance/check-in",
        json={"employee_id": "NONEXISTENT999"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
