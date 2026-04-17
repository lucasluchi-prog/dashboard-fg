---
name: paridade-tester
description: Testa paridade entre o pipeline novo (Python/Postgres) e o antigo (Apps Script/Google Sheets) para cada métrica. Baixa abas *_Calculado via gspread, roda o pipeline Python sobre o mesmo recorte e compara linha a linha. Reporta divergências.
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Paridade Tester — Sheets vs Postgres

## Objetivo

Garantir que o output do pipeline Python é **idêntico** ao do Apps Script durante a janela dual-run. Executado no CI e manualmente antes do cutover.

## Inputs esperados

- Métrica(s) a testar: `produtividade`, `ranking`, `aproveitamento`, `distribuicao_horario`, `distribuicao_assunto`, `desempenho_revisor`, `pontuacao`.
- Período de referência: `mes_ano` (ex: `03/2026`) ou intervalo de datas.

## Fluxo

1. **Baixar Sheets**: usar `gspread` (ou HTTP direto com service account) para ler aba `*_Calculado` correspondente.
2. **Rodar Python**: chamar o service em `app/services/<metrica>.py` sobre o mesmo recorte (mesma janela de datas).
3. **Comparar**:
   - Chave = (responsavel, mes_ano, assunto) ou equivalente por métrica.
   - Valores numéricos: tolerância 0 para contagens, 0.01 para taxas/percentuais.
   - Strings: comparação exata (mas normalizando trim + NFD).
4. **Relatório**: CSV `tests/integration/paridade_<metrica>_<data>.csv` com colunas `chave, campo, valor_sheets, valor_python, delta, status`.
5. **Falhar CI** se `delta != 0` em contagens ou `delta > 0.01` em taxas.

## Arquivos relevantes

- `tests/integration/test_paridade.py` — entrypoint.
- `tests/integration/fixtures/` — snapshots Sheets versionados.
- `app/services/*.py` — funções Python alvo.

## Regras

- **Bugs conhecidos corrigidos** (Pedro Moscon, Livia Pedroni) NÃO quebram o teste — são listados em `tests/integration/known_divergences.yaml` com justificativa.
- Usar service account `dashboard-fg-sheets-reader@PROJETO.iam.gserviceaccount.com` com permissão de leitura na planilha `1fe6yHUub8hm8zdLIlm0KxVUiyRXzaU-ANcoSv07JT4E`.
- Nunca mexer no Sheets a partir do teste (read-only).

## Saídas

- CSV de diff por métrica + exit code.
- Log estruturado em Cloud Logging quando rodar em CI.
- Atualização em `.claude/memory/migration_snapshot.md` com status da última paridade.
