"""Contratos do ranking gamificado."""

from pydantic import BaseModel


class RankingItem(BaseModel):
    posicao: int
    responsavel: str
    grupo: str
    pontos_totais: float
    total_atividades: int
    aproveitamento_medio: float
    mes_ano: str
