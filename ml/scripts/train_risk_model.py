"""
KindBite — Waste Risk Classifier Trainer
Trains a Random Forest Classifier to assign waste risk levels:
- LOW: Surplus < 12% or < 3kg
- MEDIUM: Surplus 12-25% or 3-8kg
- HIGH: Surplus > 25% or > 8kg
Evaluates Accuracy, Precision, Recall, and F1 score.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "models" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def train():
    print("⚠️ Training KindBite Waste Risk Classifier...")
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "val.csv"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    pipeline_info = joblib.load(ARTIFACTS_DIR / "preprocessing_pipeline.joblib")
    feature_cols = pipeline_info["feature_names"]

    X_train = train_df[feature_cols].copy()
    X_train["prep_quantity_input"] = train_df["prepared_quantity_kg"]
    y_train = train_df["waste_risk"]

    X_val = val_df[feature_cols].copy()
    X_val["prep_quantity_input"] = val_df["prepared_quantity_kg"]
    y_val = val_df["waste_risk"]

    classes = ["LOW", "MEDIUM", "HIGH"]

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    val_preds = clf.predict(X_val)
    acc = float(accuracy_score(y_val, val_preds))
    f1_macro = float(f1_score(y_val, val_preds, average="macro"))
    report = classification_report(y_val, val_preds, output_dict=True)

    model_path = ARTIFACTS_DIR / "waste_risk_model.joblib"
    joblib.dump(clf, model_path)

    metadata = {
        "model_name": "waste_risk_classifier",
        "algorithm": "RandomForestClassifier",
        "version": "1.0.0",
        "classes": classes,
        "metrics": {
            "accuracy": round(acc, 4),
            "macro_f1": round(f1_macro, 4),
            "classification_report": report,
        },
    }

    meta_path = ARTIFACTS_DIR / "risk_model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Waste risk model trained successfully:")
    print(f"   Validation Accuracy: {acc:.4f}")
    print(f"   Validation Macro F1: {f1_macro:.4f}")
    print(f"   Artifact saved:      {model_path}")


if __name__ == "__main__":
    train()
