"""
KindBite — Authentication endpoints
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
POST /auth/refresh
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models import AccountStatus, User, UserRole, VerificationStatus
from app.schemas.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.audit import record_audit
from app.services.notification import create_notification

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        status=AccountStatus.ACTIVE,  # auto-activate for now; add email verification later
        verification_status=VerificationStatus.UNVERIFIED,
    )
    db.add(user)
    await db.flush()  # get user.id

    # Create role-specific profile
    from app.models import Restaurant, NGO, Volunteer
    if payload.role == UserRole.RESTAURANT:
        restaurant = Restaurant(
            owner_id=user.id,
            name=payload.organization_name or payload.full_name,
            address=payload.address or "",
            city=payload.city or "Mumbai",
            pincode=payload.pincode or "400001",
        )
        db.add(restaurant)
    elif payload.role == UserRole.NGO:
        ngo = NGO(
            owner_id=user.id,
            name=payload.organization_name or payload.full_name,
            address=payload.address or "",
            city=payload.city or "Mumbai",
            pincode=payload.pincode or "400001",
        )
        db.add(ngo)
    elif payload.role == UserRole.VOLUNTEER:
        volunteer = Volunteer(
            user_id=user.id,
            city=payload.city or "Mumbai",
            address=payload.address,
            pincode=payload.pincode,
        )
        db.add(volunteer)

    await db.commit()
    await db.refresh(user)

    await record_audit(
        db, actor_id=user.id, action="USER_REGISTERED",
        resource_type="user", resource_id=user.id,
        ip_address=request.client.host if request.client else None,
    )

    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and receive JWT tokens."""
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.is_active or user.status == AccountStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    await record_audit(
        db, actor_id=user.id, action="USER_LOGIN",
        resource_type="user", resource_id=user.id,
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(
        access_token=create_access_token(user.id, extra={"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint — client should discard tokens."""
    # Token revocation requires a denylist; for now, client-side logout suffices.
    return {"message": "Logged out successfully. Please discard your tokens."}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return UserOut.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Issue new access token using refresh token."""
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise JWTError("wrong token type")
        user_id = data.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return TokenResponse(
        access_token=create_access_token(user.id, extra={"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )
