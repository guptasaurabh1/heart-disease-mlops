"""Generate notebooks/01_eda.ipynb programmatically so it stays in sync
with the source modules and is valid JSON."""
from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# Heart Disease - Exploratory Data Analysis

This notebook explores the combined UCI Heart Disease dataset (four collection
sites: Cleveland, Hungary, Switzerland, Long Beach VA). It mirrors `src/eda.py`
so the figures here match the ones the headless pipeline produces for the
report and CI.

Sections:
1. Load the cleaned data
2. Target balance
3. Missing values
4. Numeric distributions by class
5. Correlation structure
6. Disease prevalence by site
7. Feature relationships
8. Takeaways for modelling
""")

code("""import sys, os
sys.path.append(os.path.abspath(".."))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import config, data_prep

sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.max_columns", None)
""")

md("""## 1. Load the cleaned data

`data_prep.load_clean()` builds the dataset on first call: it concatenates the
four sites, converts `?` markers to NaN, recodes `chol == 0` (a 'not measured'
placeholder) to NaN, and binarizes the 0-4 target into present/absent.""")

code("""df = data_prep.load_clean()
print("Shape:", df.shape)
df.head()""")

code("""df.describe(include="all").T""")

md("""## 2. Target balance

The combined dataset is close to balanced, which is healthier than the
Cleveland-only version. We still report precision/recall, not just accuracy,
because the cost of a false negative (a missed case) is high in screening.""")

code("""ax = df["target"].value_counts().sort_index().plot(
    kind="bar", color=["#4C72B0", "#DD8452"], rot=0)
ax.set_xticklabels(["No disease", "Disease"])
ax.set_title("Target class balance")
print(df["target"].value_counts(normalize=True).round(3).to_dict())
plt.show()""")

md("""## 3. Missing values

`ca`, `thal`, and `slope` are missing for large fractions of rows, mostly from
the non-Cleveland sites. This is why imputation lives inside the pipeline: the
fill values get learned on training data and reused at inference.""")

code("""miss = df.drop(columns=["target", "source"]).isna().mean().sort_values(ascending=False)
print((miss[miss > 0] * 100).round(1))
miss[miss > 0].mul(100).sort_values().plot(kind="barh", color="#C44E52")
plt.xlabel("Missing (%)"); plt.title("Missing values by feature"); plt.show()""")

md("""## 4. Numeric distributions by class

Overlaying the two classes shows where they separate. `thalach` (max heart
rate) and `oldpeak` (exercise ST depression) shift visibly between groups.""")

code("""num = config.NUMERIC_FEATURES
fig, axes = plt.subplots(2, 3, figsize=(14, 7)); axes = axes.ravel()
for ax, col in zip(axes, num):
    for label, color in zip([0, 1], ["#4C72B0", "#DD8452"]):
        ax.hist(df.loc[df.target == label, col].dropna(), bins=25, alpha=0.6,
                color=color, label="No disease" if label == 0 else "Disease")
    ax.set_title(col); ax.legend(fontsize=8)
axes[-1].axis("off"); plt.tight_layout(); plt.show()""")

md("""## 5. Correlation structure

Strongest correlates of the target: `thal`, `cp`, `exang`, `ca` (positive) and
`thalach` (negative). No pair of predictors is so collinear that we need to
drop one.""")

code("""corr = df[config.FEATURE_COLUMNS + ["target"]].apply(pd.to_numeric, errors="coerce").corr()
plt.figure(figsize=(11, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            square=True, annot_kws={"size": 7})
plt.title("Feature correlation heatmap"); plt.show()
print(corr["target"].drop("target").sort_values(ascending=False).round(2))""")

md("""## 6. Disease prevalence by site

Prevalence ranges widely across sites (Hungary ~36%, Switzerland ~94%). That
is why `source` is kept out of the model features: it would let the model cheat
off site identity instead of learning clinical signal.""")

code("""rate = df.groupby("source")["target"].agg(["count", "mean"]).round(3)
print(rate)
(rate["mean"] * 100).plot(kind="bar", color="#55A868", rot=0)
plt.ylabel("Disease prevalence (%)"); plt.title("Prevalence by site"); plt.show()""")

md("""## 7. Feature relationships""")

code("""fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for label, color in zip([0, 1], ["#4C72B0", "#DD8452"]):
    s = df[df.target == label]
    axes[0].scatter(s.age, s.thalach, s=18, alpha=0.5, color=color,
                    label="No disease" if label == 0 else "Disease")
axes[0].set_xlabel("Age"); axes[0].set_ylabel("Max heart rate")
axes[0].set_title("Age vs max heart rate"); axes[0].legend()
df.boxplot(column="oldpeak", by="target", ax=axes[1])
axes[1].set_title("ST depression by class"); plt.suptitle("")
plt.tight_layout(); plt.show()""")

md("""## 8. Takeaways for modelling

- The dataset is roughly balanced, so accuracy is meaningful but recall still
  matters most for a screening tool.
- Missingness is heavy in `ca`, `thal`, `slope`. Median / most-frequent
  imputation inside the pipeline handles it without leaking test statistics.
- `thal`, `cp`, `exang`, `ca`, `oldpeak`, and `thalach` carry the most signal.
- `source` is excluded from features to avoid leaking site prevalence.

Next: `python -m src.train` fits Logistic Regression, Random Forest, and
XGBoost with tuning and cross-validation, logging everything to MLflow.
""")

nb["cells"] = cells
out = Path("notebooks/01_eda.ipynb")
nbf.write(nb, out)
print("Wrote", out, "with", len(cells), "cells")
