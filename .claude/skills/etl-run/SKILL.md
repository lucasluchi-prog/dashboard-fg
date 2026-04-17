---
name: etl-run
description: Executa o ETL localmente (coleta DataJuri + refresh materialized views + log em etl_run). Use quando o usuario quiser rodar o pipeline, popular o banco, testar coleta ou forcar um refresh dos dados. Triggers "etl run", "rodar pipeline", "popular banco", "refresh dashboard", "coletar atividades".
---

# /etl-run

Dispara o pipeline ETL contra a instância Postgres alvo (local ou Cloud SQL via proxy).

## Pré-condições

- `docker compose up -d postgres` rodando (ou Cloud SQL proxy ativo).
- `projeto-api/.env` preenchido (`DATABASE_URL`, `DATAJURI_TOKEN`, `DATAJURI_TENANT`).
- Migrations aplicadas: `uv run alembic upgrade head`.

## Comandos

```bash
cd projeto-api
uv run python -m app.etl                       # roda completo
uv run python -m app.etl --incremental         # apenas ultimos N dias
uv run python -m app.etl --dry-run             # coleta sem gravar
```

## Pós-condições

- Tabela `atividade` upserted (on_conflict_do_update por id).
- Materialized views `mv_produtividade`, `mv_ranking`, `mv_aproveitamento*`, `mv_distribuicao_*` refreshed concurrently.
- Linha nova em `etl_run` com `status` (`ok` | `partial` | `fail`) e `detalhes` JSONB.

## Erros comuns

- `DATABASE_URL` aponta para Cloud SQL sem proxy -> usar `cloud-sql-proxy` local.
- Token DataJuri expirado -> renovar via fluxo OAuth registrado em `services/datajuri_client.py`.
- MVs travam em `REFRESH CONCURRENTLY` se faltarem unique indexes -> validar no Alembic.
