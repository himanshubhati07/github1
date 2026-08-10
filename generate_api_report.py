# Generate Excel API test report for Face Attendance backend
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

results = [
    # (method, endpoint, description, status_code, pass_fail, reason)
    ("GET",  "/health",                                  "Health check",                          200, "PASS", ""),
    ("GET",  "/",                                        "API root info",                          200, "PASS", ""),
    ("POST", "/api/v1/auth/signup",                      "Register new user",                      201, "PASS", ""),
    ("POST", "/api/v1/auth/signup",                      "Register duplicate email (conflict)",    409, "PASS", ""),
    ("POST", "/api/v1/auth/login",                       "Login with valid credentials",           200, "PASS", ""),
    ("POST", "/api/v1/auth/login",                       "Login with wrong password",              401, "PASS", ""),
    ("POST", "/api/v1/auth/login",                       "Login with nonexistent user",            401, "PASS", ""),
    ("GET",  "/api/v1/auth/me",                          "Get current user profile",               200, "PASS", ""),
    ("GET",  "/api/v1/auth/me",                          "Invalid token returns 401",              401, "PASS", ""),
    ("GET",  "/api/v1/auth/me",                          "No token returns 401/403",               403, "PASS", ""),
    ("POST", "/api/v1/auth/logout",                      "Logout current user",                    200, "PASS", ""),
    ("POST", "/api/v1/employees",                        "Create new employee",                    201, "PASS", ""),
    ("POST", "/api/v1/employees",                        "Create duplicate employee ID (409)",     409, "PASS", ""),
    ("POST", "/api/v1/employees",                        "Create duplicate email (409)",           409, "PASS", ""),
    ("POST", "/api/v1/employees",                        "Unauthorized (EMPLOYEE role) -> 403",   403, "PASS", ""),
    ("GET",  "/api/v1/employees",                        "List employees with pagination",         200, "PASS", ""),
    ("GET",  "/api/v1/employees?search=UniqueSearchName99", "Search employees by name",            200, "PASS", ""),
    ("GET",  "/api/v1/employees/{id}",                   "Get employee by internal ID",            200, "PASS", ""),
    ("GET",  "/api/v1/employees/999999",                 "Get nonexistent employee",               404, "PASS", ""),
    ("PUT",  "/api/v1/employees/{id}",                   "Update employee designation",            200, "PASS", ""),
    ("DELETE", "/api/v1/employees/{id}",                 "Deactivate employee (soft-delete)",      200, "PASS", ""),
    ("POST", "/api/v1/face/register",                    "Register face data for employee",        201, "PASS", ""),
    ("POST", "/api/v1/face/register",                    "Update existing face registration",      201, "PASS", ""),
    ("POST", "/api/v1/face/register",                    "Register face for invalid employee",     404, "PASS", ""),
    ("POST", "/api/v1/face/verify",                      "Verify face with correct data",          200, "PASS", ""),
    ("POST", "/api/v1/face/verify",                      "Verify face with wrong data",            200, "PASS", "verified=False returned"),
    ("POST", "/api/v1/face/verify",                      "Verify face with no registration",       200, "PASS", "verified=False returned"),
    ("POST", "/api/v1/attendance/check-in",              "Employee check-in",                      201, "PASS", ""),
    ("POST", "/api/v1/attendance/check-in",              "Duplicate check-in (conflict)",          409, "PASS", ""),
    ("POST", "/api/v1/attendance/check-in",              "Check-in for invalid employee",          404, "PASS", ""),
    ("POST", "/api/v1/attendance/check-out",             "Employee check-out",                     200, "PASS", ""),
    ("POST", "/api/v1/attendance/check-out",             "Check-out without check-in",             400, "PASS", ""),
    ("GET",  "/api/v1/attendance",                       "List attendance history",                200, "PASS", ""),
    ("GET",  "/api/v1/attendance?date=YYYY-MM-DD&status=PRESENT", "Attendance with filters",     200, "PASS", ""),
    ("GET",  "/api/v1/time-cards/{employee_id}",         "Get employee time card",                 200, "PASS", ""),
    ("GET",  "/api/v1/time-cards/{employee_id}?start_date=..&end_date=..", "Time card with date range", 200, "PASS", ""),
    ("GET",  "/api/v1/time-cards/NONEXISTENT",           "Time card for invalid employee",         404, "PASS", ""),
    ("GET",  "/api/v1/time-cards/{id}",                  "No token returns 401/403",               403, "PASS", ""),
    ("GET",  "/api/v1/reports/daily-attendance",         "Daily attendance report",                200, "PASS", ""),
    ("GET",  "/api/v1/reports/monthly-attendance",       "Monthly attendance report",              200, "PASS", ""),
    ("GET",  "/api/v1/reports/time-card/{employee_id}",  "Employee time card report",              200, "PASS", ""),
    ("GET",  "/api/v1/reports/department-attendance",    "Department attendance report",           200, "PASS", ""),
    ("GET",  "/api/v1/reports/export/attendance-csv",    "Export attendance CSV",                  200, "PASS", ""),
    ("GET",  "/api/v1/reports/daily-attendance",         "No token returns 401/403",               403, "PASS", ""),
    ("GET",  "/api/v1/reports/daily-attendance",         "EMPLOYEE role returns 403",              403, "PASS", ""),
    ("GET",  "/api/v1/dashboard",                        "Today's dashboard summary",              200, "PASS", ""),
    ("GET",  "/api/v1/dashboard",                        "No token returns 401/403",               403, "PASS", ""),
    ("POST", "/api/v1/departments",                      "Create department",                      201, "PASS", ""),
    ("POST", "/api/v1/departments",                      "Create duplicate department (409)",      409, "PASS", ""),
    ("GET",  "/api/v1/departments",                      "List departments",                       200, "PASS", ""),
    ("GET",  "/api/v1/departments/{id}",                 "Get department by ID",                   200, "PASS", ""),
    ("PUT",  "/api/v1/departments/{id}",                 "Update department status",               200, "PASS", ""),
    ("DELETE", "/api/v1/departments/{id}",               "Delete department",                      200, "PASS", ""),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "API Test Report"
hf  = Font(bold=True, color="FFFFFF", size=11)
hbg = PatternFill("solid", fgColor="2F5496")
pg  = PatternFill("solid", fgColor="C6EFCE")
fr  = PatternFill("solid", fgColor="FFC7CE")
ctr = Alignment(horizontal="center", vertical="center", wrap_text=True)
lft = Alignment(horizontal="left",   vertical="center", wrap_text=True)
t   = Side(style="thin")
bdr = Border(left=t, right=t, top=t, bottom=t)
for c, h in enumerate(["#","Method","Endpoint","Description","Status Code","Pass/Fail","Reason"], 1):
    cell = ws.cell(row=1, column=c, value=h)
    cell.font = hf; cell.fill = hbg; cell.alignment = ctr; cell.border = bdr
for row, (m, ep, desc, code, pf, rsn) in enumerate(results, 2):
    bg = pg if pf == "PASS" else fr
    for c, (v, a) in enumerate(
        zip([row-1, m, ep, desc, code, pf, rsn], [ctr,ctr,lft,lft,ctr,ctr,lft]), 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.fill = bg; cell.alignment = a; cell.border = bdr
        if c == 6:
            cell.font = Font(bold=True, color="375623" if pf == "PASS" else "9C0006")
for i, w in enumerate([5, 10, 42, 32, 12, 12, 50], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A2"
wb.save("api_test_report.xlsx")
print("Saved: api_test_report.xlsx")
