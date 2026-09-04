"""Train and select the Resort OS predictive-maintenance model.

Usage:  python ml/train.py
Input:  ml/training_data.csv
Output: ml/model.pkl
"""
import hashlib
import os
import pickle
from datetime import datetime, timezone

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate

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
    df = pd.read_csv(DATA_PATH)
    missing = set(NUMERIC_FEATURES + [CATEGORICAL_FEATURE, TARGET]) - set(df.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {sorted(missing)}")
    if df[NUMERIC_FEATURES + [TARGET]].isnull().any().any():
        raise ValueError("Training data contains missing numeric or target values")

    asset_types = sorted(df[CATEGORICAL_FEATURE].dropna().unique().tolist())
    if not asset_types:
        raise ValueError("Training data contains no asset types")

    # Keep the encoded schema explicit because the FastAPI inference path uses it.
    df_encoded = pd.get_dummies(df, columns=[CATEGORICAL_FEATURE], prefix="type")
    type_columns = [f"type_{asset_type}" for asset_type in asset_types]
    feature_cols = NUMERIC_FEATURES + type_columns
    for column in type_columns:
        if column not in df_encoded:
            df_encoded[column] = 0
    X = df_encoded[feature_cols]
    y = df_encoded[TARGET]

    candidates = {
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=250,
            learning_rate=0.035,
            max_depth=4,
            min_samples_leaf=8,
            subsample=0.85,
            max_features="sqrt",
            random_state=42,
        ),
        "gradient_boosting_deep": GradientBoostingClassifier(
            n_estimators=350,
            learning_rate=0.025,
            max_depth=3,
            min_samples_leaf=8,
            subsample=0.9,
            random_state=42,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=250,
            learning_rate=0.05,
            max_leaf_nodes=31,
            l2_regularization=0.5,
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=1,
            max_features="sqrt",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "roc_auc": "roc_auc",
        "average_precision": "average_precision",
        "f1": "f1",
    }
    benchmark = {}
    for name, candidate in candidates.items():
        scores = cross_validate(candidate, X, y, cv=cv, scoring=scoring, n_jobs=1)
        benchmark[name] = {
            metric: round(float(scores[f"test_{metric}"].mean()), 6)
            for metric in scoring
        }

    # Accuracy is the primary selection metric; the other metrics make ties deterministic.
    selected_name = max(
        benchmark,
        key=lambda name: (
            benchmark[name]["accuracy"],
            benchmark[name]["roc_auc"],
            benchmark[name]["f1"],
        ),
    )
    model = candidates[selected_name]
    model.fit(X, y)

    print(f"[INFO] Loaded {len(df)} samples from {DATA_PATH}")
    print(f"       Failure distribution:\n{y.value_counts().to_string()}\n")
    print("── 5-fold model benchmark ──")
    for name, metrics in benchmark.items():
        print(f"  {name:26s} accuracy={metrics['accuracy']:.4f} roc_auc={metrics['roc_auc']:.4f} f1={metrics['f1']:.4f}")
    print(f"[INFO] Selected model: {selected_name}")

    importances = getattr(model, "feature_importances_", None)
    if importances is not None:
        print("── Feature Importances ──")
        for feat, imp in sorted(zip(feature_cols, importances), key=lambda item: item[1], reverse=True):
            print(f"  {feat:40s} {imp:.4f}")

    artifact = {
        "model": model,
        "feature_cols": feature_cols,
        "numeric_features": NUMERIC_FEATURES,
        "asset_types": asset_types,
        "target": TARGET,
        "classes": model.classes_.tolist(),
        "failure_class_index": int(list(model.classes_).index(1)),
        "prediction_threshold": 0.70,
        "selected_model": selected_name,
        "cv_metrics": benchmark[selected_name],
        "all_benchmarks": benchmark,
        "training_rows": len(df),
        "training_data_sha256": hashlib.sha256(open(DATA_PATH, "rb").read()).hexdigest(),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    print(f"\n[OK] Model saved → {MODEL_PATH}")
    print(f"     Features: {feature_cols}")
    print(f"     CV accuracy: {benchmark[selected_name]['accuracy']:.4f}")


if __name__ == "__main__":
    train()
