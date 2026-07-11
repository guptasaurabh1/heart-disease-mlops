"""
Exploratory data analysis for the combined heart-disease dataset.

Run this as a module (python -m src.eda) to regenerate every figure in
reports/figures. The notebook in notebooks/01_eda.ipynb walks through the
same analysis cell by cell with commentary; this script is the headless
version so the CI job and the report build can reproduce the plots without
a kernel.
"""
from __future__ import annotations

import logging

import matplotlib

matplotlib.use("Agg")  # headless backend, safe in CI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import config, data_prep

logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = ["#4C72B0", "#DD8452"]
PRETTY = {
    "age": "Age (years)",
    "trestbps": "Resting BP (mm Hg)",
    "chol": "Cholesterol (mg/dl)",
    "thalach": "Max heart rate",
    "oldpeak": "ST depression (oldpeak)",
}


def _save(fig, name: str) -> None:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out = config.FIGURES_DIR / name
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", out.name)


def plot_class_balance(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(5, 4))
    counts = df[config.TARGET].value_counts().sort_index()
    bars = ax.bar(["No disease", "Disease"], counts.values, color=PALETTE)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 4, str(v), ha="center", fontweight="bold")
    ax.set_title("Target class balance")
    ax.set_ylabel("Patients")
    _save(fig, "01_class_balance.png")


def plot_missingness(df: pd.DataFrame) -> None:
    miss = df.drop(columns=[config.TARGET, "source"]).isna().mean().sort_values(ascending=False)
    miss = miss[miss > 0]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(miss.index[::-1], (miss.values[::-1] * 100), color="#C44E52")
    ax.set_xlabel("Missing (%)")
    ax.set_title("Missing values by feature")
    for i, v in enumerate(miss.values[::-1] * 100):
        ax.text(v + 0.5, i, f"{v:.0f}%", va="center", fontsize=8)
    _save(fig, "02_missingness.png")


def plot_histograms(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    axes = axes.ravel()
    for ax, col in zip(axes, config.NUMERIC_FEATURES):
        for label, color in zip([0, 1], PALETTE):
            sub = df.loc[df[config.TARGET] == label, col].dropna()
            ax.hist(sub, bins=25, alpha=0.6, color=color,
                    label="No disease" if label == 0 else "Disease")
        ax.set_title(PRETTY.get(col, col))
        ax.legend(fontsize=8)
    axes[-1].axis("off")
    fig.suptitle("Numeric feature distributions by class", fontsize=13)
    fig.tight_layout()
    _save(fig, "03_histograms.png")


def plot_correlation(df: pd.DataFrame) -> None:
    numeric = df[config.FEATURE_COLUMNS + [config.TARGET]].apply(pd.to_numeric, errors="coerce")
    corr = numeric.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, square=True, cbar_kws={"shrink": 0.7}, ax=ax,
                annot_kws={"size": 7})
    ax.set_title("Feature correlation heatmap")
    _save(fig, "04_correlation_heatmap.png")


def plot_disease_by_source(df: pd.DataFrame) -> None:
    rate = df.groupby("source")[config.TARGET].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(rate.index, rate.values * 100, color="#55A868")
    for b, v in zip(bars, rate.values * 100):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", fontsize=9)
    ax.set_ylabel("Disease prevalence (%)")
    ax.set_title("Disease prevalence by collection site")
    _save(fig, "05_disease_by_source.png")


def plot_relationships(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # age vs max heart rate, colored by outcome
    for label, color in zip([0, 1], PALETTE):
        sub = df[df[config.TARGET] == label]
        axes[0].scatter(sub["age"], sub["thalach"], s=18, alpha=0.5, color=color,
                        label="No disease" if label == 0 else "Disease")
    axes[0].set_xlabel("Age (years)")
    axes[0].set_ylabel("Max heart rate")
    axes[0].set_title("Age vs max heart rate")
    axes[0].legend()

    # oldpeak distribution by class
    data = [df.loc[df[config.TARGET] == 0, "oldpeak"].dropna(),
            df.loc[df[config.TARGET] == 1, "oldpeak"].dropna()]
    axes[1].boxplot(data, tick_labels=["No disease", "Disease"], patch_artist=True,
                    boxprops=dict(facecolor="#4C72B0", alpha=0.6))
    axes[1].set_ylabel("ST depression (oldpeak)")
    axes[1].set_title("Exercise ST depression by class")
    fig.tight_layout()
    _save(fig, "06_relationships.png")


def run() -> dict:
    df = data_prep.load_clean()
    plot_class_balance(df)
    plot_missingness(df)
    plot_histograms(df)
    plot_correlation(df)
    plot_disease_by_source(df)
    plot_relationships(df)

    summary = {
        "rows": int(len(df)),
        "disease": int(df[config.TARGET].sum()),
        "no_disease": int((df[config.TARGET] == 0).sum()),
        "prevalence_pct": round(100 * df[config.TARGET].mean(), 1),
        "by_source": df.groupby("source")[config.TARGET].agg(["count", "mean"]).round(3).to_dict(),
    }
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(run())
