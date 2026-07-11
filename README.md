# Heart Disease Risk Prediction — End-to-End MLOps

**MLOps (AIMLCZG523) — Assignment 01**
**Saurabh Gupta — 2024AC05396**

Predict the presence of heart disease from patient health data and serve the
model as a containerized, monitored API. This repository covers the full
lifecycle: data cleaning, EDA, model training with experiment tracking, a
reproducible serving pipeline, CI/CD, containerization, Kubernetes deployment,
and monitoring.

The dataset is the UCI Heart Disease set. Rather than using only the Cleveland
subset (303 rows), this project combines all four collection sites (Cleveland,
Hungary, Switzerland, Long Beach VA) into a single ~920-row dataset, which
gives real missing values to handle and a richer analysis.

## Results at a glance

Four models were tuned with randomized search under 5-fold stratified
cross-validation. XGBoost was selected on held-out recall/ROC-AUC (highest
recall matters most in a screening context).

| Model | CV ROC-AUC | Test ROC-AUC | Accuracy | Precision | Recall | F1 |
|-------|-----------:|-------------:|---------:|----------:|-------:|---:|
| Logistic Regression | 0.881 | 0.895 | 0.799 | 0.816 | 0.824 | 0.820 |
| Random Forest | 0.883 | 0.909 | 0.815 | 0.827 | 0.843 | 0.835 |
| **XGBoost (selected)** | 0.877 | **0.909** | 0.848 | 0.818 | **0.912** | 0.849 |
| SVM (RBF, calibrated) | 0.883 | 0.900 | 0.793 | 0.786 | 0.863 | 0.822 |

Numbers come from a fixed seed (42); rerun `python -m src.train` to reproduce.

## Quick start

```bash
# 1. Environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Data -> EDA -> train
python data/download_data.py --check     # verify bundled raw files
python -m src.data_prep                   # build data/processed/heart_clean.csv
python -m src.eda                         # write reports/figures/*.png
python -m src.train                       # train, tune, log to MLflow, save model

# 3. Inspect experiments
PYTHONWARNINGS=ignore::FutureWarning mlflow ui --backend-store-uri sqlite:///mlflow.db  # http://localhost:5000

# 4. Serve locally
uvicorn api.main:app --reload             # http://localhost:8000/docs

# 5. Tests + lint
pytest -q
ruff check .
```

A `Makefile` wraps these: `make install`, `make data`, `make eda`, `make train`,
`make test`, `make lint`, `make serve`, `make docker-build`, `make compose-up`.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + whether the model loaded |
| POST | `/predict` | JSON patient record → prediction, probability, confidence |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | Swagger UI |

```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":4,"trestbps":145,"chol":233,"fbs":1,"restecg":2,
       "thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
# -> {"prediction":1,"label":"disease","probability":0.8017,"confidence":0.8017,
#     "risk_band":"high","model_type":"xgboost"}
```

## Docker

```bash
docker build -t heart-disease-api:latest -f docker/Dockerfile .
docker run --rm -p 8000:8000 heart-disease-api:latest
bash scripts/smoke_test.sh                # hits /health, /predict, /metrics
```

## Full stack with monitoring

```bash
docker compose up --build
# API        http://localhost:8000/docs
# Prometheus http://localhost:9090
# Grafana    http://localhost:3000  (admin / admin), dashboard "Heart Disease API"
```

## Kubernetes

```bash
# raw manifests
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl get svc heart-api

# or Helm
helm install heart k8s/helm/heart-api
```

On Minikube, build the image into the cluster (`eval $(minikube docker-env)`
before `docker build`) and reach the service with `minikube service heart-api`.

## Project structure

```
heart-disease-mlops/
├── api/                  FastAPI app + pydantic schemas
├── data/
│   ├── raw/              four UCI site files + codebook (committed)
│   ├── processed/        cleaned CSV (generated)
│   └── download_data.py  fetch/verify raw data
├── src/
│   ├── config.py         paths + feature schema
│   ├── data_prep.py      load, clean, binarize
│   ├── preprocessing.py  ColumnTransformer pipeline
│   ├── eda.py            headless figure generation
│   ├── train.py          train + tune + MLflow + select
│   └── predict.py        inference helper
├── notebooks/01_eda.ipynb
├── tests/                pytest suite (data, preprocessing, model, api)
├── models/               saved pipeline + metadata (generated)
├── docker/Dockerfile
├── docker-compose.yml
├── monitoring/           prometheus.yml + grafana provisioning + dashboard
├── k8s/                  deployment, service, ingress, Helm chart
├── .github/workflows/ci.yml
├── reports/figures/      EDA + architecture + ROC/confusion plots
└── scripts/              smoke test, notebook generator
```

## Reproducibility notes

- The full preprocessing (impute → scale → one-hot) is saved inside the model
  pipeline, so inference reuses the exact transforms learned at training time.
- A fixed random seed (42) makes splits, CV, and tuning deterministic.
- Raw data is committed so the project runs offline and in CI.
- The CI pipeline fails on lint errors, test failures, or training errors and
  uploads the model, figures, and MLflow runs as artifacts.

## Video demo

Full walkthrough of the pipeline (EDA → training → MLflow → API → Docker →
CI/CD → Kubernetes → monitoring): **[add your video link here]**

## License / data attribution

UCI Heart Disease dataset. Principal investigators: Andras Janosi (Hungarian
Institute of Cardiology), William Steinbrunn (University Hospital Zurich),
Matthias Pfisterer (University Hospital Basel), Robert Detrano (V.A. Medical
Center, Long Beach and Cleveland Clinic Foundation).
