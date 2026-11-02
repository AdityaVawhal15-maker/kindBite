"""KindBite — NGO endpoints"""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_ngo_or_admin
from app.db.session import get_db
from app.models import NGO, NGORequirement, User
from app.schemas.schemas import NGOCreate, NGOOut, NGOUpdate

router = APIRouter()


async def _get_ngo(user: User, db: AsyncSession) -> NGO:
    r = await db.execute(select(NGO).where(NGO.owner_id == user.id))
    ngo = r.scalar_one_or_none()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO profile not found.")
    return ngo


@router.get("/me", response_model=NGOOut)
async def get_my_ngo(
    current_user: User = Depends(require_ngo_or_admin),
    db: AsyncSession = Depends(get_db),
):
    return NGOOut.model_validate(await _get_ngo(current_user, db))


@router.patch("/me", response_model=NGOOut)
async def update_my_ngo(
    payload: NGOUpdate,
    current_user: User = Depends(require_ngo_or_admin),
    db: AsyncSession = Depends(get_db),
):
    ngo = await _get_ngo(current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ngo, field, value)
    await db.commit()
    await db.refresh(ngo)
    return NGOOut.model_validate(ngo)


@router.get("", response_model=List[NGOOut])
async def list_ngos(
    city: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(NGO).where(NGO.is_active == True)
    if city:
        q = q.where(NGO.city == city)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return [NGOOut.model_validate(n) for n in result.scalars().all()]
