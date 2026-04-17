"""Endpoint de Produtividade."""

from fastapi import APIRouter

from app.deps import CurrentUser, SessionDep
from app.schemas.produtividade import ProdutividadeItem
from app.services import produtividade as produtividade_service

router = APIRouter(prefix="/api/produtividade", tags=["produtividade"])


@router.get("", response_model=list[ProdutividadeItem])
async def listar_produtividade(
    _user: CurrentUser,
    db: SessionDep,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[ProdutividadeItem]:
    return await produtividade_service.listar(db, grupo=grupo, mes_ano=mes_ano)
