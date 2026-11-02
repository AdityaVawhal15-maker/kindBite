"""
KindBite — Data Preprocessing & Feature Engineering
Loads synthetic restaurant dataset, constructs temporal, environmental,
and food category features, and prepares train/test splits.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
SYNTHETIC_CSV = DATA_DIR / "synthetic" / "mumbai_restaurant_demand_surplus.csv"
PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = ROOT_DIR / "ml" / "models" / "artifacts"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def encode_cyclical(df: pd.DataFrame, col: str, max_val: int) -> pd.DataFrame:
    """Encode cyclical features (day of week, month) using sine and cosine."""
    df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / max_val)
    df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / max_val)
    return df


def preprocess():
    print("🧹 Starting data preprocessing and feature engineering...")
    if not SYNTHETIC_CSV.exists():
        print(f"Dataset not found at {SYNTHETIC_CSV}. Running generator first...")
        from ml.scripts.generate_dataset import generate
        generate()

    df = pd.read_csv(SYNTHETIC_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["date", "restaurant_id", "food_item_id"]).reset_index(drop=True)

    # Cyclical features
    df = encode_cyclical(df, "day_of_week", 7)
    df = encode_cyclical(df, "month", 12)

    # Rolling average demand per (restaurant, item) to simulate kitchen history
    df["rolling_avg_demand_7d"] = (
        df.groupby(["restaurant_id", "food_item_id"])["actual_demand_kg"]
        .transform(lambda x: x.shift(1).rolling(window=7, min_periods=1).mean())
    )
    # Fill initial missing values with actual demand
    df["rolling_avg_demand_7d"] = df["rolling_avg_demand_7d"].fillna(df["actual_demand_kg"])

    # Categorical columns to encode
    cat_cols = ["restaurant_type", "food_category", "dietary_label", "weather_condition"]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded_cats = encoder.fit_transform(df[cat_cols])
    cat_feature_names = encoder.get_feature_names_out(cat_cols)
    encoded_cat_df = pd.DataFrame(encoded_cats, columns=cat_feature_names, index=df.index)

    # Numerical feature columns for scaling
    num_cols = [
        "temperature_celsius",
        "humidity_percent",
        "precipitation_mm",
        "price_inr",
        "shelf_life_hours",
        "festival_multiplier",
        "rolling_avg_demand_7d",
    ]
    scaler = StandardScaler()
    scaled_nums = scaler.fit_transform(df[num_cols])
    scaled_num_df = pd.DataFrame(scaled_nums, columns=[f"{c}_scaled" for c in num_cols], index=df.index)

    # Base feature set
    base_features = [
        "is_weekend",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
    ]

    # Combine all engineered features
    X_features = pd.concat([df[base_features], scaled_num_df, encoded_cat_df], axis=1)

    # Save preprocessing metadata & transformers
    pipeline_artifacts = {
        "encoder": encoder,
        "scaler": scaler,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "base_features": base_features,
        "feature_names": list(X_features.columns),
    }
    joblib.dump(pipeline_artifacts, ARTIFACTS_DIR / "preprocessing_pipeline.joblib")

    # Attach targets and identifier metadata
    processed_df = pd.concat([
        df[["date", "restaurant_id", "food_item_id", "food_name", "prepared_quantity_kg", "actual_demand_kg", "surplus_quantity_kg", "surplus_percentage", "waste_risk"]],
        X_features,
    ], axis=1)

    # Time-based split: First 80% train, next 10% validation, last 10% test
    n = len(processed_df)
    train_end = int(n * 0.80)
    val_end = int(n * 0.90)

    train_df = processed_df.iloc[:train_end]
    val_df = processed_df.iloc[train_end:val_end]
    test_df = processed_df.iloc[val_end:]

    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)

    print(f"✅ Processed dataset:")
    print(f"   Train samples: {len(train_df):,}")
    print(f"   Val samples:   {len(val_df):,}")
    print(f"   Test samples:  {len(test_df):,}")
    print(f"   Feature count: {len(X_features.columns)}")
    print(f"   Pipeline artifact saved: {ARTIFACTS_DIR / 'preprocessing_pipeline.joblib'}")


if __name__ == "__main__":
    preprocess()
