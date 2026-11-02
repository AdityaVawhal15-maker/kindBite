"""KindBite — ML status and metrics endpoints (admin-only training trigger)"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, require_admin
from app.models import User
from app.services.ml_inference import get_ml_service

router = APIRouter()


@router.get("/status")
async def ml_status(_: User = Depends(get_current_user)):
    """Get ML model availability and metadata."""
    ml = get_ml_service()
    return ml.get_status()


@router.get("/metrics")
async def ml_metrics(_: User = Depends(get_current_user)):
    """Get evaluation metrics for loaded models."""
    ml = get_ml_service()
    status = ml.get_status()
    metrics = {}
    for model_type in ["demand", "surplus", "risk"]:
        info = status.get(f"{model_type}_model", {}).get("info") or {}
        metrics[model_type] = info.get("evaluation_metrics", {})
    return {"metrics": metrics, "note": "Metrics recorded during training. Run ml:train to update."}
