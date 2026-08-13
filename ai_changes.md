COMMIT_MESSAGE: Standardize Python FastAPI configuration, secrets, database URL, and port

## Features Added
- Confirmed the complete API is implemented in Python with FastAPI; no API entities, fields, routes, or business rules were invented because the requested language conversion was already satisfied.
- Standardized local, Docker, and shell startup configuration on the required port 46375.
- Removed hardcoded database and JWT secret fallback values from Python source so runtime configuration comes from `.env_22412b214a31e30d`.

## Files Modified
- `.env_22412b214a31e30d` — Set the application port to 46375 and retained the working resolved local PostgreSQL URL.
- `app/core/security.py` — Require `SECRET_KEY` from the loaded environment instead of embedding a source fallback.
- `app/database.py` — Require `DATABASE_URL` from the loaded environment instead of embedding credentials in Python source.
- `docker-compose.yml` — Replace the unreachable container-host DB URL with its prescribed localhost fallback and standardize API port 46375.
- `start.sh` — Start the Python FastAPI application on port 46375 without reload mode.
- `tests/conftest.py` — Require the test database base URL from the loaded environment instead of embedding credentials in test source.

## Files Added
- None.

## Secrets Extracted
- `SECRET_KEY` -> written to `.env_22412b214a31e30d` and required by `app/core/security.py`.
- `DATABASE_URL` -> written to `.env_22412b214a31e30d` and required by application/test database configuration.

## DB URLs Resolved
- `postgresql+asyncpg://myuser:mypassword@db:5432/gen_f07875928c` -> `postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_60a0e5ebed` in `docker-compose.yml`.
- `postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c` -> unchanged because it was pre-resolved as working; retained in `.env_22412b214a31e30d`.

## Test Results Summary
- 55 PASSED, 0 FAILED, 0 SKIPPED.
- Syntax compilation: PASSED.
- `app.main:app` import check: PASSED.
- Real Uvicorn server boot and `GET /health` on port 46375: PASSED (HTTP 200).
- The shared PostgreSQL server exhausted its global connection slots during one monolithic pytest process; running the same complete suite by test module released connections between modules and all 55 tests passed.
