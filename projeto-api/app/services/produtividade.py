"""Produtividade — paridade 1:1 com `calcularProdutividade` (Calculator.js:210)."""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produtividade_calc import ProdutividadeCalculada
from app.schemas.produtividade import ProdutividadeItem
from app.services.dias_uteis import dias_uteis_quinzena, eh_dia_util
from app.services.normalize import (
    buscar_grupo,
    extrair_mes_ano,
    is_assunto_excluido,
    is_excluido_por_grupo,
    parse_data,
)


def calcular_produtividade(
    atividades: Iterable[dict[str, Any]],
    *,
    feriados: set[date],
    assuntos_permitidos: dict[str, set[str]] | None = None,
    assuntos_excluidos_grupo: dict[str, set[str]] | None = None,
    hoje: date | None = None,
) -> list[dict[str, Any]]:
    """Retorna linhas agregadas por (responsavel, mes_ano, natureza, quinzena, assunto).

    `atividades`: dicts no shape do ETL (chaves do Sheets):
        Responsavel, ConcluidoPor, Status, Assunto, Natureza, Data, Data Conclusao,
        Data Prazo Fatal, Responsavel Atividade Principal, Pasta.

    `assuntos_permitidos[grupo]` = whitelist; ausência = todos permitidos.
    `assuntos_excluidos_grupo[grupo]` = blacklist adicional à global.
    """
    whitelist = assuntos_permitidos or {}
    blacklist_g = assuntos_excluidos_grupo or {}
    grupos: dict[str, dict[str, Any]] = {}

    for row in atividades:
        cp = str(row.get("ConcluidoPor") or "").strip()
        responsavel = cp or row.get("Responsavel") or "Sem Responsavel"
        situacao = str(row.get("Status") or "")
        if not situacao.strip().lower().startswith("conclu"):
            continue

        assunto = str(row.get("Assunto") or "").strip()
        natureza = str(row.get("Natureza") or "")
        grupo = buscar_grupo(responsavel)

        if is_assunto_excluido(assunto):
            continue
        if is_excluido_por_grupo(assunto, grupo, blacklist_g):
            continue
        # Whitelist por grupo
        if grupo and grupo in whitelist and assunto not in whitelist[grupo]:
            continue

        # Filtrar revisão onde responsavel == responsavel da atividade principal
        resp_principal = str(row.get("Responsavel Atividade Principal") or "").strip()
        if assunto.lower().startswith("revis") and resp_principal and responsavel == resp_principal:
            continue

        data_concl_raw = row.get("Data Conclusao") or row.get("dataConclusao")
        if not data_concl_raw:
            continue
        mes_ano = extrair_mes_ano(data_concl_raw)
        if not mes_ano:
            continue
        dt_concl = parse_data(data_concl_raw)
        if dt_concl is None:
            continue
        quinzena = "Q1" if dt_concl.day <= 15 else "Q2"

        chave = f"{responsavel}|{mes_ano}|{natureza}|{quinzena}|{assunto}"
        g = grupos.get(chave)
        if g is None:
            g = {
                "responsavel": responsavel,
                "mesAno": mes_ano,
                "natureza": natureza,
                "assunto": assunto,
                "grupo": grupo,
                "quinzena": quinzena,
                "totalConcluidas": 0,
                "noPrazo": 0,
                "foraDoPrazo": 0,
                "concluidasDiaUtil": 0,
            }
            grupos[chave] = g

        g["totalConcluidas"] += 1
        if eh_dia_util(dt_concl, feriados):
            g["concluidasDiaUtil"] += 1

        prazo_raw = row.get("Data Prazo Fatal") or row.get("dataPrazoFatal")
        if prazo_raw:
            dt_prazo = parse_data(prazo_raw)
            if dt_prazo is not None:
                if dt_concl.date() <= dt_prazo.date():
                    g["noPrazo"] += 1
                else:
                    g["foraDoPrazo"] += 1

    resultado: list[dict[str, Any]] = []
    for g in grupos.values():
        dias_uteis = dias_uteis_quinzena(g["mesAno"], g["quinzena"], feriados, hoje)
        media_diaria = round(g["concluidasDiaUtil"] / dias_uteis, 2) if dias_uteis > 0 else 0.0
        total_com_prazo = g["noPrazo"] + g["foraDoPrazo"]
        taxa_prazo = (
            round((g["noPrazo"] / total_com_prazo) * 100, 2) if total_com_prazo > 0 else None
        )
        resultado.append({
            "responsavel": g["responsavel"],
            "mes_ano": g["mesAno"],
            "natureza": g["natureza"],
            "assunto": g["assunto"],
            "grupo": g["grupo"],
            "quinzena": g["quinzena"],
            "total_concluidas": g["totalConcluidas"],
            "concluidas_dias_uteis": g["concluidasDiaUtil"],
            "dias_uteis_periodo": dias_uteis,
            "media_diaria": media_diaria,
            "no_prazo": g["noPrazo"],
            "fora_do_prazo": g["foraDoPrazo"],
            "taxa_prazo_pct": taxa_prazo,
        })
    return resultado


