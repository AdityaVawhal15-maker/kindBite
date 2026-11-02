"""
KindBite — FastAPI dependencies (auth, db, current user)
"""
from __future__ import annotations

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User, UserRole, AccountStatus

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("No subject")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active or user.status == AccountStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    return user


def require_role(*roles: UserRole):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires role: {', '.join(r.value for r in roles)}",
            )
        return current_user
    return checker


require_restaurant = require_role(UserRole.RESTAURANT)
require_ngo = require_role(UserRole.NGO)
require_volunteer = require_role(UserRole.VOLUNTEER)
require_admin = require_role(UserRole.ADMIN)
require_restaurant_or_admin = require_role(UserRole.RESTAURANT, UserRole.ADMIN)
require_ngo_or_admin = require_role(UserRole.NGO, UserRole.ADMIN)
