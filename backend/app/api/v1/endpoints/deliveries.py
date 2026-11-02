"""
KindBite — Delivery management endpoints
Includes simplified VRP-based route planning (OR-Tools when available).
NOTE: Real GPS/navigation not available unless GOOGLE_MAPS_API_KEY is configured.
Distances are simulated in development mode.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import (
    DeliveryAssignment, DeliveryEvent, DeliveryStatus,
    Donation, DonationStatus, DonationStatusHistory, User, Volunteer, UserRole,
)
from app.schemas.schemas import DeliveryAssignRequest, DeliveryOut
from app.services.routing import compute_route

router = APIRouter()


@router.post("/assign", response_model=DeliveryOut, status_code=201)
async def assign_delivery(
    payload: DeliveryAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a volunteer to deliver a donation. Admin or NGO can assign."""
    if current_user.role not in [UserRole.ADMIN, UserRole.NGO]:
        raise HTTPException(status_code=403, detail="Only admins and NGOs can assign deliveries.")

    d_result = await db.execute(select(Donation).where(Donation.id == payload.donation_id))
    donation = d_result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")
    if donation.status != DonationStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Donation must be ACCEPTED before assigning a volunteer.")

    v_result = await db.execute(select(Volunteer).where(Volunteer.id == payload.volunteer_id))
    volunteer = v_result.scalar_one_or_none()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found.")
    if not volunteer.is_available:
        raise HTTPException(status_code=422, detail="Volunteer is not available.")

    # Compute route (simulated if Maps not configured)
    route = await compute_route(donation, volunteer)

    delivery = DeliveryAssignment(
        donation_id=donation.id,
        volunteer_id=volunteer.id,
        status=DeliveryStatus.PENDING,
        pickup_address=donation.pickup_address,
        pickup_latitude=donation.pickup_latitude,
        pickup_longitude=donation.pickup_longitude,
        estimated_distance_km=route.get("distance_km"),
        estimated_duration_minutes=route.get("duration_minutes"),
        route_notes=route.get("notes"),
    )
    db.add(delivery)

    donation.status = DonationStatus.ASSIGNED
    h = DonationStatusHistory(
        donation_id=donation.id,
        status=DonationStatus.ASSIGNED,
        changed_by=current_user.id,
        notes=f"Volunteer assigned: {volunteer.id}",
    )
    db.add(h)

    event = DeliveryEvent(
        delivery_id=delivery.id,
        event_type="ASSIGNED",
        created_by=current_user.id,
    )
    db.add(event)

    volunteer.is_available = False  # Mark as busy
    await db.commit()
    await db.refresh(delivery)
    return DeliveryOut.model_validate(delivery)


@router.get("", response_model=List[DeliveryOut])
async def list_deliveries(
    status: Optional[DeliveryStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(DeliveryAssignment)
    if current_user.role == UserRole.VOLUNTEER:
        vol_result = await db.execute(select(Volunteer).where(Volunteer.user_id == current_user.id))
        vol = vol_result.scalar_one_or_none()
        if vol:
            q = q.where(DeliveryAssignment.volunteer_id == vol.id)
    if status:
        q = q.where(DeliveryAssignment.status == status)
    q = q.order_by(DeliveryAssignment.assigned_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return [DeliveryOut.model_validate(d) for d in result.scalars().all()]


@router.get("/{delivery_id}", response_model=DeliveryOut)
async def get_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DeliveryAssignment).where(DeliveryAssignment.id == delivery_id))
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    return DeliveryOut.model_validate(delivery)


@router.post("/{delivery_id}/pickup", response_model=DeliveryOut)
async def confirm_pickup(
    delivery_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Volunteer confirms food pickup."""
    result = await db.execute(select(DeliveryAssignment).where(DeliveryAssignment.id == delivery_id))
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")

    if delivery.status not in [DeliveryStatus.PENDING, DeliveryStatus.ACCEPTED]:
        raise HTTPException(status_code=400, detail="Cannot confirm pickup for this delivery.")

    delivery.status = DeliveryStatus.IN_TRANSIT
    delivery.picked_up_at = datetime.now(timezone.utc)

    # Update donation
    d_result = await db.execute(select(Donation).where(Donation.id == delivery.donation_id))
    donation = d_result.scalar_one_or_none()
    if donation:
        donation.status = DonationStatus.COLLECTED
        donation.collected_at = datetime.now(timezone.utc)

    event = DeliveryEvent(
        delivery_id=delivery.id,
        event_type="PICKUP",
        created_by=current_user.id,
        notes="Food picked up by volunteer.",
    )
    db.add(event)
    await db.commit()
    await db.refresh(delivery)
    return DeliveryOut.model_validate(delivery)


@router.post("/{delivery_id}/complete", response_model=DeliveryOut)
async def complete_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Volunteer confirms successful delivery to NGO."""
    result = await db.execute(select(DeliveryAssignment).where(DeliveryAssignment.id == delivery_id))
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found.")

    if delivery.status != DeliveryStatus.IN_TRANSIT:
        raise HTTPException(status_code=400, detail="Delivery must be in transit to complete.")

    delivery.status = DeliveryStatus.DELIVERED
    delivery.delivered_at = datetime.now(timezone.utc)

    d_result = await db.execute(select(Donation).where(Donation.id == delivery.donation_id))
    donation = d_result.scalar_one_or_none()
    if donation:
        donation.status = DonationStatus.DELIVERED
        donation.delivered_at = datetime.now(timezone.utc)

    # Mark volunteer available again
    v_result = await db.execute(select(Volunteer).where(Volunteer.id == delivery.volunteer_id))
    volunteer = v_result.scalar_one_or_none()
    if volunteer:
        volunteer.is_available = True

    event = DeliveryEvent(
        delivery_id=delivery.id,
        event_type="DELIVERED",
        created_by=current_user.id,
        notes="Food delivered to NGO.",
    )
    db.add(event)
    await db.commit()
    await db.refresh(delivery)
    return DeliveryOut.model_validate(delivery)
