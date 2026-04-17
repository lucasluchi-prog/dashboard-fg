---
name: db-migrate
description: Cria nova migration Alembic com autogenerate e aplica (upgrade head). Use quando o usuario alterar um modelo SQLAlchemy ou quiser sincronizar schema do banco. Triggers "db migrate", "nova migration", "alembic", "atualizar schema", "aplicar migration".
---

# /db-migrate

Gera e aplica migration Alembic no Postgres alvo.

## Comandos

```bash
cd projeto-api
# 1. Gerar revision autogenerate
uv run alembic revision --autogenerate -m "add_coluna_x_em_atividade"

# 2. Revisar arquivo criado em alembic/versions/*.py
#    Ajustar manualmente se:
#    - MATERIALIZED VIEWS (autogenerate ignora)
#    - INDEXES GIN/GIST
#    - CHECK constraints complexas

# 3. Aplicar
uv run alembic upgrade head

# 4. Reverter 1 passo (dev apenas)
uv run alembic downgrade -1
```

## Regras

- **Nunca** alterar migration ja aplicada em produção (Cloud SQL). Criar nova.
- Materialized views, triggers e functions custom entram como `op.execute("""...""")` manuais.
- Nomear revisão em snake_case curto, descritivo (`add_assunto_excluido_idx`).
- Após gerar, rodar `uv run alembic upgrade head` e `uv run pytest tests/integration` para validar paridade.

## Validação

```bash
uv run alembic current        # revisão atual aplicada
uv run alembic history        # cronologia completa
uv run alembic check           # detecta drift entre models e banco
```
