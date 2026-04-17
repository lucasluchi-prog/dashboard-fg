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
├── .github/          # Workflows CI (api + web)
├── infra/            # setup-gcp.sh, setup-gcp-free.sh, scheduler.sh
└── .claude/          # Convenções e skills do projeto para Claude Code
```

## Subir local

```bash
# 1. Banco
docker compose up -d postgres

# 2. Backend
cd projeto-api
pip install -e '.[dev]'
cp .env.example .env   # preencher DATAJURI_TOKEN, OAUTH_* etc
alembic upgrade head
python scripts/seed_from_apps_script.py   # popular grupos, pontuações, feriados
uvicorn app.main:app --reload --port 8080

# 3. Frontend
cd ../projeto-web
npm install
npm run dev   # http://localhost:5173
```

## ETL

```bash
cd projeto-api
python -m app.etl                # pipeline completo
python -m app.etl --incremental  # só últimos N dias
python -m app.etl --dry-run      # sem gravar
```

## Testes

```bash
cd projeto-api
pytest              # unit + integration
pytest tests/unit   # só unitários (sem banco)
```

## Deploy — três rotas

### Rota A — 100% GCP com Cloud SQL (~R$80–100/mês)

Usa `infra/setup-gcp.sh` + `projeto-api/cloudbuild.yaml` + `projeto-api/cloudbuild.etl.yaml`.
Cloud SQL `db-f1-micro` (Postgres 15 HA off) + backup automático.

```bash
PROJECT_ID=<seu-projeto> bash infra/setup-gcp.sh
gcloud builds submit --config projeto-api/cloudbuild.yaml projeto-api/ \
  --substitutions=_CLOUDSQL_INSTANCE=$PROJECT_ID:southamerica-east1:dashboard-fg
gcloud builds submit --config projeto-api/cloudbuild.etl.yaml projeto-api/ \
  --substitutions=_CLOUDSQL_INSTANCE=$PROJECT_ID:southamerica-east1:dashboard-fg
gcloud builds submit --config projeto-web/cloudbuild.yaml projeto-web/
PROJECT_ID=<seu-projeto> bash infra/scheduler.sh
```

### Rota B — **Free tier total** (Supabase + Cloud Run)

Substitui o Cloud SQL por Supabase Postgres (500 MB free, managed, permanente).
Custo: **R$0/mês** para piloto.

1. Criar projeto em [supabase.com](https://supabase.com) (Free tier).
2. Em `Settings → Database → Connection pooling`, copiar o pooler URL (port 6543).
3. Em `Settings → Database → Connection string`, copiar o URL direto (port 5432).
4. Rodar:

```bash
PROJECT_ID=<seu-projeto> \
SUPABASE_DB_URL='postgresql://postgres:SENHA@db.xxx.supabase.co:5432/postgres' \
SUPABASE_DB_URL_POOL='postgresql://postgres:SENHA@pooler.xxx.supabase.co:6543/postgres' \
bash infra/setup-gcp-free.sh

# Adicionar manualmente os secrets OAuth e DataJuri no Secret Manager
gcloud builds submit --config projeto-api/cloudbuild.free.yaml projeto-api/
gcloud builds submit --config projeto-api/cloudbuild.etl.free.yaml projeto-api/
gcloud builds submit --config projeto-web/cloudbuild.yaml projeto-web/ \
  --substitutions=_API_URL=https://dashboard-fg-api-XXX.run.app
PROJECT_ID=<seu-projeto> bash infra/scheduler.sh
```

**Contrapartidas do free tier Supabase:**

- Projeto pausa após **7 dias sem conexão** — o Cloud Scheduler ETL a cada 2h mantém ativo.
- Limite de **500 MB**. Nossos dados agregados (~50k atividades × ~2KB) ≈ 100 MB. Folga ampla.
- Latência um pouco maior que Cloud SQL regional (Supabase é multi-region).
- Máximo **60 conexões simultâneas**. Usamos o pooler (PgBouncer) — suficiente para o tráfego interno.

**Quando considerar migrar para Cloud SQL:**

- Dados > 400 MB.
- Latência p95 > 200ms começa a incomodar.
- Precisa de HA / backup PITR granular.
- Quer integrar com outras apps GCP sem NAT externo.

Migração Supabase → Cloud SQL: `pg_dump | pg_restore`, swap secret no Secret Manager, novo deploy. Sem mudança de código.

### Rota C — **Firebase Hosting + Cloud Run API + Supabase** (recomendada)

Otimização da rota B: troca o Cloud Run Web pelo **Firebase Hosting** (CDN global, SSL automático, custom domain incluído, sem cold start).

Vantagens:
- Custom domain em 1 clique (`dashboard.furtadoguerini.com.br`).
- Deploy do frontend em ~15s via `firebase deploy`.
- Mesmo projeto GCP usado pelo OAuth e Cloud Run, auth integrada.
- Free tier: 10 GB storage + 360 MB/dia transfer.

```bash
# 1. Banco + API igual à rota B
PROJECT_ID=<seu-projeto> \
SUPABASE_DB_URL='...' SUPABASE_DB_URL_POOL='...' \
bash infra/setup-gcp-free.sh
gcloud builds submit --config projeto-api/cloudbuild.free.yaml projeto-api/
gcloud builds submit --config projeto-api/cloudbuild.etl.free.yaml projeto-api/

# 2. Frontend via Firebase Hosting
npm install -g firebase-tools
firebase login
sed -i "s/SUBSTITUIR_PELO_PROJECT_ID/$PROJECT_ID/g" .firebaserc
PROJECT_ID=<seu-projeto> bash infra/deploy-firebase-hosting.sh

# 3. Scheduler
PROJECT_ID=<seu-projeto> bash infra/scheduler.sh
```

O arquivo [projeto-web/firebase.json](projeto-web/firebase.json) já tem os `rewrites` que apontam `/api/**`, `/login`, `/logout`, `/auth/**` para o Cloud Run `dashboard-fg-api`. Vite + SPA fallback estão configurados.

**Custom domain:** `Firebase Console → Hosting → Add custom domain` → `dashboard.furtadoguerini.com.br`. Firebase gera TXT + A/AAAA records, você configura no registrar. SSL em ~24h.

## Convenções

Veja `.claude/CLAUDE.md`. Resumo:

- Python 3.11+, ruff, pyright strict.
- TS strict, Tailwind only, TanStack Query only.
- Alembic para toda mudança de schema; migrations nunca reescritas.
- Paridade zero-tolerance com Apps Script (contagens) até cutover.
- Sem deletar pastas legadas (`cloudrun-live/`, `appscript-clasp/` etc).

## Autorizações pendentes

- [ ] Criar projeto Supabase (rota B) **ou** Cloud SQL instance (rota A).
- [ ] Configurar OAuth Consent Screen + Client ID (domínio `furtadoguerini.com.br`).
- [ ] Cutover DNS (`dashboard.furtadoguerini.com.br`) — só após validação do time.
