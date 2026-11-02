"""
KindBite — Synthetic Dataset Generator
Simulates realistic Mumbai restaurant demand, preparation, weather patterns,
festivals, and surplus waste metrics across 365 days.
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
from datetime import date, timedelta
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data" / "synthetic"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEED = int(os.getenv("SYNTHETIC_SEED", "42"))
random.seed(SEED)

RESTAURANTS = [
    {
        "id": "rest_spice_craft",
        "name": "The Spice Craft",
        "type": "Fine Dining",
        "locality": "Bandra West",
        "pincode": "400050",
        "capacity_seats": 120,
    },
    {
        "id": "rest_bombay_bistro",
        "name": "Bombay Bistro & Cafe",
        "type": "Cafe & Bakery",
        "locality": "Colaba",
        "pincode": "400001",
        "capacity_seats": 65,
    },
    {
        "id": "rest_tandoor_nights",
        "name": "Tandoor Nights",
        "type": "Casual Mughlai Dining",
        "locality": "Andheri East",
        "pincode": "400093",
        "capacity_seats": 150,
    },
    {
        "id": "rest_green_leaf",
        "name": "Green Leaf Organics",
        "type": "Pure Veg & Salads",
        "locality": "Juhu",
        "pincode": "400049",
        "capacity_seats": 80,
    },
    {
        "id": "rest_mumbai_dabbawala",
        "name": "Mumbai Express Kitchen",
        "type": "Cloud Kitchen / Thali",
        "locality": "Dadar",
        "pincode": "400014",
        "capacity_seats": 0,
    },
]

FOOD_ITEMS = [
    # Cooked Meals
    {"id": "item_01", "name": "Veg Dum Biryani", "category": "COOKED_MEALS", "dietary": "VEG", "shelf_life_h": 4, "base_demand": 24.0, "price": 280.0},
    {"id": "item_02", "name": "Chicken Tikka Biryani", "category": "COOKED_MEALS", "dietary": "NON_VEG", "shelf_life_h": 4, "base_demand": 30.0, "price": 360.0},
    {"id": "item_03", "name": "Paneer Butter Masala", "category": "COOKED_MEALS", "dietary": "VEG", "shelf_life_h": 5, "base_demand": 18.0, "price": 320.0},
    {"id": "item_04", "name": "Dal Makhani", "category": "COOKED_MEALS", "dietary": "VEG", "shelf_life_h": 6, "base_demand": 22.0, "price": 240.0},
    {"id": "item_05", "name": "Mixed Vegetable Curry", "category": "COOKED_MEALS", "dietary": "VEG", "shelf_life_h": 5, "base_demand": 16.0, "price": 220.0},
    {"id": "item_06", "name": "Creamy White Sauce Pasta", "category": "COOKED_MEALS", "dietary": "VEG", "shelf_life_h": 4, "base_demand": 14.0, "price": 310.0},
    {"id": "item_07", "name": "Steamed Basmati Rice", "category": "COOKED_MEALS", "dietary": "VEGAN", "shelf_life_h": 6, "base_demand": 28.0, "price": 140.0},
    {"id": "item_08", "name": "Butter Naan & Roti Mix", "category": "BAKERY", "dietary": "VEG", "shelf_life_h": 4, "base_demand": 20.0, "price": 160.0},
    # Bakery
    {"id": "item_09", "name": "Artisan Sourdough Loaf", "category": "BAKERY", "dietary": "VEGAN", "shelf_life_h": 24, "base_demand": 12.0, "price": 190.0},
    {"id": "item_10", "name": "Butter Croissants", "category": "BAKERY", "dietary": "VEG", "shelf_life_h": 12, "base_demand": 10.0, "price": 140.0},
    {"id": "item_11", "name": "Veg Club Sandwiches", "category": "BAKERY", "dietary": "VEG", "shelf_life_h": 4, "base_demand": 15.0, "price": 180.0},
    # Salads / Produce
    {"id": "item_12", "name": "Sprouted Bean & Corn Salad", "category": "RAW_PRODUCE", "dietary": "VEGAN", "shelf_life_h": 6, "base_demand": 10.0, "price": 210.0},
    {"id": "item_13", "name": "Mediterranean Quinoa Bowl", "category": "RAW_PRODUCE", "dietary": "VEGAN", "shelf_life_h": 6, "base_demand": 11.0, "price": 260.0},
    # Desserts
    {"id": "item_14", "name": "Dark Chocolate Walnut Brownie", "category": "DESSERTS", "dietary": "VEG", "shelf_life_h": 48, "base_demand": 8.0, "price": 160.0},
    {"id": "item_15", "name": "Gulab Jamun", "category": "DESSERTS", "dietary": "VEG", "shelf_life_h": 24, "base_demand": 12.0, "price": 180.0},
]


def get_weather_for_date(curr_date: date):
    """Simulate realistic Mumbai weather conditions based on season."""
    month = curr_date.month
    # Monsoon: June - September
    if 6 <= month <= 9:
        rain_prob = 0.75
        is_rain = random.random() < rain_prob
        if is_rain:
            heavy_rain = random.random() < 0.35
            cond = "Heavy Rain" if heavy_rain else "Rain"
            precip = random.uniform(35.0, 110.0) if heavy_rain else random.uniform(8.0, 32.0)
            temp = random.uniform(26.0, 29.5)
            humidity = random.uniform(85.0, 98.0)
        else:
            cond = "Humid Overcast"
            precip = random.uniform(0.0, 3.0)
            temp = random.uniform(28.0, 31.5)
            humidity = random.uniform(80.0, 92.0)
    # Summer: March - May
    elif 3 <= month <= 5:
        cond = "Hot & Sunny"
        precip = 0.0
        temp = random.uniform(32.0, 38.5)
        humidity = random.uniform(62.0, 78.0)
    # Winter / Post-monsoon: October - February
    else:
        cond = "Pleasant" if month in (12, 1, 2) else "Warm & Clear"
        precip = 0.0
        temp = random.uniform(22.0, 31.0)
        humidity = random.uniform(50.0, 72.0)

    return cond, round(temp, 1), round(humidity, 1), round(precip, 1)


def get_festival_flag(curr_date: date):
    """Detect notable Mumbai holidays and festivals."""
    m, d = curr_date.month, curr_date.day
    # Approx dates for Mumbai festivals
    if (m == 9 and 10 <= d <= 20):
        return "Ganesh Chaturthi", 1.35  # High sweet & veg demand
    elif (m == 11 and 1 <= d <= 5):
        return "Diwali", 1.45  # Peak festive feast
    elif (m == 4 and 10 <= d <= 12):
        return "Eid-ul-Fitr", 1.40  # Peak Mughlai/Biryani
    elif (m == 12 and d in (24, 25, 31)) or (m == 1 and d == 1):
        return "New Year / Christmas", 1.50
    elif (m == 8 and d == 15) or (m == 1 and d == 26) or (m == 10 and d == 2):
        return "National Holiday", 1.20
    return "None", 1.0


def generate():
    print(f"🎲 Generating synthetic Mumbai restaurant dataset (Seed={SEED})...")
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)

    records = []
    delta_days = (end_date - start_date).days + 1

    for day_i in range(delta_days):
        curr_date = start_date + timedelta(days=day_i)
        dow = curr_date.weekday()  # 0=Mon, 6=Sun
        is_weekend = 1 if dow in (4, 5, 6) else 0  # Fri/Sat/Sun considered weekend dining
        weather_cond, temp_c, humidity_pct, precip_mm = get_weather_for_date(curr_date)
        festival_name, festival_mult = get_festival_flag(curr_date)

        # Weather impact: Heavy rain suppresses in-restaurant dining
        weather_mult = 1.0
        if weather_cond == "Heavy Rain":
            weather_mult = 0.65  # 35% footfall drop
        elif weather_cond == "Rain":
            weather_mult = 0.85
        elif weather_cond == "Hot & Sunny" and temp_c > 36.0:
            weather_mult = 0.90

        # Day of week multiplier
        dow_mult = {0: 0.82, 1: 0.85, 2: 0.88, 3: 0.95, 4: 1.25, 5: 1.40, 6: 1.35}[dow]

        for rest in RESTAURANTS:
            # Each restaurant carries a subset of 5-8 food items
            for item in FOOD_ITEMS:
                # Match item category to restaurant type
                if rest["type"] == "Cafe & Bakery" and item["category"] not in ("BAKERY", "DESSERTS", "RAW_PRODUCE"):
                    continue
                if rest["type"] == "Pure Veg & Salads" and item["dietary"] == "NON_VEG":
                    continue

                # Expected baseline demand
                base_demand = item["base_demand"]
                noise = random.gauss(0, base_demand * 0.08)

                actual_demand = base_demand * dow_mult * weather_mult * festival_mult + noise
                actual_demand = max(2.0, round(actual_demand, 2))

                # Chef's preparation decision:
                # Typically prepares based on baseline * dow forecast, plus 10-25% safety buffer.
                # However, chefs cannot predict extreme rain drops accurately -> causing surplus spikes!
                expected_prep_forecast = base_demand * dow_mult * (festival_mult if festival_mult > 1.0 else 1.0)
                prep_buffer = random.uniform(1.10, 1.25)
                prepared_qty = round(expected_prep_forecast * prep_buffer, 2)

                # If actual demand turns out higher than prep (sold out), surplus is 0
                surplus_kg = max(0.0, round(prepared_qty - actual_demand, 2))
                surplus_pct = round((surplus_kg / prepared_qty) * 100, 1) if prepared_qty > 0 else 0.0

                # Risk label
                if surplus_pct < 12.0 or surplus_kg < 3.0:
                    risk = "LOW"
                elif surplus_pct < 25.0 or surplus_kg < 8.0:
                    risk = "MEDIUM"
                else:
                    risk = "HIGH"

                records.append({
                    "date": curr_date.isoformat(),
                    "day_of_week": dow,
                    "is_weekend": is_weekend,
                    "month": curr_date.month,
                    "restaurant_id": rest["id"],
                    "restaurant_type": rest["type"],
                    "locality": rest["locality"],
                    "pincode": rest["pincode"],
                    "food_item_id": item["id"],
                    "food_name": item["name"],
                    "food_category": item["category"],
                    "dietary_label": item["dietary"],
                    "shelf_life_hours": item["shelf_life_h"],
                    "price_inr": item["price"],
                    "weather_condition": weather_cond,
                    "temperature_celsius": temp_c,
                    "humidity_percent": humidity_pct,
                    "precipitation_mm": precip_mm,
                    "festival_event": festival_name,
                    "festival_multiplier": festival_mult,
                    "prepared_quantity_kg": prepared_qty,
                    "actual_demand_kg": actual_demand,
                    "surplus_quantity_kg": surplus_kg,
                    "surplus_percentage": surplus_pct,
                    "waste_risk": risk,
                })

    csv_path = DATA_DIR / "mumbai_restaurant_demand_surplus.csv"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    meta_path = DATA_DIR / "dataset_metadata.json"
    metadata = {
        "dataset_name": "KindBite Mumbai Restaurant Demand & Surplus Dataset",
        "description": "High-fidelity synthetic dataset modeled after Mumbai restaurant footfalls, monsoon anomalies, religious festivals, and prep buffer waste behaviors.",
        "record_count": len(records),
        "date_range": [start_date.isoformat(), end_date.isoformat()],
        "features": list(records[0].keys()),
        "restaurants_count": len(RESTAURANTS),
        "food_items_count": len(FOOD_ITEMS),
        "generator_seed": SEED,
    }
    with open(meta_path, mode="w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Generated {len(records):,} records saved to:")
    print(f"   CSV:  {csv_path}")
    print(f"   Meta: {meta_path}")


if __name__ == "__main__":
    generate()
