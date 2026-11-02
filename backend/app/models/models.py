"""
KindBite — SQLAlchemy ORM Models
All tables use proper primary keys, foreign keys, indexes, and timestamps.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


# ── Enumerations ───────────────────────────────────────────

class UserRole(str, enum.Enum):
    RESTAURANT = "RESTAURANT"
    NGO = "NGO"
    VOLUNTEER = "VOLUNTEER"
    ADMIN = "ADMIN"


class AccountStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class DonationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    MATCHED = "MATCHED"
    ACCEPTED = "ACCEPTED"
    ASSIGNED = "ASSIGNED"
    COLLECTED = "COLLECTED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class WasteRisk(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class FoodCategory(str, enum.Enum):
    COOKED_MEALS = "COOKED_MEALS"
    RAW_PRODUCE = "RAW_PRODUCE"
    BAKERY = "BAKERY"
    DAIRY = "DAIRY"
    BEVERAGES = "BEVERAGES"
    PACKAGED_FOOD = "PACKAGED_FOOD"
    SNACKS = "SNACKS"
    DESSERTS = "DESSERTS"
    OTHER = "OTHER"


class DietaryLabel(str, enum.Enum):
    VEG = "VEG"
    NON_VEG = "NON_VEG"
    VEGAN = "VEGAN"
    JAIN = "JAIN"


class StorageCondition(str, enum.Enum):
    ROOM_TEMPERATURE = "ROOM_TEMPERATURE"
    REFRIGERATED = "REFRIGERATED"
    FROZEN = "FROZEN"
    HOT_HOLD = "HOT_HOLD"


# ── Users ─────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.PENDING)
    verification_status = Column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="owner", uselist=False)
    ngo = relationship("NGO", back_populates="owner", uselist=False)
    volunteer = relationship("Volunteer", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor")

    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_status", "status"),
    )


# ── Restaurants ────────────────────────────────────────────

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, default="Mumbai")
    pincode = Column(String(10), nullable=False)
    state = Column(String(100), nullable=False, default="Maharashtra")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    fssai_number = Column(String(50), nullable=True)
    gstin = Column(String(20), nullable=True)
    food_categories = Column(JSONB, nullable=True)  # list of FoodCategory
    opening_hours = Column(JSONB, nullable=True)  # {"mon": {"open": "09:00", "close": "22:00"}, ...}
    is_active = Column(Boolean, nullable=False, default=True)
    verification_status = Column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    owner = relationship("User", back_populates="restaurant")
    food_items = relationship("FoodItem", back_populates="restaurant")
    preparation_records = relationship("PreparationRecord", back_populates="restaurant")
    sales_records = relationship("SalesRecord", back_populates="restaurant")
    donations = relationship("Donation", back_populates="restaurant")
    demand_predictions = relationship("DemandPrediction", back_populates="restaurant")
    surplus_predictions = relationship("SurplusPrediction", back_populates="restaurant")

    __table_args__ = (
        Index("ix_restaurants_city", "city"),
        Index("ix_restaurants_pincode", "pincode"),
    )


# ── NGOs ──────────────────────────────────────────────────

class NGO(Base):
    __tablename__ = "ngos"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    registration_number = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, default="Mumbai")
    pincode = Column(String(10), nullable=False)
    state = Column(String(100), nullable=False, default="Maharashtra")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    # Capacity
    daily_receiving_capacity_kg = Column(Numeric(10, 2), nullable=True)
    storage_capacity_kg = Column(Numeric(10, 2), nullable=True)
    # Preferences
    food_category_preferences = Column(JSONB, nullable=True)
    dietary_preferences = Column(JSONB, nullable=True)
    service_areas = Column(JSONB, nullable=True)  # list of pincodes/areas
    operating_hours = Column(JSONB, nullable=True)
    collection_capabilities = Column(JSONB, nullable=True)  # ["self_pickup", "needs_delivery"]
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    verification_status = Column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    owner = relationship("User", back_populates="ngo")
    requirements = relationship("NGORequirement", back_populates="ngo")
    donations_accepted = relationship("Donation", back_populates="ngo")
    donation_matches = relationship("DonationMatch", back_populates="ngo")

    __table_args__ = (
        Index("ix_ngos_city", "city"),
        Index("ix_ngos_pincode", "pincode"),
    )


class NGORequirement(Base):
    __tablename__ = "ngo_requirements"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    ngo_id = Column(UUID(as_uuid=False), ForeignKey("ngos.id"), nullable=False)
    food_category = Column(Enum(FoodCategory), nullable=False)
    quantity_needed_kg = Column(Numeric(10, 2), nullable=True)
    frequency = Column(String(50), nullable=True)  # daily, weekly
    dietary_label = Column(Enum(DietaryLabel), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    ngo = relationship("NGO", back_populates="requirements")


# ── Volunteers ────────────────────────────────────────────

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, unique=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False, default="Mumbai")
    pincode = Column(String(10), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    vehicle_type = Column(String(50), nullable=True)  # bicycle, motorcycle, car, van
    carrying_capacity_kg = Column(Numeric(10, 2), nullable=True)
    is_available = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    verification_status = Column(
        Enum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    user = relationship("User", back_populates="volunteer")
    deliveries = relationship("DeliveryAssignment", back_populates="volunteer")

    __table_args__ = (
        Index("ix_volunteers_city", "city"),
        Index("ix_volunteers_available", "is_available"),
    )


# ── Food Items ────────────────────────────────────────────

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(Enum(FoodCategory), nullable=False)
    dietary_label = Column(Enum(DietaryLabel), nullable=True)
    unit = Column(String(20), nullable=False, default="kg")
    price_inr = Column(Numeric(10, 2), nullable=True)
    allergens = Column(JSONB, nullable=True)
    storage_condition = Column(Enum(StorageCondition), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    restaurant = relationship("Restaurant", back_populates="food_items")
    preparation_records = relationship("PreparationRecord", back_populates="food_item")
    sales_records = relationship("SalesRecord", back_populates="food_item")

    __table_args__ = (
        Index("ix_food_items_restaurant", "restaurant_id"),
        Index("ix_food_items_category", "category"),
    )


# ── Preparation Records ───────────────────────────────────

class PreparationRecord(Base):
    __tablename__ = "preparation_records"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    food_item_id = Column(UUID(as_uuid=False), ForeignKey("food_items.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    prepared_quantity_kg = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    preparation_start_time = Column(DateTime(timezone=True), nullable=True)
    preparation_end_time = Column(DateTime(timezone=True), nullable=True)
    storage_condition = Column(Enum(StorageCondition), nullable=True)
    expected_selling_period_hours = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    restaurant = relationship("Restaurant", back_populates="preparation_records")
    food_item = relationship("FoodItem", back_populates="preparation_records")

    __table_args__ = (
        Index("ix_prep_records_restaurant_date", "restaurant_id", "date"),
    )


# ── Sales Records ─────────────────────────────────────────

class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    food_item_id = Column(UUID(as_uuid=False), ForeignKey("food_items.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    prepared_quantity_kg = Column(Numeric(10, 3), nullable=True)
    sold_quantity_kg = Column(Numeric(10, 3), nullable=False)
    leftover_quantity_kg = Column(Numeric(10, 3), nullable=True)
    revenue_inr = Column(Numeric(12, 2), nullable=True)
    import_batch_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    restaurant = relationship("Restaurant", back_populates="sales_records")
    food_item = relationship("FoodItem", back_populates="sales_records")

    __table_args__ = (
        Index("ix_sales_restaurant_date", "restaurant_id", "date"),
        Index("ix_sales_food_item", "food_item_id"),
    )


# ── Demand Predictions ────────────────────────────────────

class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    food_item_id = Column(UUID(as_uuid=False), ForeignKey("food_items.id"), nullable=True)
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    predicted_demand_kg = Column(Numeric(10, 3), nullable=False)
    lower_bound_kg = Column(Numeric(10, 3), nullable=True)
    upper_bound_kg = Column(Numeric(10, 3), nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    feature_importances = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    restaurant = relationship("Restaurant", back_populates="demand_predictions")

    __table_args__ = (
        Index("ix_demand_pred_restaurant_date", "restaurant_id", "prediction_date"),
    )


# ── Surplus Predictions ───────────────────────────────────

class SurplusPrediction(Base):
    __tablename__ = "surplus_predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    food_item_id = Column(UUID(as_uuid=False), ForeignKey("food_items.id"), nullable=True)
    preparation_record_id = Column(
        UUID(as_uuid=False), ForeignKey("preparation_records.id"), nullable=True
    )
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    prepared_quantity_kg = Column(Numeric(10, 3), nullable=False)
    predicted_demand_kg = Column(Numeric(10, 3), nullable=False)
    predicted_surplus_kg = Column(Numeric(10, 3), nullable=False)
    predicted_surplus_pct = Column(Float, nullable=True)
    waste_risk = Column(Enum(WasteRisk), nullable=True)
    risk_score = Column(Float, nullable=True)  # 0.0-1.0
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    restaurant = relationship("Restaurant", back_populates="surplus_predictions")

    __table_args__ = (
        Index("ix_surplus_pred_restaurant_date", "restaurant_id", "prediction_date"),
    )


# ── Model Registry ────────────────────────────────────────

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # demand, surplus, risk, matching
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=True)
    dataset_version = Column(String(50), nullable=True)
    training_timestamp = Column(DateTime(timezone=True), nullable=True)
    feature_schema = Column(JSONB, nullable=True)
    evaluation_metrics = Column(JSONB, nullable=True)
    artifact_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    __table_args__ = (
        Index("ix_model_registry_type", "model_type"),
        UniqueConstraint("model_name", "version", name="uq_model_name_version"),
    )


# ── Donations ─────────────────────────────────────────────

class Donation(Base):
    __tablename__ = "donations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    restaurant_id = Column(UUID(as_uuid=False), ForeignKey("restaurants.id"), nullable=False)
    ngo_id = Column(UUID(as_uuid=False), ForeignKey("ngos.id"), nullable=True)

    # Food details
    food_name = Column(String(255), nullable=False)
    food_category = Column(Enum(FoodCategory), nullable=False)
    quantity_kg = Column(Numeric(10, 3), nullable=False)
    servings = Column(Integer, nullable=True)
    dietary_label = Column(Enum(DietaryLabel), nullable=True)
    allergens = Column(JSONB, nullable=True)
    storage_condition = Column(Enum(StorageCondition), nullable=True)
    storage_temp_celsius = Column(Float, nullable=True)
    preparation_datetime = Column(DateTime(timezone=True), nullable=False)
    collection_deadline = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)

    # Pickup location
    pickup_address = Column(Text, nullable=False)
    pickup_city = Column(String(100), nullable=True)
    pickup_pincode = Column(String(10), nullable=True)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)

    # Safety
    safety_confirmed = Column(Boolean, nullable=False, default=False)
    handler_declaration = Column(Boolean, nullable=False, default=False)
    is_eligible = Column(Boolean, nullable=True)  # null = not yet assessed

    # Status
    status = Column(Enum(DonationStatus), nullable=False, default=DonationStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
    published_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    restaurant = relationship("Restaurant", back_populates="donations")
    ngo = relationship("NGO", back_populates="donations_accepted")
    status_history = relationship("DonationStatusHistory", back_populates="donation")
    matches = relationship("DonationMatch", back_populates="donation")
    delivery = relationship("DeliveryAssignment", back_populates="donation", uselist=False)
    safety_check = relationship("FoodSafetyCheck", back_populates="donation", uselist=False)

    __table_args__ = (
        Index("ix_donations_restaurant", "restaurant_id"),
        Index("ix_donations_status", "status"),
        Index("ix_donations_city", "pickup_city"),
        Index("ix_donations_deadline", "collection_deadline"),
    )


class DonationStatusHistory(Base):
    __tablename__ = "donation_status_history"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    donation_id = Column(UUID(as_uuid=False), ForeignKey("donations.id"), nullable=False)
    status = Column(Enum(DonationStatus), nullable=False)
    changed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    donation = relationship("Donation", back_populates="status_history")

    __table_args__ = (Index("ix_donation_status_history_donation", "donation_id"),)


class DonationMatch(Base):
    __tablename__ = "donation_matches"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    donation_id = Column(UUID(as_uuid=False), ForeignKey("donations.id"), nullable=False)
    ngo_id = Column(UUID(as_uuid=False), ForeignKey("ngos.id"), nullable=False)
    match_score = Column(Float, nullable=True)
    score_breakdown = Column(JSONB, nullable=True)
    recommended_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    is_selected = Column(Boolean, nullable=False, default=False)

    donation = relationship("Donation", back_populates="matches")
    ngo = relationship("NGO", back_populates="donation_matches")

    __table_args__ = (
        Index("ix_donation_matches_donation", "donation_id"),
        Index("ix_donation_matches_ngo", "ngo_id"),
    )


# ── Food Safety Checks ────────────────────────────────────

class FoodSafetyCheck(Base):
    __tablename__ = "food_safety_checks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    donation_id = Column(UUID(as_uuid=False), ForeignKey("donations.id"), nullable=False, unique=True)
    preparation_time_ok = Column(Boolean, nullable=True)
    storage_condition_ok = Column(Boolean, nullable=True)
    allergens_declared = Column(Boolean, nullable=True)
    packaging_ok = Column(Boolean, nullable=True)
    within_deadline = Column(Boolean, nullable=True)
    overall_eligible = Column(Boolean, nullable=True)
    assessed_at = Column(DateTime(timezone=True), nullable=True)
    assessed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    fssai_compliant = Column(Boolean, nullable=True)

    donation = relationship("Donation", back_populates="safety_check")

    __table_args__ = (Index("ix_safety_checks_donation", "donation_id"),)


# ── Deliveries ────────────────────────────────────────────

class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    donation_id = Column(UUID(as_uuid=False), ForeignKey("donations.id"), nullable=False, unique=True)
    volunteer_id = Column(UUID(as_uuid=False), ForeignKey("volunteers.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING)
    pickup_address = Column(Text, nullable=True)
    dropoff_address = Column(Text, nullable=True)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    dropoff_latitude = Column(Float, nullable=True)
    dropoff_longitude = Column(Float, nullable=True)
    estimated_distance_km = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    route_notes = Column(Text, nullable=True)  # simulated when Maps not configured
    assigned_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    donation = relationship("Donation", back_populates="delivery")
    volunteer = relationship("Volunteer", back_populates="deliveries")
    events = relationship("DeliveryEvent", back_populates="delivery")

    __table_args__ = (
        Index("ix_deliveries_volunteer", "volunteer_id"),
        Index("ix_deliveries_status", "status"),
    )


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    delivery_id = Column(
        UUID(as_uuid=False), ForeignKey("delivery_assignments.id"), nullable=False
    )
    event_type = Column(String(50), nullable=False)  # ASSIGNED, ACCEPTED, PICKUP, DELIVERED, FAILED
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    delivery = relationship("DeliveryAssignment", back_populates="events")

    __table_args__ = (Index("ix_delivery_events_delivery", "delivery_id"),)


# ── Notifications ─────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    type = Column(String(50), nullable=True)  # donation, delivery, system, verification
    is_read = Column(Boolean, nullable=False, default=False)
    related_id = Column(String(100), nullable=True)  # donation_id, delivery_id, etc.
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user", "user_id"),
        Index("ix_notifications_read", "is_read"),
    )


# ── Audit Logs ────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    actor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    actor = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_actor", "actor_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created", "created_at"),
    )
