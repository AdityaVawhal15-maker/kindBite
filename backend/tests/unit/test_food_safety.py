"""
KindBite Unit Tests — Food Safety Verification
Validates that food safety assessment enforces strict FSSAI rules,
rejects expired / high-temp foods, and that no AI output can override a safety failure.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import pytest

from app.models import Donation, FoodCategory, StorageCondition
from app.services.food_safety import assess_donation_safety


@pytest.mark.asyncio
async def test_fresh_food_with_valid_declarations_passes():
    now = datetime.now(timezone.utc)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        preparation_datetime=now - timedelta(hours=1.5),
        collection_deadline=now + timedelta(hours=2.5),
        storage_condition=StorageCondition.HOT_HOLD,
        storage_temp_celsius=64.0,
        safety_confirmed=True,
        handler_declaration=True,
        allergens=["dairy"],
    )

    result = await assess_donation_safety(donation)

    assert result["preparation_time_ok"] is True
    assert result["storage_condition_ok"] is True
    assert result["allergens_declared"] is True
    assert result["packaging_ok"] is True
    assert result["within_deadline"] is True
    assert result["overall_eligible"] is True


@pytest.mark.asyncio
async def test_expired_prep_time_fails_safety_check():
    now = datetime.now(timezone.utc)
    # Cooked meal prepared 6 hours ago (exceeds 4-hour shelf life limit)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        preparation_datetime=now - timedelta(hours=6),
        collection_deadline=now + timedelta(hours=1),
        storage_condition=StorageCondition.HOT_HOLD,
        storage_temp_celsius=65.0,
        safety_confirmed=True,
        handler_declaration=True,
        allergens=[],
    )

    result = await assess_donation_safety(donation)

    assert result["preparation_time_ok"] is False
    assert result["overall_eligible"] is False


@pytest.mark.asyncio
async def test_refrigerated_food_with_warm_temperature_fails():
    now = datetime.now(timezone.utc)
    # Cold food stored at 12°C (exceeds 5°C safety limit)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        preparation_datetime=now - timedelta(hours=2),
        collection_deadline=now + timedelta(hours=2),
        storage_condition=StorageCondition.REFRIGERATED,
        storage_temp_celsius=12.0,
        safety_confirmed=True,
        handler_declaration=True,
        allergens=[],
    )

    result = await assess_donation_safety(donation)

    assert result["storage_condition_ok"] is False
    assert result["overall_eligible"] is False


@pytest.mark.asyncio
async def test_missing_handler_declaration_fails():
    now = datetime.now(timezone.utc)
    donation = Donation(
        food_category=FoodCategory.COOKED_MEALS,
        preparation_datetime=now - timedelta(hours=1),
        collection_deadline=now + timedelta(hours=2),
        storage_condition=StorageCondition.ROOM_TEMPERATURE,
        safety_confirmed=True,
        handler_declaration=False,  # Chef did not attest safe packaging
        allergens=[],
    )

    result = await assess_donation_safety(donation)

    assert result["packaging_ok"] is False
    assert result["overall_eligible"] is False


@pytest.mark.asyncio
async def test_high_allergen_bakery_without_allergen_declaration_fails():
    now = datetime.now(timezone.utc)
    donation = Donation(
        food_category=FoodCategory.BAKERY,
        preparation_datetime=now - timedelta(hours=2),
        collection_deadline=now + timedelta(hours=4),
        storage_condition=StorageCondition.ROOM_TEMPERATURE,
        safety_confirmed=True,
        handler_declaration=True,
        allergens=None,  # Not declared for high-allergen category
    )

    result = await assess_donation_safety(donation)

    assert result["allergens_declared"] is False
    assert result["overall_eligible"] is False
