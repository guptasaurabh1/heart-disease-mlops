"""
Train, tune, track, and select the heart-disease classifier.

What this does, end to end:
  * loads the clean dataset and makes a stratified train/test split,
  * defines four candidate models (logistic regression, random forest,
    XGBoost, and SVM with calibration),
  * tunes each with randomized search under stratified k-fold CV,
  * logs params, CV scores, held-out test metrics, and plot artifacts to
    MLflow under one experiment,
  * picks the winner by test recall (because in a screening context a
    missed positive case is the most costly error),
  * saves the fitted pipeline to models/model.joblib plus a metadata JSON
    the API reads at startup.

Run: python -m src.train
View runs: mlflow ui --backend-store-uri ./mlruns
"""
from __future__ import annotations

import argparse
import json
import logging
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
from scipy.stats import loguniform, randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from xgboost import XGBClassifier

from src import config, data_prep
from src.preprocessing import build_pipeline

# Squelch chatty MLflow internals during training.
logging.getLogger("mlflow.sklearn").setLevel(logging.ERROR)
logging.getLogger("mlflow.tracking").setLevel(logging.ERROR)
logging.getLogger("mlflow.store.db").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    """One model to try, with the search space for its tunable params."""

    name: str
    estimator: object
    param_dist: dict = field(default_factory=dict)
    n_iter: int = 12


def candidates() -> list[Candidate]:
    """The three models we compare. Param names are prefixed 'model__'
    because the estimator sits inside a Pipeline step named 'model'."""
    return [
        Candidate(
            name="logistic_regression",
            estimator=LogisticRegression(max_iter=3000, class_weight="balanced"),
            param_dist={
                "model__C": loguniform(1e-2, 5e1),
                "model__solver": ["lbfgs", "saga"],
            },
            n_iter=12,
        ),
        Candidate(
            name="random_forest",
            estimator=RandomForestClassifier(
                class_weight="balanced", random_state=config.RANDOM_STATE
            ),
            param_dist={
                "model__n_estimators": randint(100, 400),
                "model__max_depth": randint(4, 10),
                "model__min_samples_split": randint(2, 10),
                "model__min_samples_leaf": randint(1, 6),
                "model__max_features": ["sqrt", "log2", None],
            },
            n_iter=20,
        ),
        Candidate(
            name="xgboost",
            estimator=XGBClassifier(
                eval_metric="logloss",
                random_state=config.RANDOM_STATE,
                tree_method="hist",
            ),
            param_dist={
                "model__n_estimators": randint(100, 500),
                "model__max_depth": randint(3, 9),
                "model__learning_rate": loguniform(1e-2, 2e-1),
                "model__subsample": loguniform(0.5, 1.0),
                "model__colsample_bytree": loguniform(0.5, 1.0),
                "model__reg_lambda": loguniform(1e-2, 5e0),
            },
            n_iter=20,
        ),
        Candidate(
            name="svm",
            estimator=CalibratedClassifierCV(
                estimator=SVC(random_state=config.RANDOM_STATE, probability=True)
            ),
            param_dist={
                "model__estimator__C": loguniform(1e-2, 5e1),
                "model__estimator__gamma": loguniform(1e-3, 1e-1),
                "model__estimator__kernel": ["rbf", "poly", "sigmoid"],
            },
            n_iter=12,
        ),
    ]


def evaluate(model, X, y) -> dict:
    """Compute the full metric set on a held-out split."""
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "roc_auc": roc_auc_score(y, proba),
    }


def _log_plots(model, X_test, y_test, run_name: str) -> None:
    """Render ROC curve and confusion matrix, log both to the active run."""
    fig, ax = plt.subplots(figsize=(5, 5))
    RocCurveDisplay.from_estimator(model, X_test, y_test, ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", alpha=0.6)
    ax.set_title(f"ROC curve - {run_name}")
    mlflow.log_figure(fig, f"plots/roc_{run_name}.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_estimator(
        model, X_test, y_test, ax=ax, cmap="Blues",
        display_labels=["No disease", "Disease"],
    )
    ax.set_title(f"Confusion matrix - {run_name}")
    mlflow.log_figure(fig, f"plots/confusion_{run_name}.png")
    plt.close(fig)


def train(seed: int = config.RANDOM_STATE) -> dict:
    df = data_prep.load_clean()
    X = df[config.FEATURE_COLUMNS]
    y = df[config.TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=seed
    )
    logger.info("Train %d rows, test %d rows", len(X_train), len(X_test))

    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=seed)

    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT)

    results = []
    for cand in candidates():
        with mlflow.start_run(run_name=cand.name):
            pipe = build_pipeline(cand.estimator)
            search = RandomizedSearchCV(
                pipe,
                param_distributions=cand.param_dist,
                n_iter=cand.n_iter,
                scoring="roc_auc",
                cv=cv,
                random_state=seed,
                n_jobs=-1,
                refit=True,
            )
            search.fit(X_train, y_train)
            best = search.best_estimator_

            test_metrics = evaluate(best, X_test, y_test)
            cv_auc = float(search.best_score_)

            mlflow.log_param("model_type", cand.name)
            mlflow.log_params({k: str(v) for k, v in search.best_params_.items()})
            mlflow.log_metric("cv_roc_auc", cv_auc)
            for metric, value in test_metrics.items():
                mlflow.log_metric(f"test_{metric}", value)

            _log_plots(best, X_test, y_test, cand.name)
            mlflow.sklearn.log_model(best, name="model")

            logger.info(
                "%-20s cv_auc=%.3f  test_auc=%.3f  acc=%.3f  recall=%.3f",
                cand.name, cv_auc, test_metrics["roc_auc"],
                test_metrics["accuracy"], test_metrics["recall"],
            )

            results.append({
                "name": cand.name,
                "cv_roc_auc": cv_auc,
                "best_params": {k: str(v) for k, v in search.best_params_.items()},
                "test_metrics": test_metrics,
                "estimator": best,
            })

    winner = max(results, key=lambda r: r["test_metrics"]["recall"])
    logger.info("Best model: %s (test recall %.3f)",
                winner["name"], winner["test_metrics"]["recall"])

    # Persist the winning pipeline and metadata for the API.
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(winner["estimator"], config.MODEL_PATH)

    metadata = {
        "model_type": winner["name"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": config.FEATURE_COLUMNS,
        "numeric_features": config.NUMERIC_FEATURES,
        "categorical_features": config.CATEGORICAL_FEATURES,
        "cv_roc_auc": winner["cv_roc_auc"],
        "test_metrics": winner["test_metrics"],
        "best_params": winner["best_params"],
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "all_models": [
            {"name": r["name"], "cv_roc_auc": r["cv_roc_auc"],
             "test_metrics": r["test_metrics"]}
            for r in results
        ],
    }
    config.METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    logger.info("Saved model to %s", config.MODEL_PATH)

    return metadata


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=config.RANDOM_STATE)
    args = parser.parse_args()
    meta = train(seed=args.seed)
    print(json.dumps({k: v for k, v in meta.items() if k != "all_models"}, indent=2))
