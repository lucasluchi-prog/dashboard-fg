# Runbook — Deploy Rota C (Firebase Hosting + Cloud Run + Supabase)

Passos manuais que só você (Lucas) pode executar — exigem autenticação interativa.
Tempo total: ~30-45 min.

## Pré-requisitos verificados

- [x] `gcloud` instalado e logado como `lucasluchi@furtadoguerini.com.br`
- [x] `firebase-tools` 15.15.0 instalado
- [x] Projeto GCP atual: `vocal-mountain-492622-u7`
- [x] Node.js 24.14, Python 3.14

## Etapa 1 — Criar projeto Supabase (5 min)

1. Acessar https://supabase.com/dashboard e entrar com Google (`lucasluchi@furtadoguerini.com.br`).
2. `New project`:
   - **Name:** `dashboard-fg`
   - **Database password:** gerar forte, **salvar em 1Password/Bitwarden**
   - **Region:** `South America (São Paulo)` (`sa-east-1`)
   - **Pricing plan:** Free
3. Aguardar ~2 min provisionar.
4. Em `Project Settings → Database → Connection string`:
   - Copiar **URI** (port 5432) → `SUPABASE_DB_URL` (use para Alembic)
   - Marcar `Use connection pooling` e copiar URI do pooler (port 6543, mode: Transaction) → `SUPABASE_DB_URL_POOL` (use para API em runtime)
5. Substituir `[YOUR-PASSWORD]` pela senha real em ambos URLs.

Formatos esperados:

```
SUPABASE_DB_URL=postgresql://postgres:SENHA@db.xxxxxxxx.supabase.co:5432/postgres
SUPABASE_DB_URL_POOL=postgresql://postgres.xxxxxxxx:SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

## Etapa 2 — Decidir projeto GCP (2 min)

**Opção A — reutilizar `vocal-mountain-492622-u7`** (mais simples, mas mistura com o site de processos).

**Opção B — criar novo projeto `dashboard-fg`** (recomendado para isolar billing/permissões):

```bash
gcloud projects create dashboard-fg-<sufixo-random> \
  --name="Dashboard FG" \
  --labels=app=dashboard-fg

# Vincular billing (obrigatório mesmo para free tier)
gcloud beta billing projects link dashboard-fg-<sufixo-random> \
  --billing-account=<ID-DO-BILLING-ACCOUNT>

# Listar billing accounts disponíveis
gcloud beta billing accounts list
```

Exportar escolha:

```bash
export PROJECT_ID=vocal-mountain-492622-u7   # ou dashboard-fg-xxx
gcloud config set project $PROJECT_ID
```

## Etapa 3 — OAuth Consent Screen + Client ID (10 min)

1. Acessar https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID
2. **User type:** `Internal` (só @furtadoguerini.com.br — só aparece se for Workspace admin; senão `External` + adicionar emails como test users).
3. Preencher:
   - **App name:** Dashboard FG
   - **User support email:** lucasluchi@furtadoguerini.com.br
   - **Authorized domains:** `furtadoguerini.com.br` (+ `web.app` temporariamente, se for usar domínio Firebase padrão)
   - **Developer contact:** lucasluchi@furtadoguerini.com.br
4. `Save and continue`.
5. Em `Credentials → Create credentials → OAuth client ID`:
   - **Type:** Web application
   - **Name:** Dashboard FG web
   - **Authorized JavaScript origins:**
     - `https://<PROJECT_ID>.web.app` (temporário)
     - `https://dashboard.furtadoguerini.com.br` (após custom domain)
     - `http://localhost:5173` (dev)
   - **Authorized redirect URIs:**
     - `https://dashboard-fg-api-<hash>-rj.a.run.app/auth/callback` (preencher depois do primeiro deploy)
     - `http://localhost:8080/auth/callback` (dev)
6. Download JSON → guardar `OAUTH_CLIENT_ID` e `OAUTH_CLIENT_SECRET`.

## Etapa 4 — Rodar setup GCP (3 min)

```bash
cd C:/Users/lucas/www/dashboard-fg

PROJECT_ID=<seu-projeto> \
SUPABASE_DB_URL="postgresql://postgres:SENHA@db.xxxxxxxx.supabase.co:5432/postgres" \
SUPABASE_DB_URL_POOL="postgresql://postgres.xxxxxxxx:SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres" \
bash infra/setup-gcp-free.sh
```

Isso:
- Habilita APIs (Cloud Run, Cloud Build, Secret Manager, etc)
- Cria Artifact Registry `dashboard-fg` em `southamerica-east1`
- Cria 3 secrets no Secret Manager (db-url, db-url-sync, session)

Adicionar manualmente os 4 secrets restantes:

