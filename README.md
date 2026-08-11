# Employee Attendance Management System — Backend API

A complete Spring Boot backend API for managing employee attendance, time tracking, face recognition (demo/mock), reports, and dashboard analytics.

---

## Tech Stack

- **Java 17** + **Spring Boot 3.2.5**
- **PostgreSQL** (database)
- **Spring Security** + **JWT (HS256)** authentication
- **Spring Data JPA** / Hibernate
- **Swagger / OpenAPI** via springdoc-openapi
- **Apache Commons CSV** for CSV export

---

## Prerequisites

- Java 17+
- Maven 3.9+
- PostgreSQL 14+

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | `EmployeeAttendance...` | HS256 signing secret |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://localhost:5432/gen_054b6290d0` | DB URL |
| `SPRING_DATASOURCE_USERNAME` | `myuser` | DB username |
| `SPRING_DATASOURCE_PASSWORD` | `mypassword` | DB password |

---

## Run Locally

```bash
# 1. Clone and enter directory
cd <project-root>

# 2. Build and run
chmod +x start.sh && ./start.sh

# OR run directly with Maven
mvn spring-boot:run
```

Server starts at **http://localhost:55513**

---

## Run with Docker

```bash
# Start PostgreSQL + App
docker-compose up -d

# View logs
make logs

# Stop
docker-compose down
```

---

## API Documentation

Swagger UI: **http://localhost:55513/docs**  
OpenAPI JSON: **http://localhost:55513/api-docs**

---

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Get current user profile |
| POST | `/api/v1/auth/logout` | Logout |

### Employees (`/api/v1/employees`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/employees` | Add employee |
| GET | `/api/v1/employees` | List employees (search, filter, paginate) |
| GET | `/api/v1/employees/{id}` | Get employee by ID |
| PUT | `/api/v1/employees/{id}` | Update employee |
| DELETE | `/api/v1/employees/{id}` | Deactivate employee |

### Face Recognition (`/api/v1/face`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/face/register` | Register face data |
| POST | `/api/v1/face/verify` | Verify face data |

### Attendance (`/api/v1/attendance`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/attendance/check-in` | Employee check-in |
| POST | `/api/v1/attendance/check-out` | Employee check-out |
| GET | `/api/v1/attendance` | Attendance history (filters, pagination) |

### Time Cards (`/api/v1/time-cards`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/time-cards/{employeeId}` | Get time card for employee |

### Dashboard (`/api/v1/dashboard`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard` | Today's attendance summary |

### Reports (`/api/v1/reports`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/daily-attendance` | Daily attendance report |
| GET | `/api/v1/reports/monthly-attendance` | Monthly attendance report |
| GET | `/api/v1/reports/time-card/{employeeId}` | Employee time card report |
| GET | `/api/v1/reports/department-attendance` | Department attendance report |
| GET | `/api/v1/reports/export/csv` | Export attendance CSV |

### Departments (`/api/v1/departments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/departments` | Create department |
| GET | `/api/v1/departments` | List departments |
| GET | `/api/v1/departments/{id}` | Get department |
| PUT | `/api/v1/departments/{id}` | Update department |
| DELETE | `/api/v1/departments/{id}` | Delete department |

---

## Sample Requests

### Login
```bash
curl -X POST http://localhost:55513/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"Admin@123"}'
```

### Check In
```bash
curl -X POST http://localhost:55513/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"employeeId":"EMP001"}'
```

### Get Dashboard
```bash
curl http://localhost:55513/api/v1/dashboard \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Seed Data

The application seeds the following demo data on startup:

- **5 Departments**: Engineering, Human Resources, Sales, Finance, Operations
- **2 Users**: admin@company.com and hr@company.com (password: `Admin@123`)
- **5 Employees**: EMP001–EMP005
- **3 Face Registrations**: EMP001, EMP002, EMP003
- **6 Attendance Records**: past 2 days

---

## Business Rules

1. One attendance record per employee per working day
2. Cannot check in twice on the same day
3. Cannot check out without checking in first
4. Cannot check out twice
5. Working hours calculated automatically on check-out
6. Late status: check-in after 9:00 AM is marked LATE
7. Inactive employees cannot record attendance
8. Duplicate employee IDs and emails are rejected

---

## Authentication

All APIs except `/api/v1/auth/signup` and `/api/v1/auth/login` should include:
```
Authorization: Bearer <JWT_TOKEN>
```

JWT expires in 30 minutes.
