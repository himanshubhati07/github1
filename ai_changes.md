COMMIT_MESSAGE: Remove duplicate /reports/time-card endpoint and unused API dead code cleanup

## Features Added
- No new features; this change removes extra/unused APIs from the project.

## Files Modified
- app/routers/reports.py — Removed the duplicate `GET /api/v1/reports/time-card/{employee_id}` endpoint which was an exact functional duplicate of the dedicated `GET /api/v1/time-cards/{employee_id}` in timecards.py. Also removed the now-unused `TimeCardResponse` import. Updated env file reference.
- app/routers/face.py — Updated env file reference to .env_22412b214a31e30d. Comment updated to reflect accurate scope.
- app/main.py — Updated env file reference to .env_22412b214a31e30d.
- app/database.py — Updated env file reference to .env_22412b214a31e30d.
- app/core/security.py — Updated env file reference to .env_22412b214a31e30d.
- app/core/auth.py — Updated env file reference to .env_22412b214a31e30d.
- app/models.py — Updated env file reference to .env_22412b214a31e30d.
- app/schemas.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/attendance.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/auth.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/dashboard.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/departments.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/employees.py — Updated env file reference to .env_22412b214a31e30d.
- app/routers/timecards.py — Updated env file reference to .env_22412b214a31e30d.
- tests/conftest.py — Updated env file reference to .env_22412b214a31e30d.
- tests/test_reports.py — Removed test for the removed duplicate `GET /reports/time-card/{employee_id}` endpoint.
- seed.py — Updated env file reference to .env_22412b214a31e30d.

## Files Added
- .env_22412b214a31e30d — New canonical env file with DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, LATE_THRESHOLD, PORT.

## Secrets Extracted
- DATABASE_URL -> written to .env_22412b214a31e30d
- SECRET_KEY -> written to .env_22412b214a31e30d
- ALGORITHM -> written to .env_22412b214a31e30d
- ACCESS_TOKEN_EXPIRE_MINUTES -> written to .env_22412b214a31e30d
- LATE_THRESHOLD -> written to .env_22412b214a31e30d

## DB URLs Resolved
- postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c -> postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c (working, no change needed)

## Test Results Summary
52 PASSED, 0 FAILED, 0 SKIPPED
