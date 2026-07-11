"""
Inference helper shared by the API and the tests.

Loads the fitted pipeline and metadata once, then exposes a single predict()
that takes a plain dict of raw feature values and returns the label, the
probability of disease, and a human-readable risk band. Because the saved
object is the full Pipeline (preprocessing + model), a raw patient record
goes through the identical imputation, scaling, and encoding seen in
training. No feature engineering is duplicated here.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache

import joblib
import pandas as pd

from src import config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_model():
    """Load and cache the fitted pipeline. Raises if it was never trained."""
    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No model at {config.MODEL_PATH}. Run `python -m src.train` first."
        )
    model = joblib.load(config.MODEL_PATH)
    logger.info("Loaded model from %s", config.MODEL_PATH)
    return model


@lru_cache(maxsize=1)
def load_metadata() -> dict:
    if config.METADATA_PATH.exists():
        return json.loads(config.METADATA_PATH.read_text())
    return {}


def _risk_band(prob: float) -> str:
    if prob < 0.34:
        return "low"
    if prob < 0.67:
        return "moderate"
    return "high"


def predict(features: dict) -> dict:
    """Score one patient.

    `features` must contain the 13 model inputs (see config.FEATURE_COLUMNS).
    Missing keys are allowed and become NaN, which the imputer fills, but the
    API layer enforces the full schema before reaching here.
    """
    model = load_model()
    row = {col: features.get(col) for col in config.FEATURE_COLUMNS}
    frame = pd.DataFrame([row], columns=config.FEATURE_COLUMNS)

    proba = float(model.predict_proba(frame)[0, 1])
    label = int(proba >= 0.5)

    return {
        "prediction": label,
        "label": "disease" if label == 1 else "no_disease",
        "probability": round(proba, 4),
        "confidence": round(proba if label == 1 else 1 - proba, 4),
        "risk_band": _risk_band(proba),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sample = {
        "age": 63, "sex": 1, "cp": 4, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3,
        "slope": 3, "ca": 0, "thal": 6,
    }
    print(predict(sample))
