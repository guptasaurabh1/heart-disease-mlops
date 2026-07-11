"""Tests for the data loading and cleaning layer."""
import pandas as pd

from src import config, data_prep


def test_load_raw_combines_all_sites():
    df = data_prep.load_raw()
    assert len(df) == 920
    assert set(df["source"].unique()) == {"cleveland", "hungarian", "switzerland", "va"}
    # the 14 named columns plus the source tag
    assert "num" in df.columns


def test_clean_binarizes_target():
    df = data_prep.clean(data_prep.load_raw())
    assert config.TARGET in df.columns
    assert config.TARGET_RAW not in df.columns
    assert set(df[config.TARGET].unique()).issubset({0, 1})


def test_clean_recodes_zero_cholesterol_to_nan():
    raw = data_prep.load_raw()
    n_zero = int((pd.to_numeric(raw["chol"], errors="coerce") == 0).sum())
    cleaned = data_prep.clean(raw)
    # every original zero should now be NaN, none should remain as 0
    assert (cleaned["chol"] == 0).sum() == 0
    assert cleaned["chol"].isna().sum() >= n_zero


def test_clean_handles_question_mark_markers():
    df = data_prep.clean(data_prep.load_raw())
    # ca/thal carry a lot of missingness once "?" becomes NaN
    assert df["ca"].isna().sum() > 0
    assert df["thal"].isna().sum() > 0


def test_feature_columns_present_after_clean():
    df = data_prep.clean(data_prep.load_raw())
    for col in config.FEATURE_COLUMNS:
        assert col in df.columns


def test_target_not_all_one_class():
    df = data_prep.clean(data_prep.load_raw())
    counts = df[config.TARGET].value_counts()
    assert counts.min() > 0 and len(counts) == 2
