#!/usr/bin/env bash
# Cria/atualiza os Cloud Scheduler Jobs que disparam o ETL.
# Executar manualmente após aprovação GCP.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-southamerica-east1}"
JOB_NAME="dashboard-fg-etl"
SA_EMAIL="${SA_EMAIL:-scheduler-sa@${PROJECT_ID}.iam.gserviceaccount.com}"

JOB_URI="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run"

cria_ou_atualiza() {
  local id="$1" schedule="$2" args="$3"
  if gcloud scheduler jobs describe "$id" --location="$REGION" >/dev/null 2>&1; then
    echo "Atualizando $id..."
    gcloud scheduler jobs update http "$id" \
      --location="$REGION" \
      --schedule="$schedule" \
      --time-zone="America/Sao_Paulo" \
      --uri="$JOB_URI" \
      --http-method=POST \
      --message-body="{\"overrides\":{\"containerOverrides\":[{\"args\":$args}]}}" \
      --oauth-service-account-email="$SA_EMAIL" \
      --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
  else
    echo "Criando $id..."
    gcloud scheduler jobs create http "$id" \
      --location="$REGION" \
      --schedule="$schedule" \
      --time-zone="America/Sao_Paulo" \
      --uri="$JOB_URI" \
      --http-method=POST \
      --message-body="{\"overrides\":{\"containerOverrides\":[{\"args\":$args}]}}" \
      --oauth-service-account-email="$SA_EMAIL" \
      --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
  fi
}

# 6h diário — coleta completa
cria_ou_atualiza "dashboard-fg-etl-completo" "0 6 * * *" '[]'

# A cada 2h das 8h às 20h — incremental
cria_ou_atualiza "dashboard-fg-etl-incremental" "0 8-20/2 * * *" '["--incremental"]'

echo "Done."
