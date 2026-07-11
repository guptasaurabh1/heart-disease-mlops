"""Tests for the preprocessing ColumnTransformer and pipeline assembly."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src import config
from src.preprocessing import build_pipeline, build_preprocessor


def _toy_frame(n=20):
    rng = np.random.default_rng(0)
    data = {}
    for col in config.NUMERIC_FEATURES:
        vals = rng.normal(150, 20, n)
        vals[0] = np.nan  # force a missing value to exercise the imputer
        data[col] = vals
    for col in config.CATEGORICAL_FEATURES:
        vals = rng.integers(0, 3, n).astype(float)
        vals[1] = np.nan
        data[col] = vals
    return pd.DataFrame(data)


def test_preprocessor_handles_missing_values():
    X = _toy_frame()
    pre = build_preprocessor()
    out = pre.fit_transform(X)
    # no NaN should survive imputation
    assert not np.isnan(out).any()


def test_preprocessor_expands_categoricals():
    X = _toy_frame()
    pre = build_preprocessor()
    out = pre.fit_transform(X)
    # one-hot encoding means more output columns than input columns
    assert out.shape[1] > len(config.FEATURE_COLUMNS)


def test_pipeline_fits_and_predicts():
    X = _toy_frame(40)
    y = pd.Series(np.r_[np.zeros(20), np.ones(20)].astype(int))
    pipe = build_pipeline(LogisticRegression(max_iter=500))
    pipe.fit(X, y)
    preds = pipe.predict(X)
    assert set(np.unique(preds)).issubset({0, 1})
    assert len(preds) == len(y)


def test_pipeline_handles_unseen_category_at_inference():
    X = _toy_frame(40)
    y = pd.Series(np.r_[np.zeros(20), np.ones(20)].astype(int))
    pipe = build_pipeline(LogisticRegression(max_iter=500))
    pipe.fit(X, y)
    # inject a category the model never saw; handle_unknown='ignore' should cope
    novel = X.iloc[[0]].copy()
    novel.loc[:, "thal"] = 99
    assert pipe.predict(novel).shape == (1,)
