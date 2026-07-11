"""
FastAPI service for heart-disease risk scoring.

Endpoints:
  GET  /          banner + links
  GET  /health    liveness + whether the model loaded
  POST /predict   JSON patient record -> prediction, probability, confidence
  GET  /metrics   Prometheus exposition format

Every request is timed and counted with prometheus_client so Prometheus can
scrape /metrics and Grafana can chart request rate, latency, and the split
of predicted classes. Structured log lines go to stdout, which is what you
want inside a container so a log driver or Loki can pick them up.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

from api.schemas import HealthResponse, PatientFeatures, PredictionResponse
from src import predict as predictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s level=%(levelname)s logger=%(name)s msg="%(message)s"',
)
logger = logging.getLogger("heart-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model at boot so the first /predict is not slow, and so a
    broken artifact fails the container immediately instead of on first use."""
    try:
        predictor.load_model()
        meta = predictor.load_metadata()
        logger.info("Model ready: %s", meta.get("model_type", "unknown"))
    except FileNotFoundError as exc:
        logger.error("Model not available at startup: %s", exc)
    yield


app = FastAPI(
    title="Heart Disease Risk API",
    description="Predicts presence of heart disease from patient health data.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- Prometheus metrics --------------------------------------------------
REQUEST_COUNT = Counter(
    "api_requests_total", "Total API requests", ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)
PREDICTION_COUNT = Counter(
    "model_predictions_total", "Predictions by class", ["label"]
)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    endpoint = request.url.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
    REQUEST_COUNT.labels(
        endpoint=endpoint, method=request.method, status=response.status_code
    ).inc()
    logger.info(
        "request endpoint=%s method=%s status=%s latency_ms=%.1f",
        endpoint, request.method, response.status_code, elapsed * 1000,
    )
    return response


@app.get("/")
def root():
    return {
        "service": "Heart Disease Risk API",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        predictor.load_model()
        meta = predictor.load_metadata()
        return HealthResponse(
            status="ok", model_loaded=True, model_type=meta.get("model_type")
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=503,
            content={"status": "model_unavailable", "model_loaded": False},
        )


@app.post("/predict", response_model=PredictionResponse)
def predict(features: PatientFeatures):
    result = predictor.predict(features.model_dump())
    PREDICTION_COUNT.labels(label=result["label"]).inc()
    meta = predictor.load_metadata()
    result["model_type"] = meta.get("model_type")
    logger.info(
        "prediction label=%s probability=%.4f", result["label"], result["probability"]
    )
    return PredictionResponse(**result)


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
