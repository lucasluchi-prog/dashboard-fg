"""Feriados nacionais considerados nos cálculos de dias úteis."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Feriado(Base):
    __tablename__ = "feriado"

    data: Mapped[date] = mapped_column(Date, primary_key=True)
    descricao: Mapped[str | None] = mapped_column(String(120), nullable=True)
