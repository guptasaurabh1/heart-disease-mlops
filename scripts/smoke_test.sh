#!/usr/bin/env bash
# Smoke test: hit the running API and fail loudly if anything is off.
# Used by CI after the container starts, and handy locally too.
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"

echo "1. Health check"
curl -fs "${BASE}/health" | grep -q '"model_loaded":true'
echo "   ok"

echo "2. Valid prediction"
RESP=$(curl -fs -X POST "${BASE}/predict" \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":4,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}')
echo "   response: ${RESP}"
echo "${RESP}" | grep -q '"prediction"'
echo "   ok"

echo "3. Validation rejects bad input (expect 422)"
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE}/predict" \
  -H "Content-Type: application/json" \
  -d '{"age":999}')
test "${CODE}" = "422"
echo "   got ${CODE}, ok"

echo "4. Metrics endpoint"
curl -fs "${BASE}/metrics" | grep -q "api_requests_total"
echo "   ok"

echo "All smoke tests passed."
