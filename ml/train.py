"""
Resort OS — PEMS Model Training
Trains a Random Forest classifier on synthetic room-asset data.

Usage:  python ml/train.py
Input:  ml/training_data.csv
Output: ml/model.pkl
"""
import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(MODEL_DIR, "training_data.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ── Feature columns ─────────────────────────────────────────────────────
NUMERIC_FEATURES = [
    "power_draw",
    "usage_hours",
    "operating_hours_since_service",
    "error_log_count",
]
CATEGORICAL_FEATURE = "asset_type"
TARGET = "failure"


def train():
    # Load data
    df = pd.read_csv(DATA_PATH)
    print(f"[INFO] Loaded {len(df)} samples from {DATA_PATH}")
    print(f"       Failure distribution:\n{df[TARGET].value_counts().to_string()}\n")

    # Encode asset_type as one-hot
    df_encoded = pd.get_dummies(df, columns=[CATEGORICAL_FEATURE], prefix="type")
    feature_cols = NUMERIC_FEATURES + [c for c in df_encoded.columns if c.startswith("type_")]

    X = df_encoded[feature_cols]
    y = df_encoded[TARGET]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("── Classification Report ──")
    print(classification_report(y_test, y_pred, target_names=["No Failure", "Failure"]))

    # Feature importances
    importances = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    print("── Feature Importances ──")
    for feat, imp in importances:
        bar = "█" * int(imp * 50)
        print(f"  {feat:40s} {imp:.4f}  {bar}")

    # Save model + metadata
    artifact = {
        "model": model,
        "feature_cols": feature_cols,
        "numeric_features": NUMERIC_FEATURES,
        "asset_types": ["AC", "TV", "Set-top box"],
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    print(f"\n[OK] Model saved → {MODEL_PATH}")
    print(f"     Features: {feature_cols}")


if __name__ == "__main__":
    train()
