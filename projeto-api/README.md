# projeto-api — Dashboard FG Backend

FastAPI 0.115 + Pydantic v2 + SQLAlchemy 2.0 async + Alembic + httpx + authlib.

## Dev

```bash
# 1. Deps (via uv; pip -e . também funciona)
uv sync

# 2. Banco local
docker compose -f ../docker-compose.yml up -d postgres
cp .env.example .env   # preencher DATAJURI_* e OAUTH_*

# 3. Migrations
uv run alembic upgrade head

# 4. Seed (grupos, pontuações, feriados)
uv run python scripts/seed_from_apps_script.py

# 5. API
uv run uvicorn app.main:app --reload --port 8080
```

## ETL

```bash
uv run python -m app.etl                 # coleta completa + refresh MVs
uv run python -m app.etl --incremental   # só últimos 2 dias
uv run python -m app.etl --dry-run
```

## Testes

```bash
uv run pytest              # unit + integration
uv run pytest tests/unit   # só unit (sem docker)
uv run pytest -k paridade  # paridade contra Sheets
```

## Estrutura

```
app/
├── main.py            FastAPI factory
├── config.py          pydantic-settings
├── auth.py            OAuth Google + validate_google_user
├── db.py              async engine + session
├── deps.py            Dependências FastAPI
├── models/            ORM SQLAlchemy 2.0
├── schemas/           Pydantic v2
├── services/          Lógica de negócio pura (+ datajuri_client.py)
├── routers/           health, auth, dashboard, produtividade, ranking, aproveitamento, admin
└── etl/               Cloud Run Job: collector.py, pipeline.py
alembic/               Migrations versionadas
scripts/               seed_from_apps_script.py + init-db.sql
tests/                 unit + integration
```
