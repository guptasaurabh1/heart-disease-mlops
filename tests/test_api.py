"""API-level tests using FastAPI's TestClient."""
import pytest
from fastapi.testclient import TestClient

from api.main import app
from src import config

client = TestClient(app)

SAMPLE = {
    "age": 63, "sex": 1, "cp": 4, "trestbps": 145, "chol": 233,
    "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3,
    "slope": 3, "ca": 0, "thal": 6,
}

needs_model = pytest.mark.skipif(
    not config.MODEL_PATH.exists(), reason="model not trained yet"
)


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert "docs" in r.json()


def test_metrics_endpoint_exposes_prometheus():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "api_requests_total" in r.text


@needs_model
def test_health_reports_model_loaded():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is True


@needs_model
def test_predict_returns_valid_payload():
    r = client.post("/predict", json=SAMPLE)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["probability"] <= 1.0
    assert body["risk_band"] in ("low", "moderate", "high")


def test_predict_rejects_out_of_range_age():
    bad = dict(SAMPLE)
    bad["age"] = 999
    assert client.post("/predict", json=bad).status_code == 422


def test_predict_rejects_missing_required_field():
    bad = dict(SAMPLE)
    bad.pop("age")
    assert client.post("/predict", json=bad).status_code == 422


def test_predict_rejects_bad_sex_value():
    bad = dict(SAMPLE)
    bad["sex"] = 5
    assert client.post("/predict", json=bad).status_code == 422
