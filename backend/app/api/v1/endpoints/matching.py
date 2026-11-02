"""
KindBite — Intelligent NGO Matching Service & Endpoints

Match Score Formula:
MatchScore = w1*FoodCompatibility + w2*CapacityCompatibility
           + w3*UrgencyCompatibility + w4*RequirementMatch
           + w5*DistancePenalty

Weights are documented and transparent.
Hard constraints are applied before scoring.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_ngo_or_admin
from app.db.session import get_db
from app.models import (
    Donation, DonationMatch, DonationStatus, DonationStatusHistory,
    NGO, Restaurant, User, UserRole,
)
from app.schemas.schemas import MatchRecommendation

router = APIRouter()

# Documented matching weights
MATCH_WEIGHTS = {
    "food_compatibility": 0.35,
    "capacity_compatibility": 0.25,
    "urgency_compatibility": 0.20,
    "requirement_match": 0.15,
    "distance_penalty": 0.05,  # subtract
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def simulated_distance_km(donation: Donation, ngo: NGO) -> float:
    """Use real coords if available, otherwise simulate by pincode proximity."""
    if (donation.pickup_latitude and donation.pickup_longitude
            and ngo.latitude and ngo.longitude):
        return haversine_km(
            donation.pickup_latitude, donation.pickup_longitude,
            ngo.latitude, ngo.longitude,
        )
    # Simulate: same pincode = 2 km, else 15 km
    if donation.pickup_pincode and ngo.pincode:
        if donation.pickup_pincode == ngo.pincode:
            return 2.0
        elif donation.pickup_pincode[:3] == ngo.pincode[:3]:
            return 8.0
    return 15.0


def score_match(donation: Donation, ngo: NGO) -> dict:
    """
    Score a donation-NGO pair. Returns scores and overall match_score.
    Hard constraint: capacity must not be exceeded.
    """
    W = MATCH_WEIGHTS
    breakdown = {}

    # 1. Food compatibility
    food_compat = 0.0
    if ngo.food_category_preferences:
        if donation.food_category.value in ngo.food_category_preferences:
            food_compat = 1.0
        else:
            food_compat = 0.3  # partial credit
    else:
        food_compat = 0.7  # no preference = accepts most things
    breakdown["food_compatibility"] = round(food_compat, 3)

    # 2. Capacity compatibility (HARD CONSTRAINT: donation must fit)
    capacity = float(ngo.daily_receiving_capacity_kg or 999)
    qty = float(donation.quantity_kg)
    if qty > capacity:
        return None  # Hard constraint violated — reject this match
    capacity_score = min(1.0, (capacity - qty) / max(capacity, 1) + 0.5)
    breakdown["capacity_compatibility"] = round(capacity_score, 3)

    # 3. Urgency compatibility (closer to deadline = higher urgency for NGOs with fast pickup)
    now = datetime.now(timezone.utc)
    deadline = donation.collection_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    hours_remaining = (deadline - now).total_seconds() / 3600
    if hours_remaining <= 0:
        return None  # Expired
    urgency_score = max(0.0, min(1.0, hours_remaining / 24))
    breakdown["urgency_compatibility"] = round(urgency_score, 3)

    # 4. Requirement match
    req_score = 0.5  # default
    if ngo.dietary_preferences and donation.dietary_label:
        if donation.dietary_label.value in ngo.dietary_preferences:
            req_score = 1.0
        else:
            req_score = 0.2
    breakdown["requirement_match"] = round(req_score, 3)

    # 5. Distance penalty (normalize over 0-30 km range)
    dist_km = simulated_distance_km(donation, ngo)
    dist_penalty = min(1.0, dist_km / 30.0)
    breakdown["distance_penalty"] = round(dist_penalty, 3)
    breakdown["distance_km"] = round(dist_km, 2)

    # Final score
    score = (
        W["food_compatibility"] * food_compat
        + W["capacity_compatibility"] * capacity_score
        + W["urgency_compatibility"] * urgency_score
        + W["requirement_match"] * req_score
        - W["distance_penalty"] * dist_penalty
    )
    return {"score": round(max(0.0, score), 4), "breakdown": breakdown, "dist_km": dist_km}


@router.post("/recommend", response_model=List[MatchRecommendation])
async def recommend_matches(
    donation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate match recommendations for a donation."""
    d_result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = d_result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if donation.status not in [DonationStatus.PUBLISHED, DonationStatus.MATCHED]:
        raise HTTPException(status_code=400, detail="Donation must be PUBLISHED to match.")

    # Get all active, verified NGOs
    ngos_result = await db.execute(
        select(NGO).where(NGO.is_active == True)
    )
    ngos = ngos_result.scalars().all()

    recommendations = []
    for ngo in ngos:
        result = score_match(donation, ngo)
        if result is None:
            continue  # hard constraint failed

        # Get ngo owner for user info
        ngo_user = await db.execute(select(User).where(User.id == ngo.owner_id))
        ngo_user = ngo_user.scalar_one_or_none()

        recommendations.append(
            MatchRecommendation(
                ngo_id=ngo.id,
                ngo_name=ngo.name,
                match_score=result["score"],
                score_breakdown={
                    "food_compatibility": result["breakdown"]["food_compatibility"],
                    "capacity_compatibility": result["breakdown"]["capacity_compatibility"],
                    "urgency_compatibility": result["breakdown"]["urgency_compatibility"],
                    "requirement_match": result["breakdown"]["requirement_match"],
                    "distance_penalty": result["breakdown"]["distance_penalty"],
                },
                distance_km=result["dist_km"],
                capacity_available_kg=float(ngo.daily_receiving_capacity_kg or 0),
                food_compatible=result["breakdown"]["food_compatibility"] > 0.5,
            )
        )

    # Save recommendations to DB
    for rec in recommendations:
        existing = await db.execute(
            select(DonationMatch).where(
                DonationMatch.donation_id == donation_id,
                DonationMatch.ngo_id == rec.ngo_id,
            )
        )
        if existing.scalar_one_or_none():
            continue
        dm = DonationMatch(
            donation_id=donation_id,
            ngo_id=rec.ngo_id,
            match_score=rec.match_score,
            score_breakdown=rec.score_breakdown,
        )
        db.add(dm)

    await db.commit()

    # Sort by score descending
    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    return recommendations[:10]  # top 10


