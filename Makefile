.PHONY: help install data eda train test lint serve docker-build docker-run compose-up clean

help:
	@echo "Targets: install data eda train test lint serve docker-build docker-run compose-up clean"

install:
	pip install -r requirements.txt

data:
	python -m src.data_prep

eda:
	python -m src.eda

train:
	python -m src.train

test:
	pytest -q

lint:
	ruff check .

serve:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t heart-disease-api:latest -f docker/Dockerfile .

docker-run:
	docker run --rm -p 8000:8000 heart-disease-api:latest

compose-up:
	docker compose up --build

mlflow-ui:
	mlflow ui --backend-store-uri ./mlruns

clean:
	rm -rf mlruns __pycache__ .pytest_cache .ruff_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
