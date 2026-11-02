"""
KindBite — ML Prediction endpoints
These call the ML service which loads pre-trained models from disk.
Models must be trained first via: npm run ml:train
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_restaurant_or_admin
from app.db.session import get_db
from app.models import Restaurant, SalesRecord, DemandPrediction, SurplusPrediction, User, WasteRisk
from app.schemas.schemas import (
    DemandPredictionRequest, DemandPredictionOut,
    SurplusPredictionRequest, SurplusPredictionOut,
)
from app.services.ml_inference import get_ml_service

router = APIRouter()


async def _get_restaurant(user: User, db: AsyncSession) -> Restaurant:
    r = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = r.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    return restaurant


@router.post("/demand", response_model=DemandPredictionOut, status_code=201)
async def predict_demand(
    payload: DemandPredictionRequest,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Predict food demand for a given date using the trained ML model."""
    restaurant = await _get_restaurant(current_user, db)
    ml = get_ml_service()

    # Build inference features from historical sales
    result = await db.execute(
        select(SalesRecord)
        .where(SalesRecord.restaurant_id == restaurant.id)
        .order_by(SalesRecord.date.desc())
        .limit(60)
    )
    history = result.scalars().all()

    prediction = ml.predict_demand(
        restaurant_id=restaurant.id,
        food_item_id=payload.food_item_id,
        prediction_date=payload.prediction_date,
        sales_history=[
            {"date": str(r.date), "sold_kg": float(r.sold_quantity_kg or 0)}
            for r in history
        ],
    )

    record = DemandPrediction(
        restaurant_id=restaurant.id,
        food_item_id=payload.food_item_id,
        prediction_date=payload.prediction_date,
        predicted_demand_kg=prediction["predicted_demand_kg"],
        lower_bound_kg=prediction.get("lower_bound_kg"),
        upper_bound_kg=prediction.get("upper_bound_kg"),
        model_name=prediction.get("model_name"),
        model_version=prediction.get("model_version"),
        confidence=prediction.get("confidence"),
        feature_importances=prediction.get("feature_importances"),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return DemandPredictionOut.model_validate(record)


@router.post("/surplus", response_model=SurplusPredictionOut, status_code=201)
async def predict_surplus(
    payload: SurplusPredictionRequest,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Predict surplus for a given preparation and date."""
    restaurant = await _get_restaurant(current_user, db)
    ml = get_ml_service()

    # First get demand prediction
    result = await db.execute(
        select(SalesRecord)
        .where(SalesRecord.restaurant_id == restaurant.id)
        .order_by(SalesRecord.date.desc())
        .limit(60)
    )
    history = result.scalars().all()

    demand_pred = ml.predict_demand(
        restaurant_id=restaurant.id,
        food_item_id=payload.food_item_id,
        prediction_date=payload.prediction_date,
        sales_history=[
            {"date": str(r.date), "sold_kg": float(r.sold_quantity_kg or 0)}
            for r in history
        ],
    )
    predicted_demand = demand_pred["predicted_demand_kg"]

    # Predict surplus
    surplus_pred = ml.predict_surplus(
        prepared_kg=payload.prepared_quantity_kg,
        predicted_demand_kg=predicted_demand,
        restaurant_id=restaurant.id,
    )

    # Classify risk
    risk_result = ml.classify_waste_risk(
        prepared_kg=payload.prepared_quantity_kg,
        predicted_surplus_kg=surplus_pred["predicted_surplus_kg"],
    )

    record = SurplusPrediction(
        restaurant_id=restaurant.id,
        food_item_id=payload.food_item_id,
        preparation_record_id=payload.preparation_record_id,
        prediction_date=payload.prediction_date,
        prepared_quantity_kg=payload.prepared_quantity_kg,
        predicted_demand_kg=predicted_demand,
        predicted_surplus_kg=max(0, surplus_pred["predicted_surplus_kg"]),
        predicted_surplus_pct=surplus_pred.get("predicted_surplus_pct"),
        waste_risk=WasteRisk(risk_result["waste_risk"]),
        risk_score=risk_result.get("risk_score"),
        model_name=surplus_pred.get("model_name"),
        model_version=surplus_pred.get("model_version"),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return SurplusPredictionOut.model_validate(record)


@router.post("/risk")
async def classify_risk(
    prepared_kg: float,
    predicted_surplus_kg: float,
    current_user: User = Depends(require_restaurant_or_admin),
):
    """Classify waste risk level given prepared and predicted surplus quantities."""
    if prepared_kg <= 0:
        raise HTTPException(status_code=422, detail="prepared_kg must be positive.")
    ml = get_ml_service()
    return ml.classify_waste_risk(
        prepared_kg=prepared_kg,
        predicted_surplus_kg=max(0, predicted_surplus_kg),
    )


@router.get("/history")
async def get_prediction_history(
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)

    demand_result = await db.execute(
        select(DemandPrediction)
        .where(DemandPrediction.restaurant_id == restaurant.id)
        .order_by(DemandPrediction.prediction_date.desc())
        .limit(30)
    )
    surplus_result = await db.execute(
        select(SurplusPrediction)
        .where(SurplusPrediction.restaurant_id == restaurant.id)
        .order_by(SurplusPrediction.prediction_date.desc())
        .limit(30)
    )

    return {
        "demand_predictions": [
            DemandPredictionOut.model_validate(p)
            for p in demand_result.scalars().all()
        ],
        "surplus_predictions": [
            SurplusPredictionOut.model_validate(p)
            for p in surplus_result.scalars().all()
        ],
    }