# ---- Acesso HTTP (router) ----

async def listar(
    db: AsyncSession,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[ProdutividadeItem]:
    """Le da tabela `produtividade_calculada` (populada pelo ETL)."""
    stmt = select(ProdutividadeCalculada)
    if grupo:
        stmt = stmt.where(ProdutividadeCalculada.grupo == grupo)
    if mes_ano:
        stmt = stmt.where(ProdutividadeCalculada.mes_ano == mes_ano)
    stmt = stmt.order_by(
        ProdutividadeCalculada.grupo,
        ProdutividadeCalculada.responsavel,
        ProdutividadeCalculada.mes_ano,
    )
    try:
        result = await db.execute(stmt)
    except ProgrammingError:
        await db.rollback()
        return []

    def _aggregate(rows: list[ProdutividadeCalculada]) -> list[ProdutividadeItem]:
        """Agrega por (responsavel, grupo, mes_ano, quinzena) — o schema antigo tinha só 1 quinzena por linha."""
        bucket: dict[tuple[str, str, str, str | None], dict[str, Any]] = {}
        for r in rows:
            key = (r.responsavel, r.grupo or "", r.mes_ano, r.quinzena)
            b = bucket.get(key)
            if b is None:
                b = {
                    "responsavel": r.responsavel,
                    "grupo": r.grupo or "",
                    "mes_ano": r.mes_ano,
                    "quinzena": r.quinzena,
                    "total_concluidas": 0,
                    "total_atribuidas": 0,
                    "prazos_no_prazo": 0,
                    "prazos_em_atraso": 0,
                    "ativ_por_dia_util_sum": 0.0,
                    "count": 0,
                }
                bucket[key] = b
            b["total_concluidas"] += r.total_concluidas
            b["total_atribuidas"] += r.total_concluidas + (r.fora_do_prazo or 0)
            b["prazos_no_prazo"] += r.no_prazo
            b["prazos_em_atraso"] += r.fora_do_prazo
            b["ativ_por_dia_util_sum"] += r.media_diaria
            b["count"] += 1

        items: list[ProdutividadeItem] = []
        for b in bucket.values():
            taxa = (
                b["total_concluidas"] / b["total_atribuidas"]
                if b["total_atribuidas"] > 0
                else 0.0
            )
            media = b["ativ_por_dia_util_sum"] / b["count"] if b["count"] > 0 else 0.0
            items.append(
                ProdutividadeItem(
                    responsavel=b["responsavel"],
                    grupo=b["grupo"],
                    mes_ano=b["mes_ano"],
                    quinzena=b["quinzena"],
                    total_concluidas=b["total_concluidas"],
                    total_atribuidas=b["total_atribuidas"],
                    taxa_conclusao=taxa,
                    prazos_no_prazo=b["prazos_no_prazo"],
                    prazos_em_atraso=b["prazos_em_atraso"],
                    atividades_por_dia_util=media,
                )
            )
        return items

    return _aggregate(list(result.scalars().all()))
