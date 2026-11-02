"""
KindBite — ML Inference Service
Loads trained models from disk (JobLib) and provides inference.
Falls back to simple statistical heuristics if models not yet trained.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

_instance: Optional["MLService"] = None


def get_ml_service() -> "MLService":
    global _instance
    if _instance is None:
        _instance = MLService()
    return _instance


class MLService:
    """
    Loads serialized ML models from disk.
    If models are unavailable (not yet trained), falls back to
    deterministic heuristic estimates clearly labelled as HEURISTIC.
    """

    def __init__(self):
        self.models_dir = os.environ.get("ML_MODELS_DIR", "./ml/models/artifacts")
        self._demand_model = None
        self._surplus_model = None
        self._risk_model = None
        self._registry: Dict[str, Any] = {}
        self._load_models()

    def _load_models(self):
        registry_path = os.path.join(self.models_dir, "model_registry.json")
        if os.path.exists(registry_path):
            with open(registry_path) as f:
                self._registry = json.load(f)

        try:
            import joblib
            demand_path = self._registry.get("demand", {}).get("artifact_path", "")
            if demand_path and os.path.exists(demand_path):
                self._demand_model = joblib.load(demand_path)
                logger.info("Demand model loaded", path=demand_path)
        except Exception as e:
            logger.warning("Could not load demand model", error=str(e))

        try:
            import joblib
            surplus_path = self._registry.get("surplus", {}).get("artifact_path", "")
            if surplus_path and os.path.exists(surplus_path):
                self._surplus_model = joblib.load(surplus_path)
                logger.info("Surplus model loaded", path=surplus_path)
        except Exception as e:
            logger.warning("Could not load surplus model", error=str(e))

        try:
            import joblib
            risk_path = self._registry.get("risk", {}).get("artifact_path", "")
            if risk_path and os.path.exists(risk_path):
                self._risk_model = joblib.load(risk_path)
                logger.info("Risk model loaded", path=risk_path)
        except Exception as e:
            logger.warning("Could not load risk model", error=str(e))

    def _extract_temporal_features(self, date: datetime) -> Dict[str, Any]:
        return {
            "day_of_week": date.weekday(),
            "month": date.month,
            "day": date.day,
            "is_weekend": 1 if date.weekday() >= 5 else 0,
            "quarter": (date.month - 1) // 3 + 1,
            "week_of_year": date.isocalendar()[1],
        }

    def predict_demand(
        self,
        restaurant_id: str,
        food_item_id: Optional[str],
        prediction_date: datetime,
        sales_history: List[Dict],
    ) -> Dict[str, Any]:
        """
        Predict food demand. Uses trained model if available,
        otherwise falls back to moving average heuristic.
        """
        features = self._extract_temporal_features(prediction_date)

        # Try trained model
        if self._demand_model is not None:
            try:
                import pandas as pd
                import numpy as np

                if len(sales_history) > 0:
                    hist_values = [h["sold_kg"] for h in sales_history[-30:]]
                    lag_1 = hist_values[0] if hist_values else 10.0
                    lag_7 = hist_values[6] if len(hist_values) > 6 else lag_1
                    rolling_mean = float(pd.Series(hist_values).mean())
                    rolling_std = float(pd.Series(hist_values).std() or 1.0)
                else:
                    lag_1 = lag_7 = rolling_mean = 10.0
                    rolling_std = 1.0

                X = pd.DataFrame([{
                    **features,
                    "lag_1": lag_1,
                    "lag_7": lag_7,
                    "rolling_mean_7": rolling_mean,
                    "rolling_std_7": rolling_std,
                }])

                model_info = self._registry.get("demand", {})
                feature_cols = model_info.get("feature_schema", {}).get("features", list(X.columns))
                # Fill missing columns with 0
                for col in feature_cols:
                    if col not in X.columns:
                        X[col] = 0
                X = X[feature_cols]

                pred = float(self._demand_model.predict(X)[0])
                pred = max(0.5, pred)  # no negative demand

                return {
                    "predicted_demand_kg": round(pred, 3),
                    "lower_bound_kg": round(max(0, pred * 0.8), 3),
                    "upper_bound_kg": round(pred * 1.2, 3),
                    "model_name": model_info.get("algorithm", "XGBoost"),
                    "model_version": model_info.get("version", "1.0"),
                    "confidence": 0.82,
                    "method": "ml_model",
                }
            except Exception as e:
                logger.warning("ML demand inference failed, using heuristic", error=str(e))

        # Fallback: moving average heuristic
        return self._heuristic_demand(sales_history, features)

    def _heuristic_demand(self, history: List[Dict], features: Dict) -> Dict[str, Any]:
        """Simple moving average baseline with day-of-week adjustment."""
        if not history:
            base = 10.0
        else:
            values = [h["sold_kg"] for h in history[:30]]
            base = sum(values) / len(values)

        # Day-of-week multiplier (weekends get +20% for demo)
        dow_mult = 1.2 if features["is_weekend"] else 1.0
        pred = base * dow_mult
        pred = max(0.5, pred)

        return {
            "predicted_demand_kg": round(pred, 3),
            "lower_bound_kg": round(max(0, pred * 0.75), 3),
            "upper_bound_kg": round(pred * 1.25, 3),
            "model_name": "MovingAverage_Heuristic",
            "model_version": "baseline",
            "confidence": 0.60,
            "method": "heuristic_fallback",
            "note": "ML model not available. Using moving average baseline. Train models with: npm run ml:train",
        }

    def predict_surplus(
        self,
        prepared_kg: float,
        predicted_demand_kg: float,
        restaurant_id: str,
    ) -> Dict[str, Any]:
        """
        Predict surplus. Never returns negative surplus as a donation quantity.
        """
        raw_surplus = prepared_kg - predicted_demand_kg
        predicted_surplus = max(0.0, raw_surplus)
        surplus_pct = (predicted_surplus / prepared_kg * 100) if prepared_kg > 0 else 0.0

        if self._surplus_model is not None:
            try:
                import pandas as pd
                X = pd.DataFrame([{
                    "prepared_kg": prepared_kg,
                    "predicted_demand_kg": predicted_demand_kg,
                    "surplus_ratio": prepared_kg / max(predicted_demand_kg, 0.1),
                }])

                model_info = self._registry.get("surplus", {})
                feature_cols = model_info.get("feature_schema", {}).get("features", list(X.columns))
                for col in feature_cols:
                    if col not in X.columns:
                        X[col] = 0
                X = X[feature_cols]

                ml_surplus = float(self._surplus_model.predict(X)[0])
                ml_surplus = max(0.0, min(ml_surplus, prepared_kg))

                return {
                    "predicted_surplus_kg": round(ml_surplus, 3),
                    "predicted_surplus_pct": round(ml_surplus / prepared_kg * 100, 1),
                    "model_name": model_info.get("algorithm", "RandomForest"),
                    "model_version": model_info.get("version", "1.0"),
                    "method": "ml_model",
                }
            except Exception as e:
                logger.warning("ML surplus inference failed, using arithmetic", error=str(e))

        return {
            "predicted_surplus_kg": round(predicted_surplus, 3),
            "predicted_surplus_pct": round(surplus_pct, 1),
            "model_name": "Arithmetic_Heuristic",
            "model_version": "baseline",
            "method": "heuristic_fallback",
            "note": "ML model not available. Using prepared_kg - predicted_demand_kg.",
        }

    def classify_waste_risk(
        self,
        prepared_kg: float,
        predicted_surplus_kg: float,
    ) -> Dict[str, Any]:
        """
        Classify waste risk. Returns LOW, MEDIUM, or HIGH.
        Based on surplus as a fraction of prepared quantity.
        """
        if prepared_kg <= 0:
            return {"waste_risk": "LOW", "risk_score": 0.0, "method": "arithmetic"}

        surplus_ratio = predicted_surplus_kg / prepared_kg

        if self._risk_model is not None:
            try:
                import pandas as pd
                X = pd.DataFrame([{
                    "prepared_kg": prepared_kg,
                    "predicted_surplus_kg": predicted_surplus_kg,
                    "surplus_ratio": surplus_ratio,
                }])

                model_info = self._registry.get("risk", {})
                feature_cols = model_info.get("feature_schema", {}).get("features", list(X.columns))
                for col in feature_cols:
                    if col not in X.columns:
                        X[col] = 0
                X = X[feature_cols]

                risk_label = self._risk_model.predict(X)[0]
                risk_proba = self._risk_model.predict_proba(X)[0]

                return {
                    "waste_risk": str(risk_label),
                    "risk_score": round(float(max(risk_proba)), 3),
                    "surplus_ratio": round(surplus_ratio, 3),
                    "method": "ml_model",
                    "model_name": model_info.get("algorithm", "XGBoostClassifier"),
                }
            except Exception as e:
                logger.warning("ML risk classification failed, using heuristic", error=str(e))

        # Heuristic thresholds (documented)
        if surplus_ratio <= 0.10:
            risk = "LOW"
            score = surplus_ratio / 0.10 * 0.33
        elif surplus_ratio <= 0.25:
            risk = "MEDIUM"
            score = 0.33 + (surplus_ratio - 0.10) / 0.15 * 0.34
        else:
            risk = "HIGH"
            score = min(0.99, 0.67 + (surplus_ratio - 0.25) / 0.75 * 0.32)

        return {
            "waste_risk": risk,
            "risk_score": round(score, 3),
            "surplus_ratio": round(surplus_ratio, 3),
            "method": "heuristic_thresholds",
            "note": "Heuristic: LOW<10%, MEDIUM 10-25%, HIGH>25% surplus ratio",
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "demand_model": {
                "loaded": self._demand_model is not None,
                "info": self._registry.get("demand"),
            },
            "surplus_model": {
                "loaded": self._surplus_model is not None,
                "info": self._registry.get("surplus"),
            },
            "risk_model": {
                "loaded": self._risk_model is not None,
                "info": self._registry.get("risk"),
            },
            "models_dir": self.models_dir,
            "note": "Train models via: npm run ml:train",
        }
