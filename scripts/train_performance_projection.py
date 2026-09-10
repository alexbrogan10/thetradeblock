#!/usr/bin/env python3
"""Trains the Player Performance Projection model (Section 38).

Predicts a player's *next*-season performance score from features known
as of the prior season -- age, position, prior performance, prior
availability, and current contract terms (used as a proxy for "contract
situation at prediction time," since this dataset has no historical
contract table; see app/ml/features.py docstring).

Leakage prevention: every feature is derived from data at or before the
prediction point; the target season's own stats are never used as a
feature for that same season.

Run from the repo root (so the model lands in ./models/) with the
backend package importable, e.g.:

    cd backend && python ../scripts/train_performance_projection.py

Outputs:
  - models/player_performance_projection_v1.joblib  (the fitted pipeline)
  - a `model_versions` row recording features/parameters/metrics/limitations
    (Section 39 -- Model Versioning)
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

import joblib  # noqa: E402

from app.database.session import SessionLocal  # noqa: E402
from app.ml.features import FEATURE_COLUMNS, build_feature_row  # noqa: E402
from app.models.contract import Contract  # noqa: E402
from app.models.model_version import ModelVersion  # noqa: E402
from app.models.player import Player  # noqa: E402
from app.models.player_statistic import PlayerStatistic  # noqa: E402
from app.ml.features import performance_score_for_season  # noqa: E402

MODEL_DIR = REPO_ROOT / "models"
MODEL_PATH = MODEL_DIR / "player_performance_projection_v1.joblib"
MODEL_NAME = "player-performance-projection"
MODEL_VERSION = "v1.0"


def build_training_data(db) -> pd.DataFrame:
    rows = []
    players = db.query(Player).all()
    for player in players:
        seasons = (
            db.query(PlayerStatistic)
            .filter(PlayerStatistic.player_id == player.id)
            .order_by(PlayerStatistic.season)
            .all()
        )
        if len(seasons) < 2:
            continue  # need a prior season to predict a later one

        prior_season, target_season = seasons[-2], seasons[-1]
        contract = db.query(Contract).filter(Contract.player_id == player.id).first()

        feature_row = build_feature_row(player, prior_season, contract)
        target = performance_score_for_season(player.position, target_season.stats or {})

        record = feature_row.as_dict()
        record["target_performance"] = target
        rows.append(record)

    return pd.DataFrame(rows)


def main():
    db = SessionLocal()
    try:
        df = build_training_data(db)
        if len(df) < 20:
            print(f"Only {len(df)} training rows available; need at least 20. "
                  "Run scripts/seed_demo_data.py first.")
            return

        X = df[FEATURE_COLUMNS]
        y = df["target_performance"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        preprocessor = ColumnTransformer(
            transformers=[("position", OneHotEncoder(handle_unknown="ignore"), ["position"])],
            remainder="passthrough",
        )
        n_estimators = 200
        max_depth = 6
        model = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "regressor",
                    RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42),
                ),
            ]
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = mean_squared_error(y_test, preds) ** 0.5
        r2 = r2_score(y_test, preds)

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        db.query(ModelVersion).filter(ModelVersion.model_name == MODEL_NAME).delete()
        db.add(
            ModelVersion(
                model_name=MODEL_NAME,
                version=MODEL_VERSION,
                features=FEATURE_COLUMNS,
                parameters={
                    "model_type": "RandomForestRegressor",
                    "n_estimators": n_estimators,
                    "max_depth": max_depth,
                    "random_state": 42,
                },
                evaluation_metrics={
                    "mae": round(float(mae), 2),
                    "rmse": round(float(rmse), 2),
                    "r2": round(float(r2), 3),
                    "n_train": len(X_train),
                    "n_test": len(X_test),
                },
                dataset_version="demo-synthetic-v1",
                limitations=[
                    "Trained on a single synthetic season-to-season transition per "
                    "player (2024->2025 in the demo dataset); not validated against "
                    "real-world outcomes.",
                    "Uses each player's CURRENT contract as a proxy for their "
                    "contract situation at prediction time -- there is no historical "
                    "contract table in this dataset.",
                    "The train/test split is a random hold-out, not a season-based "
                    "split, because only one transition exists per player here. A "
                    "real deployment with multiple seasons per player MUST use a "
                    "season-based split to avoid leakage.",
                ],
            )
        )
        db.commit()

        print(f"Trained on {len(X_train)} rows, tested on {len(X_test)}.")
        print(f"MAE={mae:.2f}  RMSE={rmse:.2f}  R2={r2:.3f}")
        print(f"Saved model to {MODEL_PATH}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
