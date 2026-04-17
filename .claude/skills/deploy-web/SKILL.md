---
name: deploy-web
description: Faz build e deploy do frontend React (dashboard-fg-web) no Cloud Run via nginx. Use quando o usuario quiser publicar mudancas no frontend. Triggers "deploy web", "deploy frontend", "publicar site", "cloud run web".
---

# /deploy-web

Publica o frontend React (Vite + nginx) em Cloud Run (`southamerica-east1`).

## Pré-condições

- `gcloud auth login` ativo, projeto GCP selecionado.
- Build de produção funciona localmente: `npm run build` em `projeto-web/` sem erros.
- Types OpenAPI sincronizados com a API: `npm run openapi:pull` (gera `src/api/types.ts`).

## Deploy

```bash
cd projeto-web

# Build + deploy source-based (Cloud Build usa Dockerfile)
gcloud run deploy dashboard-fg-web \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated=false \
  --set-env-vars="API_BASE=https://dashboard-fg-api-XXX.a.run.app" \
  --min-instances=0 \
  --max-instances=3 \
  --cpu=1 \
  --memory=256Mi
```

## Pós-condições

- Nova revisão promovida a 100% do tráfego.
- Health check: `curl https://dashboard-fg-web-XXX.a.run.app/healthz` -> `200 ok`.
- SPA serve `index.html` para qualquer rota (fallback nginx).
- `/api/*` proxied para `dashboard-fg-api`.

## Rollback

```bash
gcloud run services update-traffic dashboard-fg-web \
  --to-revisions=REVISAO_ANTERIOR=100 \
  --region=southamerica-east1
```

## Erros comuns

- Build falha por tipagem: `npm run typecheck` localmente antes.
- `/api/*` retorna 404: conferir `nginx.conf` e env `API_BASE`.
- CSP bloqueia OAuth popup: verificar headers `Content-Security-Policy`.
