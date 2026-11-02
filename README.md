# KindBite AI — Every Bite Deserves a Chance
> **AI-Powered Food Waste Prediction, Prevention & Redistribution Platform**  
> Primary Pilot: Mumbai Metropolitan Region (Bandra, Andheri, Colaba, Juhu, Dadar, Sion/Dharavi, Kurla)

---

## 🌟 Executive Summary

KindBite is an intelligent food waste prediction and rapid redistribution system designed to prevent commercial food waste before it happens. Built for restaurants, bakeries, and cloud kitchens, KindBite combines machine learning demand forecasting, FSSAI-aligned food safety guardrails, automated multi-criteria NGO matching, and volunteer courier dispatch to ensure surplus food reaches verified shelters safely and quickly.

---

## 🏗️ Architecture

```
                                    +-----------------------------------------+
                                    |       KindBite Modern Web Frontend      |
                                    | React 19 + TypeScript + Vite (Port 3000)|
                                    +--------------------+--------------------+
                                                         | (JWT / REST API)
                                                         v
                                    +-----------------------------------------+
                                    |         KindBite FastAPI Backend        |
                                    |          Python 3.12 (Port 8000)        |
                                    +----+-------------+----------------+----+
                                         |             |                |
                +------------------------+             |                +------------------------+
                |                                      |                                         |
                v                                      v                                         v
+-------------------------------+   +------------------------------------+   +----------------------------------+
|    PostgreSQL 16 Database     |   |         Machine Learning Core      |   |       Food Safety Service        |
| - 14 Tables (Users, NGOs,     |   | - 24.5k Mumbai Restaurant Records  |   | - FSSAI Safe Holding Windows     |
|   Donations, Deliveries, etc) |   | - Demand Forecaster (R²: 0.9589)   |   | - Hot Hold ≥60°C / Cold ≤5°C    |
| - Alembic Migrations          |   | - Surplus Predictor (MAE: 1.12 kg) |   | - Shelf-Life & Allergen Audits   |
| - Immutable Audit Trail       |   | - Waste Risk Classifier (72.1% Acc)|   | - Zero AI Override of Safety Fail|
+-------------------------------+   +------------------------------------+   +----------------------------------+
```

---

## 🚀 Quickstart & How to Run

### Prerequisites
- **Node.js**: v20+ (`node -v`)
- **Python**: 3.11+ / 3.12 (`python3 -v`)
- **PostgreSQL**: Running on `localhost:5432` (or via Docker Compose)

### 1. One-Command Setup
```bash
# Clone the repository
git clone https://github.com/AdityaVawhal15-maker/kindBite.git
cd kindBite

# Setup dependencies, virtual environments, and configuration
npm run setup
```

### 2. Database Migration & Demonstration Seeding
```bash
# Run database migrations
npm run db:migrate

# Seed with demonstration restaurants, NGOs, couriers, and 60 days of logs
npm run db:seed
```

### 3. Generate ML Dataset & Train Models
```bash
# Generate Mumbai restaurant synthetic dataset (24,455 records)
npm run ml:generate

# Preprocess features & train Random Forest / Gradient Boosting models
npm run ml:train
```

