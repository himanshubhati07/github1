# Face registration and verification router (mock/demo implementation)
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Employee, EmployeeStatus, FaceRegistration, User
from app.schemas import FaceRegisterRequest, FaceRegisterResponse, FaceVerifyRequest, FaceVerifyResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/face", tags=["Face Recognition"])


def _mock_face_reference(employee_id: str, face_data: str) -> str:
    """Generate a deterministic mock face reference hash for demo mode."""
    combined = f"{employee_id}:{face_data}"
    return hashlib.sha256(combined.encode()).hexdigest()


def _mock_verify_face(stored_reference: str, employee_id: str, face_data: str) -> bool:
    """Demo mode: verify face by comparing stored reference hash."""
    expected = _mock_face_reference(employee_id, face_data)
    return stored_reference == expected


@router.post("/register", response_model=FaceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_face(
    payload: FaceRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register face data for an employee (demo/mock mode).
    Accepts employee_id string and face_data (base64 or any string in demo mode).
    Prevents duplicate registration.
    """
    if not payload.face_data or len(payload.face_data.strip()) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Invalid face data provided", "error_code": "INVALID_FACE_DATA"},
        )

    # Find employee by employee_id string
    result = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )
    if emp.status == EmployeeStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "Cannot register face for inactive employee", "error_code": "EMPLOYEE_INACTIVE"},
        )

    # Check for existing registration
    existing = await db.execute(
        select(FaceRegistration).where(FaceRegistration.employee_id == emp.id)
    )
    face_reg = existing.scalar_one_or_none()

    face_reference = _mock_face_reference(payload.employee_id, payload.face_data)

    if face_reg:
        # Update existing registration
        face_reg.face_reference = face_reference
        face_reg.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(face_reg)
        return FaceRegisterResponse(
            success=True,
            message="Face data updated successfully",
            employee_id=payload.employee_id,
            registered_at=face_reg.registered_at,
        )
    else:
        new_reg = FaceRegistration(
            employee_id=emp.id,
            face_reference=face_reference,
            registered_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_reg)
        await db.commit()
        await db.refresh(new_reg)
        return FaceRegisterResponse(
            success=True,
            message="Face registered successfully",
            employee_id=payload.employee_id,
            registered_at=new_reg.registered_at,
        )


@router.post("/verify", response_model=FaceVerifyResponse)
async def verify_face(
    payload: FaceVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify an employee's face (demo/mock mode).
    Returns verification result without recording attendance.
    """
    # Find employee
    result = await db.execute(select(Employee).where(Employee.employee_id == payload.employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Employee not found", "error_code": "EMPLOYEE_NOT_FOUND"},
        )
    if emp.status == EmployeeStatus.INACTIVE:
        return FaceVerifyResponse(
            success=False,
            verified=False,
            employee_id=payload.employee_id,
            employee_name=emp.name,
            message="Employee is inactive",
        )

    # Get face registration
    reg_result = await db.execute(
        select(FaceRegistration).where(FaceRegistration.employee_id == emp.id)
    )
    face_reg = reg_result.scalar_one_or_none()
    if not face_reg:
        return FaceVerifyResponse(
            success=False,
            verified=False,
            employee_id=payload.employee_id,
            employee_name=emp.name,
            message="No face data registered for this employee",
        )

    verified = _mock_verify_face(face_reg.face_reference, payload.employee_id, payload.face_data)
    return FaceVerifyResponse(
        success=True,
        verified=verified,
        employee_id=payload.employee_id,
        employee_name=emp.name,
        message="Face verified successfully" if verified else "Face verification failed",
    )
