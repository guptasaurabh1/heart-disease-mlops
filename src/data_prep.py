"""
Load the raw UCI heart-disease files, clean them, and write one tidy CSV.

The four processed.*.data files share the same 14-column layout but use the
string "?" for missing values and code the target from 0 to 4. This module:

  * reads each file and tags it with its source site,
  * converts "?" to real NaN,
  * collapses the 0-4 target down to a binary present/absent label,
  * fixes a known data-quality issue (cholesterol recorded as 0),
  * returns a single DataFrame (and can persist it to disk).

I deliberately do NOT impute here. Imputation belongs inside the sklearn
Pipeline so the exact same fill values learned on the training fold get
reused at inference time. Doing it here would leak test statistics.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def _read_one(path, site: str) -> pd.DataFrame:
    """Read a single site file into a DataFrame with the standard schema."""
    df = pd.read_csv(path, header=None, names=config.COLUMN_NAMES, na_values=["?"])
    df["source"] = site
    logger.info("Loaded %-12s %4d rows from %s", site, len(df), path.name)
    return df


def load_raw() -> pd.DataFrame:
    """Concatenate all four collection sites into one frame."""
    frames = [_read_one(path, site) for site, path in config.RAW_FILES.items()]
    df = pd.concat(frames, ignore_index=True)
    logger.info("Combined dataset: %d rows", len(df))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning rules and produce the binary target.

    Steps:
      1. Coerce every feature column to numeric (some arrive as object
         because of the "?" markers).
      2. Treat chol == 0 as missing. A serum cholesterol of zero is not
         physiologically real; it is how the Switzerland site encoded
         "not measured".
      3. Binarize the target: anything > 0 means disease present.
    """
    df = df.copy()

    for col in config.FEATURE_COLUMNS + [config.TARGET_RAW]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # chol == 0 is a placeholder, not a measurement.
    zero_chol = (df["chol"] == 0).sum()
    if zero_chol:
        logger.info("Recoding %d rows with chol == 0 to NaN", zero_chol)
        df.loc[df["chol"] == 0, "chol"] = np.nan

    # Same trick is sometimes used for resting blood pressure.
    zero_bps = (df["trestbps"] == 0).sum()
    if zero_bps:
        logger.info("Recoding %d rows with trestbps == 0 to NaN", zero_bps)
        df.loc[df["trestbps"] == 0, "trestbps"] = np.nan

    df[config.TARGET] = (df[config.TARGET_RAW] > 0).astype(int)
    df = df.drop(columns=[config.TARGET_RAW])

    return df


def build_dataset(save: bool = True) -> pd.DataFrame:
    """Full path from raw files to a clean DataFrame, optionally saved to CSV."""
    df = clean(load_raw())
    if save:
        config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        df.to_csv(config.CLEAN_CSV, index=False)
        logger.info("Wrote cleaned dataset to %s", config.CLEAN_CSV)
    return df


def load_clean() -> pd.DataFrame:
    """Read the cleaned CSV, building it first if it does not exist yet."""
    if not config.CLEAN_CSV.exists():
        return build_dataset(save=True)
    return pd.read_csv(config.CLEAN_CSV)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    frame = build_dataset(save=True)
    print(frame.head())
    print("\nShape:", frame.shape)
    print("\nTarget balance:\n", frame[config.TARGET].value_counts())
    print("\nMissing per column:\n", frame.isna().sum())
