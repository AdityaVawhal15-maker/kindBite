"""
KindBite — Final Model Evaluation on Held-Out Test Set
Loads test.csv, computes comprehensive metrics across all models,
and outputs a structured evaluation report.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "models" / "artifacts"


def evaluate():
    print("🧪 Running KindBite Comprehensive Model Evaluation on Test Set...")
    test_path = PROCESSED_DIR / "test.csv"
    if not test_path.exists():
        raise FileNotFoundError(f"Test split not found at {test_path}")

    test_df = pd.read_csv(test_path)
    pipeline_info = joblib.load(ARTIFACTS_DIR / "preprocessing_pipeline.joblib")
    feature_cols = pipeline_info["feature_names"]

    # ── 1. Demand Model Evaluation ────────────────────────
    demand_model = joblib.load(ARTIFACTS_DIR / "demand_model.joblib")
    X_demand = test_df[feature_cols]
    y_demand = test_df["actual_demand_kg"]
    pred_demand = demand_model.predict(X_demand)

    demand_mae = float(mean_absolute_error(y_demand, pred_demand))
    demand_rmse = float(np.sqrt(mean_squared_error(y_demand, pred_demand)))
    demand_r2 = float(r2_score(y_demand, pred_demand))
    demand_mape = float(np.mean(np.abs((y_demand - pred_demand) / y_demand)) * 100)

    # ── 2. Surplus Model Evaluation ───────────────────────
    surplus_model = joblib.load(ARTIFACTS_DIR / "surplus_model.joblib")
    X_surplus = test_df[feature_cols].copy()
    X_surplus["prep_quantity_input"] = test_df["prepared_quantity_kg"]
    y_surplus = test_df["surplus_quantity_kg"]
    pred_surplus = np.clip(surplus_model.predict(X_surplus), 0.0, None)

    surplus_mae = float(mean_absolute_error(y_surplus, pred_surplus))
    surplus_rmse = float(np.sqrt(mean_squared_error(y_surplus, pred_surplus)))
    surplus_r2 = float(r2_score(y_surplus, pred_surplus))

    # ── 3. Waste Risk Model Evaluation ───────────────────
    risk_model = joblib.load(ARTIFACTS_DIR / "waste_risk_model.joblib")
    X_risk = test_df[feature_cols].copy()
    X_risk["prep_quantity_input"] = test_df["prepared_quantity_kg"]
    y_risk = test_df["waste_risk"]
    pred_risk = risk_model.predict(X_risk)

    labels = ["LOW", "MEDIUM", "HIGH"]
    risk_acc = float(accuracy_score(y_risk, pred_risk))
    risk_f1 = float(f1_score(y_risk, pred_risk, average="macro"))
    risk_prec = float(precision_score(y_risk, pred_risk, average="macro"))
    risk_rec = float(recall_score(y_risk, pred_risk, average="macro"))
    cm = confusion_matrix(y_risk, pred_risk, labels=labels).tolist()

    report = {
        "status": "success",
        "test_samples": len(test_df),
        "demand_model": {
            "algorithm": "RandomForestRegressor",
            "test_mae_kg": round(demand_mae, 3),
            "test_rmse_kg": round(demand_rmse, 3),
            "test_r2": round(demand_r2, 4),
            "test_mape_pct": round(demand_mape, 2),
        },
        "surplus_model": {
            "algorithm": "GradientBoostingRegressor",
            "test_mae_kg": round(surplus_mae, 3),
            "test_rmse_kg": round(surplus_rmse, 3),
            "test_r2": round(surplus_r2, 4),
        },
        "waste_risk_classifier": {
            "algorithm": "RandomForestClassifier",
            "test_accuracy": round(risk_acc, 4),
            "test_macro_f1": round(risk_f1, 4),
            "test_macro_precision": round(risk_prec, 4),
            "test_macro_recall": round(risk_rec, 4),
            "confusion_matrix": {
                "labels": labels,
                "matrix": cm,
            },
        },
    }

    report_path = ARTIFACTS_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("==================================================")
    print(" KINDBITE ML PIPELINE EVALUATION REPORT")
    print("==================================================")
    print(f"Test samples: {len(test_df):,}")
    print("\n1. Demand Forecaster:")
    print(f"   MAE:  {demand_mae:.3f} kg")
    print(f"   RMSE: {demand_rmse:.3f} kg")
    print(f"   R²:   {demand_r2:.4f}")
    print(f"   MAPE: {demand_mape:.2f}%")
    print("\n2. Surplus Predictor:")
    print(f"   MAE:  {surplus_mae:.3f} kg")
    print(f"   RMSE: {surplus_rmse:.3f} kg")
    print(f"   R²:   {surplus_r2:.4f}")
    print("\n3. Waste Risk Classifier:")
    print(f"   Accuracy: {risk_acc:.4f} ({risk_acc*100:.1f}%)")
    print(f"   Macro F1: {risk_f1:.4f}")
    print("==================================================")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    evaluate()