@router.get("/donation/{donation_id}")
async def get_donation_matches(
    donation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get saved match recommendations for a donation."""
    result = await db.execute(
        select(DonationMatch, NGO)
        .join(NGO, DonationMatch.ngo_id == NGO.id)
        .where(DonationMatch.donation_id == donation_id)
        .order_by(DonationMatch.match_score.desc())
    )
    rows = result.all()
    return [
        {
            "match_id": str(m.id),
            "ngo_id": m.ngo_id,
            "ngo_name": n.name,
            "match_score": m.match_score,
            "score_breakdown": m.score_breakdown,
            "is_selected": m.is_selected,
            "recommended_at": m.recommended_at,
        }
        for m, n in rows
    ]


@router.post("/accept/{donation_id}")
async def ngo_accept_donation(
    donation_id: str,
    current_user: User = Depends(require_ngo_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """NGO accepts a published donation."""
    # Get NGO
    ngo_result = await db.execute(select(NGO).where(NGO.owner_id == current_user.id))
    ngo = ngo_result.scalar_one_or_none()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO profile not found.")

    d_result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = d_result.scalar_one_or_none()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found.")

    if donation.status != DonationStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Donation is not available for acceptance.")

    # Check capacity
    cap = float(ngo.daily_receiving_capacity_kg or 999)
    if float(donation.quantity_kg) > cap:
        raise HTTPException(
            status_code=422,
            detail=f"Donation quantity ({donation.quantity_kg} kg) exceeds your configured capacity ({cap} kg).",
        )

    donation.status = DonationStatus.ACCEPTED
    donation.ngo_id = ngo.id

    h = DonationStatusHistory(
        donation_id=donation.id,
        status=DonationStatus.ACCEPTED,
        changed_by=current_user.id,
        notes=f"Accepted by NGO: {ngo.name}",
    )
    db.add(h)
    await db.commit()
    return {"message": "Donation accepted successfully.", "donation_id": donation_id}
