"""Grupo (time) e Pessoa (membro)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Grupo(Base):
    __tablename__ = "grupo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    pessoas: Mapped[list[Pessoa]] = relationship(back_populates="grupo")


class Pessoa(Base):
    __tablename__ = "pessoa"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # = datajuri proprietarioId
    nome: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    grupo_id: Mapped[int | None] = mapped_column(
        ForeignKey("grupo.id", ondelete="SET NULL"), nullable=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    grupo: Mapped[Grupo | None] = relationship(back_populates="pessoas")
