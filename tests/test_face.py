# Tests for face registration and verification endpoints
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_employee_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


async def create_employee_and_get_id(client: AsyncClient, token: str) -> str:
    payload = make_employee_payload()
    resp = await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["employee_id"]


@pytest.mark.asyncio
async def test_face_register_success(client: AsyncClient):
    token = await get_admin_token(client)
    emp_id = await create_employee_and_get_id(client, token)
    resp = await client.post(
        "/api/v1/face/register",
        json={"employee_id": emp_id, "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["employee_id"] == emp_id


@pytest.mark.asyncio
async def test_face_register_update_existing(client: AsyncClient):
    """Second registration should update, not error."""
    token = await get_admin_token(client)
    emp_id = await create_employee_and_get_id(client, token)
    await client.post(
        "/api/v1/face/register",
        json={"employee_id": emp_id, "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp2 = await client.post(
        "/api/v1/face/register",
        json={"employee_id": emp_id, "face_data": "new_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 201
    assert resp2.json()["success"] is True


@pytest.mark.asyncio
async def test_face_register_invalid_employee(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.post(
        "/api/v1/face/register",
        json={"employee_id": "NONEXISTENT", "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_face_verify_success(client: AsyncClient):
    token = await get_admin_token(client)
    emp_id = await create_employee_and_get_id(client, token)
    # Register face
    await client.post(
        "/api/v1/face/register",
        json={"employee_id": emp_id, "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Verify with same data
    resp = await client.post(
        "/api/v1/face/verify",
        json={"employee_id": emp_id, "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is True


@pytest.mark.asyncio
async def test_face_verify_wrong_data(client: AsyncClient):
    token = await get_admin_token(client)
    emp_id = await create_employee_and_get_id(client, token)
    await client.post(
        "/api/v1/face/register",
        json={"employee_id": emp_id, "face_data": "correct_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.post(
        "/api/v1/face/verify",
        json={"employee_id": emp_id, "face_data": "wrong_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["verified"] is False


@pytest.mark.asyncio
async def test_face_verify_no_registration(client: AsyncClient):
    token = await get_admin_token(client)
    emp_id = await create_employee_and_get_id(client, token)
    resp = await client.post(
        "/api/v1/face/verify",
        json={"employee_id": emp_id, "face_data": "demo_face_data"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["verified"] is False
