"""
KindBite — Pydantic Schemas for request/response validation
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.models import (
    AccountStatus, DietaryLabel, DonationStatus, FoodCategory,
    StorageCondition, UserRole, VerificationStatus, WasteRisk, DeliveryStatus,
)


# ── Shared base ────────────────────────────────────────────

class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── Auth schemas ───────────────────────────────────────────

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-]{7,20}$")
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    role: UserRole
    organization_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, pattern=r"^[0-9]{6}$")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    status: AccountStatus
    verification_status: VerificationStatus
    created_at: Optional[datetime] = None


# ── Restaurant schemas ─────────────────────────────────────

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    address: str
    city: str = "Mumbai"
    pincode: str = Field(..., pattern=r"^[0-9]{6}$")
    state: str = "Maharashtra"
    phone: Optional[str] = None
    website: Optional[str] = None
    fssai_number: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    food_categories: Optional[List[str]] = None
    opening_hours: Optional[Dict[str, Any]] = None


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    food_categories: Optional[List[str]] = None
    opening_hours: Optional[Dict[str, Any]] = None


class RestaurantOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    address: str
    city: str
    pincode: str
    state: str
    phone: Optional[str] = None
    website: Optional[str] = None
    fssai_number: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    food_categories: Optional[List[str]] = None
    opening_hours: Optional[Dict[str, Any]] = None
    verification_status: VerificationStatus
    is_active: bool
    created_at: Optional[datetime] = None


# ── Food Item schemas ──────────────────────────────────────

class FoodItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: FoodCategory
    dietary_label: Optional[DietaryLabel] = None
    unit: str = "kg"
    price_inr: Optional[float] = None
    allergens: Optional[List[str]] = None
    storage_condition: Optional[StorageCondition] = None


class FoodItemOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    name: str
    category: FoodCategory
    dietary_label: Optional[DietaryLabel] = None
    unit: str
    price_inr: Optional[float] = None
    allergens: Optional[List[str]] = None
    storage_condition: Optional[StorageCondition] = None
    is_active: bool


# ── Sales schemas ──────────────────────────────────────────

class SalesRecordCreate(BaseModel):
    food_item_id: str
    date: datetime
    prepared_quantity_kg: Optional[float] = Field(None, ge=0)
    sold_quantity_kg: float = Field(..., ge=0)
    leftover_quantity_kg: Optional[float] = Field(None, ge=0)
    revenue_inr: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class SalesRecordOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    food_item_id: str
    date: datetime
    prepared_quantity_kg: Optional[float] = None
    sold_quantity_kg: float
    leftover_quantity_kg: Optional[float] = None
    revenue_inr: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ── Preparation schemas ────────────────────────────────────

class PreparationCreate(BaseModel):
    food_item_id: str
    date: datetime
    prepared_quantity_kg: float = Field(..., gt=0)
    storage_condition: Optional[StorageCondition] = None
    expected_selling_period_hours: Optional[int] = Field(None, ge=1, le=72)
    notes: Optional[str] = None


class PreparationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    food_item_id: str
    date: datetime
    prepared_quantity_kg: float
    storage_condition: Optional[StorageCondition] = None
    expected_selling_period_hours: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ── Prediction schemas ─────────────────────────────────────

class DemandPredictionRequest(BaseModel):
    food_item_id: Optional[str] = None
    prediction_date: datetime


class DemandPredictionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    food_item_id: Optional[str] = None
    prediction_date: datetime
    predicted_demand_kg: float
    lower_bound_kg: Optional[float] = None
    upper_bound_kg: Optional[float] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    feature_importances: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class SurplusPredictionRequest(BaseModel):
    food_item_id: Optional[str] = None
    preparation_record_id: Optional[str] = None
    prediction_date: datetime
    prepared_quantity_kg: float = Field(..., gt=0)


class SurplusPredictionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    food_item_id: Optional[str] = None
    prediction_date: datetime
    prepared_quantity_kg: float
    predicted_demand_kg: float
    predicted_surplus_kg: float
    predicted_surplus_pct: Optional[float] = None
    waste_risk: Optional[WasteRisk] = None
    risk_score: Optional[float] = None
    model_name: Optional[str] = None
    created_at: Optional[datetime] = None


# ── Donation schemas ───────────────────────────────────────

class DonationCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=255)
    food_category: FoodCategory
    quantity_kg: float = Field(..., gt=0)
    servings: Optional[int] = Field(None, ge=1)
    dietary_label: Optional[DietaryLabel] = None
    allergens: Optional[List[str]] = None
    storage_condition: Optional[StorageCondition] = None
    storage_temp_celsius: Optional[float] = None
    preparation_datetime: datetime
    collection_deadline: datetime
    notes: Optional[str] = None
    pickup_address: str
    pickup_city: Optional[str] = None
    pickup_pincode: Optional[str] = None
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    safety_confirmed: bool = False
    handler_declaration: bool = False

    @model_validator(mode="after")
    def deadline_after_prep(self):
        if self.collection_deadline <= self.preparation_datetime:
            raise ValueError("Collection deadline must be after preparation time")
        return self


class DonationUpdate(BaseModel):
    quantity_kg: Optional[float] = Field(None, gt=0)
    servings: Optional[int] = None
    collection_deadline: Optional[datetime] = None
    notes: Optional[str] = None
    pickup_address: Optional[str] = None


class DonationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    restaurant_id: str
    ngo_id: Optional[str] = None
    food_name: str
    food_category: FoodCategory
    quantity_kg: float
    servings: Optional[int] = None
    dietary_label: Optional[DietaryLabel] = None
    allergens: Optional[List[str]] = None
    storage_condition: Optional[StorageCondition] = None
    preparation_datetime: datetime
    collection_deadline: datetime
    pickup_address: str
    pickup_city: Optional[str] = None
    status: DonationStatus
    safety_confirmed: bool
    handler_declaration: bool
    is_eligible: Optional[bool] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── NGO schemas ────────────────────────────────────────────

class NGOCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    address: str
    city: str = "Mumbai"
    pincode: str = Field(..., pattern=r"^[0-9]{6}$")
    state: str = "Maharashtra"
    phone: Optional[str] = None
    registration_number: Optional[str] = None
    description: Optional[str] = None
    daily_receiving_capacity_kg: Optional[float] = Field(None, gt=0)
    storage_capacity_kg: Optional[float] = Field(None, gt=0)
    food_category_preferences: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    collection_capabilities: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class NGOUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    daily_receiving_capacity_kg: Optional[float] = None
    storage_capacity_kg: Optional[float] = None
    food_category_preferences: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    collection_capabilities: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class NGOOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    address: str
    city: str
    pincode: str
    state: str
    phone: Optional[str] = None
    registration_number: Optional[str] = None
    description: Optional[str] = None
    daily_receiving_capacity_kg: Optional[float] = None
    storage_capacity_kg: Optional[float] = None
    food_category_preferences: Optional[List[str]] = None
    dietary_preferences: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    collection_capabilities: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    verification_status: VerificationStatus
    is_active: bool
    created_at: Optional[datetime] = None


# ── Volunteer schemas ──────────────────────────────────────

class VolunteerCreate(BaseModel):
    address: Optional[str] = None
    city: str = "Mumbai"
    pincode: Optional[str] = None
    vehicle_type: Optional[str] = None
    carrying_capacity_kg: Optional[float] = Field(None, gt=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VolunteerUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    vehicle_type: Optional[str] = None
    carrying_capacity_kg: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VolunteerOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    city: str
    vehicle_type: Optional[str] = None
    carrying_capacity_kg: Optional[float] = None
    is_available: bool
    verification_status: VerificationStatus
    created_at: Optional[datetime] = None


# ── Delivery schemas ───────────────────────────────────────

class DeliveryAssignRequest(BaseModel):
    donation_id: str
    volunteer_id: str


class DeliveryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    donation_id: str
    volunteer_id: str
    status: DeliveryStatus
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    estimated_distance_km: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    route_notes: Optional[str] = None
    assigned_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


# ── Match schemas ──────────────────────────────────────────

class MatchRecommendation(BaseModel):
    ngo_id: str
    ngo_name: str
    match_score: float
    score_breakdown: Dict[str, float]
    distance_km: Optional[float] = None
    capacity_available_kg: Optional[float] = None
    food_compatible: bool


# ── Notification schemas ───────────────────────────────────

class NotificationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str
    body: str
    type: Optional[str] = None
    is_read: bool
    related_id: Optional[str] = None
    created_at: Optional[datetime] = None


# ── Pagination ─────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# ── Error schemas ──────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
