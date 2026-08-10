# Pydantic v2 schemas for Face Attendance app
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator
import re


# ─── Common ──────────────────────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None


# ─── Auth ────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    role: Optional[str] = "EMPLOYEE"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    status: str
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


# ─── Department ───────────────────────────────────────────────────────────────

class DepartmentCreate(BaseModel):
    name: str
    status: Optional[str] = "ACTIVE"


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str
    created_at: datetime


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


# ─── Employee ─────────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    photo: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[str] = "ACTIVE"


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    photo: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[str] = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    name: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    joining_date: Optional[date]
    photo: Optional[str]
    status: str
    department_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class EmployeeListResponse(BaseModel):
    success: bool = True
    total: int
    limit: int
    offset: int
    data: List[EmployeeOut]


# ─── Face ─────────────────────────────────────────────────────────────────────

class FaceRegisterRequest(BaseModel):
    employee_id: str  # the employee_id string like "EMP001"
    face_data: str    # base64 or mock face data string


class FaceRegisterResponse(BaseModel):
    success: bool
    message: str
    employee_id: str
    registered_at: Optional[datetime] = None


class FaceVerifyRequest(BaseModel):
    employee_id: str
    face_data: str


class FaceVerifyResponse(BaseModel):
    success: bool
    verified: bool
    employee_id: str
    employee_name: Optional[str] = None
    message: str


# ─── Attendance ───────────────────────────────────────────────────────────────

class CheckInRequest(BaseModel):
    employee_id: str  # "EMP001" string
    face_verified: Optional[bool] = False


class CheckOutRequest(BaseModel):
    employee_id: str


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    attendance_date: date
    time_in: Optional[time]
    time_out: Optional[time]
    working_hours: Optional[float]
    status: str
    created_at: datetime
    # Joined fields
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    department: Optional[str] = None


class AttendanceResponse(BaseModel):
    success: bool = True
    employee_id: str
    employee_name: Optional[str] = None
    date: str
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    working_hours: Optional[str] = None
    status: str


class AttendanceListResponse(BaseModel):
    success: bool = True
    total: int
    limit: int
    offset: int
    data: List[AttendanceOut]


# ─── Time Card ────────────────────────────────────────────────────────────────

class TimeCardResponse(BaseModel):
    success: bool = True
    employee_id: str
    employee_name: str
    total_working_days: int
    present_days: int
    absent_days: int
    late_days: int
    total_working_hours: str
    average_working_hours: str


# ─── Reports ──────────────────────────────────────────────────────────────────

class DailyAttendanceReport(BaseModel):
    success: bool = True
    date: str
    total_employees: int
    present: int
    absent: int
    late: int
    records: List[AttendanceOut]


class MonthlyAttendanceReport(BaseModel):
    success: bool = True
    month: int
    year: int
    total_employees: int
    records: List[AttendanceOut]


class DepartmentAttendanceReport(BaseModel):
    success: bool = True
    department: str
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    total_employees: int
    present: int
    absent: int
    late: int
    records: List[AttendanceOut]


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    success: bool = True
    total_employees: int
    present_today: int
    absent_today: int
    currently_checked_in: int
    late_today: int
    today_summary: List[AttendanceOut]
