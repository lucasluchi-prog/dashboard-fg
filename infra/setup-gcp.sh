#!/usr/bin/env bash
# Setup inicial do projeto GCP para dashboard-fg.
# Executar UMA VEZ após aprovação do Lucas.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-southamerica-east1}"
SQL_INSTANCE="${SQL_INSTANCE:-dashboard-fg}"
SQL_DB="${SQL_DB:-dashboard_fg}"
SQL_USER="${SQL_USER:-dashboard}"

echo "== Habilitando APIs"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
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

echo "== Cloud SQL (db-f1-micro)"
if ! gcloud sql instances describe "$SQL_INSTANCE" >/dev/null 2>&1; then
  gcloud sql instances create "$SQL_INSTANCE" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=03:00
fi

if ! gcloud sql databases describe "$SQL_DB" --instance="$SQL_INSTANCE" >/dev/null 2>&1; then
  gcloud sql databases create "$SQL_DB" --instance="$SQL_INSTANCE"
fi

read -rsp "Senha do usuário Postgres ($SQL_USER): " SQL_PW
echo
if ! gcloud sql users list --instance="$SQL_INSTANCE" | grep -q "^$SQL_USER"; then
  gcloud sql users create "$SQL_USER" --instance="$SQL_INSTANCE" --password="$SQL_PW"
fi

INSTANCE_CONN=$(gcloud sql instances describe "$SQL_INSTANCE" --format='value(connectionName)')
DB_URL_ASYNC="postgresql+asyncpg://$SQL_USER:$SQL_PW@/$SQL_DB?host=/cloudsql/$INSTANCE_CONN"
DB_URL_SYNC="postgresql+psycopg2://$SQL_USER:$SQL_PW@/$SQL_DB?host=/cloudsql/$INSTANCE_CONN"

echo "== Secret Manager"
for s in \
  "dashboard-fg-db-url=$DB_URL_ASYNC" \
  "dashboard-fg-db-url-sync=$DB_URL_SYNC" \
  "dashboard-fg-session=$(openssl rand -hex 32)"; do
  name="${s%%=*}"
  value="${s#*=}"
  if ! gcloud secrets describe "$name" >/dev/null 2>&1; then
    echo -n "$value" | gcloud secrets create "$name" --data-file=-
  else
    echo "Secret $name já existe — pulando (use 'gcloud secrets versions add' para atualizar)"
  fi
done

echo "Pronto. Adicione manualmente:"
echo "  - dashboard-fg-oauth-client / dashboard-fg-oauth-secret (do OAuth Consent Screen)"
echo "  - dashboard-fg-datajuri-user / dashboard-fg-datajuri-password"
echo "Instance connection: $INSTANCE_CONN"
