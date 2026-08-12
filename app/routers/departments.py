# Departments router: CRUD for departments
import os
from dotenv import load_dotenv
load_dotenv('.env_22412b214a31e30d', override=True)

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Department, DepartmentStatus, User
from app.schemas import DepartmentCreate, DepartmentOut, DepartmentUpdate
from app.core.auth import get_current_user, require_roles

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Create a new department."""
    existing = await db.execute(select(Department).where(Department.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Department already exists", "error_code": "DEPARTMENT_EXISTS"},
        )
    try:
        dept_status = DepartmentStatus(payload.status.upper() if payload.status else "ACTIVE")
    except ValueError:
        dept_status = DepartmentStatus.ACTIVE
    dept = Department(name=payload.name, status=dept_status, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.get("", response_model=List[DepartmentOut])
async def list_departments(
    skip: int = Query(0, alias="offset"),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all departments with pagination."""
    result = await db.execute(select(Department).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{dept_id}", response_model=DepartmentOut)
async def get_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a department by ID."""
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Department not found"})
    return dept


@router.put("/{dept_id}", response_model=DepartmentOut)
async def update_department(
    dept_id: int,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Update a department."""
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Department not found"})
    if payload.name is not None:
        dept.name = payload.name
    if payload.status is not None:
        try:
            dept.status = DepartmentStatus(payload.status.upper())
        except ValueError:
            pass
    dept.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(dept)
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_200_OK)
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    """Delete a department."""
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Department not found"})
    await db.delete(dept)
    await db.commit()
    return {"success": True, "message": "Department deleted"}
