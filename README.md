# Employee Attendance Management System — FastAPI Backend

A complete, production-ready FastAPI backend for Employee Attendance Management with Face Recognition (demo/mock mode).
Implements the full feature set of a Java Spring Boot / JPA design — migrated to Python / FastAPI / SQLAlchemy / PostgreSQL.

## Technology Stack

| Layer             | Technology                                               |
|-------------------|----------------------------------------------------------|
| Language          | Python 3.11+                                             |
| Web Framework     | FastAPI (async, equivalent to Spring Web/MVC)            |
| ORM               | SQLAlchemy 2.x async (equivalent to Spring Data JPA / Hibernate) |
| Database          | PostgreSQL (equivalent to MySQL target in prompt)        |
| Auth              | JWT via python-jose + BCrypt passwords (passlib)         |
| Validation        | Pydantic v2 (equivalent to Jakarta Bean Validation)      |
| API Docs          | Swagger/OpenAPI (built-in FastAPI)                       |
| Testing           | pytest + pytest-asyncio + httpx                          |
| Migrations        | Alembic (equivalent to Flyway/Liquibase)                 |
| Dependency Mgmt   | pip / requirements.txt (equivalent to Maven)             |

## Project Architecture

```
app/
├── __init__.py
├── main.py              # FastAPI app, CORS, router registration, global exception handler
├── database.py          # Async SQLAlchemy engine + session factory
├── models.py            # ORM entities: User, Employee, Department, FaceRegistration, Attendance
├── schemas.py           # Pydantic v2 DTOs (request/response models)
├── core/
│   ├── security.py      # JWT creation/verification + BCrypt password hashing
│   └── auth.py          # get_current_user dependency + require_roles RBAC
└── routers/
    ├── auth.py          # /api/v1/auth/* (signup, login, me, logout)
    ├── employees.py     # /api/v1/employees/* (CRUD, search, pagination, sort)
    ├── face.py          # /api/v1/face/* (register, verify — mock FaceRecognitionService)
    ├── attendance.py    # /api/v1/attendance/* (check-in, check-out, history)
    ├── timecards.py     # /api/v1/time-cards/* (per-employee time card)
    ├── reports.py       # /api/v1/reports/* (daily, monthly, department, CSV export)
    ├── dashboard.py     # /api/v1/dashboard (today's attendance metrics)
    └── departments.py   # /api/v1/departments/* (CRUD)
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip

## Environment Variables

All secrets are stored in `.env_22412b214a31e30d`. The following variables are supported:

| Variable                   | Description                              | Default                     |
|----------------------------|------------------------------------------|-----------------------------|
| `DATABASE_URL`             | Async PostgreSQL connection URL          | (see env file)              |
| `SECRET_KEY`               | JWT signing secret                       | (see env file)              |
| `ALGORITHM`                | JWT algorithm                            | HS256                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime in minutes         | 30                          |
| `LATE_THRESHOLD`           | Check-in time after which = LATE (HH:MM)| 09:00                       |
| `PORT`                     | Server port                              | 36455                       |

> **Never commit real secrets.** Use environment variables or a secrets manager in production.

## Setup & Run Locally

```bash
# 1. Clone & install dependencies
pip install -r requirements.txt

# 2. Seed demo data (creates DB tables + inserts sample records)
python3 seed.py

