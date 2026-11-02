"""
KindBite Unit Tests — Matching Engine
Validates scoring calculations, hard constraints, and distance penalty.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from app.api.v1.endpoints.matching import haversine_km, score_match
from app.models import Donation, FoodCategory, NGO, StorageCondition


def test_haversine_known_coordinates():
    # Mumbai Bandra to Dadar approx 5.5-6.0 km
    lat1, lon1 = 19.0596, 72.8295  # Bandra
    lat2, lon2 = 19.0178, 72.8478  # Dadar
    dist = haversine_km(lat1, lon1, lat2, lon2)
    assert 4.0 <= dist <= 7.0


def test_hard_constraint_capacity_exceeded():
    now = datetime.now(timezone.utc)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        quantity_kg=250.0,  # 250 kg
        collection_deadline=now + timedelta(hours=3),
    )
    ngo = NGO(
        daily_receiving_capacity_kg=100.0,  # Only 100 kg capacity!
        food_category_preferences=[FoodCategory.COOKED_MEALS.value],
    )

    result = score_match(donation, ngo)
    assert result is None  # Must reject when capacity is exceeded!


def test_matching_score_calculation():
    now = datetime.now(timezone.utc)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        quantity_kg=25.0,
        collection_deadline=now + timedelta(hours=3),
        pickup_latitude=19.0596,
        pickup_longitude=72.8295,
    )
    ngo = NGO(
        daily_receiving_capacity_kg=150.0,
        food_category_preferences=[FoodCategory.COOKED_MEALS.value],
        latitude=19.0415,
        longitude=72.8617,
    )

    match = score_match(donation, ngo)
    assert match is not None
    assert "score" in match
    assert match["score"] > 0.60
    assert "food_compatibility" in match["breakdown"]
    assert match["breakdown"]["food_compatibility"] == 1.0
