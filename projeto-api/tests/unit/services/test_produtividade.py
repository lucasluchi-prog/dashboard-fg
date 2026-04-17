"""Testes de produtividade."""

from datetime import date

from app.services.dias_uteis import FERIADOS_HARDCODED
from app.services.produtividade import calcular_produtividade
from tests.unit.fixtures.atividades_sample import ATIVIDADES


def _linhas_por_responsavel(rows, responsavel: str):
    return [r for r in rows if r["responsavel"] == responsavel]


def test_produtividade_kalebe_noprazo_e_atrasado():
    # hoje fixado em 2026-04-01 para produzir dias_uteis estáveis
    rows = calcular_produtividade(
        ATIVIDADES, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    kalebe = _linhas_por_responsavel(rows, "Kalebe Prado")

    # 2 atividades concluídas (petição no prazo Q1 + emenda fora de prazo Q2)
    assert len(kalebe) == 2
    # a revisão feita por Kalebe é autorrevisão -> filtrada
    # a atividade "Pendente" não aparece

    # Soma total
    assert sum(r["total_concluidas"] for r in kalebe) == 2

    # A petição ficou no prazo, a emenda ficou atrasada
    total_no_prazo = sum(r["no_prazo"] for r in kalebe)
    total_atraso = sum(r["fora_do_prazo"] for r in kalebe)
    assert total_no_prazo == 1
    assert total_atraso == 1


def test_produtividade_filtra_autorrevisao_e_blacklist():
    rows = calcular_produtividade(
        ATIVIDADES, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    # Pedro tem 1 habilitação (blacklist global, filtrada) + 2 válidas = 2 linhas
    pedro = _linhas_por_responsavel(rows, "Pedro Moscon")
    assert len(pedro) == 2
    # Nenhum deles é "Habilitação"
    assunto_l = [r["assunto"].lower() for r in pedro]
    assert "habilitação" not in assunto_l
    assert "habilitacao" not in [a.lower() for a in assunto_l]


def test_produtividade_luiza_revisao_contada():
    rows = calcular_produtividade(
        ATIVIDADES, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    luiza = _linhas_por_responsavel(rows, "Luiza Machado")
    # Revisão não é autorrevisão (Luiza != Kalebe), deve contar
    assert len(luiza) == 1
    assert luiza[0]["total_concluidas"] == 1


def test_produtividade_fora_de_janela_descartada():
    rows = calcular_produtividade(
        ATIVIDADES, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    # A atividade de 2019 tinha que ser descartada
    mes_anos = {r["mes_ano"] for r in rows}
    assert "03/2019" not in mes_anos


def test_produtividade_grupo_preenchido():
    rows = calcular_produtividade(
        ATIVIDADES, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    kalebe = _linhas_por_responsavel(rows, "Kalebe Prado")
    assert kalebe[0]["grupo"] == "Previdenciario - Operacional"
