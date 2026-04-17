"""Fixtures compartilhadas (pytest)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("ENV", "dev")
os.environ.setdefault("SESSION_SECRET", "x" * 40)


@pytest.fixture
def sample_atividade() -> dict:
    """Uma atividade mock no shape do payload DataJuri."""
    return {
        "id": 123456,
        "processo": {"pasta": "12345", "tipoProcesso": "Judicial"},
        "assunto": "Petição Inicial – PREV",
        "status": "Concluído",
        "data": "01/03/2026 10:30",
        "dataConclusao": "02/03/2026 14:45",
        "proprietarioId": 99,
        "proprietario": {"nome": "Kalebe Prado"},
        "concluidoPor": {"id": 99, "nome": "Kalebe Prado"},
        "atividade": {"assunto": "Petição Inicial – PREV", "proprietario": {"nome": "Kalebe"}},
        "aproveitamento": "Revisão sem ressalva",
    }
