# Tests for departments endpoints
import pytest
from httpx import AsyncClient
from tests.utils.factories import make_signup_payload, make_department_payload


async def get_admin_token(client: AsyncClient) -> str:
    payload = make_signup_payload(role="ADMIN")
    resp = await client.post("/api/v1/auth/signup", json=payload)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_department_payload()
    resp = await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["name"] == payload["name"]


@pytest.mark.asyncio
async def test_create_department_duplicate(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_department_payload()
    await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    r2 = await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_list_departments(client: AsyncClient):
    token = await get_admin_token(client)
    resp = await client.get("/api/v1/departments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_department_by_id(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_department_payload()
    create_resp = await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    dept_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/departments/{dept_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == dept_id


@pytest.mark.asyncio
async def test_update_department(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_department_payload()
    create_resp = await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    dept_id = create_resp.json()["id"]
    resp = await client.put(
        f"/api/v1/departments/{dept_id}",
        json={"status": "INACTIVE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "INACTIVE"


@pytest.mark.asyncio
async def test_delete_department(client: AsyncClient):
    token = await get_admin_token(client)
    payload = make_department_payload()
    create_resp = await client.post("/api/v1/departments", json=payload, headers={"Authorization": f"Bearer {token}"})
    dept_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/departments/{dept_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
