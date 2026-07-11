"""
Build the preprocessing half of the model pipeline.

The whole point of putting this in a sklearn ColumnTransformer is
reproducibility: the median used to fill a missing cholesterol, the mean and
standard deviation used to scale age, the categories seen for chest-pain type
all get learned on the training fold and frozen inside the fitted object. At
inference the API calls the exact same transformer, so a single patient row
goes through identical maths to what the model saw during training.

Numeric features  -> median impute -> standard scale
Categorical feats -> most-frequent impute -> one-hot encode (ignore unknowns)
"""
from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import config


def build_preprocessor() -> ColumnTransformer:
    """Return an unfitted ColumnTransformer for the heart-disease features."""
    numeric_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, config.NUMERIC_FEATURES),
            ("cat", categorical_pipe, config.CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def build_pipeline(estimator) -> Pipeline:
    """Glue the preprocessor to a classifier into one fit/predict object."""
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", estimator),
        ]
    )
