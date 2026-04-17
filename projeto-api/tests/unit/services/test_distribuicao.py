"""Testes de distribuição por horário e por assunto."""

from app.services.distribuicao import (
    calcular_distribuicao_assunto,
    calcular_distribuicao_horario,
)
from tests.unit.fixtures.atividades_sample import ATIVIDADES


def test_horario_kalebe_e_pedro():
    rows = calcular_distribuicao_horario(ATIVIDADES)
    # Cada responsavel aparece em pelo menos 1 hora
    responsaveis = {r["responsavel"] for r in rows}
    assert "Kalebe Prado" in responsaveis
    assert "Pedro Moscon" in responsaveis

    # Pedro tem 3 atividades concluídas consideradas:
    #   Habilitação (status conclu, mas status filtra só "conclu", passa; porém
    #   distribuicao_horario NÃO filtra blacklist de assunto)
    #   Réplica 08/03 14h, Recurso Inominado 09/03 11h; + Habilitação 07/03 10h; e a de 2019
    # total = 4 entradas, uma por hora
    pedro = [r for r in rows if r["responsavel"] == "Pedro Moscon"]
    total_pedro = sum(r["contagem"] for r in pedro)
    assert total_pedro == 4


def test_assunto_filtra_blacklist_global():
    rows = calcular_distribuicao_assunto(ATIVIDADES)
    pedro_habilitacao = [
        r for r in rows
        if r["responsavel"] == "Pedro Moscon" and r["assunto"].lower() == "habilitação"
    ]
    # Distribuicao_Assunto filtra a blacklist global
    assert len(pedro_habilitacao) == 0


def test_assunto_filtra_autorrevisao():
    rows = calcular_distribuicao_assunto(ATIVIDADES)
    # Kalebe autorrevisão foi filtrada
    autorrevisoes = [
        r for r in rows
        if r["responsavel"] == "Kalebe Prado" and r["assunto"].lower().startswith("revis")
    ]
    assert len(autorrevisoes) == 0
