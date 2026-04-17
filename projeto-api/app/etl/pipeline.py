"""Orquestrador ETL: coleta DataJuri -> upsert atividades -> recalcula métricas -> persiste."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import Base, get_session_factory
from app.etl.collector import coletar_e_upsert
from app.models import (
    AproveitamentoCalculada,
    AproveitamentoIndividualCalculada,
    AproveitamentoPeticaoCalculada,
    AssuntoExcluido,
    Atividade,
    DesempenhoRevisorCalculada,
    DistribuicaoAssuntoCalculada,
    DistribuicaoHorarioCalculada,
    EtlRun,
    Grupo,
    Pessoa,
    PontuacaoRanking,
    ProdutividadeCalculada,
    RankingCalculada,
)
from app.services.aproveitamento import (
    calcular_aproveitamento,
    calcular_aproveitamento_individual,
    calcular_aproveitamento_peticao,
    calcular_desempenho_revisor,
)
from app.services.dias_uteis import FERIADOS_HARDCODED, load_feriados
from app.services.distribuicao import (
    calcular_distribuicao_assunto,
    calcular_distribuicao_horario,
)
from app.services.normalize import buscar_grupo, normalize
from app.services.produtividade import calcular_produtividade
from app.services.ranking import calcular_ranking

logger = logging.getLogger(__name__)


def _atividade_para_row(a: Atividade, pessoa_by_id: dict[int, Pessoa]) -> dict[str, Any]:
    """Converte Atividade ORM -> dict no shape esperado pelos services (chaves do Sheets)."""
    responsavel = ""
    if a.responsavel_id and a.responsavel_id in pessoa_by_id:
        responsavel = pessoa_by_id[a.responsavel_id].nome
    elif a.raw_json:
        responsavel = str(a.raw_json.get("proprietario", {}).get("nome") or "")
    concluido_por = ""
    if a.concluido_por_id and a.concluido_por_id in pessoa_by_id:
        concluido_por = pessoa_by_id[a.concluido_por_id].nome
    elif a.raw_json:
        concluido_por = str(a.raw_json.get("concluidoPor", {}).get("nome") or "")
    resp_ativ_principal = ""
    if a.responsavel_ativ_principal_id and a.responsavel_ativ_principal_id in pessoa_by_id:
        resp_ativ_principal = pessoa_by_id[a.responsavel_ativ_principal_id].nome
    elif a.raw_json:
        resp_ativ_principal = str(
            a.raw_json.get("atividade", {}).get("proprietario", {}).get("nome") or ""
        )

    return {
        "Pasta": a.pasta,
        "Assunto": a.assunto,
        "Assunto Atividade Principal": a.assunto_ativ_principal or a.assunto,
        "Status": a.status,
        "Data": a.data,
        "Data Conclusao": a.data_conclusao,
        "Data Prazo Fatal": a.data_prazo_fatal,
        "Responsavel": responsavel,
        "ConcluidoPor": concluido_por,
        "Responsavel Atividade Principal": resp_ativ_principal,
        "Aproveitamento": a.aproveitamento,
        "Natureza": a.tipo_processo or "",
    }


async def _load_atividades_raw(db: AsyncSession) -> list[dict[str, Any]]:
    result = await db.execute(select(Pessoa))
    pessoas = {p.id: p for p in result.scalars().all()}
    result = await db.execute(select(Atividade))
    ativs = list(result.scalars().all())
    return [_atividade_para_row(a, pessoas) for a in ativs]


async def _load_assuntos_excluidos_grupo(db: AsyncSession) -> dict[str, set[str]]:
    """Carrega blacklist por grupo da tabela `assunto_excluido` (grupo_id != NULL)."""
    stmt = (
        select(Grupo.nome, AssuntoExcluido.assunto_norm)
        .join(Grupo, AssuntoExcluido.grupo_id == Grupo.id)
        .where(AssuntoExcluido.grupo_id.isnot(None))
    )
    result = await db.execute(stmt)
    mapa: dict[str, set[str]] = {}
    for grupo_nome, assunto_norm in result.all():
        mapa.setdefault(grupo_nome, set()).add(assunto_norm)
    return mapa


async def _load_pontuacao_por_grupo(db: AsyncSession) -> dict[str, dict[str, int]]:
    stmt = select(Grupo.nome, PontuacaoRanking.assunto_norm, PontuacaoRanking.pontos).join(
        Grupo, PontuacaoRanking.grupo_id == Grupo.id
    )
    result = await db.execute(stmt)
    mapa: dict[str, dict[str, int]] = {}
    for grupo_nome, assunto_norm, pontos in result.all():
        mapa.setdefault(grupo_nome, {})[assunto_norm] = pontos
    return mapa


async def _upsert(db: AsyncSession, model: type[Base], rows: list[dict[str, Any]], idx: list[str]) -> None:
    if not rows:
        return
    stmt = pg_insert(model).values(rows)
    update_cols = {
        c.name: stmt.excluded[c.name]
        for c in model.__table__.columns
        if c.name != "id" and c.name not in idx and c.name != "calculado_em"
    }
    stmt = stmt.on_conflict_do_update(index_elements=idx, set_=update_cols)
    await db.execute(stmt)


async def recalcular_metricas(db: AsyncSession) -> dict[str, int]:
    """Roda todos os cálculos e persiste. Retorna contagem por tabela."""
    atividades = await _load_atividades_raw(db)
    logger.info("Carregadas %d atividades para cálculo", len(atividades))

    # Feriados: prefere tabela `feriado`; fallback hardcoded.
    feriados_db = await load_feriados(db)
    feriados = feriados_db or FERIADOS_HARDCODED

    blacklist_g = await _load_assuntos_excluidos_grupo(db)
    pont_por_grupo = await _load_pontuacao_por_grupo(db)

    # 1. Aproveitamento individual primeiro (o ranking depende dele)
    aprov_indiv = calcular_aproveitamento_individual(atividades)
    taxa_aprov_map = {
        f"{normalize(r['avaliado'])}|{r['mes_ano']}": float(r["taxa_pct"]) for r in aprov_indiv
    }

    # 2. Produtividade
    prod = calcular_produtividade(
        atividades,
        feriados=feriados,
        assuntos_excluidos_grupo=blacklist_g,
    )

    # 3. Aproveitamento agregado
    aprov = calcular_aproveitamento(atividades)

    # 4. Aproveitamento petição
    aprov_pet = calcular_aproveitamento_peticao(atividades)

    # 5. Desempenho do revisor
    desemp = calcular_desempenho_revisor(atividades)

    # 6. Ranking (depende do aprov individual)
    ranking = calcular_ranking(
        atividades,
        pontuacao_por_grupo=pont_por_grupo,
        taxa_aprov_map=taxa_aprov_map,
        assuntos_excluidos_grupo=blacklist_g,
    )

    # 7. Distribuição
    dist_hora = calcular_distribuicao_horario(atividades)
    dist_assunto = calcular_distribuicao_assunto(
        atividades, assuntos_excluidos_grupo=blacklist_g
    )

    # Truncar (garantia de replace total) e inserir.
    for tabela in (
        ProdutividadeCalculada,
        AproveitamentoCalculada,
        AproveitamentoIndividualCalculada,
        AproveitamentoPeticaoCalculada,
        DesempenhoRevisorCalculada,
        RankingCalculada,
        DistribuicaoHorarioCalculada,
        DistribuicaoAssuntoCalculada,
    ):
        await db.execute(tabela.__table__.delete())

    await _upsert(db, ProdutividadeCalculada, prod, ["responsavel", "mes_ano", "natureza", "quinzena", "assunto"])
    # Para aproveitamento, alimenta grupo (não vem do service)
    for r in aprov:
        r["grupo"] = buscar_grupo(r["responsavel"])
    await _upsert(db, AproveitamentoCalculada, aprov, ["responsavel", "mes_ano", "natureza", "assunto"])
    await _upsert(db, AproveitamentoIndividualCalculada, aprov_indiv, ["avaliado", "mes_ano"])
    await _upsert(db, AproveitamentoPeticaoCalculada, aprov_pet, ["responsavel_atividade_principal", "mes_ano"])
    await _upsert(db, DesempenhoRevisorCalculada, desemp, ["revisor", "mes_ano"])

    # Ranking: remover campos não persistidos
    ranking_db = [
        {
            "responsavel": r["responsavel"],
            "mes_ano": r["mes_ano"],
            "grupo": r["grupo"],
            "posicao": r["posicao"],
            "pontos_brutos": r["pontos_brutos"],
            "pontos_validos": r["pontos_validos"],
            "total_atividades": r["total_atividades"],
            "taxa_aprov": r["taxa_aprov"],
        }
        for r in ranking
    ]
    await _upsert(db, RankingCalculada, ranking_db, ["responsavel", "mes_ano"])

    await _upsert(
        db, DistribuicaoHorarioCalculada, dist_hora, ["responsavel", "mes_ano", "hora"]
    )
    await _upsert(
        db, DistribuicaoAssuntoCalculada, dist_assunto,
        ["responsavel", "mes_ano", "assunto"],
    )

    await db.commit()
    return {
        "atividades": len(atividades),
        "produtividade": len(prod),
        "aproveitamento": len(aprov),
        "aproveitamento_individual": len(aprov_indiv),
        "aproveitamento_peticao": len(aprov_pet),
        "desempenho_revisor": len(desemp),
        "ranking": len(ranking),
        "distribuicao_horario": len(dist_hora),
        "distribuicao_assunto": len(dist_assunto),
    }


async def run_pipeline(incremental: bool = False, dry_run: bool = False) -> None:
    settings = get_settings()
    inicio = datetime.now(timezone.utc)
    factory = get_session_factory()

    async with factory() as db:
        run = EtlRun(inicio=inicio, status="running", detalhes={"incremental": incremental})
        db.add(run)
        await db.commit()
        await db.refresh(run)

        try:
            coletados = await coletar_e_upsert(
                db,
                data_inicio=settings.datajuri_data_inicio,
                incremental=incremental,
                dry_run=dry_run,
            )
            contagens: dict[str, int] = {"coletados": coletados}
            if not dry_run:
                contagens.update(await recalcular_metricas(db))

            run.fim = datetime.now(timezone.utc)
            run.status = "ok"
            run.detalhes = {
                "incremental": incremental,
                "dry_run": dry_run,
                **contagens,
            }
            await db.commit()
            logger.info("ETL OK: %s", contagens)

        except Exception as e:  # noqa: BLE001
            run.fim = datetime.now(timezone.utc)
            run.status = "fail"
            run.detalhes = {"incremental": incremental, "erro": str(e)}
            await db.commit()
            logger.exception("ETL falhou")
            raise
