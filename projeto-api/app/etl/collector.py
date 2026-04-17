"""Collector — puxa páginas do DataJuri e faz upsert em `atividade`."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Atividade
from app.services.datajuri_client import DataJuriClient, nested_value

logger = logging.getLogger(__name__)

CAMPOS_ATIVIDADE = ",".join(
    [
        "id",
        "processo.pasta",
        "assunto",
        "status",
        "data",
        "dataPrazoFatal",
        "prazoFatal",
        "proprietario.nome",
        "proprietarioId",
        "aproveitamento",
        "consideracoes",
        "observacao",
        "dataConclusao",
        "atividade.proprietario.nome",
        "atividade.assunto",
        "concluidoPor.nome",
        "concluidoPor.id",
        "processo.tipoProcesso",
    ]
)


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    # DataJuri formatos: "dd/MM/yyyy HH:mm" ou ISO
    if isinstance(value, str):
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def to_row(registro: dict[str, Any]) -> dict[str, Any]:
    """Converte registro DataJuri -> dict pronto pra upsert em `atividade`."""
    return {
        "id": int(registro["id"]),
        "pasta": str(nested_value(registro, "processo.pasta") or "") or None,
        "assunto": registro.get("assunto"),
        "status": registro.get("status"),
        "data": _parse_datetime(registro.get("data")),
        "data_prazo_fatal": _parse_datetime(registro.get("dataPrazoFatal")),
        "data_conclusao": _parse_datetime(registro.get("dataConclusao")),
        "responsavel_id": registro.get("proprietarioId"),
        "concluido_por_id": nested_value(registro, "concluidoPor.id") or None,
        "responsavel_ativ_principal_id": None,
        "assunto_ativ_principal": str(nested_value(registro, "atividade.assunto") or "") or None,
        "aproveitamento": registro.get("aproveitamento"),
        "tipo_processo": str(nested_value(registro, "processo.tipoProcesso") or "") or None,
        "raw_json": registro,
        "coletado_em": datetime.now(timezone.utc),
    }


async def coletar_e_upsert(
    db: AsyncSession,
    *,
    data_inicio: str,
    incremental: bool = False,
    dry_run: bool = False,
) -> int:
    """Coleta tudo desde `data_inicio` (ou últimos N dias se `incremental`) e upserta."""
    criterio = f"data >= '{data_inicio}'"
    if incremental:
        criterio = "data >= DATE_SUB(NOW(), INTERVAL 2 DAY)"

    total = 0
    async with DataJuriClient() as client:
        registros = await client.fetch_all("Atividade", CAMPOS_ATIVIDADE, criterio)

    logger.info("Coletados %d registros do DataJuri", len(registros))
    if dry_run:
        return len(registros)

    batch_size = 500
    rows = [to_row(r) for r in registros if r.get("id") is not None]
    for i in range(0, len(rows), batch_size):
        chunk = rows[i : i + batch_size]
        stmt = pg_insert(Atividade).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                col.name: stmt.excluded[col.name]
                for col in Atividade.__table__.columns
                if col.name != "id"
            },
        )
        await db.execute(stmt)
        total += len(chunk)
        logger.info("Upsert chunk %d-%d / %d", i, i + len(chunk), len(rows))

    await db.commit()
    return total
