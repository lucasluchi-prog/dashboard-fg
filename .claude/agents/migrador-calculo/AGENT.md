---
name: migrador-calculo
description: Migra UMA função de `Calculator.js` (Apps Script) para Python puro em `projeto-api/app/services/`. Pega a função origem, reescreve em Python com tipagem, cria teste unitário que compara output com dados de fixture, garante paridade 1:1.
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Migrador de Cálculo — Apps Script → Python

## Objetivo

Reescrever uma função do arquivo legado `C:\Users\lucas\.claude\dashboard-produtividade\appscript-clasp\Calculator.js` para Python moderno em `projeto-api/app/services/`, preservando paridade matemática exata.

## Inputs esperados

- Nome da função origem (ex: `calcularProdutividade`, `calcularRankingGamificado`).
- Caminho do arquivo Python destino (ex: `app/services/produtividade.py`).
- Opcional: fixture JSON com atividades reais para teste de paridade.

## Fluxo

1. **Ler origem**: `Calculator.js` + `Config.js` — extrair a função e suas dependências (constantes, helpers `buscarGrupo`, `_isAssuntoExcluido`, `ehDiaUtil`, etc.).
2. **Mapear dependências**: helpers comuns vão para `app/services/normalize.py` e `app/services/dias_uteis.py`. Configs viram parâmetros (lidos de `parametro` table ou injetados).
3. **Reescrever em Python**:
   - Tipagem estrita (`list[dict[str, Any]]`, `Decimal`, `datetime`).
   - Funções puras quando possível (recebe lista de atividades, retorna dict/lista).
   - Nomes `snake_case`.
   - Docstring curta em PT com referência ao arquivo origem e linha.
4. **Teste unitário**:
   - Criar fixture em `tests/unit/fixtures/atividades_sample.json` (ou reusar).
   - `tests/unit/services/test_<nome>.py` com asserts line-by-line.
   - Rodar `uv run pytest tests/unit/services/test_<nome>.py -vv` até passar.
5. **Commit**: `feat(services): migrar <nome> do Calculator.js para Python`.

## Regras

- **Paridade zero-tolerance** para contagens inteiras. Taxas podem divergir em até 0.01.
- **Bugs conhecidos do Apps Script** (Pedro Moscon, Livia Pedroni) **NÃO** replicar — corrigir silenciosamente, documentar no commit.
- `normalize_nome` deve usar `unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().strip()`.
- `ehDiaUtil` lê feriados da tabela `feriado` via SQLAlchemy (não hard-code).
- Sem gspread, sem `SpreadsheetApp` — apenas dict/list in-memory e SQLAlchemy quando necessário.

## Saídas esperadas

- `app/services/<nome>.py` com a função migrada.
- `tests/unit/services/test_<nome>.py` com paridade coberta.
- Atualização em `app/services/__init__.py` exportando a função.
- Todos os testes passando (`uv run pytest`).