# 3. Start server
chmod +x ./start.sh && bash ./start.sh
# or directly:
uvicorn app.main:app --host 0.0.0.0 --port 36455 --reload
```

## Demo Credentials (after seeding)

| Role     | Email                       | Password    |
|----------|-----------------------------|-------------|
| ADMIN    | admin@faceattend.com        | Admin@123   |
| HR       | hr@faceattend.com           | HR@123456   |
| EMPLOYEE | employee@faceattend.com     | Emp@12345   |

## Swagger / OpenAPI Documentation

- **Swagger UI**: http://localhost:36455/docs  ← JWT auth configurable via "Authorize" button
- **ReDoc**:      http://localhost:36455/redoc
- **OpenAPI**:    http://localhost:36455/openapi.json
- **Health**:     http://localhost:36455/health

## API Endpoints Reference

### Auth `/api/v1/auth`
| Method | Path    | Description                   | Auth Required | Roles  |
|--------|---------|-------------------------------|---------------|--------|
| POST   | /signup | Register new user account     | No            | —      |
| POST   | /login  | Login → receive JWT token     | No            | —      |
| GET    | /me     | Get current user profile      | Yes           | Any    |
| POST   | /logout | Logout (discard token)        | Yes           | Any    |

**Signup fields**: name, email, password, confirm_password, role  
**Login fields**: email, password  

### Employees `/api/v1/employees`
| Method | Path        | Description                              | Roles    |
|--------|-------------|------------------------------------------|----------|
| POST   | /           | Create employee                          | ADMIN/HR |
| GET    | /           | List employees (search/filter/page/sort) | Any      |
| GET    | /search     | Dedicated search (q, department, status, employee_id, email) | Any |
| GET    | /{id}       | Get employee by internal ID              | Any      |
| PUT    | /{id}       | Update employee fields                   | ADMIN/HR |
| DELETE | /{id}       | Deactivate employee (soft delete)        | ADMIN/HR |

**Employee fields**: id, employeeId, employeeName, email, phoneNumber, department, designation, joiningDate, employeePhoto, status (ACTIVE/INACTIVE), createdAt, updatedAt

**List query params**: `search`, `department`, `status`, `sort_by`, `sort_order`, `offset`, `limit`

### Face Recognition `/api/v1/face`
| Method | Path      | Description                             | Auth |
|--------|-----------|-----------------------------------------|------|
| POST   | /register | Register face data for employee (mock)  | Yes  |
| POST   | /verify   | Verify employee face (mock)             | Yes  |

*Mock mode: face data is SHA-256 hashed for deterministic demo verification.*

### Attendance `/api/v1/attendance`
| Method | Path       | Description                              | Auth |
|--------|------------|------------------------------------------|------|
| POST   | /check-in  | Employee check-in (records time, status) | Yes  |
| POST   | /check-out | Employee check-out (calculates hours)    | Yes  |
| GET    | /          | Attendance history with filters          | Yes  |

**History query params**: `date`, `date_from`, `date_to`, `employee_id`, `department`, `status`, `search`, `sort_by`, `sort_order`, `offset`, `limit`

### Time Cards `/api/v1/time-cards`
| Method | Path           | Description                              | Auth |
|--------|----------------|------------------------------------------|------|
| GET    | /{employee_id} | Employee time card (totals + averages)   | Yes  |

**Query params**: `start_date`, `end_date`

### Reports `/api/v1/reports`
| Method | Path                       | Description                    | Roles    |
|--------|----------------------------|--------------------------------|----------|
| GET    | /daily-attendance          | Daily attendance report        | ADMIN/HR |
| GET    | /monthly-attendance        | Monthly attendance report      | ADMIN/HR |
| GET    | /time-card/{employee_id}   | Employee time card report      | Any      |
| GET    | /department-attendance     | Department attendance report   | ADMIN/HR |
| GET    | /export/attendance-csv     | Export attendance as CSV       | ADMIN/HR |

### Dashboard `/api/v1/dashboard`
| Method | Path | Description                                    | Auth |
|--------|------|------------------------------------------------|------|
| GET    | /    | Today's metrics: total, present, absent, late  | Yes  |

**Response fields**: total_employees, present_today, absent_today, currently_checked_in, late_today, today_summary

### Departments `/api/v1/departments`
| Method | Path   | Description             | Roles    |
|--------|--------|-------------------------|----------|
| POST   | /      | Create department       | ADMIN/HR |
| GET    | /      | List all departments    | Any      |
| GET    | /{id}  | Get department by ID    | Any      |
| PUT    | /{id}  | Update department       | ADMIN/HR |
| DELETE | /{id}  | Delete department       | ADMIN    |

## API Response Format

**Success:**
```json
{
  "success": true,
  "message": "Employee created successfully",
  "data": {}
}
```

**Error:**
```json
{
  "success": false,
  "message": "Employee already exists",
  "errorCode": "EMPLOYEE_ALREADY_EXISTS"
}
```

**Paginated:**
```json
{
  "success": true,
  "total": 50,
  "limit": 20,
  "offset": 0,
  "data": []
}
```

## Role-Based Authorization

| Role     | Permissions                                                          |
|----------|----------------------------------------------------------------------|
| ADMIN    | All operations: manage users/employees, view attendance/reports/dashboard |
| HR       | Manage employees, view attendance, reports, dashboard                |
| EMPLOYEE | Own attendance: check-in/out, own time card                         |

## Running Tests

```bash
pytest tests/ -v --tb=short
```

Tests cover: authentication, employee CRUD/search/filter/pagination, duplicate handling,
face registration/verification, check-in/check-out rules, time calculations, time cards,
dashboard calculations, reports, authorization, invalid requests, and error handling.

## Business Rules Implemented

1. One attendance record per employee per working day.
2. No duplicate check-in on the same day.
3. No check-out without prior check-in.
4. No duplicate check-out.
5. Time out must be after time in.
6. Working hours calculated automatically (service layer).
7. Successful check-in marks PRESENT; after LATE_THRESHOLD marks LATE.
8. INACTIVE employees cannot record attendance.
9. Duplicate employee IDs or emails → 409 Conflict.
10. Face verification uses mock SHA-256 hash for complete frontend testing.
11. Role-based access: protected APIs return 401/403 when unauthorized.
12. Database unique constraints + application-level checks prevent concurrent duplicates.

## Docker

```bash
docker-compose up -d
```

## Seed / Demo Data

After running `python3 seed.py`, the database contains:
- 3 users: admin, HR manager, employee
- 5 departments: Engineering, HR, Finance, Marketing, Operations
- 5 employees (EMP001–EMP005) with face registrations
- 5 days of attendance records for all employees

## Frontend Integration Guide

1. Call `POST /api/v1/auth/login` with email/password → receive `access_token`
2. Include `Authorization: Bearer <token>` in all subsequent requests
3. Use `/api/v1/employees/search` for advanced employee lookup
4. Use `/api/v1/face/register` then `/api/v1/face/verify` for face-based check-in flow
5. Check `/api/v1/dashboard` for real-time today's summary
6. Use `/api/v1/reports/export/attendance-csv` for CSV export

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `asyncpg` connection error | Ensure PostgreSQL is running and DATABASE_URL is correct |
| JWT 401 errors | Check token expiry (default 30 min); re-login to get new token |
| 403 Forbidden | Ensure your account has the required role (ADMIN/HR) |
| Duplicate check-in 409 | Employee already checked in today; use check-out endpoint |
| `bcrypt` version error | Run `pip install bcrypt==4.0.1` |
