---
name: Migration Snapshot
description: Checkpoint do progresso da migração Apps Script -> Python/React/Postgres do Dashboard de Produtividade
type: project
---

# Migration Snapshot — Dashboard FG

## Estado atual (2026-04-17)

- **Sprint 0**: ✅ scaffold, `.claude`, `.vscode`, `.cursor`, docker-compose.
- **Sprint 1**: ✅ backend FastAPI + SQLAlchemy async + Alembic + routers + OAuth Google.
- **Sprint 2a**: ✅ services Python puros com paridade 1:1 ao Calculator.js (normalize com en-dash fix, produtividade, ranking, aproveitamento, aproveitamento_individual, aproveitamento_peticao, desempenho_revisor, distribuicao_horario, distribuicao_assunto).
- **Sprint 2b**: ✅ migration `20260417_1430` com 8 tabelas calculadas (substitui MVs placeholder).
- **Sprint 2c**: ✅ ETL orquestra coleta + cálculos + persistência. 45/45 testes unitários verdes.
- **Sprint 2d**: ✅ `tests/integration/test_paridade.py` com 5 comparações (produtividade, aproveitamento, aprov_individual, desempenho_revisor, ranking) opt-in via `SHEETS_SERVICE_ACCOUNT`.
- **Sprint 3**: ✅ frontend React completo (Dashboard + Ranking, hooks TanStack Query, Tailwind, Recharts).
- **Sprint 4/5**: aguardam aprovação GCP + validação do time.

## Paridade por métrica

| Métrica | Service Python | Teste unit | Paridade Sheets |
|---|---|---|---|
| produtividade | `app/services/produtividade.py::calcular_produtividade` | ✅ | opt-in gspread |
| ranking | `app/services/ranking.py::calcular_ranking` | ✅ | opt-in gspread |
| aproveitamento | `app/services/aproveitamento.py::calcular_aproveitamento` | ✅ | opt-in gspread |
| aproveitamento_individual | `...::calcular_aproveitamento_individual` | ✅ | opt-in gspread |
| aproveitamento_peticao | `...::calcular_aproveitamento_peticao` | ✅ | (stub) |
| desempenho_revisor | `...::calcular_desempenho_revisor` | ✅ | opt-in gspread |
| distribuicao_horario | `app/services/distribuicao.py::calcular_distribuicao_horario` | ✅ | — |
| distribuicao_assunto | `...::calcular_distribuicao_assunto` | ✅ | — |
| pontuacao (pré-ranking) | (agrupado em ranking) | ✅ | — |

## Melhorias sobre o Apps Script

- `normalize()` converte en-dash/em-dash/figure-dash para hyphen regular — o Apps Script falha silenciosamente quando um assunto tem `–` (ex: "Petição Inicial – PREV") e a tabela de pontuação usa `-`. Agora "Petição Inicial – PREV" pontua corretamente no ranking.

## Divergências conhecidas

Nenhuma ainda — preencher à medida que testes rodarem.

## Bugs do Apps Script corrigidos na migração

- Pedro Moscon (grupo Previdenciário - Operacional) — detalhar no commit quando corrigido.
- Livia Pedroni — detalhar no commit quando corrigido.

## Referências

- Plano: `C:\Users\lucas\.claude\plans\sobre-o-dashboard-de-lovely-sifakis.md`
- Legado: `C:\Users\lucas\.claude\dashboard-produtividade\`
- Spreadsheet origem: `1fe6yHUub8hm8zdLIlm0KxVUiyRXzaU-ANcoSv07JT4E`
