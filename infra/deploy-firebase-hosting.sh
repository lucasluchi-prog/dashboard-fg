#!/usr/bin/env bash
# Deploy do frontend via Firebase Hosting (free tier):
#   - rewrite /api/** -> Cloud Run service dashboard-fg-api
#   - fallback SPA para /index.html
#   - SSL automático + custom domain grátis
#
# Pré-requisitos:
#   npm install -g firebase-tools
#   firebase login  (abre browser)
#   firebase use <PROJECT_ID>  (ou configurar .firebaserc)

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"

cd "$(dirname "$0")/../projeto-web"

echo "== Build Vite"
npm run build

echo "== Firebase deploy (projeto $PROJECT_ID)"
firebase deploy --only hosting --project="$PROJECT_ID"

echo ""
echo "Pronto. URL padrão: https://$PROJECT_ID.web.app"
echo "Adicionar custom domain em: Firebase Console -> Hosting -> Add custom domain"
echo "Sugerido: dashboard.furtadoguerini.com.br"
