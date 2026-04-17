"""Tabela raw das atividades vindas do DataJuri."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Atividade(Base):
    __tablename__ = "atividade"
    __table_args__ = (
        Index("idx_ativ_status_data", "status", "data_conclusao"),
        Index("idx_ativ_responsavel", "concluido_por_id", "data_conclusao"),
        Index("idx_ativ_assunto", "assunto"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # = datajuri id
    pasta: Mapped[str | None] = mapped_column(String(60), nullable=True)
    assunto: Mapped[str | None] = mapped_column(String(240), nullable=True)
    status: Mapped[str | None] = mapped_column(String(60), nullable=True)
    data: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_prazo_fatal: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_conclusao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    responsavel_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("pessoa.id", ondelete="SET NULL"), nullable=True
    )
    concluido_por_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("pessoa.id", ondelete="SET NULL"), nullable=True
    )
    responsavel_ativ_principal_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("pessoa.id", ondelete="SET NULL"), nullable=True
    )

    assunto_ativ_principal: Mapped[str | None] = mapped_column(String(240), nullable=True)
    aproveitamento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tipo_processo: Mapped[str | None] = mapped_column(String(120), nullable=True)

    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    coletado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )
