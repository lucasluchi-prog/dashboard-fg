"""Tabelas pré-calculadas pelo ETL — substitui as abas `*_Calculado` do Sheets."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ProdutividadeCalculada(Base):
    """Uma linha por (responsavel, mes_ano, natureza, quinzena, assunto)."""

    __tablename__ = "produtividade_calculada"
    __table_args__ = (
        UniqueConstraint(
            "responsavel", "mes_ano", "natureza", "quinzena", "assunto",
            name="ux_produtividade",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    natureza: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    assunto: Mapped[str] = mapped_column(String(240), nullable=False, default="")
    grupo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quinzena: Mapped[str] = mapped_column(String(2), nullable=False)
    total_concluidas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    concluidas_dias_uteis: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dias_uteis_periodo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    media_diaria: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    no_prazo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fora_do_prazo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxa_prazo_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class AproveitamentoCalculada(Base):
    __tablename__ = "aproveitamento_calculada"
    __table_args__ = (
        UniqueConstraint(
            "responsavel", "mes_ano", "natureza", "assunto",
            name="ux_aproveitamento",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    natureza: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    assunto: Mapped[str] = mapped_column(String(240), nullable=False, default="")
    grupo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sem_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_ressalva_e_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sem_aproveitamento: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_revisoes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pontuacao_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pontuacao_maxima: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxa_aproveitamento_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class AproveitamentoIndividualCalculada(Base):
    __tablename__ = "aproveitamento_individual_calculada"
    __table_args__ = (
        UniqueConstraint("avaliado", "mes_ano", name="ux_aprov_individual"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    avaliado: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    sem_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ressalva_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sem_aproveitamento: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxa_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class AproveitamentoPeticaoCalculada(Base):
    __tablename__ = "aproveitamento_peticao_calculada"
    __table_args__ = (
        UniqueConstraint(
            "responsavel_atividade_principal", "mes_ano", name="ux_aprov_peticao",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel_atividade_principal: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(16), nullable=False)
    revisao_sem_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revisao_com_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revisao_com_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revisao_ressalva_acrescimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revisao_sem_aproveitamento: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_revisoes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    media_aproveitamento_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    revisores: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assunto_mais_frequente: Mapped[str | None] = mapped_column(String(240), nullable=True)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class DesempenhoRevisorCalculada(Base):
    __tablename__ = "desempenho_revisor_calculada"
    __table_args__ = (UniqueConstraint("revisor", "mes_ano", name="ux_desempenho_revisor"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    revisor: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    total_revisoes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sem_ressalva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    com_correcao: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxa_correcao_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assunto_mais_corrigido: Mapped[str | None] = mapped_column(String(240), nullable=True)
    qtd_assunto_mais_corrigido: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class RankingCalculada(Base):
    __tablename__ = "ranking_calculada"
    __table_args__ = (UniqueConstraint("responsavel", "mes_ano", name="ux_ranking"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    grupo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    posicao: Mapped[int] = mapped_column(Integer, nullable=False)
    pontos_brutos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pontos_validos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_atividades: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taxa_aprov: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class DistribuicaoHorarioCalculada(Base):
    __tablename__ = "distribuicao_horario_calculada"
    __table_args__ = (
        UniqueConstraint("responsavel", "mes_ano", "hora", name="ux_dist_horario"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    hora: Mapped[int] = mapped_column(Integer, nullable=False)
    contagem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class DistribuicaoAssuntoCalculada(Base):
    __tablename__ = "distribuicao_assunto_calculada"
    __table_args__ = (
        UniqueConstraint(
            "responsavel", "mes_ano", "assunto", name="ux_dist_assunto",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    responsavel: Mapped[str] = mapped_column(String(180), nullable=False)
    mes_ano: Mapped[str] = mapped_column(String(7), nullable=False)
    assunto: Mapped[str] = mapped_column(String(240), nullable=False)
    contagem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
