"""
KindBite — Donation endpoints
Full donation lifecycle: DRAFT → PUBLISHED → MATCHED → ACCEPTED → ASSIGNED → COLLECTED → DELIVERED
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_ngo_or_admin, require_restaurant_or_admin
from app.db.session import get_db
from app.models import (
    Donation, DonationStatus, DonationStatusHistory, FoodSafetyCheck,
    Restaurant, User, UserRole,
)
from app.schemas.schemas import DonationCreate, DonationOut, DonationUpdate
from app.services.food_safety import assess_donation_safety
from app.services.notification import create_notification

router = APIRouter()


async def _get_restaurant(user: User, db: AsyncSession) -> Restaurant:
    r = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = r.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    return restaurant


async def _add_status_history(db: AsyncSession, donation: Donation, status: DonationStatus, user_id: str, notes: str = None):
    h = DonationStatusHistory(
        donation_id=donation.id,
        status=status,
        changed_by=user_id,
        notes=notes,
    )
    db.add(h)


@router.post("", response_model=DonationOut, status_code=201)
async def create_donation(
    payload: DonationCreate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)

    donation = Donation(
        restaurant_id=restaurant.id,
        **payload.model_dump(),
        status=DonationStatus.DRAFT,
    )
    db.add(donation)
    await db.flush()

    # Run food safety check
    safety = await assess_donation_safety(donation)
    safety_check = FoodSafetyCheck(
        donation_id=donation.id,
        **safety,
    )
    db.add(safety_check)
    donation.is_eligible = safety["overall_eligible"]

    await _add_status_history(db, donation, DonationStatus.DRAFT, current_user.id)
    await db.commit()
    await db.refresh(donation)
    return DonationOut.model_validate(donation)


@router.get("", response_model=List[DonationOut])
async def list_donations(
    status: Optional[DonationStatus] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Donation)

    # Restaurants see only their own donations
    if current_user.role == UserRole.RESTAURANT:
        r = await db.execute(select(Restaurant).where(Restaurant.owner_id == current_user.id))
        restaurant = r.scalar_one_or_none()
        if restaurant:
            q = q.where(Donation.restaurant_id == restaurant.id)

    if status:
        q = q.where(Donation.status == status)
    if city:
        q = q.where(Donation.pickup_city == city)
    if category:
        q = q.where(Donation.food_category == category)

    q = q.order_by(Donation.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return [DonationOut.model_validate(d) for d in result.scalars().all()]


@router.get("/{donation_id}", response_model=DonationOut)
async def get_donation(
    donation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")
    return DonationOut.model_validate(donation)


@router.patch("/{donation_id}", response_model=DonationOut)
async def update_donation(
    donation_id: str,
    payload: DonationUpdate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if donation.status not in [DonationStatus.DRAFT, DonationStatus.PUBLISHED]:
        raise HTTPException(status_code=400, detail="Cannot edit a donation after it is matched.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(donation, field, value)

    await db.commit()
    await db.refresh(donation)
    return DonationOut.model_validate(donation)


@router.post("/{donation_id}/publish", response_model=DonationOut)
async def publish_donation(
    donation_id: str,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Publish a draft donation so NGOs can discover it."""
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if donation.status != DonationStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft donations can be published.")

    if not donation.safety_confirmed or not donation.handler_declaration:
        raise HTTPException(
            status_code=422,
            detail="Safety confirmation and handler declaration are required before publishing.",
        )

    if donation.is_eligible is False:
        raise HTTPException(
            status_code=422,
            detail="Donation failed food safety check and cannot be published. Please review safety fields.",
        )

    donation.status = DonationStatus.PUBLISHED
    donation.published_at = datetime.now(timezone.utc)
    await _add_status_history(db, donation, DonationStatus.PUBLISHED, current_user.id)

    await db.commit()
    await db.refresh(donation)
    return DonationOut.model_validate(donation)


@router.post("/{donation_id}/cancel", response_model=DonationOut)
async def cancel_donation(
    donation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if donation.status in [DonationStatus.COLLECTED, DonationStatus.DELIVERED]:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed donation.")

    donation.status = DonationStatus.CANCELLED
    await _add_status_history(db, donation, DonationStatus.CANCELLED, current_user.id)
    await db.commit()
    await db.refresh(donation)
    return DonationOut.model_validate(donation)
