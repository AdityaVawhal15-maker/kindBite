"""KindBite — Admin endpoints"""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import (
    AuditLog, Donation, DonationStatus, NGO, Restaurant, User,
    VerificationStatus, Volunteer,
)
from app.schemas.schemas import UserOut
from app.services.audit import record_audit

router = APIRouter()


@router.get("/analytics")
async def admin_analytics(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Platform-wide analytics for administrators."""
    total_users = await db.execute(select(func.count(User.id)))
    total_restaurants = await db.execute(select(func.count(Restaurant.id)))
    total_ngos = await db.execute(select(func.count(NGO.id)))
    total_volunteers = await db.execute(select(func.count(Volunteer.id)))
    total_donations = await db.execute(select(func.count(Donation.id)))
    delivered = await db.execute(
        select(func.count(Donation.id)).where(Donation.status == DonationStatus.DELIVERED)
    )
    total_kg = await db.execute(
        select(func.sum(Donation.quantity_kg)).where(Donation.status == DonationStatus.DELIVERED)
    )

    return {
        "users": {
            "total": total_users.scalar() or 0,
            "restaurants": total_restaurants.scalar() or 0,
            "ngos": total_ngos.scalar() or 0,
            "volunteers": total_volunteers.scalar() or 0,
        },
        "donations": {
            "total": total_donations.scalar() or 0,
            "delivered": delivered.scalar() or 0,
            "total_kg_rescued": float(total_kg.scalar() or 0),
        },
    }


@router.get("/verifications")
async def list_verifications(
    entity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List entities pending verification."""
    results = {}

    if not entity_type or entity_type == "restaurant":
        r = await db.execute(
            select(Restaurant)
            .where(Restaurant.verification_status == VerificationStatus.PENDING)
            .offset(skip).limit(limit)
        )
        results["restaurants"] = [
            {"id": x.id, "name": x.name, "city": x.city, "status": x.verification_status}
            for x in r.scalars().all()
        ]

    if not entity_type or entity_type == "ngo":
        r = await db.execute(
            select(NGO)
            .where(NGO.verification_status == VerificationStatus.PENDING)
            .offset(skip).limit(limit)
        )
        results["ngos"] = [
            {"id": x.id, "name": x.name, "city": x.city, "status": x.verification_status}
            for x in r.scalars().all()
        ]

    return results


@router.post("/verifications/{entity_type}/{entity_id}/approve")
async def approve_entity(
    entity_type: str,
    entity_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    entity = await _get_entity(entity_type, entity_id, db)
    entity.verification_status = VerificationStatus.VERIFIED
    await record_audit(db, actor_id=admin.id, action="VERIFICATION_APPROVED",
                       resource_type=entity_type, resource_id=entity_id)
    await db.commit()
    return {"message": f"{entity_type} {entity_id} verified."}


@router.post("/verifications/{entity_type}/{entity_id}/reject")
async def reject_entity(
    entity_type: str,
    entity_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    entity = await _get_entity(entity_type, entity_id, db)
    entity.verification_status = VerificationStatus.REJECTED
    await record_audit(db, actor_id=admin.id, action="VERIFICATION_REJECTED",
                       resource_type=entity_type, resource_id=entity_id)
    await db.commit()
    return {"message": f"{entity_type} {entity_id} rejected."}


async def _get_entity(entity_type: str, entity_id: str, db):
    if entity_type == "restaurant":
        r = await db.execute(select(Restaurant).where(Restaurant.id == entity_id))
        entity = r.scalar_one_or_none()
    elif entity_type == "ngo":
        r = await db.execute(select(NGO).where(NGO.id == entity_id))
        entity = r.scalar_one_or_none()
    elif entity_type == "volunteer":
        r = await db.execute(select(Volunteer).where(Volunteer.id == entity_id))
        entity = r.scalar_one_or_none()
    else:
        raise HTTPException(status_code=400, detail="Unknown entity type.")
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type} not found.")
    return entity


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    action: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Return audit logs. Admin only."""
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    if action:
        q = q.where(AuditLog.action == action)
    result = await db.execute(q)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "created_at": log.created_at,
        }
        for log in logs
    ]
