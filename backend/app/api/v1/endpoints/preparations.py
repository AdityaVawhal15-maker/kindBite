"""KindBite — Preparation record endpoints"""
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_restaurant_or_admin
from app.db.session import get_db
from app.models import FoodItem, PreparationRecord, Restaurant, User
from app.schemas.schemas import PreparationCreate, PreparationOut

router = APIRouter()


async def _get_restaurant(user: User, db: AsyncSession) -> Restaurant:
    r = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = r.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    return restaurant


@router.post("", response_model=PreparationOut, status_code=201)
async def create_preparation(
    payload: PreparationCreate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)

    fi = await db.execute(
        select(FoodItem).where(
            FoodItem.id == payload.food_item_id,
            FoodItem.restaurant_id == restaurant.id,
        )
    )
    if not fi.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Food item not found.")

    record = PreparationRecord(restaurant_id=restaurant.id, **payload.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return PreparationOut.model_validate(record)


@router.get("", response_model=List[PreparationOut])
async def list_preparations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)
    result = await db.execute(
        select(PreparationRecord)
        .where(PreparationRecord.restaurant_id == restaurant.id)
        .order_by(PreparationRecord.date.desc())
        .offset(skip)
        .limit(limit)
    )
    return [PreparationOut.model_validate(r) for r in result.scalars().all()]