```bash
# OAuth (da Etapa 3)
echo -n "SEU_CLIENT_ID.apps.googleusercontent.com" | gcloud secrets create dashboard-fg-oauth-client --data-file=-
echo -n "SEU_CLIENT_SECRET" | gcloud secrets create dashboard-fg-oauth-secret --data-file=-

# DataJuri (credenciais do escritório)
echo -n "USUARIO_DATAJURI" | gcloud secrets create dashboard-fg-datajuri-user --data-file=-
echo -n "SENHA_DATAJURI" | gcloud secrets create dashboard-fg-datajuri-password --data-file=-
```

## Etapa 5 — Dar permissões aos service accounts (2 min)

```bash
# Cloud Build precisa acessar Secret Manager
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Cloud Run service account (default compute SA) precisa acessar secrets
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Etapa 6 — Deploy API + ETL (~10 min)

```bash
# API (primeira vez: ~5-7 min)
gcloud builds submit --config projeto-api/cloudbuild.free.yaml projeto-api/

# Pegar a URL gerada
API_URL=$(gcloud run services describe dashboard-fg-api \
  --region=southamerica-east1 \
  --format='value(status.url)')
echo "API_URL=$API_URL"

# Voltar ao Console OAuth (Etapa 3) e adicionar:
#   Authorized redirect URIs: $API_URL/auth/callback

# ETL Job
gcloud builds submit --config projeto-api/cloudbuild.etl.free.yaml projeto-api/
```

## Etapa 7 — Deploy Frontend (Firebase Hosting) (~3 min)

```bash
firebase login   # abre browser, logar com lucasluchi@furtadoguerini.com.br

cd C:/Users/lucas/www/dashboard-fg

# Atualizar .firebaserc
sed -i "s/SUBSTITUIR_PELO_PROJECT_ID/$PROJECT_ID/g" .firebaserc

# Ativar Firebase no projeto GCP existente
firebase projects:addfirebase $PROJECT_ID

# Build + deploy
cd projeto-web
npm install
npm run build
firebase deploy --only hosting --project=$PROJECT_ID

# URL será:
echo "Web: https://$PROJECT_ID.web.app"
```

## Etapa 8 — Scheduler (2 min)

```bash
# Criar service account do scheduler
gcloud iam service-accounts create dashboard-fg-scheduler \
  --display-name="Dashboard FG Scheduler"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:dashboard-fg-scheduler@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

SA_EMAIL="dashboard-fg-scheduler@$PROJECT_ID.iam.gserviceaccount.com" \
PROJECT_ID=$PROJECT_ID \
bash infra/scheduler.sh
```

## Etapa 9 — Primeiro ETL manual (5 min)

```bash
gcloud run jobs execute dashboard-fg-etl --region=southamerica-east1 --wait
```

Ver logs:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=dashboard-fg-etl" \
  --limit=50 --format='value(textPayload)'
```

## Etapa 10 — Validar E2E (5 min)

1. Acessar `https://<PROJECT_ID>.web.app` → deve redirecionar para OAuth Google.
2. Logar com `lucasluchi@furtadoguerini.com.br` → deve voltar ao dashboard.
3. Verificar dados carregando (pode estar vazio se ETL não rodou antes).
4. Rodar ETL manualmente se necessário e reload.

## Etapa 11 (Sprint 5) — Custom Domain + Cutover DNS

1. Firebase Console → Hosting → Add custom domain → `dashboard.furtadoguerini.com.br`.
2. Firebase mostra TXT record (verificação) + A/AAAA records (produção).
3. No registrar do `furtadoguerini.com.br` (provavelmente Registro.br):
   - Adicionar TXT na zona.
   - Adicionar A/AAAA apontando para IPs do Firebase.
   - TTL 300s para rollback rápido.
4. Aguardar ~15-60 min propagação + ~1-24h SSL.
5. Adicionar `dashboard.furtadoguerini.com.br` aos `Authorized JavaScript origins` do OAuth.
6. Comunicar time.
7. Após 2-3 semanas de uso dual, desabilitar triggers do Apps Script legado.

---

## Troubleshooting

**`dashboard-fg-api` retorna 500:** logs em Cloud Run → provável `statement_cache_size` ou senha Supabase errada.

```bash
gcloud run services logs read dashboard-fg-api --region=southamerica-east1 --limit=50
```

**Alembic falha:** URL sync deve usar `db.xxx.supabase.co:5432` (não pooler). Teste local:

```bash
DATABASE_URL_SYNC="postgresql+psycopg2://postgres:SENHA@db.xxx.supabase.co:5432/postgres" \
  alembic upgrade head
```

**ETL não coleta:** verificar secrets `dashboard-fg-datajuri-user/password`. Testar `fetch_page` local.

**OAuth 403 "redirect_uri_mismatch":** adicionar o URI exato (com hash) em `Authorized redirect URIs`.

**Firebase Hosting cache antigo:** `firebase deploy --only hosting --force` + limpar cache do browser.
