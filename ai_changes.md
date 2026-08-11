COMMIT_MESSAGE: Add face ID editing API (PUT /api/v1/face/{employeeId}) for updating registered face data

## Features Added
- New PUT endpoint `/api/v1/face/{employeeId}` to edit/update an employee's registered face ID data
- FaceEditRequest DTO with validation for the new face data field
- updateFace() service method in FaceService that validates employee exists/active, retrieves the existing face registration, updates the face reference, and persists the change

## Files Modified
- `src/main/resources/application.properties` — Updated server.port from 55513 to 55049
- `start.sh` — Updated SERVER_PORT from 55513 to 55049
- `src/main/java/com/example/app/controller/FaceController.java` — Added PUT /{employeeId} endpoint for face editing
- `src/main/java/com/example/app/service/FaceService.java` — Added updateFace() method for face data update logic

## Files Added
- `src/main/java/com/example/app/dto/FaceEditRequest.java` — DTO for face edit request with @NotBlank validation on faceData field
- `api_tests/test_face_edit.sh` — Curl-based test script covering full lifecycle of the new face edit API

## Secrets Moved
- None (all secrets were already using application.properties with environment variable fallbacks)

## DB URLs Resolved
- jdbc:postgresql://localhost:5432/gen_054b6290d0 -> jdbc:postgresql://localhost:5432/gen_054b6290d0 (SAME - working, no change needed)

## Test Results Summary
7 PASSED, 0 FAILED, 0 SKIPPED
- POST /api/v1/auth/signup: PASSED (201)
- POST /api/v1/employees: PASSED (201)
- POST /api/v1/face/register: PASSED (201)
- PUT /api/v1/face/{employeeId}: PASSED (200) — new face edit endpoint
- PUT /api/v1/face/NONEXISTENT: PASSED (404) — correctly rejects missing employee
- PUT /api/v1/face/{employeeId} (invalid body): PASSED (400) — validation enforced
- GET /actuator/health: PASSED (200)
