# Attendance router: check-in, check-out, attendance history
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

from datetime import datetime, date, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.database import get_db
from app.models import Employee, EmployeeStatus, Attendance, AttendanceStatus, User
from app.schemas import (
    CheckInRequest, CheckOutRequest, AttendanceOut, AttendanceListResponse,
    AttendanceResponse,
)
from app.core.auth import get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# Configurable late threshold (24h format HH:MM)
LATE_THRESHOLD_STR = os.getenv("LATE_THRESHOLD", "09:00")


def _parse_late_threshold() -> time:
    h, m = LATE_THRESHOLD_STR.split(":")
    return time(int(h), int(m))


def _format_hours(hours: Optional[float]) -> str:
    if hours is None:
        return "0h 0m"
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}m"


def _to_attendance_out(att: Attendance, emp: Optional[Employee] = None) -> AttendanceOut:
    """Convert Attendance ORM to AttendanceOut schema with joined employee data."""
    return AttendanceOut(
        id=att.id,
        employee_id=att.employee_id,
        attendance_date=att.attendance_date,
        time_in=att.time_in,
        time_out=att.time_out,
        working_hours=att.working_hours,
        status=att.status.value if att.status else "ABSENT",
        created_at=att.created_at,
        employee_name=emp.name if emp else (att.employee.name if att.employee else None),
        employee_code=emp.employee_id if emp else (att.employee.employee_id if att.employee else None),
        department=emp.department if emp else (att.employee.department if att.employee else None),
    )


@router.post("/check-in", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def check_in(
    payload: CheckInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record employee check-in for today. Prevents duplicate check-in."""
    # Find employee
    result = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )
    if emp.status == EmployeeStatus.INACTIVE:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": "Inactive employees cannot record attendance", "error_code": "EMPLOYEE_INACTIVE"},
        )

    today = date.today()
    now = datetime.now()
    current_time = now.time()

    # Check for existing attendance
    existing = await db.execute(
        select(Attendance).where(
            and_(Attendance.employee_id == emp.id, Attendance.attendance_date == today)
        )
    )
    att = existing.scalar_one_or_none()
    if att and att.time_in is not None:
        raise HTTPException(
            status_code=409,
            detail={"success": False, "message": "Employee already checked in today", "error_code": "ALREADY_CHECKED_IN"},
        )

    # Determine late status
    late_threshold = _parse_late_threshold()
    att_status = AttendanceStatus.LATE if current_time > late_threshold else AttendanceStatus.PRESENT

    if att:
        # Update existing absent record
        att.time_in = current_time
        att.status = att_status
        att.updated_at = datetime.utcnow()
    else:
        att = Attendance(
            employee_id=emp.id,
            attendance_date=today,
            time_in=current_time,
            status=att_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(att)

    await db.commit()
    await db.refresh(att)

    return AttendanceResponse(
        employee_id=emp.employee_id,
        employee_name=emp.name,
        date=str(today),
        time_in=current_time.strftime("%I:%M %p"),
        status=att_status.value,
    )


@router.post("/check-out", response_model=AttendanceResponse)
async def check_out(
    payload: CheckOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record employee check-out for today. Calculates working hours."""
    result = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )

    today = date.today()
    att_result = await db.execute(
        select(Attendance).where(
            and_(Attendance.employee_id == emp.id, Attendance.attendance_date == today)
        )
    )
    att = att_result.scalar_one_or_none()

    if not att or att.time_in is None:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": "No check-in found for today", "error_code": "NO_CHECK_IN"},
        )
    if att.time_out is not None:
        raise HTTPException(
            status_code=409,
            detail={"success": False, "message": "Employee already checked out today", "error_code": "ALREADY_CHECKED_OUT"},
        )

    now_time = datetime.now().time()
    # Ensure time_out > time_in
    time_in_dt = datetime.combine(today, att.time_in)
    time_out_dt = datetime.combine(today, now_time)
    if time_out_dt <= time_in_dt:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": "Check-out time must be after check-in time", "error_code": "INVALID_CHECKOUT_TIME"},
        )

    working_seconds = (time_out_dt - time_in_dt).seconds
    working_hours = working_seconds / 3600.0

    att.time_out = now_time
    att.working_hours = working_hours
    att.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(att)

    return AttendanceResponse(
        employee_id=emp.employee_id,
        employee_name=emp.name,
        date=str(today),
        time_in=att.time_in.strftime("%I:%M %p"),
        time_out=now_time.strftime("%I:%M %p"),
        working_hours=_format_hours(working_hours),
        status=att.status.value,
    )


@router.get("", response_model=AttendanceListResponse)
async def list_attendance(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_filter: Optional[str] = Query(None, alias="date", description="Single date YYYY-MM-DD"),
    employee_id: Optional[str] = Query(None, description="Employee string ID e.g. EMP001"),
    department: Optional[str] = Query(None),
    att_status: Optional[str] = Query(None, alias="status", description="PRESENT, ABSENT, LATE"),
    search: Optional[str] = Query(None, description="Search by employee name"),
    sort_by: Optional[str] = Query("attendance_date"),
    sort_order: Optional[str] = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List attendance records with filters, pagination, and sorting."""
    from sqlalchemy.orm import selectinload
    query = select(Attendance).options(selectinload(Attendance.employee))

    if date_filter:
        try:
            d = date.fromisoformat(date_filter)
            query = query.where(Attendance.attendance_date == d)
        except ValueError:
            pass
    if date_from:
        try:
            df = date.fromisoformat(date_from)
            query = query.where(Attendance.attendance_date >= df)
        except ValueError:
            pass
    if date_to:
        try:
            dt = date.fromisoformat(date_to)
            query = query.where(Attendance.attendance_date <= dt)
        except ValueError:
            pass

    if employee_id or department or search:
        query = query.join(Employee, Attendance.employee_id == Employee.id)
        if employee_id:
            query = query.where(Employee.employee_id == employee_id)
        if department:
            query = query.where(Employee.department.ilike(f"%{department}%"))
        if search:
            query = query.where(Employee.name.ilike(f"%{search}%"))

    if att_status:
        try:
            s = AttendanceStatus(att_status.upper())
            query = query.where(Attendance.status == s)
        except ValueError:
            pass

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Sort
    if sort_by == "attendance_date":
        col = Attendance.attendance_date
    elif sort_by == "time_in":
        col = Attendance.time_in
    else:
        col = Attendance.attendance_date

    if sort_order and sort_order.lower() == "asc":
        query = query.order_by(col.asc())
    else:
        query = query.order_by(col.desc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    out = [_to_attendance_out(r) for r in records]
    return AttendanceListResponse(total=total, limit=limit, offset=offset, data=out)
