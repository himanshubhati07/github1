COMMIT_MESSAGE: Extend Employee Attendance API: add /employees/search endpoint, sort_by whitelist validation, comprehensive README for Java Spring Boot feature parity — all 55 tests passing

## Features Added
- GET /api/v1/employees/search — Dedicated employee search endpoint with q, department, status, employee_id, email filters, pagination, and sorting (mirrors Java Spring Boot /api/employees/search requirement)
- Sort-by whitelist validation on GET /api/v1/employees and GET /api/v1/employees/search — prevents invalid column injection into ORM queries, returns 400 with supported fields list
- Fixed variable naming bug: query param `status` shadowed `status` module in list_employees handler, causing AttributeError on sort_by validation
- Comprehensive README.md rewrite: technology stack table, project architecture, prerequisites, all env variables, API reference for all 30+ endpoints with roles/auth requirements, API response format examples, business rules, frontend integration guide, troubleshooting table
- 2 additional tests: test_search_endpoint_dedicated, test_list_employees_sort_by_whitelist

## Files Modified
- app/routers/employees.py — Added ALLOWED_SORT_FIELDS whitelist set; added /search endpoint BEFORE /{emp_id} route; fixed sort_by validation to use literal 400 instead of status.HTTP_400_BAD_REQUEST (avoiding name collision with query param 'status')
- README.md — Complete rewrite with technology stack, architecture, env variables table, full API reference for all endpoints (auth, employees, face, attendance, time-cards, reports, dashboard, departments), response format, role-based auth table, business rules, seed data, frontend integration guide, troubleshooting
- tests/test_employees.py — Added test_search_endpoint_dedicated (tests q, employee_id, department, status filters on /search endpoint) and test_list_employees_sort_by_whitelist (asserts 400 on invalid sort_by)

## Files Added
- None (all changes extend existing files)

## Secrets Extracted
- All secrets already in .env_22412b214a31e30d (DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, LATE_THRESHOLD, PORT)

## DB URLs Resolved
- postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c — unchanged, working (CASE B — already resolved in prior commit)

## Test Results Summary
55 PASSED, 0 FAILED, 0 SKIPPED

### Endpoint Test Details
- POST /api/v1/auth/signup — PASSED (201 created, 409 duplicate, 422 validation)
- POST /api/v1/auth/login — PASSED (200 success, 401 wrong password)
- GET /api/v1/auth/me — PASSED (200 authenticated, 401 invalid token, 401/403 no token)
- POST /api/v1/auth/logout — PASSED (200 success)
- GET /api/v1/employees — PASSED (200 list with pagination)
- GET /api/v1/employees?sort_by=invalid — PASSED (400 whitelist rejection)
- POST /api/v1/employees — PASSED (201 created, 409 duplicate, 403 unauthorized)
- GET /api/v1/employees/{id} — PASSED (200 found, 404 not found)
- PUT /api/v1/employees/{id} — PASSED (200 updated)
- DELETE /api/v1/employees/{id} — PASSED (200 deactivated)
- GET /api/v1/employees?search= — PASSED (200 search results)
- GET /api/v1/employees/search — PASSED (200 with q, employee_id, department, status filters)
- POST /api/v1/attendance/check-in — PASSED (201 success, 409 duplicate, 404 invalid employee)
- POST /api/v1/attendance/check-out — PASSED (200 success, 400 no check-in)
- GET /api/v1/attendance — PASSED (200 with filters)
- POST /api/v1/face/register — PASSED (201 success, 201 update existing, 404 invalid employee)
- POST /api/v1/face/verify — PASSED (200 verified=true, 200 verified=false, 200 no registration)
- GET /api/v1/departments — PASSED (200 list)
- POST /api/v1/departments — PASSED (201 created, 409 duplicate)
- GET /api/v1/departments/{id} — PASSED (200 found)
- PUT /api/v1/departments/{id} — PASSED (200 updated)
- DELETE /api/v1/departments/{id} — PASSED (200 deleted)
- GET /api/v1/dashboard — PASSED (200 with metrics, 401/403 unauthorized)
- GET /api/v1/reports/daily-attendance — PASSED (200 with records)
- GET /api/v1/reports/monthly-attendance — PASSED (200 with data)
- GET /api/v1/reports/time-card/{id} — PASSED (200 with data)
- GET /api/v1/reports/department-attendance — PASSED (200 with data)
- GET /api/v1/reports/export/attendance-csv — PASSED (200 CSV response)
- GET /api/v1/time-cards/{id} — PASSED (200 success, 404 not found, 200 date range)
- GET /health — PASSED (200 OK)
