#!/bin/bash
BASE_URL="http://localhost:55049"
TOKEN=""
PASS=0
FAIL=0
EMPLOYEE_ID="EMP_FACE_TEST_$(date +%s)"

echo "=== Face ID Editing API Tests ==="

# Step 1: Register a user to get JWT
echo "1. POST /api/v1/auth/signup"
SIGNUP_RESP=$(curl -s --max-time 60 -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"FaceTest User\",\"email\":\"facetest_$(date +%s)@test.com\",\"password\":\"password123\",\"confirmPassword\":\"password123\"}")
echo "  Signup: $SIGNUP_RESP"
TOKEN=$(echo "$SIGNUP_RESP" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN" ]; then echo "  -> PASS (token obtained)"; PASS=$((PASS+1)); else echo "  -> FAIL (no token)"; FAIL=$((FAIL+1)); fi

# Step 2: Create a test employee
echo "2. POST /api/v1/employees (create employee)"
EMP_RESP=$(curl -s --max-time 60 -X POST "$BASE_URL/api/v1/employees" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"employeeId\":\"$EMPLOYEE_ID\",\"name\":\"Test Employee\",\"email\":\"empface_$(date +%s)@test.com\",\"status\":\"ACTIVE\"}")
echo "  Create Employee: $EMP_RESP"
EMP_STATUS=$(echo "$EMP_RESP" | grep -o '"success":true')
if [ -n "$EMP_STATUS" ]; then echo "  -> PASS"; PASS=$((PASS+1)); else echo "  -> FAIL"; FAIL=$((FAIL+1)); fi

# Step 3: Register face for the employee
echo "3. POST /api/v1/face/register"
FACE_REG_RESP=$(curl -s --max-time 60 -X POST "$BASE_URL/api/v1/face/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"employeeId\":\"$EMPLOYEE_ID\",\"faceData\":\"base64encodedFaceData1234\"}")
echo "  Face Register: $FACE_REG_RESP"
FACE_REG_STATUS=$(echo "$FACE_REG_RESP" | grep -o '"success":true')
if [ -n "$FACE_REG_STATUS" ]; then echo "  -> PASS"; PASS=$((PASS+1)); else echo "  -> FAIL"; FAIL=$((FAIL+1)); fi

# Step 4: Edit/update the face data (new endpoint)
echo "4. PUT /api/v1/face/$EMPLOYEE_ID (edit face data)"
FACE_EDIT_RESP=$(curl -s --max-time 60 -X PUT "$BASE_URL/api/v1/face/$EMPLOYEE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"faceData\":\"newBase64FaceData5678\"}")
HTTP_CODE=$(curl -s --max-time 60 -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL/api/v1/face/$EMPLOYEE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"faceData\":\"newBase64FaceData5678\"}")
echo "  Face Edit Response: $FACE_EDIT_RESP"
echo "  Face Edit HTTP Code: $HTTP_CODE"
FACE_EDIT_STATUS=$(echo "$FACE_EDIT_RESP" | grep -o '"success":true')
if [ -n "$FACE_EDIT_STATUS" ] || [ "$HTTP_CODE" = "200" ]; then echo "  -> PASS"; PASS=$((PASS+1)); else echo "  -> FAIL"; FAIL=$((FAIL+1)); fi

# Step 5: Edit face for non-existent employee (expect error)
echo "5. PUT /api/v1/face/NONEXISTENT (expect 400/404/500)"
FACE_EDIT_NE=$(curl -s --max-time 60 -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL/api/v1/face/NONEXISTENT_EMP_99" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"faceData\":\"someFaceData\"}")
echo "  HTTP Code: $FACE_EDIT_NE"
if [ "$FACE_EDIT_NE" != "200" ]; then echo "  -> PASS (correctly rejected)"; PASS=$((PASS+1)); else echo "  -> FAIL (should not return 200)"; FAIL=$((FAIL+1)); fi

# Step 6: Edit face with no faceData (validation error)
echo "6. PUT /api/v1/face/$EMPLOYEE_ID (invalid - empty faceData)"
FACE_EDIT_INV=$(curl -s --max-time 60 -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL/api/v1/face/$EMPLOYEE_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"faceData\":\"\"}")
echo "  HTTP Code: $FACE_EDIT_INV"
if [ "$FACE_EDIT_INV" = "400" ]; then echo "  -> PASS (validation rejected)"; PASS=$((PASS+1)); else echo "  -> FAIL (expected 400, got $FACE_EDIT_INV)"; FAIL=$((FAIL+1)); fi

# Step 7: Health check
echo "7. GET /actuator/health"
HEALTH=$(curl -s --max-time 60 "$BASE_URL/actuator/health" | grep -o '"status":"UP"')
if [ -n "$HEALTH" ]; then echo "  -> PASS"; PASS=$((PASS+1)); else echo "  -> FAIL"; FAIL=$((FAIL+1)); fi

# Cleanup: delete test employee (if delete endpoint exists)
echo "8. DELETE /api/v1/employees/$EMPLOYEE_ID (cleanup)"
DEL_RESP=$(curl -s --max-time 60 -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/api/v1/employees/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "  Cleanup HTTP Code: $DEL_RESP"

echo ""
echo "=== RESULTS: $PASS PASSED, $FAIL FAILED ==="
if [ "$FAIL" -eq 0 ]; then
  echo "PASSED"
  exit 0
else
  echo "FAILED: $FAIL test(s) failed"
  exit 1
fi
