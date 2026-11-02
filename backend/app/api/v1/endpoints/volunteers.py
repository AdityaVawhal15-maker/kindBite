"""KindBite — Volunteer endpoints"""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import User, UserRole, Volunteer
from app.schemas.schemas import VolunteerOut, VolunteerUpdate

router = APIRouter()


async def _get_volunteer(user: User, db: AsyncSession) -> Volunteer:
    r = await db.execute(select(Volunteer).where(Volunteer.user_id == user.id))
    v = r.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Volunteer profile not found.")
    return v


@router.get("/me", response_model=VolunteerOut)
async def get_my_volunteer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.VOLUNTEER and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not a volunteer account.")
    return VolunteerOut.model_validate(await _get_volunteer(current_user, db))


@router.patch("/me", response_model=VolunteerOut)
async def update_my_volunteer(
    payload: VolunteerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    volunteer = await _get_volunteer(current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(volunteer, field, value)
    await db.commit()
    await db.refresh(volunteer)
    return VolunteerOut.model_validate(volunteer)


@router.patch("/me/availability")
async def toggle_availability(
    available: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    volunteer = await _get_volunteer(current_user, db)
    volunteer.is_available = available
    await db.commit()
    return {"message": f"Availability set to {'available' if available else 'unavailable'}."}


@router.get("", response_model=List[VolunteerOut])
async def list_volunteers(
    available_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Volunteer).where(Volunteer.is_active == True)
    if available_only:
        q = q.where(Volunteer.is_available == True)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return [VolunteerOut.model_validate(v) for v in result.scalars().all()]
