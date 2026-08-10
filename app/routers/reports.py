# Reports router: daily, monthly, time-card, department attendance, CSV export
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

import csv
import io
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Employee, Attendance, AttendanceStatus, User
from app.schemas import (
    AttendanceOut, DailyAttendanceReport, MonthlyAttendanceReport,
    DepartmentAttendanceReport, TimeCardResponse,
)
from app.core.auth import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])


def _format_hours(hours: float) -> str:
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}m"


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


@router.get("/daily-attendance", response_model=DailyAttendanceReport)
async def daily_attendance_report(
    report_date: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD (defaults to today)"),
    department: Optional[str] = Query(None),
    att_status: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Daily attendance report for all employees."""
    try:
        target_date = date.fromisoformat(report_date) if report_date else date.today()
    except ValueError:
        target_date = date.today()

    query = (
        select(Attendance)
        .where(Attendance.attendance_date == target_date)
        .options(selectinload(Attendance.employee))
    )
    if department or att_status:
        query = query.join(Employee, Attendance.employee_id == Employee.id)
        if department:
            query = query.where(Employee.department.ilike(f"%{department}%"))
        if att_status:
            try:
                query = query.where(Attendance.status == AttendanceStatus(att_status.upper()))
            except ValueError:
                pass

    result = await db.execute(query)
    records = result.scalars().all()

    att_outs = [_to_att_out(r) for r in records]
    present = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE))
    absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    late = sum(1 for r in records if r.status == AttendanceStatus.LATE)

    return DailyAttendanceReport(
        date=str(target_date),
        total_employees=len(records),
        present=present,
        absent=absent,
        late=late,
        records=att_outs,
    )


@router.get("/monthly-attendance", response_model=MonthlyAttendanceReport)
async def monthly_attendance_report(
    month: int = Query(..., ge=1, le=12, description="Month number 1-12"),
    year: int = Query(..., ge=2000, description="4-digit year"),
    employee_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Monthly attendance report."""
    import calendar
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    query = (
        select(Attendance)
        .where(and_(Attendance.attendance_date >= first_day, Attendance.attendance_date <= last_day))
        .options(selectinload(Attendance.employee))
    )

    if employee_id or department:
        query = query.join(Employee, Attendance.employee_id == Employee.id)
        if employee_id:
            query = query.where(Employee.employee_id == employee_id)
        if department:
            query = query.where(Employee.department.ilike(f"%{department}%"))

    result = await db.execute(query)
    records = result.scalars().all()

    return MonthlyAttendanceReport(
        month=month,
        year=year,
        total_employees=len(records),
        records=[_to_att_out(r) for r in records],
    )


@router.get("/time-card/{employee_id}", response_model=TimeCardResponse)
async def employee_time_card_report(
    employee_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Time card report for a specific employee."""
    emp_result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
    emp = emp_result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Employee not found"})

    att_query = select(Attendance).where(Attendance.employee_id == emp.id)
    if start_date:
        try:
            att_query = att_query.where(Attendance.attendance_date >= date.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            att_query = att_query.where(Attendance.attendance_date <= date.fromisoformat(end_date))
        except ValueError:
            pass

    att_result = await db.execute(att_query)
    records = att_result.scalars().all()

    present_days = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE))
    absent_days = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    late_days = sum(1 for r in records if r.status == AttendanceStatus.LATE)
    total_hours = sum(r.working_hours for r in records if r.working_hours is not None)
    avg_hours = total_hours / present_days if present_days > 0 else 0.0

    return TimeCardResponse(
        employee_id=emp.employee_id,
        employee_name=emp.name,
        total_working_days=len(records),
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        total_working_hours=_format_hours(total_hours),
        average_working_hours=_format_hours(avg_hours),
    )


@router.get("/department-attendance", response_model=DepartmentAttendanceReport)
async def department_attendance_report(
    department: str = Query(...),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    att_status: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Attendance report filtered by department."""
    query = (
        select(Attendance)
        .join(Employee, Attendance.employee_id == Employee.id)
        .where(Employee.department.ilike(f"%{department}%"))
        .options(selectinload(Attendance.employee))
    )
    if date_from:
        try:
            query = query.where(Attendance.attendance_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.where(Attendance.attendance_date <= date.fromisoformat(date_to))
        except ValueError:
            pass
    if att_status:
        try:
            query = query.where(Attendance.status == AttendanceStatus(att_status.upper()))
        except ValueError:
            pass

    result = await db.execute(query)
    records = result.scalars().all()
    present = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE))
    absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    late = sum(1 for r in records if r.status == AttendanceStatus.LATE)

    return DepartmentAttendanceReport(
        department=department,
        date_from=date_from,
        date_to=date_to,
        total_employees=len(records),
        present=present,
        absent=absent,
        late=late,
        records=[_to_att_out(r) for r in records],
    )


@router.get("/export/attendance-csv")
async def export_attendance_csv(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    employee_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "HR")),
):
    """Export attendance records as CSV."""
    query = select(Attendance).options(selectinload(Attendance.employee))
    if date_from:
        try:
            query = query.where(Attendance.attendance_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.where(Attendance.attendance_date <= date.fromisoformat(date_to))
        except ValueError:
            pass
    if employee_id or department:
        query = query.join(Employee, Attendance.employee_id == Employee.id)
        if employee_id:
            query = query.where(Employee.employee_id == employee_id)
        if department:
            query = query.where(Employee.department.ilike(f"%{department}%"))

    result = await db.execute(query)
    records = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Employee ID", "Employee Name", "Department", "Date", "Time In", "Time Out", "Working Hours", "Status"])
    for r in records:
        emp = r.employee
        writer.writerow([
            emp.employee_id if emp else "",
            emp.name if emp else "",
            emp.department if emp else "",
            str(r.attendance_date),
            str(r.time_in) if r.time_in else "",
            str(r.time_out) if r.time_out else "",
            f"{_format_hours(r.working_hours)}" if r.working_hours else "",
            r.status.value if r.status else "",
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.read().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"},
    )
