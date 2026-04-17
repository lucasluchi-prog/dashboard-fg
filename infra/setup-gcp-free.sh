#!/usr/bin/env bash
# Setup gratuito — Cloud Run + Supabase Postgres (sem Cloud SQL).
# Roda UMA vez após aprovação.
#
# Pré-requisitos manuais:
#   1. Conta Supabase criada em https://supabase.com (Free tier)
#   2. Projeto Supabase criado em região us-east-1 ou sa-east-1
#   3. Em Settings -> Database, copiar:
#      - "Connection string" (mode: Session) -> SUPABASE_DB_URL
#      Exemplo:
#      postgresql://postgres:SENHA@db.xxxxxxxxxx.supabase.co:5432/postgres
#   4. Em Settings -> Database -> Connection pooling (PgBouncer),
#      copiar o pooler URL (port 6543) -> SUPABASE_DB_URL_POOL
#      Usar esse para o app (Cloud Run async + pool frio).
#
# Uso:
#   PROJECT_ID=meu-proj \
#   SUPABASE_DB_URL_POOL='postgresql://postgres:SENHA@pooler.xxx.supabase.co:6543/postgres' \
#   SUPABASE_DB_URL='postgresql://postgres:SENHA@db.xxx.supabase.co:5432/postgres' \
#   bash infra/setup-gcp-free.sh

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-southamerica-east1}"
: "${SUPABASE_DB_URL_POOL:?set SUPABASE_DB_URL_POOL}"
: "${SUPABASE_DB_URL:?set SUPABASE_DB_URL}"

echo "== Habilitando APIs (apenas as do free tier)"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  --project="$PROJECT_ID"

echo "== Artifact Registry"
if ! gcloud artifacts repositories describe dashboard-fg --location="$REGION" >/dev/null 2>&1; then
  gcloud artifacts repositories create dashboard-fg \
    --repository-format=docker \
    --location="$REGION" \
    --description="Imagens do Dashboard FG"
fi

# Converter URLs Supabase para formatos esperados pelo SQLAlchemy
# async (app) usa asyncpg via URL-pooler (PgBouncer)
# sync (alembic) usa psycopg2 via URL direto
DB_URL_ASYNC="${SUPABASE_DB_URL_POOL/postgresql:\/\//postgresql+asyncpg://}"
DB_URL_SYNC="${SUPABASE_DB_URL/postgresql:\/\//postgresql+psycopg2://}"

echo "== Secret Manager (criar se não existir)"
set_secret() {
  local name="$1" value="$2"
  if ! gcloud secrets describe "$name" >/dev/null 2>&1; then
    echo -n "$value" | gcloud secrets create "$name" --data-file=-
    echo "  criado: $name"
  else
    echo "  existe:  $name (para atualizar: gcloud secrets versions add $name --data-file=-)"
  fi
}
set_secret "dashboard-fg-db-url" "$DB_URL_ASYNC"
set_secret "dashboard-fg-db-url-sync" "$DB_URL_SYNC"
set_secret "dashboard-fg-session" "$(openssl rand -hex 32)"

echo ""
echo "Pronto. Falta adicionar manualmente no Secret Manager:"
echo "  - dashboard-fg-oauth-client   (Google OAuth Consent Screen client_id)"
echo "  - dashboard-fg-oauth-secret   (client_secret)"
echo "  - dashboard-fg-datajuri-user"
echo "  - dashboard-fg-datajuri-password"
echo ""
echo "Depois:"
echo "  gcloud builds submit --config projeto-api/cloudbuild.free.yaml projeto-api/"
echo "  gcloud builds submit --config projeto-api/cloudbuild.etl.free.yaml projeto-api/"
echo "  gcloud builds submit --config projeto-web/cloudbuild.yaml projeto-web/"
echo "  bash infra/scheduler.sh"