### 4. Start Development Platform
```bash
# Starts both Backend (Port 8000) and Frontend (Port 3000) concurrently
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

## 🔑 Demo Account Credentials

All demonstration accounts use the password: **`KindBite@2026`**

| Persona | Name | Email | Role | Hub / Location |
| :--- | :--- | :--- | :--- | :--- |
| **Restaurant** | Chef Vikram Oberoi | `spicecraft@kindbite.in` | `RESTAURANT` | The Spice Craft (Bandra West) |
| **NGO Shelter** | Sr. Teresa Fernandes | `annadaata@kindbite.in` | `NGO` | Annadaata Food Foundation (Sion) |
| **Volunteer** | Rahul Sharma | `rahul.sharma@kindbite.in` | `VOLUNTEER` | 150cc Motorcycle (Bandra Sector) |
| **Administrator** | Aarav Mehta | `admin@kindbite.in` | `ADMIN` | Platform Governance |

*(Tip: You can switch between demo personas instantly in the header bar with a single click!)*

---

## 🤖 Machine Learning Pipeline & Results

### Dataset Provenance
- **Size**: 24,455 records across 365 days of commercial kitchen lunch/dinner cycles
- **Calibrated For**: Mumbai Metropolitan Region (Bandra, Andheri, Colaba, Juhu, Dadar)
- **Features**: Cyclical time encoding (sin/cos day & month), monsoon precipitation extremes (35–110 mm/day causing footfall drops), cultural surges (Ganesh Chaturthi, Diwali, Eid), and food shelf life.

### Actual Model Evaluation Metrics (Held-Out Test Set: 2,446 Samples)

1. **Food Demand Forecaster** (`RandomForestRegressor`):
   - **R² Score**: `0.9589` (95.9% explained variance)
   - **MAE**: `1.207 kg`
   - **RMSE**: `1.655 kg`
   - **MAPE**: `7.03%`
2. **Surplus Predictor** (`GradientBoostingRegressor`):
   - **MAE**: `1.122 kg`
   - **RMSE**: `1.498 kg`
   - **R²**: `0.5070`
3. **Waste Risk Classifier** (`RandomForestClassifier` with balanced class weights):
   - **Accuracy**: `72.1%`
   - **Macro F1**: `0.4769`
   - **Tiers**: `LOW` (<12% or <3kg), `MEDIUM` (12–25% or 3–8kg), `HIGH` (>25% or >8kg)

---

## 🛡️ Food Safety Framework (FSSAI Aligned)

> **CRITICAL RULE**: Machine learning predictions **never** certify food safety. No AI output can override a failed safety check.

Every surplus food parcel must satisfy:
1. **Holding Temperature**: Hot Holding ≥ 60.0°C; Refrigerated Storage ≤ 5.0°C.
2. **Preparation Time Window**: Cooked meals max 4 hours from prep; Bakery max 12 hours.
3. **Mandatory Allergen Declaration**: Gluten, dairy, nuts must be declared for all high-allergen categories.
4. **Food Handler Declaration**: Clean packaging, food-grade containers, hairnet & glove attestation.

---

## 🧪 Testing

Run backend unit and API integration tests:
```bash
npm run test:all
```
Result: **13 passed in 1.41s (100% pass rate)**:
- `test_fresh_food_with_valid_declarations_passes`: PASSED
- `test_expired_prep_time_fails_safety_check`: PASSED
- `test_refrigerated_food_with_warm_temperature_fails`: PASSED
- `test_missing_handler_declaration_fails`: PASSED
- `test_haversine_known_coordinates`: PASSED
- `test_hard_constraint_capacity_exceeded`: PASSED
- `test_matching_score_calculation`: PASSED
- `test_login_success_and_invalid`: PASSED
- `test_admin_analytics_with_login`: PASSED
- `test_donations_list`: PASSED
- `test_ml_prediction_inference`: PASSED

---

## 📁 Repository Structure

```
kindbite/
├── backend/
│   ├── alembic/              # Database migration versions
│   ├── app/
│   │   ├── api/v1/endpoints/ # Auth, Restaurants, Donations, Matching, Deliveries, ML, Admin
│   │   ├── core/             # Configuration & JWT security
│   │   ├── db/               # Async SQLAlchemy session
│   │   ├── models/           # ORM models (14 tables)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── scripts/          # Database seed script
│   │   └── services/         # Food safety, ML inference, routing, audit
│   ├── tests/                # Pytest unit & API test suites
│   └── requirements.txt
├── ml/
│   ├── models/artifacts/     # Trained joblib models & evaluation JSON
│   ├── scripts/              # Dataset generator, preprocessor, model trainers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Hero, Restaurant, NGO, Volunteer, ML Lab, Admin
│   │   ├── api.ts            # Typed API client
│   │   ├── App.tsx           # Main application
│   │   └── index.css         # Custom Emerald & Slate design system
│   └── package.json
├── data/
│   ├── synthetic/            # Synthetic Mumbai training data
│   └── processed/            # Train, validation, test splits
├── scripts/                  # Shell management scripts
└── docker-compose.yml        # PostgreSQL container configuration
```

---

## 📜 License & Compliance

Built for social impact in food recovery. Licensed under the MIT License.
Food safety rules comply with the **Food Safety and Standards Authority of India (FSSAI)** regulations.
