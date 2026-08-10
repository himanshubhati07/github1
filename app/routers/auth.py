# Authentication router: signup, login, me, logout
import os
from dotenv import load_dotenv
load_dotenv('.env_0421df12-3f2a-4fe0-beb1-bb42dc42c8bd', override=True)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models import User, UserRole, UserStatus
from app.schemas import SignupRequest, LoginRequest, TokenResponse, UserOut, SuccessResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Email already registered", "error_code": "EMAIL_ALREADY_EXISTS"},
        )
    # Validate role
    role_str = (payload.role or "EMPLOYEE").upper()
    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.EMPLOYEE

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=role,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email + password and receive a JWT."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid email or password", "error_code": "INVALID_CREDENTIALS"},
        )
    if user.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "User account is inactive", "error_code": "USER_INACTIVE"},
        )
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user profile."""
    return UserOut.model_validate(current_user)


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (client should discard token)."""
    return SuccessResponse(message="Logged out successfully")
