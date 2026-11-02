"""
KindBite — Surplus Prediction Model Trainer
Predicts surplus food quantity (in kg) based on preparation quantity,
forecasted demand, day of week, weather, and category.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "models" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def train():
    print("🥘 Training KindBite Surplus Prediction Model...")
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    pipeline_info = joblib.load(ARTIFACTS_DIR / "preprocessing_pipeline.joblib")
    feature_cols = pipeline_info["feature_names"]

    # In surplus prediction, the chef's planned preparation quantity is a primary input feature
    X_train = train_df[feature_cols].copy()
    X_train["prep_quantity_input"] = train_df["prepared_quantity_kg"]
    y_train = train_df["surplus_quantity_kg"]

    X_val = val_df[feature_cols].copy()
    X_val["prep_quantity_input"] = val_df["prepared_quantity_kg"]
    y_val = val_df["surplus_quantity_kg"]

    model = GradientBoostingRegressor(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=5,
        min_samples_split=4,
        random_state=42,
    )
    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    # Clip any negative predictions to 0.0 kg
    val_preds = np.clip(val_preds, 0.0, None)

    mae = float(mean_absolute_error(y_val, val_preds))
    rmse = float(np.sqrt(mean_squared_error(y_val, val_preds)))
    r2 = float(r2_score(y_val, val_preds))

    model_path = ARTIFACTS_DIR / "surplus_model.joblib"
    joblib.dump(model, model_path)

    metadata = {
        "model_name": "surplus_predictor",
        "algorithm": "GradientBoostingRegressor",
        "version": "1.0.0",
        "train_samples": len(train_df),
        "validation_samples": len(val_df),
        "metrics": {
            "mae_kg": round(mae, 3),
            "rmse_kg": round(rmse, 3),
            "r2_score": round(r2, 4),
        },
    }

    meta_path = ARTIFACTS_DIR / "surplus_model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Surplus model trained successfully:")
    print(f"   Validation MAE:  {mae:.3f} kg")
    print(f"   Validation RMSE: {rmse:.3f} kg")
    print(f"   Validation R²:   {r2:.4f}")
    print(f"   Artifact saved:  {model_path}")


if __name__ == "__main__":
    train()
