# Tests for Employee management endpoints
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_employee_payload


async def get_admin_token(client: AsyncClient) -> str:
    """Helper: signup as ADMIN and return token."""
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


async def create_employee(client: AsyncClient, token: str, **overrides) -> dict:
    payload = make_employee_payload(**overrides)
    resp = await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp


@pytest.mark.asyncio
async def test_create_employee_success(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await create_employee(client, token)
    assert resp.status_code == 201
    data = resp.json()
    assert "employee_id" in data


@pytest.mark.asyncio
async def test_create_employee_duplicate_id(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_employee_payload()
    r1 = await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_create_employee_duplicate_email(client: AsyncClient):
    token = await get_admin_token(client)
    payload1 = make_employee_payload()
    r1 = await client.post("/api/v1/employees", json=payload1, headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 201
    # Same email, different employee_id
    payload2 = make_employee_payload(email=payload1["email"])
    r2 = await client.post("/api/v1/employees", json=payload2, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient):
    token = await get_admin_token(client)
    await create_employee(client, token)
    resp = await client.get("/api/v1/employees", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_employee_by_id(client: AsyncClient):
    token = await get_admin_token(client)
    created = await create_employee(client, token)
    emp_internal_id = created.json()["id"]
    resp = await client.get(f"/api/v1/employees/{emp_internal_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == emp_internal_id


@pytest.mark.asyncio
async def test_get_employee_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get("/api/v1/employees/999999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_employee(client: AsyncClient):
    token = await get_admin_token(client)
    created = await create_employee(client, token)
    emp_id = created.json()["id"]
    resp = await client.put(
        f"/api/v1/employees/{emp_id}",
        json={"designation": "Senior Developer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["designation"] == "Senior Developer"


@pytest.mark.asyncio
async def test_deactivate_employee(client: AsyncClient):
    token = await get_admin_token(client)
    created = await create_employee(client, token)
    emp_id = created.json()["id"]
    resp = await client.delete(f"/api/v1/employees/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    # Verify status is INACTIVE
    get_resp = await client.get(f"/api/v1/employees/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.json()["status"] == "INACTIVE"


@pytest.mark.asyncio
async def test_search_employee(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_employee_payload(name="UniqueSearchName99")
    await client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {token}"})
    resp = await client.get(
        "/api/v1/employees?search=UniqueSearchName99",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_employee_unauthorized(client: AsyncClient):
    """Regular EMPLOYEE role should be forbidden from creating employees."""
    payload = make_signup_payload(role="EMPLOYEE")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    token = resp.json()["access_token"]
    emp_payload = make_employee_payload()
    resp2 = await client.post("/api/v1/employees", json=emp_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 403
