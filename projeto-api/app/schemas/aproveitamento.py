"""Contratos de aproveitamento (ponderação de revisão)."""

from pydantic import BaseModel


class AproveitamentoItem(BaseModel):
    responsavel: str
    grupo: str
    mes_ano: str
    aproveitamento_medio: float
    total_revisadas: int
    sem_ressalva: int
    com_ressalva: int
    com_acrescimo: int
    com_ressalva_e_acrescimo: int
    sem_aproveitamento: int


class AproveitamentoIndividualItem(BaseModel):
    responsavel: str
    grupo: str
    assunto: str
    mes_ano: str
    total_revisadas: int
    aproveitamento_medio: float
