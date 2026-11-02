"""
KindBite — Food Demand Forecasting Model Trainer
Trains a Random Forest Regressor to forecast daily food item demand (in kg).
Evaluates MAE, RMSE, and R2 on validation set.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "models" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def train():
    print("📈 Training KindBite Demand Forecasting Model...")
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"

    if not train_path.exists():
        print("Processed data not found. Running preprocessor...")
        from ml.scripts.preprocess_data import preprocess
        preprocess()

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    pipeline_info = joblib.load(ARTIFACTS_DIR / "preprocessing_pipeline.joblib")
    feature_cols = pipeline_info["feature_names"]

    X_train = train_df[feature_cols]
    y_train = train_df["actual_demand_kg"]

    X_val = val_df[feature_cols]
    y_val = val_df["actual_demand_kg"]

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=16,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    mae = float(mean_absolute_error(y_val, val_preds))
    rmse = float(np.sqrt(mean_squared_error(y_val, val_preds)))
    r2 = float(r2_score(y_val, val_preds))

    # Top feature importances
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_features = {
        feature_cols[i]: round(float(importances[i]), 4)
        for i in sorted_idx[:10]
    }

    model_path = ARTIFACTS_DIR / "demand_model.joblib"
    joblib.dump(model, model_path)

    metadata = {
        "model_name": "demand_forecaster",
        "algorithm": "RandomForestRegressor",
        "version": "1.0.0",
        "train_samples": len(train_df),
        "validation_samples": len(val_df),
        "metrics": {
            "mae_kg": round(mae, 3),
            "rmse_kg": round(rmse, 3),
            "r2_score": round(r2, 4),
        },
        "top_feature_importances": top_features,
    }

    meta_path = ARTIFACTS_DIR / "demand_model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Demand model trained successfully:")
    print(f"   Validation MAE:  {mae:.3f} kg")
    print(f"   Validation RMSE: {rmse:.3f} kg")
    print(f"   Validation R²:   {r2:.4f}")
    print(f"   Artifact saved:  {model_path}")


if __name__ == "__main__":
    train()
