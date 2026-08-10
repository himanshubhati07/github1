# Seed script: create demo data for Face Attendance app
import os
import asyncio
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

from datetime import date, datetime, time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.database import DATABASE_URL, Base
from app.models import User, Employee, Department, FaceRegistration, Attendance
from app.models import UserRole, UserStatus, EmployeeStatus, DepartmentStatus, AttendanceStatus
from app.core.security import hash_password


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        # ── Departments ──────────────────────────────────────────────
        dept_names = ["Engineering", "Human Resources", "Finance", "Marketing", "Operations"]
        depts = []
        for name in dept_names:
            existing = await db.execute(select(Department).where(Department.name == name))
            dept = existing.scalar_one_or_none()
            if not dept:
                dept = Department(name=name, status=DepartmentStatus.ACTIVE, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
                db.add(dept)
            depts.append(dept)
        await db.flush()

        # ── Users ────────────────────────────────────────────────────
        users_data = [
            ("Admin User", "admin@faceattend.com", "Admin@123", UserRole.ADMIN),
            ("HR Manager", "hr@faceattend.com", "HR@123456", UserRole.HR),
            ("Employee User", "employee@faceattend.com", "Emp@12345", UserRole.EMPLOYEE),
        ]
        for name, email, pwd, role in users_data:
            existing = await db.execute(select(User).where(User.email == email))
            if not existing.scalar_one_or_none():
                u = User(
                    name=name, email=email,
                    password=hash_password(pwd),
                    role=role, status=UserStatus.ACTIVE,
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                )
                db.add(u)

        # ── Employees ─────────────────────────────────────────────────
        employees_data = [
            ("EMP001", "Rahul Sharma", "rahul.sharma@company.com", "9876543210", "Engineering", "Software Engineer", date(2022, 1, 15)),
            ("EMP002", "Priya Singh", "priya.singh@company.com", "9876543211", "Human Resources", "HR Executive", date(2021, 6, 1)),
            ("EMP003", "Amit Kumar", "amit.kumar@company.com", "9876543212", "Finance", "Finance Analyst", date(2020, 3, 20)),
            ("EMP004", "Sneha Patel", "sneha.patel@company.com", "9876543213", "Marketing", "Marketing Manager", date(2019, 11, 5)),
            ("EMP005", "Rohan Verma", "rohan.verma@company.com", "9876543214", "Engineering", "DevOps Engineer", date(2023, 4, 10)),
        ]
        emps = []
        for emp_id, name, email, phone, dept, desig, jdate in employees_data:
            existing = await db.execute(select(Employee).where(Employee.employee_id == emp_id))
            emp = existing.scalar_one_or_none()
            if not emp:
                emp = Employee(
                    employee_id=emp_id, name=name, email=email, phone=phone,
                    department=dept, designation=desig,
                    joining_date=jdate, status=EmployeeStatus.ACTIVE,
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                )
                db.add(emp)
            emps.append(emp)
        await db.flush()

        # ── Face Registrations ─────────────────────────────────────────
        import hashlib
        for emp in emps:
            existing = await db.execute(
                select(FaceRegistration).where(FaceRegistration.employee_id == emp.id)
            )
            if not existing.scalar_one_or_none():
                face_ref = hashlib.sha256(f"{emp.employee_id}:demo_face_data".encode()).hexdigest()
                db.add(FaceRegistration(
                    employee_id=emp.id,
                    face_reference=face_ref,
                    registered_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ))

        # ── Attendance Records (last 5 days for all employees) ─────────
        from datetime import timedelta
        today = date.today()
        for emp in emps:
            for days_back in range(5, 0, -1):
                att_date = today - timedelta(days=days_back)
                existing = await db.execute(
                    select(Attendance).where(
                        Attendance.employee_id == emp.id,
                        Attendance.attendance_date == att_date,
                    )
                )
                if not existing.scalar_one_or_none():
                    t_in = time(9, 0)
                    t_out = time(18, 0)
                    wh = 9.0
                    att_status = AttendanceStatus.PRESENT
                    if days_back == 3:
                        t_in = time(9, 30)
                        att_status = AttendanceStatus.LATE
                    db.add(Attendance(
                        employee_id=emp.id,
                        attendance_date=att_date,
                        time_in=t_in,
                        time_out=t_out,
                        working_hours=wh,
                        status=att_status,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ))

        await db.commit()
        print("✅ Seed data inserted successfully.")
        print("\nDemo credentials:")
        print("  Admin:    admin@faceattend.com / Admin@123")
        print("  HR:       hr@faceattend.com / HR@123456")
        print("  Employee: employee@faceattend.com / Emp@12345")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
