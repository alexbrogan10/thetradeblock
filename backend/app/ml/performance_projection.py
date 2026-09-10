"""Runtime inference for the Player Performance Projection model
(Section 38). Training happens offline in
scripts/train_performance_projection.py; this module only loads the
already-fit model and serves predictions.

If the model hasn't been trained yet, every function here returns None
rather than raising -- the app must work (with the Phase 1-4 heuristic
projection) whether or not this optional ML model has been trained.
"""
from pathlib import Path

import joblib
import pandas as pd

from app.config import settings
from app.ml.features import FeatureRow

MODEL_PATH = Path(settings.model_dir) / "player_performance_projection_v1.joblib"

_model_cache = None
_cache_checked = False


def _load_model():
    global _model_cache, _cache_checked
    if not _cache_checked:
        _cache_checked = True
        if MODEL_PATH.exists():
            _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def is_model_available() -> bool:
    return _load_model() is not None


def predict_next_season_performance(feature_row: FeatureRow) -> dict | None:
    model = _load_model()
    if model is None:
        return None

    row = pd.DataFrame([feature_row.as_dict()])
    prediction = float(model.predict(row)[0])
    prediction = max(0.0, min(100.0, prediction))

    regressor = model.named_steps["regressor"]
    preprocessor = model.named_steps["preprocess"]
    feature_names = preprocessor.get_feature_names_out()
    importances = list(zip(feature_names, regressor.feature_importances_))
    importances.sort(key=lambda kv: kv[1], reverse=True)

    return {
        "predicted_performance_score": round(prediction, 1),
        "top_features": [
            {"feature": _clean_feature_name(name), "importance": round(float(value), 3)}
            for name, value in importances[:5]
        ],
    }


def _clean_feature_name(name: str) -> str:
    # ColumnTransformer prefixes one-hot columns like "position__QB" and
    # passthrough columns like "remainder__age" -- strip to something
    # readable for the UI.
    return name.split("__", 1)[-1]
