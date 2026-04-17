"""Endpoint de Ranking Gamificado."""

from fastapi import APIRouter

from app.deps import CurrentUser, SessionDep
from app.schemas.ranking import RankingItem
from app.services import ranking as ranking_service

router = APIRouter(prefix="/api/ranking", tags=["ranking"])


@router.get("", response_model=list[RankingItem])
async def listar_ranking(
    _user: CurrentUser,
    db: SessionDep,
    grupo: str | None = None,
    mes_ano: str | None = None,
) -> list[RankingItem]:
    return await ranking_service.listar(db, grupo=grupo, mes_ano=mes_ano)
