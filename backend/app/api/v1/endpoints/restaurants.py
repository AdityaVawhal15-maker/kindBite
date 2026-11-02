"""
KindBite — Restaurant endpoints
"""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_restaurant_or_admin, require_admin
from app.db.session import get_db
from app.models import Restaurant, User, UserRole, FoodItem
from app.schemas.schemas import RestaurantCreate, RestaurantOut, RestaurantUpdate, FoodItemCreate, FoodItemOut

router = APIRouter()


@router.get("/me", response_model=RestaurantOut)
async def get_my_restaurant(
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == current_user.id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    return RestaurantOut.model_validate(restaurant)


@router.patch("/me", response_model=RestaurantOut)
async def update_my_restaurant(
    payload: RestaurantUpdate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == current_user.id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)
    
    await db.commit()
    await db.refresh(restaurant)
    return RestaurantOut.model_validate(restaurant)


@router.get("/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    return RestaurantOut.model_validate(restaurant)


# ── Food Items ──────────────────────────────────────────────

@router.post("/me/food-items", response_model=FoodItemOut, status_code=201)
async def create_food_item(
    payload: FoodItemCreate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == current_user.id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    
    item = FoodItem(restaurant_id=restaurant.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return FoodItemOut.model_validate(item)


@router.get("/me/food-items", response_model=List[FoodItemOut])
async def list_food_items(
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == current_user.id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        return []
    
    items_result = await db.execute(
        select(FoodItem).where(FoodItem.restaurant_id == restaurant.id, FoodItem.is_active == True)
    )
    return [FoodItemOut.model_validate(i) for i in items_result.scalars().all()]
