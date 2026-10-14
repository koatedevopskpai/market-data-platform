PY ?= python
VENV := .venv
ifeq ($(OS),Windows_NT)
	BIN := $(VENV)/Scripts
else
	BIN := $(VENV)/bin
endif

.PHONY: help setup ingest test lint dbt-local dbt-bigquery clean

help:
	@echo "setup      - create venv and install dev requirements"
	@echo "ingest     - validate sample data and write dbt seeds"
	@echo "test       - run ruff + pytest"
	@echo "lint       - run ruff"
	@echo "dbt-local  - dbt deps + seed + build + test on DuckDB"
	@echo "clean      - remove build artifacts"

setup:
	$(PY) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r requirements-dev.txt

ingest:
	$(BIN)/python -m src.ingestion.fetch_market_data --source data/sample --out dbt_platform/seeds

test: lint
	$(BIN)/python -m pytest -q

lint:
	$(BIN)/python -m ruff check src tests

dbt-local: ingest
	cd dbt_platform && dbt deps && dbt seed --target local && dbt build --target local && dbt docs generate --target local

dbt-bigquery:
	cd dbt_platform && dbt deps && dbt seed --target bigquery && dbt build --target bigquery

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache
	rm -rf dbt_platform/target dbt_platform/logs dbt_platform/dbt_packages
