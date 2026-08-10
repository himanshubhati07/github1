# Factory helpers that build valid request payloads for tests
import random
import string


def random_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def make_signup_payload(**overrides):
    suffix = random_suffix()
    data = {
        "name": f"Test User {suffix}",
        "email": f"testuser_{suffix}@example.com",
        "password": "TestPass123",
        "confirm_password": "TestPass123",
        "role": "EMPLOYEE",
    }
    data.update(overrides)
    return data


def make_login_payload(email: str, password: str):
    return {"email": email, "password": password}


def make_employee_payload(**overrides):
    suffix = random_suffix()
    data = {
        "employee_id": f"EMP_{suffix.upper()}",
        "name": f"Employee {suffix}",
        "email": f"emp_{suffix}@company.com",
        "phone": "9876543210",
        "department": "Engineering",
        "designation": "Developer",
        "joining_date": "2023-01-01",
        "status": "ACTIVE",
    }
    data.update(overrides)
    return data


def make_face_register_payload(employee_id: str, face_data: str = "demo_face_data"):
    return {"employee_id": employee_id, "face_data": face_data}


def make_face_verify_payload(employee_id: str, face_data: str = "demo_face_data"):
    return {"employee_id": employee_id, "face_data": face_data}


def make_checkin_payload(employee_id: str):
    return {"employee_id": employee_id, "face_verified": True}


def make_checkout_payload(employee_id: str):
    return {"employee_id": employee_id}


def make_department_payload(**overrides):
    suffix = random_suffix()
    data = {
        "name": f"Department {suffix}",
        "status": "ACTIVE",
    }
    data.update(overrides)
    return data
