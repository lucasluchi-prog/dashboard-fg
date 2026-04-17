"""Teste de paridade — Python vs Google Sheets `*_Calculado`.

Opt-in: só roda quando `SHEETS_SERVICE_ACCOUNT` está definida.
Requer `pip install '.[paridade]'`.

Executa:
    pytest tests/integration/test_paridade.py --sheets-service-account=path.json
ou via env:
    SHEETS_SERVICE_ACCOUNT=/path/creds.json pytest tests/integration/test_paridade.py
"""

from __future__ import annotations

import csv
import os
from datetime import date
from pathlib import Path

import pytest

from app.services.aproveitamento import (
    calcular_aproveitamento,
    calcular_aproveitamento_individual,
    calcular_desempenho_revisor,
)
from app.services.dias_uteis import FERIADOS_HARDCODED
from app.services.produtividade import calcular_produtividade
from app.services.ranking import calcular_ranking

pytestmark = pytest.mark.skipif(
    not os.environ.get("SHEETS_SERVICE_ACCOUNT"),
    reason="Requer SHEETS_SERVICE_ACCOUNT e dep extra `paridade`.",
)


def _snapshots_dir() -> Path:
    p = Path(__file__).parent / "snapshots"
    p.mkdir(exist_ok=True)
    return p


def _dump_diff(nome: str, divergencias: list[dict]) -> Path:
    out = _snapshots_dir() / f"{nome}.csv"
    if not divergencias:
        return out
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted({k for d in divergencias for k in d}))
        writer.writeheader()
        for d in divergencias:
            writer.writerow(d)
    return out


def test_paridade_produtividade():  # pragma: no cover
    from tests.integration.paridade_helpers import comparar, read_atividades_raw, read_sheet

    atividades = read_atividades_raw()
    esperado = read_sheet("Produtividade_Calculado")
    atual = calcular_produtividade(
        atividades,
        feriados=FERIADOS_HARDCODED,
        hoje=date.today(),
    )
    # Mapeia colunas do Python para o shape do Sheets
    atual_mapped = [
        {
            "Responsavel": r["responsavel"],
            "Mes_Ano": r["mes_ano"],
            "Natureza": r["natureza"],
            "Assunto": r["assunto"],
            "Grupo": r["grupo"],
            "Quinzena": r["quinzena"],
            "Total Concluidas": r["total_concluidas"],
            "Concluidas Dias Uteis": r["concluidas_dias_uteis"],
            "Dias Uteis no Periodo": r["dias_uteis_periodo"],
            "Media Diaria": r["media_diaria"],
            "No Prazo": r["no_prazo"],
            "Fora do Prazo": r["fora_do_prazo"],
            "Taxa Prazo Pct": r["taxa_prazo_pct"] if r["taxa_prazo_pct"] is not None else "N/A",
        }
        for r in atual
    ]
    divs = comparar(
        esperado,
        atual_mapped,
        chaves=["Responsavel", "Mes_Ano", "Natureza", "Quinzena", "Assunto"],
        numericos=[
            "Total Concluidas", "Concluidas Dias Uteis", "Dias Uteis no Periodo",
            "Media Diaria", "No Prazo", "Fora do Prazo", "Taxa Prazo Pct",
        ],
    )
    path = _dump_diff("paridade_produtividade", divs)
    assert not divs, f"Ver divergências em {path}"


def test_paridade_aproveitamento():  # pragma: no cover
    from tests.integration.paridade_helpers import comparar, read_atividades_raw, read_sheet

    atividades = read_atividades_raw()
    esperado = read_sheet("Aproveitamento_Calculado")
    atual = calcular_aproveitamento(atividades)
    atual_mapped = [
        {
            "Responsavel": r["responsavel"],
            "Mes_Ano": r["mes_ano"],
            "Natureza": r["assunto"],  # Sheet usa "Natureza" para o assunto (legado)
            "Grupo": r["grupo"],
            "Sem Ressalva": r["sem_ressalva"],
            "Com Ressalva": r["com_ressalva"],
            "Com Acrescimo": r["com_acrescimo"],
            "Ressalva_Acrescimo": r["com_ressalva_e_acrescimo"],
            "Sem Aproveitamento": r["sem_aproveitamento"],
            "Total Revisoes": r["total_revisoes"],
            "Pontuacao Total": r["pontuacao_total"],
            "Pontuacao Maxima": r["pontuacao_maxima"],
            "Taxa Aproveitamento Pct": r["taxa_aproveitamento_pct"],
        }
        for r in atual
    ]
    divs = comparar(
        esperado,
        atual_mapped,
        chaves=["Responsavel", "Mes_Ano", "Natureza"],
        numericos=[
            "Sem Ressalva", "Com Ressalva", "Com Acrescimo",
            "Ressalva_Acrescimo", "Sem Aproveitamento",
            "Total Revisoes", "Pontuacao Total", "Pontuacao Maxima",
            "Taxa Aproveitamento Pct",
        ],
    )
    path = _dump_diff("paridade_aproveitamento", divs)
    assert not divs, f"Ver divergências em {path}"


