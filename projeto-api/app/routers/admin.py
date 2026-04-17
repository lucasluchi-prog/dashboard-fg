"""Endpoints administrativos — refresh manual, listagem de grupos."""

from typing import Any

from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select

from app.deps import CurrentUser, SessionDep
from app.models import Grupo, Pessoa

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/grupos")
async def listar_grupos(_user: CurrentUser, db: SessionDep) -> list[dict[str, Any]]:
    result = await db.execute(select(Grupo).order_by(Grupo.nome))
    return [{"id": g.id, "nome": g.nome} for g in result.scalars().all()]


@router.get("/pessoas")
async def listar_pessoas(
    _user: CurrentUser,
    db: SessionDep,
    grupo: str | None = None,
) -> list[dict[str, Any]]:
    stmt = select(Pessoa, Grupo).join(Grupo, Pessoa.grupo_id == Grupo.id, isouter=True)
    if grupo is not None:
        stmt = stmt.where(Grupo.nome == grupo)
    result = await db.execute(stmt.order_by(Pessoa.nome))
    return [
        {
            "id": pessoa.id,
            "nome": pessoa.nome,
            "email": pessoa.email,
            "ativo": pessoa.ativo,
            "grupo": grupo_obj.nome if grupo_obj else None,
        }
        for pessoa, grupo_obj in result.all()
    ]


@router.post("/refresh")
async def refresh_dashboard(
    _user: CurrentUser,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Dispara um ETL incremental em background (usar Cloud Run Job em prod)."""
    from app.etl.pipeline import run_pipeline

    background_tasks.add_task(run_pipeline, incremental=True)
    return {"status": "scheduled"}
