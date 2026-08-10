# Dashboard router: aggregated attendance stats for today
import os
from dotenv import load_dotenv
load_dotenv('.env_22412b214a31e30d', override=True)

from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Employee, Attendance, AttendanceStatus, EmployeeStatus, User
from app.schemas import DashboardResponse, AttendanceOut
from app.core.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _to_att_out(att: Attendance) -> AttendanceOut:
    emp = att.employee
    return AttendanceOut(
        id=att.id,
        employee_id=att.employee_id,
        attendance_date=att.attendance_date,
        time_in=att.time_in,
        time_out=att.time_out,
        working_hours=att.working_hours,
        status=att.status.value if att.status else "ABSENT",
        created_at=att.created_at,
        employee_name=emp.name if emp else None,
        employee_code=emp.employee_id if emp else None,
        department=emp.department if emp else None,
    )


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return today's attendance dashboard summary."""
    today = date.today()

    # Total active employees
    total_result = await db.execute(
        select(func.count()).select_from(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
    )
    total_employees = total_result.scalar() or 0

    # Today's attendance records
    today_result = await db.execute(
        select(Attendance)
        .where(Attendance.attendance_date == today)
        .options(selectinload(Attendance.employee))
    )
    today_records = today_result.scalars().all()

    present_today = sum(
        1 for r in today_records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE)
    )
    absent_today = sum(1 for r in today_records if r.status == AttendanceStatus.ABSENT)
    late_today = sum(1 for r in today_records if r.status == AttendanceStatus.LATE)
    # Currently checked in = checked in but not yet checked out
    currently_checked_in = sum(
        1 for r in today_records
        if r.time_in is not None and r.time_out is None
    )

    summary = [_to_att_out(r) for r in today_records]

    return DashboardResponse(
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        currently_checked_in=currently_checked_in,
        late_today=late_today,
        today_summary=summary,
    )
