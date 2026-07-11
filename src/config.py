"""
Central configuration for the Heart Disease MLOps project.

Everything that more than one module needs to agree on lives here: file
paths, the column schema for the UCI data, and which features are treated
as numeric vs categorical. Keeping it in one place means the training code,
the API, and the tests can never drift out of sync on column names.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

CLEAN_CSV = DATA_PROCESSED / "heart_clean.csv"
MODEL_PATH = MODELS_DIR / "model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

# ---------------------------------------------------------------------------
# Raw UCI files. Each is one collection site. Combining the four gives ~920
# rows instead of the 303 you get from Cleveland alone.
# ---------------------------------------------------------------------------
RAW_FILES = {
    "cleveland": DATA_RAW / "processed.cleveland.data",
    "hungarian": DATA_RAW / "processed.hungarian.data",
    "switzerland": DATA_RAW / "processed.switzerland.data",
    "va": DATA_RAW / "processed.va.data",
}

# The 14 columns the literature actually uses, in file order.
COLUMN_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",  # raw target, 0-4
]

TARGET_RAW = "num"
TARGET = "target"  # binary: 0 = no disease, 1 = disease present

# Feature typing for the preprocessing pipeline.
NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# MLflow
MLFLOW_EXPERIMENT = "heart-disease-classification"
MLFLOW_TRACKING_URI = "sqlite:///" + str(PROJECT_ROOT / "mlflow.db")
