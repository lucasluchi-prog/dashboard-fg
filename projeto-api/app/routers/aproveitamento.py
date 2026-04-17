"""Endpoints de Aproveitamento."""

from fastapi import APIRouter

from app.deps import CurrentUser, SessionDep
from app.schemas.aproveitamento import AproveitamentoIndividualItem, AproveitamentoItem
from app.services import aproveitamento as aproveitamento_service

router = APIRouter(prefix="/api/aproveitamento", tags=["aproveitamento"])


@router.get("", response_model=list[AproveitamentoItem])
async def listar(
    _user: CurrentUser,
    db: SessionDep,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[AproveitamentoItem]:
    return await aproveitamento_service.listar(db, grupo=grupo, mes_ano=mes_ano)


@router.get("/individual", response_model=list[AproveitamentoIndividualItem])
async def listar_individual(
    _user: CurrentUser,
    db: SessionDep,
    responsavel: str | None = None,
    mes_ano: str | None = None,
) -> list[AproveitamentoIndividualItem]:
    return await aproveitamento_service.listar_individual(
        db, responsavel=responsavel, mes_ano=mes_ano
    )
