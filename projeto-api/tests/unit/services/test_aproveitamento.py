"""Testes de aproveitamento (individual + agregado + desempenho revisor + petição)."""

from app.services.aproveitamento import (
    calcular_aproveitamento,
    calcular_aproveitamento_individual,
    calcular_aproveitamento_peticao,
    calcular_desempenho_revisor,
)
from tests.unit.fixtures.atividades_sample import ATIVIDADES


def test_aproveitamento_individual_kalebe():
    rows = calcular_aproveitamento_individual(ATIVIDADES)
    # Luiza revisou Kalebe sem ressalva e Kalebe se auto-revisou com acréscimo.
    # calcularAproveitamentoIndividual agrupa por `avaliado` (Responsavel Atividade Principal).
    # Kalebe teve 1 rev sem ressalva (Luiza) + 1 rev com acréscimo (autorrevisão) = 2 total
    kalebe = next((r for r in rows if r["avaliado"] == "Kalebe Prado"), None)
    assert kalebe is not None
    assert kalebe["total"] == 2
    assert kalebe["sem_ressalva"] == 1
    assert kalebe["com_acrescimo"] == 1
    # taxa = round((100 + 70) / 2) = 85
    assert kalebe["taxa_pct"] == 85


def test_aproveitamento_agregado_luiza_revisora():
    rows = calcular_aproveitamento(ATIVIDADES)
    # calcularAproveitamento agrupa por (responsavel = revisor, mes_ano, natureza, assunto).
    luiza = [r for r in rows if r["responsavel"] == "Luiza Machado"]
    assert len(luiza) == 1
    l = luiza[0]
    assert l["total_revisoes"] == 1
    assert l["sem_ressalva"] == 1
    assert l["pontuacao_total"] == 100
    assert l["taxa_aproveitamento_pct"] == 100.0


def test_desempenho_revisor_luiza():
    rows = calcular_desempenho_revisor(ATIVIDADES)
    luiza = next(r for r in rows if r["revisor"] == "Luiza Machado")
    assert luiza["total_revisoes"] == 1
    assert luiza["sem_ressalva"] == 1
    assert luiza["com_correcao"] == 0
    assert luiza["taxa_correcao_pct"] == 0


def test_aproveitamento_peticao_kalebe():
    rows = calcular_aproveitamento_peticao(ATIVIDADES)
    # Kalebe é o Responsavel Atividade Principal nos dois registros de revisão
    # - Luiza revisou sem ressalva (100)
    # - Autorrevisão com acréscimo (70)
    # média = (100+70)/2 = 85.0
    kalebe = next(r for r in rows if r["responsavel_atividade_principal"] == "Kalebe Prado")
    assert kalebe["total_revisoes"] == 2
    assert kalebe["revisao_sem_ressalva"] == 1
    assert kalebe["revisao_com_acrescimo"] == 1
    assert kalebe["media_aproveitamento_pct"] == 85.0
    assert "Luiza Machado" in kalebe["revisores"]
    assert "Kalebe Prado" in kalebe["revisores"]
