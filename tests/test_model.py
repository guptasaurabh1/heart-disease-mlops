"""Tests that exercise the trained artifact through the predict helper.

These are skipped automatically if no model has been trained yet, so the
suite still passes on a fresh checkout before `python -m src.train` runs.
The CI workflow trains first, so in CI these always execute.
"""
import pytest

from src import config, predict

pytestmark = pytest.mark.skipif(
    not config.MODEL_PATH.exists(),
    reason="model not trained yet (run python -m src.train)",
)

SAMPLE = {
    "age": 63, "sex": 1, "cp": 4, "trestbps": 145, "chol": 233,
    "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3,
    "slope": 3, "ca": 0, "thal": 6,
}


def test_predict_returns_expected_keys():
    out = predict.predict(SAMPLE)
    for key in ("prediction", "label", "probability", "confidence", "risk_band"):
        assert key in out


def test_probability_in_unit_interval():
    out = predict.predict(SAMPLE)
    assert 0.0 <= out["probability"] <= 1.0
    assert 0.0 <= out["confidence"] <= 1.0


def test_label_matches_prediction():
    out = predict.predict(SAMPLE)
    assert (out["prediction"] == 1) == (out["label"] == "disease")


def test_metadata_reports_decent_auc():
    meta = predict.load_metadata()
    # sanity floor: the selected model should clear a weak baseline
    assert meta["test_metrics"]["roc_auc"] > 0.75


def test_missing_feature_is_tolerated_by_imputer():
    partial = dict(SAMPLE)
    partial.pop("chol")  # imputer should fill it
    out = predict.predict(partial)
    assert 0.0 <= out["probability"] <= 1.0
