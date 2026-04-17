# Dashboard FG

Migração do **Dashboard de Produtividade** da Furtado Guerini Advocacia:
**Apps Script + Google Sheets** → **Python/FastAPI + Postgres + React/Vite**.

Plano completo: `C:\Users\lucas\.claude\plans\sobre-o-dashboard-de-lovely-sifakis.md`.

---

## Estrutura

```
dashboard-fg/
├── projeto-api/      # Backend FastAPI (SQLAlchemy async, Alembic, httpx, authlib)
├── projeto-web/      # Frontend React 18 + Vite + TS + TanStack Query + Tailwind
├── docker-compose.yml
├── .vscode/          # launch.json + tasks.json + settings.json
└── .claude/          # Convenções e skills do projeto para Claude Code
```

## Subir local

```bash
# 1. Banco
docker compose up -d postgres

# 2. Backend
cd projeto-api
uv sync
cp .env.example .env   # preencher DATAJURI_TOKEN, OAUTH_* etc
uv run alembic upgrade head
uv run python scripts/seed_from_apps_script.py   # popular grupos, pontuações, feriados
uv run uvicorn app.main:app --reload --port 8080

# 3. Frontend
cd ../projeto-web
npm install
npm run dev   # http://localhost:5173
```

## ETL

```bash
cd projeto-api
uv run python -m app.etl                # pipeline completo
uv run python -m app.etl --incremental  # só últimos N dias
uv run python -m app.etl --dry-run      # sem gravar
```

## Testes

```bash
cd projeto-api
uv run pytest              # unit + integration
uv run pytest tests/unit   # só unitários (sem banco)
```

## Deploy (Cloud Run)

```bash
# Backend
cd projeto-api && gcloud run deploy dashboard-fg-api --source . --region southamerica-east1

# Frontend
cd projeto-web && gcloud run deploy dashboard-fg-web --source . --region southamerica-east1

# ETL Job
cd projeto-api && gcloud run jobs deploy dashboard-fg-etl \
  --source . --region southamerica-east1 \
  --command=python --args="-m,app.etl"
```

## Convenções

Veja `.claude/CLAUDE.md`. Resumo:

- Python 3.11+, ruff, pyright strict.
- TS strict, Tailwind only, TanStack Query only.
- Alembic para toda mudança de schema; migrations nunca reescritas.
- Paridade zero-tolerance com Apps Script (contagens) até cutover.
- Sem deletar pastas legadas (`cloudrun-live/`, `appscript-clasp/` etc).

## Autorizações pendentes

Antes de sair do ambiente local:

- [ ] Criar Cloud SQL instance `db-f1-micro` em `southamerica-east1`.
- [ ] Criar Artifact Registry e habilitar Cloud Build.
- [ ] Configurar OAuth Consent Screen + Client ID (domínio `furtadoguerini.com.br`).
- [ ] Cloud Scheduler jobs (6h diário + 2h incremental).
- [ ] Cutover DNS (`dashboard.furtadoguerini.com.br`) — só após validação do time.
