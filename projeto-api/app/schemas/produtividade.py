"""Contratos de produtividade."""

from pydantic import BaseModel


class ProdutividadeItem(BaseModel):
    responsavel: str
    grupo: str
    mes_ano: str
    quinzena: str | None = None
    total_concluidas: int
    total_atribuidas: int
    taxa_conclusao: float
    prazos_no_prazo: int
    prazos_em_atraso: int
    atividades_por_dia_util: float
