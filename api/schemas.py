"""Pydantic models that define and validate the API contract."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PatientFeatures(BaseModel):
    """One patient record. Ranges follow the UCI codebook; values outside
    them are rejected before they reach the model."""

    age: float = Field(..., ge=1, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=1, le=4, description="Chest pain type (1-4)")
    trestbps: float = Field(..., ge=50, le=260, description="Resting blood pressure mm Hg")
    chol: float = Field(..., ge=0, le=700, description="Serum cholesterol mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG result (0-2)")
    thalach: float = Field(..., ge=50, le=260, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina")
    oldpeak: float = Field(..., ge=-3, le=10, description="ST depression vs rest")
    slope: int = Field(..., ge=1, le=3, description="Slope of peak exercise ST (1-3)")
    ca: int = Field(..., ge=0, le=3, description="Major vessels colored (0-3)")
    thal: int = Field(..., ge=3, le=7, description="Thalassemia (3, 6, 7)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 63, "sex": 1, "cp": 4, "trestbps": 145, "chol": 233,
                "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0,
                "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6,
            }
        }
    }


class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="0 = no disease, 1 = disease")
    label: str
    probability: float = Field(..., description="P(disease)")
    confidence: float = Field(..., description="Confidence in the returned label")
    risk_band: str = Field(..., description="low / moderate / high")
    model_type: Optional[str] = None

    model_config = {"protected_namespaces": ()}


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_type: Optional[str] = None

    model_config = {"protected_namespaces": ()}
