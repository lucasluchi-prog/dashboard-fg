# CLAUDE.md — dashboard-fg

Projeto de migração do **Dashboard de Produtividade** da Furtado Guerini Advocacia da stack **Apps Script + Google Sheets** para **Python/FastAPI + PostgreSQL + React/Vite**. Roda em Google Cloud Run + Cloud SQL.

Plano completo: `C:\Users\lucas\.claude\plans\sobre-o-dashboard-de-lovely-sifakis.md`.

---

## Arquitetura

```
dashboard-fg/
├── projeto-api/     FastAPI + SQLAlchemy + Alembic + httpx + authlib
├── projeto-web/     React 18 + Vite + TS + TanStack Query + Tailwind + Recharts
└── docker-compose   Postgres 15 local
```

- **Backend** em `projeto-api/`: rota `/api/*`, OAuth Google restrita ao domínio `furtadoguerini.com.br`.
- **Frontend** em `projeto-web/`: SPA, dev em `localhost:5173` com proxy para API em `localhost:8080`.
- **Banco** em Postgres 15 (docker local / Cloud SQL em produção).
- **ETL** = Cloud Run Job (imagem separada) agendado por Cloud Scheduler (6h diário + 2h incremental).

---

## Convenções obrigatórias

### Python (projeto-api/)
- Python 3.11+.
- Tipagem estrita. `pyright` / pylance em modo strict.
- Ruff para lint + format (substitui black + isort).
- Async por padrão (FastAPI + httpx + SQLAlchemy 2.0 async).
- Pydantic v2 para todos os schemas.
- SQLAlchemy declarativo (`MappedColumn`), **sem** SQL cru fora de services.
- Docstrings curtas em português.
- Testes em `tests/` (pytest). `tests/unit/` = puras; `tests/integration/` = hit DB real via docker-compose.

### TypeScript (projeto-web/)
- TS strict.
- TanStack Query para estado servidor; **sem** Redux.
- Tailwind para styling; **sem** CSS file solto.
- Componentes em PascalCase, arquivos `.tsx`.
- Hooks em camelCase com prefixo `use`.
- Tipos gerados do OpenAPI via `openapi-typescript` ficam em `src/api/types.ts`.

### SQL / Alembic
- Toda mudança de schema via Alembic (`uv run alembic revision --autogenerate -m "..."`).
- Nunca alterar migrations antigas já aplicadas em prod; criar nova.
- Nomes snake_case, tabelas no singular (`pessoa`, `atividade`, `grupo`).
- FKs com ON DELETE explícito.

### Commits
- Prefixo curto: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`, `etl:`, `db:`.
- Português no corpo.

---

## Paridade com Apps Script

**Regra absoluta**: o output Python deve ser **idêntico** ao do Apps Script para os mesmos inputs até o cutover. Qualquer divergência é bug até prova em contrário.

Arquivos de referência (read-only):
- `C:\Users\lucas\.claude\dashboard-produtividade\appscript-clasp\*.js` — lógica atual.
- `C:\Users\lucas\.claude\dashboard-produtividade\cloudrun-live\app.py` — backend atual.
- `C:\Users\lucas\.claude\dashboard-produtividade\cloudrun-live\dashboard.html` — frontend atual.

Test de paridade: `projeto-api/tests/integration/test_paridade.py` compara linha a linha. Tolerância = 0 para contagens, 0.01 para taxas.

---

## Não fazer

- Não desativar triggers Apps Script sem aprovação explícita do Lucas.
- Não deletar pastas legadas (`cloudrun/`, `cloudrun-live/`, `appscript/`, `appscript-clasp/`).
- Não fazer cutover DNS sem validação do time.
- Não commitar `.env`, service accounts JSON, credenciais.

---

## DataJuri

MCP DataJuri disponível (read-only + 2 writes opt-in). Usar em desenvolvimento para validar paridade e descobrir campos. Cliente HTTP nativo em `projeto-api/app/services/datajuri_client.py` (reimplementa `ApiClient.js`).

---

## GCP

Região padrão: `southamerica-east1`.
Serviços previstos:
- `dashboard-fg-api` (Cloud Run)
- `dashboard-fg-web` (Cloud Run)
- `dashboard-fg-etl` (Cloud Run Job, disparado por Cloud Scheduler)
- Cloud SQL Postgres 15 (db-f1-micro)

Autenticação: OAuth Google restrita ao domínio `furtadoguerini.com.br`.
