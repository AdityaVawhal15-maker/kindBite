"""
KindBite — Comprehensive Database Seeder
Seeds users, restaurants, NGOs, volunteers, food items, historical sales,
preparations, donations, safety checks, deliveries, notifications, and audit logs.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import random
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models import (
    AccountStatus,
    AuditLog,
    DeliveryAssignment,
    DeliveryEvent,
    DeliveryStatus,
    DietaryLabel,
    Donation,
    DonationMatch,
    DonationStatus,
    DonationStatusHistory,
    FoodCategory,
    FoodItem,
    FoodSafetyCheck,
    ModelRegistry,
    NGO,
    NGORequirement,
    Notification,
    PreparationRecord,
    Restaurant,
    SalesRecord,
    StorageCondition,
    User,
    UserRole,
    VerificationStatus,
    Volunteer,
    WasteRisk,
)

DEFAULT_PASSWORD = get_password_hash("KindBite@2026")
NOW = datetime.now(timezone.utc)


async def seed():
    print("🌱 Starting KindBite database seeding...")
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        existing_admin = await db.execute(
            select(User).where(User.email == "admin@kindbite.in")
        )
        if existing_admin.scalar_one_or_none():
            print("⚠️ Admin user exists. Clearing existing data for a fresh seed...")
            for table in [
                DeliveryEvent,
                DeliveryAssignment,
                FoodSafetyCheck,
                DonationMatch,
                DonationStatusHistory,
                Donation,
                SalesRecord,
                PreparationRecord,
                FoodItem,
                NGORequirement,
                Volunteer,
                NGO,
                Restaurant,
                Notification,
                AuditLog,
                User,
            ]:
                await db.execute(delete(table))
            await db.commit()
            print("🧹 Cleaned existing tables.")

        # ── 1. Create Users ──────────────────────────────────
        print("👤 Creating core users...")
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@kindbite.in",
            phone="+919820000001",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Aarav Mehta (Admin)",
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add(admin_user)

        # Restaurant owners
        rest_user_1 = User(
            id=str(uuid.uuid4()),
            email="spicecraft@kindbite.in",
            phone="+919820000002",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Chef Vikram Oberoi",
            role=UserRole.RESTAURANT,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_user_2 = User(
            id=str(uuid.uuid4()),
            email="bombaybistro@kindbite.in",
            phone="+919820000003",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Farhan Merchant",
            role=UserRole.RESTAURANT,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_user_3 = User(
            id=str(uuid.uuid4()),
            email="tandoornights@kindbite.in",
            phone="+919820000004",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Sukhbir Singh",
            role=UserRole.RESTAURANT,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_user_4 = User(
            id=str(uuid.uuid4()),
            email="greenleaf@kindbite.in",
            phone="+919820000005",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Ananya Joshi",
            role=UserRole.RESTAURANT,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([rest_user_1, rest_user_2, rest_user_3, rest_user_4])

        # NGO owners
        ngo_user_1 = User(
            id=str(uuid.uuid4()),
            email="annadaata@kindbite.in",
            phone="+919820000010",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Sister Teresa Fernandes",
            role=UserRole.NGO,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        ngo_user_2 = User(
            id=str(uuid.uuid4()),
            email="hopefeed@kindbite.in",
            phone="+919820000011",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Rashid Qureshi",
            role=UserRole.NGO,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        ngo_user_3 = User(
            id=str(uuid.uuid4()),
            email="rotaryroti@kindbite.in",
            phone="+919820000012",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Dr. Suresh Shenoy",
            role=UserRole.NGO,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([ngo_user_1, ngo_user_2, ngo_user_3])

        # Volunteers
        vol_user_1 = User(
            id=str(uuid.uuid4()),
            email="rahul.sharma@kindbite.in",
            phone="+919820000020",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Rahul Sharma",
            role=UserRole.VOLUNTEER,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        vol_user_2 = User(
            id=str(uuid.uuid4()),
            email="priya.patel@kindbite.in",
            phone="+919820000021",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Priya Patel",
            role=UserRole.VOLUNTEER,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        vol_user_3 = User(
            id=str(uuid.uuid4()),
            email="amit.verma@kindbite.in",
            phone="+919820000022",
            hashed_password=DEFAULT_PASSWORD,
            full_name="Amit Verma",
            role=UserRole.VOLUNTEER,
            status=AccountStatus.ACTIVE,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([vol_user_1, vol_user_2, vol_user_3])
        await db.flush()

        # ── 2. Create Restaurants ────────────────────────────
        print("🏪 Creating restaurant profiles...")
        rest_1 = Restaurant(
            id=str(uuid.uuid4()),
            owner_id=rest_user_1.id,
            name="The Spice Craft",
            description="Contemporary Indian cuisine specializing in slow-cooked gravies, biryanis, and tandoor bread.",
            address="Plot 42, Hill Road, Bandra West",
            city="Mumbai",
            pincode="400050",
            state="Maharashtra",
            latitude=19.0596,
            longitude=72.8295,
            phone="+912226451234",
            website="https://spicecraft.in",
            fssai_number="11521012000456",
            gstin="27ABCDE1234F1Z5",
            food_categories=[FoodCategory.COOKED_MEALS.value, FoodCategory.BAKERY.value],
            opening_hours={"open": "11:00", "close": "23:30"},
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_2 = Restaurant(
            id=str(uuid.uuid4()),
            owner_id=rest_user_2.id,
            name="Bombay Bistro & Cafe",
            description="Artisan cafe serving fresh sourdough, quiches, breakfast platters, and European mains.",
            address="14, Mandlik Road, Colaba",
            city="Mumbai",
            pincode="400001",
            state="Maharashtra",
            latitude=18.9220,
            longitude=72.8347,
            phone="+912222854321",
            website="https://bombaybistro.com",
            fssai_number="11522001000789",
            gstin="27FGHIJ5678K2Z8",
            food_categories=[FoodCategory.BAKERY.value, FoodCategory.COOKED_MEALS.value, FoodCategory.DESSERTS.value],
            opening_hours={"open": "08:30", "close": "22:00"},
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_3 = Restaurant(
            id=str(uuid.uuid4()),
            owner_id=rest_user_3.id,
            name="Tandoor Nights",
            description="Traditional Punjabi and Mughlai dining known for rich curries, kebabs, and large party buffets.",
            address="Near Metro Station, Chakala, Andheri East",
            city="Mumbai",
            pincode="400093",
            state="Maharashtra",
            latitude=19.1136,
            longitude=72.8697,
            phone="+912228389900",
            website="https://tandoornights.in",
            fssai_number="11520034000912",
            food_categories=[FoodCategory.COOKED_MEALS.value],
            opening_hours={"open": "12:00", "close": "00:00"},
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        rest_4 = Restaurant(
            id=str(uuid.uuid4()),
            owner_id=rest_user_4.id,
            name="Green Leaf Organics",
            description="Pure vegetarian farm-to-table salads, grain bowls, and wholesome South/North Indian thalis.",
            address="Gulmohar Cross Road 7, Juhu",
            city="Mumbai",
            pincode="400049",
            state="Maharashtra",
            latitude=19.1075,
            longitude=72.8263,
            phone="+912226207766",
            website="https://greenleaforganics.in",
            fssai_number="11523045000321",
            food_categories=[FoodCategory.COOKED_MEALS.value, FoodCategory.RAW_PRODUCE.value],
            opening_hours={"open": "10:00", "close": "22:30"},
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([rest_1, rest_2, rest_3, rest_4])
        await db.flush()

        # ── 3. Create NGOs ───────────────────────────────────
        print("🤝 Creating NGO profiles...")
        ngo_1 = NGO(
            id=str(uuid.uuid4()),
            owner_id=ngo_user_1.id,
            name="Annadaata Food Foundation",
            description="Operating soup kitchens and community distribution centers feeding daily wage workers and shelter homes.",
            registration_number="MH/MUM/2015/F-48291",
            address="Behind Sion Hospital, Sion East",
            city="Mumbai",
            pincode="400022",
            state="Maharashtra",
            latitude=19.0415,
            longitude=72.8617,
            phone="+912224018899",
            website="https://annadaatafoundation.org",
            daily_receiving_capacity_kg=250.0,
            storage_capacity_kg=150.0,
            food_category_preferences=[FoodCategory.COOKED_MEALS.value, FoodCategory.BAKERY.value],
            dietary_preferences=[DietaryLabel.VEG.value, DietaryLabel.NON_VEG.value],
            service_areas=["400022", "400017", "400019", "400024"],
            collection_capabilities=["self_pickup", "needs_delivery"],
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        ngo_2 = NGO(
            id=str(uuid.uuid4()),
            owner_id=ngo_user_2.id,
            name="Hope For Hunger Shelter",
            description="Dedicated shelter providing nutritious meals to underprivileged children and families in suburban Mumbai.",
            registration_number="MH/MUM/2018/F-63102",
            address="LBS Marg, Kurla West",
            city="Mumbai",
            pincode="400070",
            state="Maharashtra",
            latitude=19.0726,
            longitude=72.8845,
            phone="+912225034455",
            daily_receiving_capacity_kg=180.0,
            storage_capacity_kg=80.0,
            food_category_preferences=[FoodCategory.COOKED_MEALS.value, FoodCategory.RAW_PRODUCE.value],
            dietary_preferences=[DietaryLabel.VEG.value],
            service_areas=["400070", "400071", "400086"],
            collection_capabilities=["needs_delivery"],
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        ngo_3 = NGO(
            id=str(uuid.uuid4()),
            owner_id=ngo_user_3.id,
            name="Rotary Community Kitchen",
            description="Centralized community kitchen preparing and distributing wholesome breakfast and dinner parcels.",
            registration_number="MH/MUM/2012/F-31940",
            address="Dr. Babasaheb Ambedkar Road, Dadar East",
            city="Mumbai",
            pincode="400014",
            state="Maharashtra",
            latitude=19.0178,
            longitude=72.8478,
            phone="+912224147788",
            daily_receiving_capacity_kg=350.0,
            storage_capacity_kg=200.0,
            food_category_preferences=[FoodCategory.COOKED_MEALS.value, FoodCategory.BAKERY.value, FoodCategory.PACKAGED_FOOD.value],
            dietary_preferences=[DietaryLabel.VEG.value, DietaryLabel.JAIN.value],
            service_areas=["400014", "400028", "400016"],
            collection_capabilities=["self_pickup", "needs_delivery"],
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([ngo_1, ngo_2, ngo_3])
        await db.flush()

        # NGO Requirements
        req1 = NGORequirement(
            id=str(uuid.uuid4()),
            ngo_id=ngo_1.id,
            food_category=FoodCategory.COOKED_MEALS,
            quantity_needed_kg=80.0,
            frequency="daily",
            dietary_label=DietaryLabel.VEG,
            notes="Hot cooked lunch/dinner for 100 people daily.",
        )
        req2 = NGORequirement(
            id=str(uuid.uuid4()),
            ngo_id=ngo_2.id,
            food_category=FoodCategory.BAKERY,
            quantity_needed_kg=40.0,
            frequency="daily",
            dietary_label=DietaryLabel.VEG,
            notes="Breads, buns, or sandwiches for evening snacks.",
        )
        db.add_all([req1, req2])

        # ── 4. Create Volunteers ─────────────────────────────
        print("🚴 Creating volunteer profiles...")
        vol_1 = Volunteer(
            id=str(uuid.uuid4()),
            user_id=vol_user_1.id,
            address="Pali Hill, Bandra West",
            city="Mumbai",
            pincode="400050",
            latitude=19.0620,
            longitude=72.8270,
            vehicle_type="motorcycle",
            carrying_capacity_kg=25.0,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        vol_2 = Volunteer(
            id=str(uuid.uuid4()),
            user_id=vol_user_2.id,
            address="Lokhandwala Complex, Andheri West",
            city="Mumbai",
            pincode="400053",
            latitude=19.1410,
            longitude=72.8280,
            vehicle_type="car",
            carrying_capacity_kg=80.0,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        vol_3 = Volunteer(
            id=str(uuid.uuid4()),
            user_id=vol_user_3.id,
            address="Shivaji Park, Dadar",
            city="Mumbai",
            pincode="400028",
            latitude=19.0260,
            longitude=72.8380,
            vehicle_type="scooter",
            carrying_capacity_kg=20.0,
            is_available=True,
            verification_status=VerificationStatus.VERIFIED,
            is_active=True,
        )
        db.add_all([vol_1, vol_2, vol_3])
        await db.flush()

        # ── 5. Create Food Items ─────────────────────────────
        print("🍲 Creating restaurant menu items...")
        food_items_data = [
            # Spice Craft
            (rest_1.id, "Dum Pukht Veg Biryani", FoodCategory.COOKED_MEALS, DietaryLabel.VEG, "kg", 320.0, ["dairy"], StorageCondition.HOT_HOLD),
            (rest_1.id, "Paneer Butter Masala", FoodCategory.COOKED_MEALS, DietaryLabel.VEG, "kg", 380.0, ["dairy", "nuts"], StorageCondition.HOT_HOLD),
            (rest_1.id, "Dal Makhani", FoodCategory.COOKED_MEALS, DietaryLabel.VEG, "kg", 260.0, ["dairy"], StorageCondition.HOT_HOLD),
            (rest_1.id, "Butter Naan & Roti Assortment", FoodCategory.BAKERY, DietaryLabel.VEG, "kg", 180.0, ["gluten", "dairy"], StorageCondition.ROOM_TEMPERATURE),
            # Bombay Bistro
            (rest_2.id, "Artisan Sourdough Loaves", FoodCategory.BAKERY, DietaryLabel.VEGAN, "kg", 220.0, ["gluten"], StorageCondition.ROOM_TEMPERATURE),
            (rest_2.id, "Creamy Mushroom Penne", FoodCategory.COOKED_MEALS, DietaryLabel.VEG, "kg", 340.0, ["gluten", "dairy"], StorageCondition.HOT_HOLD),
            (rest_2.id, "Dark Chocolate Walnut Brownies", FoodCategory.DESSERTS, DietaryLabel.VEG, "kg", 450.0, ["gluten", "dairy", "nuts"], StorageCondition.ROOM_TEMPERATURE),
            # Tandoor Nights
            (rest_3.id, "Chicken Tikka Masala", FoodCategory.COOKED_MEALS, DietaryLabel.NON_VEG, "kg", 420.0, ["dairy"], StorageCondition.HOT_HOLD),
            (rest_3.id, "Subz Korma", FoodCategory.COOKED_MEALS, DietaryLabel.VEG, "kg", 290.0, ["nuts", "dairy"], StorageCondition.HOT_HOLD),
            # Green Leaf Organics
            (rest_4.id, "Quinoa & Roasted Veg Bowl", FoodCategory.COOKED_MEALS, DietaryLabel.VEGAN, "kg", 310.0, [], StorageCondition.REFRIGERATED),
            (rest_4.id, "Sprouted Moong Salad", FoodCategory.RAW_PRODUCE, DietaryLabel.VEGAN, "kg", 180.0, [], StorageCondition.REFRIGERATED),
        ]

        food_items: list[FoodItem] = []
        for r_id, name, cat, diet, unit, price, allergens, storage in food_items_data:
            fi = FoodItem(
                id=str(uuid.uuid4()),
                restaurant_id=r_id,
                name=name,
                category=cat,
                dietary_label=diet,
                unit=unit,
                price_inr=price,
                allergens=allergens,
                storage_condition=storage,
                is_active=True,
            )
            food_items.append(fi)
            db.add(fi)
        await db.flush()

        # ── 6. Historical Sales & Preparations (60 Days) ─────
        print("📊 Generating 60 days of historical sales and preparation logs...")
        sales_records = []
        prep_records = []
        random.seed(42)

        for day_offset in range(60, 0, -1):
            record_date = NOW - timedelta(days=day_offset)
            is_weekend = record_date.weekday() >= 5
            # Friday/Saturday peak factor
            multiplier = 1.35 if is_weekend else 1.0

            for fi in food_items[:6]:  # seed 6 primary items across restaurants
                base_prep = random.uniform(18.0, 32.0) * multiplier
                # demand typically 80% - 95% of prep, occasionally low (rain/lull) -> surplus
                sales_ratio = random.uniform(0.72, 0.96)
                sold_qty = round(base_prep * sales_ratio, 2)
                leftover_qty = round(base_prep - sold_qty, 2)

                prep = PreparationRecord(
                    id=str(uuid.uuid4()),
                    restaurant_id=fi.restaurant_id,
                    food_item_id=fi.id,
                    date=record_date,
                    prepared_quantity_kg=round(base_prep, 2),
                    unit="kg",
                    storage_condition=fi.storage_condition,
                    expected_selling_period_hours=6,
                )
                prep_records.append(prep)

                sale = SalesRecord(
                    id=str(uuid.uuid4()),
                    restaurant_id=fi.restaurant_id,
                    food_item_id=fi.id,
                    date=record_date,
                    prepared_quantity_kg=round(base_prep, 2),
                    sold_quantity_kg=sold_qty,
                    leftover_quantity_kg=leftover_qty,
                    revenue_inr=round(sold_qty * float(fi.price_inr or 300), 2),
                )
                sales_records.append(sale)

        db.add_all(prep_records)
        db.add_all(sales_records)
        await db.flush()

        # ── 7. Seed Real Donations Across All Lifecycle States ─
        print("🍱 Creating realistic donations across lifecycle states...")

        # A. Completed & Delivered Donation 1 (5 days ago)
        d1 = Donation(
            id=str(uuid.uuid4()),
            restaurant_id=rest_1.id,
            ngo_id=ngo_1.id,
            food_name="Dum Pukht Veg Biryani & Raita",
            food_category=FoodCategory.COOKED_MEALS,
            quantity_kg=18.5,
            servings=45,
            dietary_label=DietaryLabel.VEG,
            allergens=["dairy"],
            storage_condition=StorageCondition.HOT_HOLD,
            storage_temp_celsius=64.0,
            preparation_datetime=NOW - timedelta(days=5, hours=6),
            collection_deadline=NOW - timedelta(days=5, hours=2),
            pickup_address=rest_1.address,
            pickup_city="Mumbai",
            pickup_pincode="400050",
            pickup_latitude=rest_1.latitude,
            pickup_longitude=rest_1.longitude,
            safety_confirmed=True,
            handler_declaration=True,
            is_eligible=True,
            status=DonationStatus.DELIVERED,
            created_at=NOW - timedelta(days=5, hours=6),
            published_at=NOW - timedelta(days=5, hours=5, minutes=45),
            collected_at=NOW - timedelta(days=5, hours=3, minutes=30),
            delivered_at=NOW - timedelta(days=5, hours=2, minutes=45),
        )
        db.add(d1)
        await db.flush()

        # Safety Check for d1
        sc1 = FoodSafetyCheck(
            id=str(uuid.uuid4()),
            donation_id=d1.id,
            preparation_time_ok=True,
            storage_condition_ok=True,
            allergens_declared=True,
            packaging_ok=True,
            within_deadline=True,
            overall_eligible=True,
            assessed_at=NOW - timedelta(days=5, hours=5, minutes=40),
            assessed_by=rest_user_1.id,
            notes="Hot holding maintained at 64°C. Sealed stainless insulated containers used.",
            fssai_compliant=True,
        )
        # Delivery for d1
        deliv1 = DeliveryAssignment(
            id=str(uuid.uuid4()),
            donation_id=d1.id,
            volunteer_id=vol_1.id,
            status=DeliveryStatus.DELIVERED,
            pickup_address=rest_1.address,
            dropoff_address=ngo_1.address,
            pickup_latitude=rest_1.latitude,
            pickup_longitude=rest_1.longitude,
            dropoff_latitude=ngo_1.latitude,
            dropoff_longitude=ngo_1.longitude,
            estimated_distance_km=6.4,
            estimated_duration_minutes=24,
            assigned_at=NOW - timedelta(days=5, hours=4),
            accepted_at=NOW - timedelta(days=5, hours=3, minutes=50),
            picked_up_at=NOW - timedelta(days=5, hours=3, minutes=30),
            delivered_at=NOW - timedelta(days=5, hours=2, minutes=45),
            notes="Smooth handoff, temperature verified on delivery.",
        )
        db.add_all([sc1, deliv1])

        # B. Completed & Delivered Donation 2 (2 days ago)
        d2 = Donation(
            id=str(uuid.uuid4()),
            restaurant_id=rest_2.id,
            ngo_id=ngo_2.id,
            food_name="Assorted French Baguettes & Croissants",
            food_category=FoodCategory.BAKERY,
            quantity_kg=12.0,
            servings=35,
            dietary_label=DietaryLabel.VEG,
            allergens=["gluten", "dairy"],
            storage_condition=StorageCondition.ROOM_TEMPERATURE,
            storage_temp_celsius=24.0,
            preparation_datetime=NOW - timedelta(days=2, hours=8),
            collection_deadline=NOW - timedelta(days=2, hours=2),
            pickup_address=rest_2.address,
            pickup_city="Mumbai",
            pickup_pincode="400001",
            pickup_latitude=rest_2.latitude,
            pickup_longitude=rest_2.longitude,
            safety_confirmed=True,
            handler_declaration=True,
            is_eligible=True,
            status=DonationStatus.DELIVERED,
            created_at=NOW - timedelta(days=2, hours=8),
            published_at=NOW - timedelta(days=2, hours=7, minutes=30),
            collected_at=NOW - timedelta(days=2, hours=4),
            delivered_at=NOW - timedelta(days=2, hours=3, minutes=15),
        )
        db.add(d2)
        await db.flush()

        sc2 = FoodSafetyCheck(
            id=str(uuid.uuid4()),
            donation_id=d2.id,
            preparation_time_ok=True,
            storage_condition_ok=True,
            allergens_declared=True,
            packaging_ok=True,
            within_deadline=True,
            overall_eligible=True,
            assessed_at=NOW - timedelta(days=2, hours=7, minutes=25),
            assessed_by=rest_user_2.id,
            notes="Baked fresh in morning batch, individually wrapped in food-grade kraft paper bags.",
            fssai_compliant=True,
        )
        deliv2 = DeliveryAssignment(
            id=str(uuid.uuid4()),
            donation_id=d2.id,
            volunteer_id=vol_3.id,
            status=DeliveryStatus.DELIVERED,
            pickup_address=rest_2.address,
            dropoff_address=ngo_2.address,
            pickup_latitude=rest_2.latitude,
            pickup_longitude=rest_2.longitude,
            dropoff_latitude=ngo_2.latitude,
            dropoff_longitude=ngo_2.longitude,
            estimated_distance_km=14.2,
            estimated_duration_minutes=38,
            assigned_at=NOW - timedelta(days=2, hours=5),
            accepted_at=NOW - timedelta(days=2, hours=4, minutes=45),
            picked_up_at=NOW - timedelta(days=2, hours=4),
            delivered_at=NOW - timedelta(days=2, hours=3, minutes=15),
        )
        db.add_all([sc2, deliv2])

        # C. Active Donation — PUBLISHED (Ready for NGO match)
        d3 = Donation(
            id=str(uuid.uuid4()),
            restaurant_id=rest_1.id,
            ngo_id=None,
            food_name="Paneer Butter Masala & Steamed Jeera Rice",
            food_category=FoodCategory.COOKED_MEALS,
            quantity_kg=14.0,
            servings=35,
            dietary_label=DietaryLabel.VEG,
            allergens=["dairy", "nuts"],
            storage_condition=StorageCondition.HOT_HOLD,
            storage_temp_celsius=65.0,
            preparation_datetime=NOW - timedelta(hours=2),
            collection_deadline=NOW + timedelta(hours=3),
            pickup_address=rest_1.address,
            pickup_city="Mumbai",
            pickup_pincode="400050",
            pickup_latitude=rest_1.latitude,
            pickup_longitude=rest_1.longitude,
            safety_confirmed=True,
            handler_declaration=True,
            is_eligible=True,
            status=DonationStatus.PUBLISHED,
            created_at=NOW - timedelta(minutes=45),
            published_at=NOW - timedelta(minutes=30),
        )
        db.add(d3)
        await db.flush()

        sc3 = FoodSafetyCheck(
            id=str(uuid.uuid4()),
            donation_id=d3.id,
            preparation_time_ok=True,
            storage_condition_ok=True,
            allergens_declared=True,
            packaging_ok=True,
            within_deadline=True,
            overall_eligible=True,
            assessed_at=NOW - timedelta(minutes=32),
            assessed_by=rest_user_1.id,
            notes="Prepared for corporate lunch event, remained unserved. Kept above 63°C continuously.",
            fssai_compliant=True,
        )
        db.add(sc3)

        # Recommendation match for d3 with Annadaata
        dm3 = DonationMatch(
            id=str(uuid.uuid4()),
            donation_id=d3.id,
            ngo_id=ngo_1.id,
            match_score=0.94,
            score_breakdown={
                "food_compatibility": 1.0,
                "capacity_fit": 0.95,
                "urgency_fit": 0.90,
                "dietary_match": 1.0,
                "distance_km": 6.4,
            },
            is_selected=False,
        )
        db.add(dm3)

        # D. Active Donation — ASSIGNED / IN_TRANSIT (Assigned to Volunteer Rahul Sharma)
        d4 = Donation(
            id=str(uuid.uuid4()),
            restaurant_id=rest_3.id,
            ngo_id=ngo_1.id,
            food_name="Dal Makhani & Tandoori Roti Parcels",
            food_category=FoodCategory.COOKED_MEALS,
            quantity_kg=22.0,
            servings=50,
            dietary_label=DietaryLabel.VEG,
            allergens=["dairy", "gluten"],
            storage_condition=StorageCondition.HOT_HOLD,
            storage_temp_celsius=62.0,
            preparation_datetime=NOW - timedelta(hours=3),
            collection_deadline=NOW + timedelta(hours=2),
            pickup_address=rest_3.address,
            pickup_city="Mumbai",
            pickup_pincode="400093",
            pickup_latitude=rest_3.latitude,
            pickup_longitude=rest_3.longitude,
            safety_confirmed=True,
            handler_declaration=True,
            is_eligible=True,
            status=DonationStatus.ASSIGNED,
            created_at=NOW - timedelta(hours=2),
            published_at=NOW - timedelta(hours=1, minutes=45),
            collected_at=NOW - timedelta(minutes=20),
        )
        db.add(d4)
        await db.flush()

        sc4 = FoodSafetyCheck(
            id=str(uuid.uuid4()),
            donation_id=d4.id,
            preparation_time_ok=True,
            storage_condition_ok=True,
            allergens_declared=True,
            packaging_ok=True,
            within_deadline=True,
            overall_eligible=True,
            assessed_at=NOW - timedelta(hours=1, minutes=40),
            assessed_by=rest_user_3.id,
            notes="Temperature verified 62°C. Food packed in thermal delivery bins.",
            fssai_compliant=True,
        )
        deliv4 = DeliveryAssignment(
            id=str(uuid.uuid4()),
            donation_id=d4.id,
            volunteer_id=vol_1.id,
            status=DeliveryStatus.IN_TRANSIT,
            pickup_address=rest_3.address,
            dropoff_address=ngo_1.address,
            pickup_latitude=rest_3.latitude,
            pickup_longitude=rest_3.longitude,
            dropoff_latitude=ngo_1.latitude,
            dropoff_longitude=ngo_1.longitude,
            estimated_distance_km=9.8,
            estimated_duration_minutes=28,
            assigned_at=NOW - timedelta(hours=1),
            accepted_at=NOW - timedelta(minutes=50),
            picked_up_at=NOW - timedelta(minutes=20),
            notes="Volunteer en route to Sion community center.",
        )
        db.add_all([sc4, deliv4])
        await db.flush()

        # Delivery event for d4
        dev1 = DeliveryEvent(
            id=str(uuid.uuid4()),
            delivery_id=deliv4.id,
            event_type="PICKUP",
            latitude=rest_3.latitude,
            longitude=rest_3.longitude,
            notes="Collected 22kg food parcel from kitchen dispatch area.",
            created_by=vol_user_1.id,
        )
        db.add(dev1)

        # ── 8. Seed Notifications ────────────────────────────
        print("🔔 Creating user notifications...")
        notifications = [
            Notification(
                id=str(uuid.uuid4()),
                user_id=rest_user_1.id,
                title="Donation Matched!",
                body="Your donation of 14.0 kg Paneer Butter Masala has been matched with Annadaata Food Foundation.",
                type="donation",
                related_id=d3.id,
                is_read=False,
            ),
            Notification(
                id=str(uuid.uuid4()),
                user_id=ngo_user_1.id,
                title="New Food Match Available",
                body="14.0 kg hot meal donation is available 6.4 km away from The Spice Craft. Claim before 18:00.",
                type="donation",
                related_id=d3.id,
                is_read=False,
            ),
            Notification(
                id=str(uuid.uuid4()),
                user_id=vol_user_1.id,
                title="Delivery In Progress",
                body="You picked up 22 kg from Tandoor Nights. Heading to Annadaata Food Foundation.",
                type="delivery",
                related_id=deliv4.id,
                is_read=True,
            ),
            Notification(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                title="System Alert: Platform Health",
                body="All ML forecasting services and background tasks operational.",
                type="system",
                is_read=True,
            ),
        ]
        db.add_all(notifications)

        # ── 9. Seed Audit Logs ───────────────────────────────
        print("📋 Creating initial audit trail...")
        audit_logs = [
            AuditLog(
                id=str(uuid.uuid4()),
                actor_id=admin_user.id,
                action="SYSTEM_INIT",
                resource_type="system",
                resource_id="kindbite_core",
                details={"event": "Database seeded with demonstration entities and historical data."},
            ),
            AuditLog(
                id=str(uuid.uuid4()),
                actor_id=rest_user_1.id,
                action="CREATE_DONATION",
                resource_type="donation",
                resource_id=d3.id,
                details={"quantity_kg": 14.0, "food_name": d3.food_name},
            ),
            AuditLog(
                id=str(uuid.uuid4()),
                actor_id=vol_user_1.id,
                action="PICKUP_DELIVERY",
                resource_type="delivery",
                resource_id=deliv4.id,
                details={"status": "IN_TRANSIT"},
            ),
        ]
        db.add_all(audit_logs)

        # Commit all transactions
        await db.commit()
        print("✨ Database successfully seeded with full production test data!")
        print("🔑 Test credentials (all accounts use password: KindBite@2026):")
        print("   - Admin:      admin@kindbite.in")
        print("   - Restaurant: spicecraft@kindbite.in")
        print("   - NGO:        annadaata@kindbite.in")
        print("   - Volunteer:  rahul.sharma@kindbite.in")


if __name__ == "__main__":
    asyncio.run(seed())
