---
name: deploy-api
description: Faz build e deploy do backend FastAPI (dashboard-fg-api) no Cloud Run. Use quando o usuario quiser publicar mudancas no backend. Triggers "deploy api", "deploy backend", "publicar api", "cloud run api".
---

# /deploy-api

Publica o backend FastAPI em Cloud Run (região `southamerica-east1`).

## Pré-condições

- `gcloud auth login` ativo, projeto GCP selecionado.
- Migrations aplicadas em Cloud SQL (`uv run alembic upgrade head` apontando para proxy).
- Testes passando: `uv run pytest` em `projeto-api/`.

## Deploy

```bash
cd projeto-api

# Build + deploy source-based (Cloud Build gera imagem automaticamente)
gcloud run deploy dashboard-fg-api \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated=false \
  --set-env-vars="ENV=prod" \
  --set-secrets="DATABASE_URL=db-url:latest,DATAJURI_TOKEN=datajuri-token:latest,OAUTH_CLIENT_SECRET=oauth-secret:latest" \
  --add-cloudsql-instances=PROJETO:REGIAO:INSTANCIA \
  --min-instances=0 \
  --max-instances=5 \
  --cpu=1 \
  --memory=512Mi
```

## Pós-condições

- Nova revisão promovida a 100% do tráfego.
- Health check: `curl https://dashboard-fg-api-XXX.a.run.app/health` -> `{"status":"ok"}`.
- Logs em Cloud Logging sem erros nos 5 min seguintes.

## Rollback

```bash
gcloud run services update-traffic dashboard-fg-api \
  --to-revisions=REVISAO_ANTERIOR=100 \
  --region=southamerica-east1
```
