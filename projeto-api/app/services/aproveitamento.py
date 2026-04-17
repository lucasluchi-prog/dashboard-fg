"""Aproveitamento — paridade com `calcularAproveitamento`, `calcularAproveitamentoIndividual`,
`calcularAproveitamentoPeticao`, `calcularDesempenhoRevisor`.
"""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produtividade_calc import (
    AproveitamentoCalculada,
    AproveitamentoIndividualCalculada,
)
from app.schemas.aproveitamento import AproveitamentoIndividualItem, AproveitamentoItem
from app.services.normalize import (
    PESOS_APROVEITAMENTO,
    buscar_grupo,
    extrair_mes_ano,
    is_assunto_excluido,
    normalizar_aproveitamento,
)


def calcular_aproveitamento(
    atividades: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Paridade com `calcularAproveitamento` (Calculator.js:120).

    Agrupa por (responsavel, mes_ano, natureza, assunto) — `assunto` prefere `Assunto Atividade Principal`.
    """
    grupos: dict[str, dict[str, Any]] = {}

    for row in atividades:
        responsavel = row.get("Responsavel") or "Sem Responsavel"
        aproveitamento = row.get("Aproveitamento") or ""
        data = row.get("Data Conclusao") or row.get("Data")
        natureza = row.get("Natureza") or ""
        assunto = row.get("Assunto Atividade Principal") or row.get("Assunto") or ""
        if is_assunto_excluido(assunto):
            continue
        grupo = buscar_grupo(responsavel)
        if not aproveitamento or not data:
            continue
        mes_ano = extrair_mes_ano(data)
        if not mes_ano:
            continue

        chave = f"{responsavel}|{mes_ano}|{natureza}|{assunto}"
        g = grupos.get(chave)
        if g is None:
            g = {
                "responsavel": responsavel,
                "mesAno": mes_ano,
                "natureza": natureza,
                "assunto": assunto,
                "grupo": grupo,
                "contagens": {tipo: 0 for tipo in PESOS_APROVEITAMENTO},
            }
            grupos[chave] = g

        tipo = normalizar_aproveitamento(aproveitamento)
        if tipo and tipo in g["contagens"]:
            g["contagens"][tipo] += 1

    resultado: list[dict[str, Any]] = []
    for g in grupos.values():
        c = g["contagens"]
        sem_r = c["Revisão sem ressalva"]
        com_r = c["Revisão com ressalva"]
        com_a = c["Revisão com acréscimo"]
        res_ac = c["Revisão com ressalva e acréscimo"]
        sem_a = c["Revisão sem aproveitamento"]
        total = sem_r + com_r + com_a + res_ac + sem_a
        pontuacao = (
            sem_r * PESOS_APROVEITAMENTO["Revisão sem ressalva"]
            + com_r * PESOS_APROVEITAMENTO["Revisão com ressalva"]
            + com_a * PESOS_APROVEITAMENTO["Revisão com acréscimo"]
            + res_ac * PESOS_APROVEITAMENTO["Revisão com ressalva e acréscimo"]
            + sem_a * PESOS_APROVEITAMENTO["Revisão sem aproveitamento"]
        )
        p_max = total * 100
        taxa = round((pontuacao / p_max) * 100, 2) if p_max > 0 else 0.0
        resultado.append({
            "responsavel": g["responsavel"],
            "mes_ano": g["mesAno"],
            "natureza": g["natureza"],
            "assunto": g["assunto"],
            "grupo": g["grupo"],
            "sem_ressalva": sem_r,
            "com_ressalva": com_r,
            "com_acrescimo": com_a,
            "com_ressalva_e_acrescimo": res_ac,
            "sem_aproveitamento": sem_a,
            "total_revisoes": total,
            "pontuacao_total": pontuacao,
            "pontuacao_maxima": p_max,
            "taxa_aproveitamento_pct": taxa,
        })
    return resultado


def calcular_aproveitamento_individual(
    atividades: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Paridade com `calcularAproveitamentoIndividual` (Calculator.js:755).

    Aproveitamento por pessoa AVALIADA (Responsavel Atividade Principal).
    Filtra apenas atividades `Revis...` concluídas.
    """
    grupos: dict[str, dict[str, Any]] = {}

    for row in atividades:
        assunto = str(row.get("Assunto") or "").strip().lower()
        if "revis" not in assunto[:6]:
            continue
        status = str(row.get("Status") or "").strip().lower()
        if status not in ("concluído", "concluido"):
            continue
        avaliado = str(row.get("Responsavel Atividade Principal") or "").strip()
        if not avaliado:
            continue
        aproveitamento = str(row.get("Aproveitamento") or "").strip() or "Sem Aproveitamento"
        mes_ano = extrair_mes_ano(row.get("Data"))
        if not mes_ano:
            continue

        chave = f"{avaliado}|{mes_ano}"
        g = grupos.get(chave)
        if g is None:
            g = {
                "avaliado": avaliado,
                "mesAno": mes_ano,
                "semRessalva": 0,
                "comRessalva": 0,
                "comAcrescimo": 0,
                "ressalvaAcrescimo": 0,
                "semAproveitamento": 0,
                "total": 0,
                "somaWeighted": 0,
            }
            grupos[chave] = g

        g["total"] += 1
        ap = aproveitamento.lower()
        if "sem ressalva" in ap:
            g["semRessalva"] += 1
            g["somaWeighted"] += 100
        elif "ressalva" in ap and ("acréscimo" in ap or "acrescimo" in ap):
            g["ressalvaAcrescimo"] += 1
            g["somaWeighted"] += 40
        elif "acréscimo" in ap or "acrescimo" in ap:
            g["comAcrescimo"] += 1
            g["somaWeighted"] += 70
        elif "com ressalva" in ap:
            g["comRessalva"] += 1
            g["somaWeighted"] += 90
        elif "sem aproveitamento" in ap:
            g["semAproveitamento"] += 1

    resultado: list[dict[str, Any]] = []
    for g in grupos.values():
        taxa = round(g["somaWeighted"] / g["total"]) if g["total"] > 0 else 0
        resultado.append({
            "avaliado": g["avaliado"],
            "mes_ano": g["mesAno"],
            "sem_ressalva": g["semRessalva"],
            "com_ressalva": g["comRessalva"],
            "com_acrescimo": g["comAcrescimo"],
            "ressalva_acrescimo": g["ressalvaAcrescimo"],
            "sem_aproveitamento": g["semAproveitamento"],
            "total": g["total"],
            "taxa_pct": taxa,
        })
    return resultado


def calcular_desempenho_revisor(
    atividades: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Paridade com `calcularDesempenhoRevisor` (Calculator.js:837)."""
    grupos: dict[str, dict[str, Any]] = {}

    for row in atividades:
        assunto_l = str(row.get("Assunto") or "").strip().lower()
        if "revis" not in assunto_l[:6]:
            continue
        status = str(row.get("Status") or "").strip().lower()
        if status not in ("concluído", "concluido"):
            continue
        revisor = str(row.get("Responsavel") or "").strip()
        if not revisor:
            continue
        aproveitamento = str(row.get("Aproveitamento") or "").strip()
        if not aproveitamento:
            continue
        mes_ano = extrair_mes_ano(row.get("Data"))
        if not mes_ano:
            continue
        assunto_principal = str(row.get("Assunto Atividade Principal") or "").strip()

        chave = f"{revisor}|{mes_ano}"
        g = grupos.get(chave)
        if g is None:
            g = {
                "revisor": revisor,
                "mesAno": mes_ano,
                "total": 0,
                "semRessalva": 0,
                "comCorrecao": 0,
                "assuntos": {},
            }
            grupos[chave] = g

        g["total"] += 1
        ap_l = aproveitamento.lower()
        if "sem ressalva" in ap_l:
            g["semRessalva"] += 1
        else:
            g["comCorrecao"] += 1
            if assunto_principal:
                g["assuntos"][assunto_principal] = g["assuntos"].get(assunto_principal, 0) + 1

    resultado: list[dict[str, Any]] = []
    for g in grupos.values():
        taxa = round((g["comCorrecao"] / g["total"]) * 100) if g["total"] > 0 else 0
        max_assunto, max_qtd = "", 0
        for k, v in g["assuntos"].items():
            if v > max_qtd:
                max_assunto, max_qtd = k, v
        resultado.append({
            "revisor": g["revisor"],
            "mes_ano": g["mesAno"],
            "total_revisoes": g["total"],
            "sem_ressalva": g["semRessalva"],
            "com_correcao": g["comCorrecao"],
            "taxa_correcao_pct": taxa,
            "assunto_mais_corrigido": max_assunto,
            "qtd_assunto_mais_corrigido": max_qtd,
        })
    return resultado


def calcular_aproveitamento_peticao(
    atividades: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Paridade com `calcularAproveitamentoPeticao` (Calculator.js:921)."""
    agrupado: dict[str, dict[str, Any]] = {}

    for row in atividades:
        aproveitamento = str(row.get("Aproveitamento") or "").strip()
        if not aproveitamento:
            continue
        aprov_norm = normalizar_aproveitamento(aproveitamento)
        if not aprov_norm:
            continue
        resp_ap = str(row.get("Responsavel Atividade Principal") or "").strip()
        if not resp_ap:
            continue
        revisor = str(row.get("Responsavel") or "").strip()
        assunto = str(row.get("Assunto") or "").strip()
        if is_assunto_excluido(assunto):
            continue
        mes_ano = extrair_mes_ano(row.get("Data Conclusao")) or "Sem Data"

        chave = f"{resp_ap}|{mes_ano}"
        g = agrupado.get(chave)
        if g is None:
            g = {
                "responsavel": resp_ap,
                "mesAno": mes_ano,
                "semRessalva": 0,
                "comRessalva": 0,
                "comAcrescimo": 0,
                "ressalvaAcrescimo": 0,
                "semAproveitamento": 0,
                "total": 0,
                "somaPercentual": 0,
                "revisores": set(),
                "assuntos": {},
            }
            agrupado[chave] = g

        g["total"] += 1
        bucket = {
            "Revisão sem ressalva": "semRessalva",
            "Revisão com ressalva": "comRessalva",
            "Revisão com acréscimo": "comAcrescimo",
            "Revisão com ressalva e acréscimo": "ressalvaAcrescimo",
            "Revisão sem aproveitamento": "semAproveitamento",
        }
        g[bucket[aprov_norm]] += 1
        g["somaPercentual"] += PESOS_APROVEITAMENTO[aprov_norm]
        if revisor:
            g["revisores"].add(revisor)
        if assunto:
            g["assuntos"][assunto] = g["assuntos"].get(assunto, 0) + 1

    resultado: list[dict[str, Any]] = []
    for g in agrupado.values():
        media = round(g["somaPercentual"] / g["total"], 1) if g["total"] > 0 else 0.0
        max_assunto, max_qtd = "", 0
        for k, v in g["assuntos"].items():
            if v > max_qtd:
                max_assunto, max_qtd = k, v
        resultado.append({
            "responsavel_atividade_principal": g["responsavel"],
            "mes_ano": g["mesAno"],
            "revisao_sem_ressalva": g["semRessalva"],
            "revisao_com_ressalva": g["comRessalva"],
            "revisao_com_acrescimo": g["comAcrescimo"],
            "revisao_ressalva_acrescimo": g["ressalvaAcrescimo"],
            "revisao_sem_aproveitamento": g["semAproveitamento"],
            "total_revisoes": g["total"],
            "media_aproveitamento_pct": media,
            "revisores": ", ".join(sorted(g["revisores"])),
            "assunto_mais_frequente": max_assunto,
        })
    return resultado


# ---- Acesso HTTP ----

async def listar(
    db: AsyncSession,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[AproveitamentoItem]:
    stmt = select(AproveitamentoCalculada)
    if grupo:
        stmt = stmt.where(AproveitamentoCalculada.grupo == grupo)
    if mes_ano:
        stmt = stmt.where(AproveitamentoCalculada.mes_ano == mes_ano)
    try:
        result = await db.execute(stmt)
    except ProgrammingError:
        await db.rollback()
        return []
    # Agregar (responsavel, grupo, mes_ano) somando todas as linhas por assunto
    bucket: dict[tuple[str, str, str], dict[str, Any]] = {}
    for r in result.scalars().all():
        key = (r.responsavel, r.grupo or "", r.mes_ano)
        b = bucket.get(key)
        if b is None:
            b = {
                "responsavel": r.responsavel,
                "grupo": r.grupo or "",
                "mes_ano": r.mes_ano,
                "sem_ressalva": 0, "com_ressalva": 0, "com_acrescimo": 0,
                "com_ressalva_e_acrescimo": 0, "sem_aproveitamento": 0,
                "total_revisadas": 0, "pontuacao": 0, "p_max": 0,
            }
            bucket[key] = b
        b["sem_ressalva"] += r.sem_ressalva
        b["com_ressalva"] += r.com_ressalva
        b["com_acrescimo"] += r.com_acrescimo
        b["com_ressalva_e_acrescimo"] += r.com_ressalva_e_acrescimo
        b["sem_aproveitamento"] += r.sem_aproveitamento
        b["total_revisadas"] += r.total_revisoes
        b["pontuacao"] += r.pontuacao_total
        b["p_max"] += r.pontuacao_maxima

    items: list[AproveitamentoItem] = []
    for b in bucket.values():
        media = (b["pontuacao"] / b["p_max"]) if b["p_max"] > 0 else 0.0
        items.append(
            AproveitamentoItem(
                responsavel=b["responsavel"],
                grupo=b["grupo"],
                mes_ano=b["mes_ano"],
                aproveitamento_medio=media,
                total_revisadas=b["total_revisadas"],
                sem_ressalva=b["sem_ressalva"],
                com_ressalva=b["com_ressalva"],
                com_acrescimo=b["com_acrescimo"],
                com_ressalva_e_acrescimo=b["com_ressalva_e_acrescimo"],
                sem_aproveitamento=b["sem_aproveitamento"],
            )
        )
    return items


async def listar_individual(
    db: AsyncSession,
    responsavel: str | None = None,
    mes_ano: str | None = None,
) -> list[AproveitamentoIndividualItem]:
    stmt = select(AproveitamentoIndividualCalculada)
    if responsavel:
        stmt = stmt.where(AproveitamentoIndividualCalculada.avaliado == responsavel)
    if mes_ano:
        stmt = stmt.where(AproveitamentoIndividualCalculada.mes_ano == mes_ano)
    try:
        result = await db.execute(stmt)
    except ProgrammingError:
        await db.rollback()
        return []
    out: list[AproveitamentoIndividualItem] = []
    for r in result.scalars().all():
        out.append(
            AproveitamentoIndividualItem(
                responsavel=r.avaliado,
                grupo="",  # não persistido nesta tabela
                assunto="",
                mes_ano=r.mes_ano,
                total_revisadas=r.total,
                aproveitamento_medio=float(r.taxa_pct),
            )
        )
    return out


async def listar_desempenho_revisor(db: AsyncSession) -> list[dict[str, Any]]:
    from app.models.produtividade_calc import DesempenhoRevisorCalculada

    try:
        result = await db.execute(select(DesempenhoRevisorCalculada))
    except ProgrammingError:
        await db.rollback()
        return []
    return [
        {
            "revisor": r.revisor,
            "mes_ano": r.mes_ano,
            "total_revisoes": r.total_revisoes,
            "sem_ressalva": r.sem_ressalva,
            "com_correcao": r.com_correcao,
            "taxa_correcao_pct": r.taxa_correcao_pct,
            "assunto_mais_corrigido": r.assunto_mais_corrigido,
            "qtd_assunto_mais_corrigido": r.qtd_assunto_mais_corrigido,
        }
        for r in result.scalars().all()
    ]
