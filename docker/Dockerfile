# syntax=docker/dockerfile:1

# ---- builder: install deps into a venv we can copy out ----
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# libgomp is needed by xgboost at runtime; build tools only here
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- runtime: slim image with only what serving needs ----
FROM python:3.11-slim AS runtime

# libgomp1 for xgboost, curl for the healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

# non-root user
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Application code, the trained artifact, and processed data
COPY src/ ./src/
COPY api/ ./api/
COPY models/ ./models/

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
