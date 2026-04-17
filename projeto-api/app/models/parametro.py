"""Parâmetros chave->JSON (pesos de aproveitamento, fatores, etc) + log ETL."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Parametro(Base):
    __tablename__ = "parametro"

    chave: Mapped[str] = mapped_column(String(120), primary_key=True)
    valor: Mapped[Any] = mapped_column(JSONB, nullable=False)


class EtlRun(Base):
    """Log de execuções ETL — cada run gera uma linha."""

    __tablename__ = "etl_run"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    detalhes: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
