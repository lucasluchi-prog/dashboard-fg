SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

PY_DIR := projeto-api
WEB_DIR := projeto-web

.PHONY: help db-up db-down db-migrate db-upgrade db-seed api-install api-run api-test api-lint api-format etl-local web-install web-dev web-build web-typecheck test full-setup

help: ## Lista alvos
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "} {printf "  %-18s %s\n", $$1, $$2}'

# ---------- Banco ----------

db-up: ## Sobe Postgres local via docker-compose
	docker compose up -d postgres

db-down: ## Para e remove containers do docker-compose
	docker compose down

db-migrate: ## Cria nova migration autogenerate (make db-migrate m="nome")
	cd $(PY_DIR) && alembic revision --autogenerate -m "$(m)"

db-upgrade: ## Aplica migrations pendentes
	cd $(PY_DIR) && alembic upgrade head

db-seed: ## Seed inicial (grupos, pontuações, feriados) a partir do Apps Script
	cd $(PY_DIR) && python scripts/seed_from_apps_script.py

# ---------- API ----------

api-install: ## Instala deps de dev do backend
	cd $(PY_DIR) && pip install -e '.[dev]'

api-run: ## Sobe API em :8080 com reload
	cd $(PY_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

api-test: ## pytest completo
	cd $(PY_DIR) && pytest -q

api-unit: ## pytest só unit (sem banco)
	cd $(PY_DIR) && pytest tests/unit -q

api-lint: ## Ruff lint
	cd $(PY_DIR) && ruff check .

api-format: ## Ruff format
	cd $(PY_DIR) && ruff format .

api-typecheck: ## Pyright strict
	cd $(PY_DIR) && pyright

# ---------- ETL ----------

etl-local: ## Roda pipeline ETL completo
	cd $(PY_DIR) && python -m app.etl

etl-incremental: ## Roda ETL incremental
	cd $(PY_DIR) && python -m app.etl --incremental

etl-dry: ## Dry-run do ETL (coleta, não grava)
	cd $(PY_DIR) && python -m app.etl --dry-run

# ---------- Web ----------

web-install: ## npm install
	cd $(WEB_DIR) && npm install

web-dev: ## Vite dev server em :5173
	cd $(WEB_DIR) && npm run dev

web-build: ## Build de produção
	cd $(WEB_DIR) && npm run build

web-typecheck: ## tsc -b --noEmit
	cd $(WEB_DIR) && npm run typecheck

web-lint: ## ESLint
	cd $(WEB_DIR) && npm run lint

# ---------- Atalhos ----------

test: api-test web-typecheck ## Roda todos os testes e typecheck web

full-setup: db-up db-upgrade db-seed api-install web-install ## Setup inicial do zero
	@echo "Pronto. Rode: make api-run & make web-dev"
