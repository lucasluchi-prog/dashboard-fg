"""Casos-limite: datas na borda, atividade sem status, feriado == dia de conclusão."""

from datetime import date

from app.services.dias_uteis import FERIADOS_HARDCODED
from app.services.normalize import extrair_mes_ano, parse_data
from app.services.produtividade import calcular_produtividade
from app.services.ranking import calcular_ranking


def test_produtividade_status_vazio():
    atividades = [
        {
            "Responsavel": "Kalebe Prado",
            "ConcluidoPor": "Kalebe Prado",
            "Status": "",
            "Data Conclusao": "05/03/2026 10:00",
            "Assunto": "Réplica",
        }
    ]
    assert calcular_produtividade(atividades, feriados=FERIADOS_HARDCODED) == []


def test_produtividade_sem_data_conclusao():
    atividades = [
        {
            "Responsavel": "Kalebe Prado",
            "ConcluidoPor": "Kalebe Prado",
            "Status": "Concluído",
            "Data Conclusao": "",
            "Assunto": "Réplica",
        }
    ]
    assert calcular_produtividade(atividades, feriados=FERIADOS_HARDCODED) == []


def test_produtividade_conclusao_no_mesmo_dia_do_prazo_e_no_prazo():
    atividades = [
        {
            "Responsavel": "Kalebe Prado",
            "ConcluidoPor": "Kalebe Prado",
            "Status": "Concluído",
            "Assunto": "Réplica",
            "Data Conclusao": "10/03/2026 23:55",
            "Data Prazo Fatal": "10/03/2026 08:00",  # prazo venceu 23:55 antes? não: comparação por data, não hora
        }
    ]
    rows = calcular_produtividade(
        atividades, feriados=FERIADOS_HARDCODED, hoje=date(2026, 4, 1)
    )
    # Paridade com Apps Script: comparação por `Date(y,m,d)` — a hora é ignorada.
    # Então mesmo dia = no prazo.
    assert rows[0]["no_prazo"] == 1
    assert rows[0]["fora_do_prazo"] == 0


def test_produtividade_feriado_nao_conta_como_dia_util():
    atividades = [
        {
            "Responsavel": "Kalebe Prado",
            "ConcluidoPor": "Kalebe Prado",
            "Status": "Concluído",
            "Assunto": "Réplica",
            "Data Conclusao": "21/04/2026 10:00",  # Tiradentes 2026
            "Data Prazo Fatal": "",
        }
    ]
    rows = calcular_produtividade(
        atividades, feriados=FERIADOS_HARDCODED, hoje=date(2026, 5, 1)
    )
    # total_concluidas = 1, mas concluidas_dias_uteis = 0 (feriado)
    assert rows[0]["total_concluidas"] == 1
    assert rows[0]["concluidas_dias_uteis"] == 0


def test_ranking_ignora_mes_fora_da_janela():
    atividades = [
        {
            "Responsavel": "Kalebe Prado",
            "ConcluidoPor": "Kalebe Prado",
            "Status": "Concluído",
            "Assunto": "Réplica",
            "Data Conclusao": "01/03/2019 10:00",  # fora de 2020..2030
        }
    ]
    rows = calcular_ranking(
        atividades,
        pontuacao_por_grupo={"Previdenciario - Operacional": {"replica": 1}},
        taxa_aprov_map={},
    )
    assert rows == []


def test_ranking_sem_responsavel_filtrado():
    atividades = [
        {
            "Responsavel": "",
            "ConcluidoPor": "",
            "Status": "Concluído",
            "Assunto": "Réplica",
            "Data Conclusao": "05/03/2026 10:00",
        }
    ]
    rows = calcular_ranking(
        atividades,
        pontuacao_por_grupo={"Previdenciario - Operacional": {"replica": 1}},
        taxa_aprov_map={},
    )
    assert rows == []


def test_extrair_mes_ano_aceita_mm_yyyy_puro():
    assert extrair_mes_ano("3/2026") == "03/2026"


def test_parse_data_invalida():
    assert parse_data("nunca") is None
    assert parse_data("") is None
    assert parse_data(None) is None


def test_parse_data_31_fevereiro_e_invalida():
    # 31/02 não existe — parse_data deve retornar None (não ValueError)
    assert parse_data("31/02/2026") is None


def test_dia_util_na_virada_do_ano():
    # 01/01/2026 (quinta) é feriado
    from app.services.dias_uteis import eh_dia_util
    assert eh_dia_util(date(2026, 1, 1), FERIADOS_HARDCODED) is False
    assert eh_dia_util(date(2026, 1, 2), FERIADOS_HARDCODED) is True  # sexta
