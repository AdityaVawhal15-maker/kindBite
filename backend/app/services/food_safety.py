"""
KindBite — Food Safety Assessment Service
IMPORTANT: ML predictions cannot certify food safety.
No AI output overrides a failed safety check.
Implements FSSAI-aligned safety rules (configurable, subject to human review).
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from app.models import Donation, FoodCategory, StorageCondition


# Conservative maximum shelf life by category (hours since preparation)
# These are conservative operational guidelines, NOT legal certifications.
# Subject to human review and FSSAI compliance verification.
SHELF_LIFE_HOURS: Dict[str, int] = {
    FoodCategory.COOKED_MEALS.value: 4,
    FoodCategory.RAW_PRODUCE.value: 24,
    FoodCategory.BAKERY.value: 12,
    FoodCategory.DAIRY.value: 6,
    FoodCategory.BEVERAGES.value: 4,
    FoodCategory.PACKAGED_FOOD.value: 48,  # check labelled expiry
    FoodCategory.SNACKS.value: 24,
    FoodCategory.DESSERTS.value: 8,
    FoodCategory.OTHER.value: 4,
}


async def assess_donation_safety(donation: Donation) -> Dict[str, Any]:
    """
    Run configurable food safety checks.
    Returns a dict for the FoodSafetyCheck record.

    DISCLAIMER:
    This is an automated preliminary assessment only.
    Final food eligibility requires human verification.
    ML predictions do not certify food safety.
    """
    now = datetime.now(timezone.utc)

    # 1. Preparation time check
    max_hours = SHELF_LIFE_HOURS.get(donation.food_category.value, 4)
    if donation.preparation_datetime.tzinfo is None:
        prep_dt = donation.preparation_datetime.replace(tzinfo=timezone.utc)
    else:
        prep_dt = donation.preparation_datetime
    hours_since_prep = (now - prep_dt).total_seconds() / 3600
    preparation_time_ok = hours_since_prep <= max_hours

    # 2. Storage condition check
    storage_condition_ok = True
    if donation.storage_condition == StorageCondition.FROZEN and donation.storage_temp_celsius:
        storage_condition_ok = donation.storage_temp_celsius <= -18.0
    elif donation.storage_condition == StorageCondition.REFRIGERATED and donation.storage_temp_celsius:
        storage_condition_ok = donation.storage_temp_celsius <= 5.0

    # 3. Allergens declared (required for high-risk categories)
    high_allergen_categories = [FoodCategory.BAKERY, FoodCategory.DAIRY, FoodCategory.DESSERTS]
    if donation.food_category in high_allergen_categories:
        allergens_declared = donation.allergens is not None
    else:
        allergens_declared = True  # optional for others

    # 4. Packaging — requires handler_declaration
    packaging_ok = donation.handler_declaration

    # 5. Collection deadline within reasonable window
    if donation.collection_deadline.tzinfo is None:
        deadline = donation.collection_deadline.replace(tzinfo=timezone.utc)
    else:
        deadline = donation.collection_deadline
    within_deadline = deadline > now

    # Overall eligibility: ALL checks must pass
    # IMPORTANT: This is a conservative check. A single failure = ineligible.
    overall_eligible = all([
        preparation_time_ok,
        storage_condition_ok,
        allergens_declared,
        packaging_ok,
        within_deadline,
        donation.safety_confirmed,  # restaurant must explicitly confirm
    ])

    return {
        "preparation_time_ok": preparation_time_ok,
        "storage_condition_ok": storage_condition_ok,
        "allergens_declared": allergens_declared,
        "packaging_ok": packaging_ok,
        "within_deadline": within_deadline,
        "overall_eligible": overall_eligible,
        "assessed_at": now,
        "fssai_compliant": None,  # Requires human review
        "notes": (
            "Automated preliminary assessment. "
            "Final eligibility requires human verification. "
            "FSSAI compliance subject to authorized review."
        ),
    }
