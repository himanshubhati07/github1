# Time cards router: per-employee time card summary
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import Employee, Attendance, AttendanceStatus, User
from app.schemas import TimeCardResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/time-cards", tags=["Time Cards"])


def _format_hours(hours: float) -> str:
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}m"


@router.get("/{employee_id}", response_model=TimeCardResponse)
async def get_time_card(
    employee_id: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return time card summary for an employee within a date range."""
    result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )

    att_query = select(Attendance).where(Attendance.employee_id == emp.id)

    if start_date:
        try:
            sd = date.fromisoformat(start_date)
            att_query = att_query.where(Attendance.attendance_date >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            ed = date.fromisoformat(end_date)
            att_query = att_query.where(Attendance.attendance_date <= ed)
        except ValueError:
            pass

    att_result = await db.execute(att_query)
    records = att_result.scalars().all()

    total_working_days = len(records)
    present_days = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE))
    absent_days = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    late_days = sum(1 for r in records if r.status == AttendanceStatus.LATE)
    total_hours = sum(r.working_hours for r in records if r.working_hours is not None)
    avg_hours = total_hours / present_days if present_days > 0 else 0.0

    return TimeCardResponse(
        employee_id=emp.employee_id,
        employee_name=emp.name,
        total_working_days=total_working_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        total_working_hours=_format_hours(total_hours),
        average_working_hours=_format_hours(avg_hours),
    )
