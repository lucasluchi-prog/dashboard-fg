"""Distribuição por horário e por assunto — paridade com
`calcularDistribuicaoHorario` e `calcularDistribuicaoAssunto` (Calculator.js:596, 671)."""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produtividade_calc import (
    DistribuicaoAssuntoCalculada,
    DistribuicaoHorarioCalculada,
)
from app.services.normalize import (
    buscar_grupo,
    is_assunto_excluido,
    is_excluido_por_grupo,
    parse_data,
)


def calcular_distribuicao_horario(
    atividades: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    grupos: dict[str, int] = {}
    for row in atividades:
        status = str(row.get("Status") or "").strip().lower()
        if "conclu" not in status:
            continue
        dc = row.get("Data Conclusao") or row.get("dataConclusao")
        if not dc:
            continue
        cp = str(row.get("ConcluidoPor") or "").strip()
        responsavel = cp or str(row.get("Responsavel") or "").strip()
        if not responsavel:
            continue
        resp_princ = str(row.get("Responsavel Atividade Principal") or "").strip()
        resp_atual = str(row.get("Responsavel") or "").strip()
        if resp_princ and resp_atual and resp_princ == resp_atual:
            continue

        dt = parse_data(dc)
        if dt is None:
            continue
        hora = dt.hour
        mes_ano = f"{dt.month:02d}/{dt.year}"
        chave = f"{responsavel}|{mes_ano}|{hora}"
        grupos[chave] = grupos.get(chave, 0) + 1

    out: list[dict[str, Any]] = []
    for chave, contagem in grupos.items():
        resp, mes_ano, hora = chave.split("|")
        out.append({
            "responsavel": resp,
            "mes_ano": mes_ano,
            "hora": int(hora),
            "contagem": contagem,
        })
    return out


def calcular_distribuicao_assunto(
    atividades: Iterable[dict[str, Any]],
    *,
    assuntos_excluidos_grupo: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    blacklist_g = assuntos_excluidos_grupo or {}
    grupos: dict[str, int] = {}

    for row in atividades:
        status = str(row.get("Status") or "").strip().lower()
        if "conclu" not in status:
            continue
        dc = row.get("Data Conclusao") or row.get("dataConclusao")
        if not dc:
            continue
        cp = str(row.get("ConcluidoPor") or "").strip()
        responsavel = cp or str(row.get("Responsavel") or "").strip()
        if not responsavel:
            continue
        assunto_l = str(row.get("Assunto") or "").strip().lower()
        if assunto_l.startswith("revis"):
            resp_princ = str(row.get("Responsavel Atividade Principal") or "").strip()
            if resp_princ and responsavel == resp_princ:
                continue
        assunto = str(row.get("Assunto") or "").strip()
        if not assunto:
            continue
        if is_assunto_excluido(assunto):
            continue
        grupo = buscar_grupo(responsavel)
        if is_excluido_por_grupo(assunto, grupo, blacklist_g):
            continue

        dt = parse_data(dc)
        if dt is None:
            continue
        mes_ano = f"{dt.month:02d}/{dt.year}"
        chave = f"{responsavel}|{mes_ano}|{assunto}"
        grupos[chave] = grupos.get(chave, 0) + 1

    out: list[dict[str, Any]] = []
    for chave, contagem in grupos.items():
        resp, mes_ano, assunto = chave.split("|", 2)
        out.append({
            "responsavel": resp,
            "mes_ano": mes_ano,
            "assunto": assunto,
            "contagem": contagem,
        })
    return out


# ---- HTTP (formato esperado pelo frontend — igual ao app.py legado) ----

async def listar_horario(db: AsyncSession) -> list[dict[str, Any]]:
    """Retorna linhas já agregadas em buckets (antes_8, 8-14, após 14) para compat com dashboard."""
    try:
        result = await db.execute(select(DistribuicaoHorarioCalculada))
    except ProgrammingError:
        await db.rollback()
        return []
    # agregar por (responsavel, mes_ano) em 3 buckets
    agg: dict[tuple[str, str], dict[str, Any]] = {}
    for r in result.scalars().all():
        key = (r.responsavel, r.mes_ano)
        b = agg.get(key)
        if b is None:
            b = {
                "responsavel": r.responsavel,
                "mes_ano": r.mes_ano,
                "antes_8": 0,
                "entre_8_14": 0,
                "apos_14": 0,
                "total_atividades": 0,
            }
            agg[key] = b
        h = r.hora
        c = r.contagem
        if h < 8:
            b["antes_8"] += c
        elif h < 14:
            b["entre_8_14"] += c
        else:
            b["apos_14"] += c
        b["total_atividades"] += c
    return list(agg.values())


async def listar_assunto(db: AsyncSession) -> list[dict[str, Any]]:
    try:
        result = await db.execute(select(DistribuicaoAssuntoCalculada))
    except ProgrammingError:
        await db.rollback()
        return []
    return [
        {
            "responsavel": r.responsavel,
            "mes_ano": r.mes_ano,
            "assunto": r.assunto,
            "total": r.contagem,
        }
        for r in result.scalars().all()
    ]
