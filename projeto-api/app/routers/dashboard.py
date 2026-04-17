"""Endpoint agregado — mesmo payload do /api/dados legado (substitui Sheets)."""

from typing import Any

from fastapi import APIRouter

from app.deps import CurrentUser, SessionDep
from app.services import (
    aproveitamento as aproveitamento_service,
)
from app.services import (
    distribuicao as distribuicao_service,
)
from app.services import (
    produtividade as produtividade_service,
)
from app.services import (
    ranking as ranking_service,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def dados_dashboard(_user: CurrentUser, db: SessionDep) -> dict[str, Any]:
    """Retorna o mesmo shape do endpoint /api/dados do backend legado."""
    produtividade = await produtividade_service.listar(db)
    aprov_individual = await aproveitamento_service.listar_individual(db)
    aprov_calculado = await aproveitamento_service.listar(db)
    desempenho_revisor = await aproveitamento_service.listar_desempenho_revisor(db)
    dist_horario = await distribuicao_service.listar_horario(db)
    dist_assunto = await distribuicao_service.listar_assunto(db)
    ranking = await ranking_service.listar(db)

    from datetime import datetime

    return {
        "produtividade": [p.model_dump() for p in produtividade],
        "aprovIndividual": [a.model_dump() for a in aprov_individual],
        "aprovCalculado": [a.model_dump() for a in aprov_calculado],
        "desempenhoRevisor": desempenho_revisor,
        "distribuicaoHorario": dist_horario,
        "distribuicaoAssunto": dist_assunto,
        "rankingGamificado": [r.model_dump() for r in ranking],
        "updatedAt": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
