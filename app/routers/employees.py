# Employees router: add, list, get, update, delete/deactivate, search
import os
from dotenv import load_dotenv
load_dotenv('.env_22412b214a31e30d', override=True)

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models import Employee, EmployeeStatus, User
from app.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate, EmployeeListResponse
from app.core.auth import get_current_user, require_roles

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Create a new employee record."""
    # Check employee_id uniqueness
    dup_id = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    if dup_id.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Employee ID already exists", "error_code": "EMPLOYEE_ID_EXISTS"},
        )
    # Check email uniqueness
    dup_email = await db.execute(select(Employee).where(Employee.email == payload.email))
    if dup_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Email already exists", "error_code": "EMAIL_ALREADY_EXISTS"},
        )
    try:
        emp_status = EmployeeStatus(payload.status.upper() if payload.status else "ACTIVE")
    except ValueError:
        emp_status = EmployeeStatus.ACTIVE

    emp = Employee(
        employee_id=payload.employee_id,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        department=payload.department,
        designation=payload.designation,
        joining_date=payload.joining_date,
        photo=payload.photo,
        status=emp_status,
        department_id=payload.department_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or employee_id"),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="ACTIVE or INACTIVE"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List employees with search, filter, pagination, and sorting."""
    query = select(Employee)

    if search:
        query = query.where(
            or_(
                Employee.name.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.employee_id.ilike(f"%{search}%"),
            )
        )
    if department:
        query = query.where(Employee.department.ilike(f"%{department}%"))
    if status:
        try:
            emp_status = EmployeeStatus(status.upper())
            query = query.where(Employee.status == emp_status)
        except ValueError:
            pass

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort
    sort_col = getattr(Employee, sort_by, None) if sort_by else None
    if sort_col is not None:
        if sort_order and sort_order.lower() == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    employees = result.scalars().all()

    return EmployeeListResponse(total=total, limit=limit, offset=offset, data=employees)


@router.get("/{emp_id}", response_model=EmployeeOut)
async def get_employee(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single employee by internal ID."""
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )
    return emp


@router.put("/{emp_id}", response_model=EmployeeOut)
async def update_employee(
    emp_id: int,
    payload: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Update an employee record."""
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})

    if payload.email is not None:
        dup = await db.execute(
            select(Employee).where(Employee.email == str(payload.email), Employee.id != emp_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail={"success": False, "message": "Email already in use", "error_code": "EMAIL_ALREADY_EXISTS"},
            )
        emp.email = str(payload.email)

    for field in ("name", "phone", "department", "designation", "joining_date", "photo", "department_id"):
        val = getattr(payload, field, None)
        if val is not None:
            setattr(emp, field, val)

    if payload.status is not None:
        try:
            emp.status = EmployeeStatus(payload.status.upper())
        except ValueError:
            pass

    emp.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(emp)
    return emp


@router.delete("/{emp_id}", status_code=status.HTTP_200_OK)
async def deactivate_employee(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Deactivate (soft-delete) an employee."""
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})
    emp.status = EmployeeStatus.INACTIVE
    emp.updated_at = datetime.utcnow()
    await db.commit()
    return {"success": True, "message": "Employee deactivated successfully"}
