"""Pontuações de ranking + blacklists/whitelists de assuntos por grupo."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PontuacaoRanking(Base):
    """Pontos por (grupo, assunto normalizado) — substitui PONTUACAO_RANKING_*."""

    __tablename__ = "pontuacao_ranking"

    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupo.id", ondelete="CASCADE"), primary_key=True
    )
    assunto_norm: Mapped[str] = mapped_column(String(240), primary_key=True)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)


class AssuntoExcluido(Base):
    """Blacklist — se grupo_id for NULL, exclusão é global."""

    __tablename__ = "assunto_excluido"

    grupo_id: Mapped[int | None] = mapped_column(
        ForeignKey("grupo.id", ondelete="CASCADE"), primary_key=True, nullable=True
    )
    assunto_norm: Mapped[str] = mapped_column(String(240), primary_key=True)
    motivo: Mapped[str | None] = mapped_column(String(240), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class AssuntoPermitido(Base):
    """Whitelist — substitui Config_Assuntos."""

    __tablename__ = "assunto_permitido"

    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupo.id", ondelete="CASCADE"), primary_key=True
    )
    assunto_norm: Mapped[str] = mapped_column(String(240), primary_key=True)
