"""Ranking Gamificado — paridade 1:1 com `calcularRankingGamificado` (Calculator.js:1011).

Pontos Brutos = soma de pontuação base por atividade concluída.
Taxa Aproveitamento = lida do aproveitamento individual (por avaliado/mes).
Pontos Válidos = Pontos Brutos × (Taxa / 100).
"""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produtividade_calc import RankingCalculada
from app.schemas.ranking import RankingItem
from app.services.normalize import (
    buscar_grupo,
    extrair_mes_ano,
    is_assunto_excluido,
    is_excluido_por_grupo,
    mes_ano_label,
    normalize,
)

PontuacaoPorGrupo = dict[str, dict[str, int]]


def buscar_pontuacao_ranking(
    assunto: str | None,
    grupo: str | None,
    pontuacao_por_grupo: PontuacaoPorGrupo,
) -> int:
    """Paridade com `buscarPontuacaoRanking`.

    Match exato por assunto normalizado; fallback substring (norm in key OR key in norm).
    """
    if not grupo or grupo not in pontuacao_por_grupo:
        return 0
    tabela = pontuacao_por_grupo[grupo]
    norm = normalize(assunto)
    if not norm:
        return 0
    if norm in tabela:
        return tabela[norm]
    for key, v in tabela.items():
        if key and (key in norm or norm in key):
            return v
    return 0


def calcular_ranking(
    atividades: Iterable[dict[str, Any]],
    *,
    pontuacao_por_grupo: PontuacaoPorGrupo,
    taxa_aprov_map: dict[str, float],
    assuntos_excluidos_grupo: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    """Retorna lista ordenada de entradas com posição por mês.

    `taxa_aprov_map[normalize(nome)|mes_ano] = taxa 0..100`.
    `assuntos_excluidos_grupo[grupo] = set(normalized)`.
    """
    blacklist_g = assuntos_excluidos_grupo or {}
    acumuladores: dict[str, dict[str, Any]] = {}

    for row in atividades:
        if not str(row.get("Status") or "").strip().lower().startswith("conclu"):
            continue
        cp = str(row.get("ConcluidoPor") or "").strip()
        responsavel = cp or row.get("Responsavel") or ""
        if not responsavel:
            continue
        assunto = str(row.get("Assunto") or "").strip()
        grupo = buscar_grupo(responsavel)
        if is_assunto_excluido(assunto):
            continue
        if is_excluido_por_grupo(assunto, grupo, blacklist_g):
            continue
        # Excluir autorevisão
        if assunto.lower().startswith("revis"):
            resp_princ = str(row.get("Responsavel Atividade Principal") or "").strip()
            if resp_princ and responsavel == resp_princ:
                continue
        data_concl_raw = row.get("Data Conclusao") or row.get("dataConclusao")
        if not data_concl_raw:
            continue
        mes_ano = extrair_mes_ano(data_concl_raw)
        if not mes_ano:
            continue

        pontos_base = buscar_pontuacao_ranking(assunto, grupo, pontuacao_por_grupo)
        if pontos_base == 0:
            continue

        chave = f"{responsavel}|{mes_ano}"
        acc = acumuladores.get(chave)
        if acc is None:
            acc = {
                "responsavel": responsavel,
                "mesAno": mes_ano,
                "grupo": grupo,
                "pontosBrutos": 0,
                "totalAtividades": 0,
            }
            acumuladores[chave] = acc
        acc["pontosBrutos"] += pontos_base
        acc["totalAtividades"] += 1

    # Aplicar taxa de aproveitamento
    entries: list[dict[str, Any]] = []
    for e in acumuladores.values():
        chave_aprov = f"{normalize(e['responsavel'])}|{e['mesAno']}"
        taxa = taxa_aprov_map.get(chave_aprov, 100.0)
        pontos_validos = round(e["pontosBrutos"] * (taxa / 100))
        entries.append({
            "responsavel": e["responsavel"],
            "mes_ano": e["mesAno"],
            "grupo": e["grupo"],
            "pontos_brutos": round(e["pontosBrutos"]),
            "pontos_validos": pontos_validos,
            "total_atividades": e["totalAtividades"],
            "taxa_aprov": taxa,
        })

    # Ordenar mesAno DESC, depois pontos DESC; atribuir posicao dentro do mes
    entries.sort(key=lambda x: (x["mes_ano"], -x["pontos_validos"]), reverse=False)
    # `mes_ano` DESC: fazemos sort reverso só no mes_ano
    entries.sort(key=lambda x: x["mes_ano"], reverse=True)
    # Dentro do mesmo mes, ordenar por pontos_validos DESC mantendo ordem estável
    by_mes: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        by_mes.setdefault(e["mes_ano"], []).append(e)
    out: list[dict[str, Any]] = []
    for mes in sorted(by_mes, reverse=True):
        grupo_m = sorted(by_mes[mes], key=lambda x: x["pontos_validos"], reverse=True)
        for i, e in enumerate(grupo_m, start=1):
            e["posicao"] = i
            e["mes_label"] = mes_ano_label(e["mes_ano"])
            out.append(e)
    return out


async def listar(
    db: AsyncSession,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[RankingItem]:
    stmt = select(RankingCalculada)
    if grupo:
        stmt = stmt.where(RankingCalculada.grupo == grupo)
    if mes_ano:
        stmt = stmt.where(RankingCalculada.mes_ano == mes_ano)
    stmt = stmt.order_by(RankingCalculada.mes_ano.desc(), RankingCalculada.posicao)
    try:
        result = await db.execute(stmt)
    except ProgrammingError:
        await db.rollback()
        return []

    return [
        RankingItem(
            posicao=r.posicao,
            responsavel=r.responsavel,
            grupo=r.grupo or "",
            pontos_totais=float(r.pontos_validos),
            total_atividades=r.total_atividades,
            aproveitamento_medio=r.taxa_aprov,
            mes_ano=r.mes_ano,
        )
        for r in result.scalars().all()
    ]