def test_paridade_aproveitamento_individual():  # pragma: no cover
    from tests.integration.paridade_helpers import comparar, read_atividades_raw, read_sheet

    atividades = read_atividades_raw()
    esperado = read_sheet("Aproveitamento_Individual")
    atual = calcular_aproveitamento_individual(atividades)
    atual_mapped = [
        {
            "Avaliado": r["avaliado"],
            "Mes_Ano": r["mes_ano"],
            "Sem Ressalva": r["sem_ressalva"],
            "Com Ressalva": r["com_ressalva"],
            "Com Acrescimo": r["com_acrescimo"],
            "Ressalva_Acrescimo": r["ressalva_acrescimo"],
            "Sem Aproveitamento": r["sem_aproveitamento"],
            "Total": r["total"],
            "Taxa_Pct": r["taxa_pct"],
        }
        for r in atual
    ]
    divs = comparar(
        esperado,
        atual_mapped,
        chaves=["Avaliado", "Mes_Ano"],
        numericos=[
            "Sem Ressalva", "Com Ressalva", "Com Acrescimo",
            "Ressalva_Acrescimo", "Sem Aproveitamento",
            "Total", "Taxa_Pct",
        ],
    )
    path = _dump_diff("paridade_aproveitamento_individual", divs)
    assert not divs, f"Ver divergências em {path}"


def test_paridade_desempenho_revisor():  # pragma: no cover
    from tests.integration.paridade_helpers import comparar, read_atividades_raw, read_sheet

    atividades = read_atividades_raw()
    esperado = read_sheet("Desempenho_Revisor")
    atual = calcular_desempenho_revisor(atividades)
    atual_mapped = [
        {
            "Revisor": r["revisor"],
            "Mes_Ano": r["mes_ano"],
            "Total_Revisoes": r["total_revisoes"],
            "Sem_Ressalva": r["sem_ressalva"],
            "Com_Correcao": r["com_correcao"],
            "Taxa_Correcao_Pct": r["taxa_correcao_pct"],
            "Assunto_Mais_Corrigido": r["assunto_mais_corrigido"],
            "Qtd_Assunto_Mais_Corrigido": r["qtd_assunto_mais_corrigido"],
        }
        for r in atual
    ]
    divs = comparar(
        esperado,
        atual_mapped,
        chaves=["Revisor", "Mes_Ano"],
        numericos=[
            "Total_Revisoes", "Sem_Ressalva", "Com_Correcao",
            "Taxa_Correcao_Pct", "Qtd_Assunto_Mais_Corrigido",
        ],
    )
    path = _dump_diff("paridade_desempenho_revisor", divs)
    assert not divs, f"Ver divergências em {path}"


def test_paridade_ranking():  # pragma: no cover
    from tests.integration.paridade_helpers import comparar, read_atividades_raw, read_sheet
    from app.services.normalize import normalize

    atividades = read_atividades_raw()
    esperado = read_sheet("Ranking_Gamificado")
    aprov_indiv = read_sheet("Aproveitamento_Individual")
    taxa_map = {
        f"{normalize(str(r.get('Avaliado', '')))}|{r.get('Mes_Ano', '')}": float(
            r.get("Taxa_Pct") or 100
        )
        for r in aprov_indiv
    }
    # Pontuação por grupo lida do módulo seed (fonte única).
    from scripts.seed_from_apps_script import PONTUACAO_POR_GRUPO
    from app.services.normalize import normalize as _norm

    por_grupo = {
        g: {k: v for k, v in tabela.items()}
        for g, tabela in PONTUACAO_POR_GRUPO.items()
    }
    atual = calcular_ranking(
        atividades,
        pontuacao_por_grupo=por_grupo,
        taxa_aprov_map=taxa_map,
    )
    atual_mapped = [
        {
            "Responsavel": r["responsavel"],
            "Mes_Ano": r["mes_label"],  # Sheets usa "Mar/2026"
            "Grupo": r["grupo"],
            "Posicao": r["posicao"],
            "Pontos Brutos": r["pontos_brutos"],
            "Pontos Validos": r["pontos_validos"],
            "Total Atividades": r["total_atividades"],
            "Taxa Aproveitamento Pct": r["taxa_aprov"],
        }
        for r in atual
    ]
    divs = comparar(
        esperado,
        atual_mapped,
        chaves=["Responsavel", "Mes_Ano"],
        numericos=[
            "Posicao", "Pontos Brutos", "Pontos Validos",
            "Total Atividades", "Taxa Aproveitamento Pct",
        ],
    )
    path = _dump_diff("paridade_ranking", divs)
    assert not divs, f"Ver divergências em {path}"
