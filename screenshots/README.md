# Screenshots for the report

Captured while running the pipeline locally (MLflow, Swagger, Docker, GitHub
Actions, Kubernetes, Grafana). Referenced in `reports/final_report.docx` /
`final_report.pdf`.

## Primary set (one per required checkpoint)

| File | Shows |
|---|---|
| `mlflow_runs.png` | MLflow experiment view comparing all runs |
| `mlflow_run_detail.png` | One run's logged params/metrics/artifacts |
| `swagger_ui.png` | `http://localhost:8000/docs` — the `/predict` schema |
| `predict_response.png` | A successful `/predict` request + response |
| `docker_build.png` | `docker build ...` finishing successfully |
| `docker_run.png` | Container running, `/health` and `/predict` logs |
| `ci_pipeline.png` | Green GitHub Actions run (lint, test, train, build) |
| `k8s_service.png` | `kubectl get svc heart-api` with an external IP |
| `grafana_dashboard.png` | Heart Disease API dashboard with live traffic |
| `kubectl_pods.png` | `kubectl get pods` showing replicas `Running` |

## Supplementary evidence

Additional captures from the same session (Docker Compose bringing up Grafana,
the GitHub repo page, Actions workflow list/run detail views, Docker Desktop
Kubernetes setting, and kubectl context checks). Not individually required but
useful backup evidence.
