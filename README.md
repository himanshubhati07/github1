# Face Attendance API

A complete FastAPI backend for Employee Attendance Management with Face Recognition (demo mode).

## Architecture

```
app/
├── __init__.py
├── main.py              # FastAPI app, CORS, router registration
├── database.py          # Async SQLAlchemy engine + session
├── models.py            # ORM models (User, Employee, Department, FaceRegistration, Attendance)
├── schemas.py           # Pydantic v2 schemas
├── core/
│   ├── security.py      # JWT + password hashing
│   └── auth.py          # get_current_user dependency + require_roles
└── routers/
    ├── auth.py          # /api/v1/auth/*
    ├── employees.py     # /api/v1/employees/*
    ├── face.py          # /api/v1/face/*
    ├── attendance.py    # /api/v1/attendance/*
    ├── timecards.py     # /api/v1/time-cards/*
    ├── reports.py       # /api/v1/reports/*
    ├── dashboard.py     # /api/v1/dashboard
    └── departments.py   # /api/v1/departments/*
```

## Environment Variables

Copy the env file and edit as needed:

```
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c
SECRET_KEY=face-attendance-super-secret-key-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LATE_THRESHOLD=09:00
PORT=53677
```

## Setup & Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed demo data
python3 seed.py

# 3. Start server
chmod +x ./start.sh && bash ./start.sh
# or
uvicorn app.main:app --host 0.0.0.0 --port 53677 --reload
```

## Demo Credentials (after seeding)

| Role     | Email                       | Password    |
|----------|-----------------------------|-------------|
| ADMIN    | admin@faceattend.com        | Admin@123   |
| HR       | hr@faceattend.com           | HR@123456   |
| EMPLOYEE | employee@faceattend.com     | Emp@12345   |

## API Documentation

- Swagger UI: http://localhost:53677/docs
- ReDoc:       http://localhost:53677/redoc
- Health:      http://localhost:53677/health

## Endpoints Overview

### Auth `/api/v1/auth`
| Method | Path    | Description        | Auth Required |
|--------|---------|--------------------|---------------|
| POST   | /signup | Register new user  | No            |
| POST   | /login  | Login + get JWT    | No            |
| GET    | /me     | Current user       | Yes           |
| POST   | /logout | Logout             | Yes           |

### Employees `/api/v1/employees`
| Method | Path  | Description                          | Role     |
|--------|-------|--------------------------------------|----------|
| POST   | /     | Create employee                      | ADMIN/HR |
| GET    | /     | List employees (search/filter/page)  | Any      |
| GET    | /{id} | Get employee by ID                   | Any      |
| PUT    | /{id} | Update employee                      | ADMIN/HR |
| DELETE | /{id} | Deactivate employee                  | ADMIN/HR |

### Face `/api/v1/face`
| Method | Path      | Description       | Auth |
|--------|-----------|-------------------|------|
| POST   | /register | Register face     | Yes  |
| POST   | /verify   | Verify face       | Yes  |

### Attendance `/api/v1/attendance`
| Method | Path       | Description            | Auth |
|--------|------------|------------------------|------|
| POST   | /check-in  | Employee check-in      | Yes  |
| POST   | /check-out | Employee check-out     | Yes  |
| GET    | /          | Attendance history     | Yes  |

### Time Cards `/api/v1/time-cards`
| Method | Path           | Description            | Auth |
|--------|----------------|------------------------|------|
| GET    | /{employee_id} | Employee time card     | Yes  |

### Reports `/api/v1/reports`
| Method | Path                        | Description              | Role     |
|--------|-----------------------------|--------------------------|----------|
| GET    | /daily-attendance           | Daily report             | ADMIN/HR |
| GET    | /monthly-attendance         | Monthly report           | ADMIN/HR |
| GET    | /time-card/{employee_id}    | Employee time card report| Any      |
| GET    | /department-attendance      | Department report        | ADMIN/HR |
| GET    | /export/attendance-csv      | Export CSV               | ADMIN/HR |

### Dashboard `/api/v1/dashboard`
| Method | Path | Description          | Auth |
|--------|------|----------------------|------|
| GET    | /    | Today's dashboard    | Yes  |

### Departments `/api/v1/departments`
| Method | Path   | Description             | Role     |
|--------|--------|-------------------------|----------|
| POST   | /      | Create department       | ADMIN/HR |
| GET    | /      | List departments        | Any      |
| GET    | /{id}  | Get department by ID    | Any      |
| PUT    | /{id}  | Update department       | ADMIN/HR |
| DELETE | /{id}  | Delete department       | ADMIN    |

## Docker

```bash
docker-compose up -d
```

## Running Tests

```bash
pytest tests/ -v --tb=short
```

## Face Recognition (Demo Mode)

The app uses a deterministic hash-based mock for face recognition.
To register: POST /api/v1/face/register with `employee_id` and `face_data`.
To verify: POST /api/v1/face/verify with the **same** `employee_id` and `face_data`.

## Business Rules

1. One attendance record per employee per day.
2. Cannot check-in twice on the same day.
3. Cannot check-out without check-in.
4. Cannot check-out twice.
5. Working hours calculated automatically.
6. Late status if check-in after LATE_THRESHOLD (default 09:00).
7. Inactive employees cannot record attendance.
8. Duplicate employee IDs and emails rejected.
