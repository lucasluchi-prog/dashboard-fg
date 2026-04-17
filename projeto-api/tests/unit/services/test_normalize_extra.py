"""Extrações complementares da paridade normalize/parse."""

from datetime import datetime

from app.services.normalize import (
    buscar_grupo,
    extrair_mes_ano,
    is_assunto_excluido,
    mes_ano_label,
    normalizar_aproveitamento,
    parse_data,
)


def test_buscar_grupo_exato():
    assert buscar_grupo("Kalebe Prado") == "Previdenciario - Operacional"


def test_buscar_grupo_com_acento():
    # Paridade: "João Castelo" deve cair no mesmo grupo que "Joao Castelo".
    assert buscar_grupo("João Castelo") == "Trabalhista - Operacional"
    assert buscar_grupo("Joao Castelo") == "Trabalhista - Operacional"


def test_buscar_grupo_desconhecido():
    assert buscar_grupo("Desconhecido") == ""


def test_buscar_grupo_none():
    assert buscar_grupo(None) == ""


def test_is_assunto_excluido():
    assert is_assunto_excluido("Habilitação") is True
    assert is_assunto_excluido("Desistência") is True
    assert is_assunto_excluido("Petição Inicial – PREV") is False


def test_extrair_mes_ano_dd_mm_yyyy():
    assert extrair_mes_ano("05/03/2026 10:30") == "03/2026"
    assert extrair_mes_ano("5/3/2026") == "03/2026"


def test_extrair_mes_ano_iso():
    assert extrair_mes_ano("2026-04-01") == "04/2026"


def test_extrair_mes_ano_datetime():
    assert extrair_mes_ano(datetime(2026, 5, 17, 14, 30)) == "05/2026"


def test_extrair_mes_ano_invalido():
    assert extrair_mes_ano("01/03/2019") is None  # ano < 2020
    assert extrair_mes_ano("") is None
    assert extrair_mes_ano(None) is None


def test_parse_data_dd_mm_yyyy():
    dt = parse_data("05/03/2026 10:30")
    assert dt == datetime(2026, 3, 5, 10, 30)


def test_parse_data_sem_hora():
    dt = parse_data("05/03/2026")
    assert dt == datetime(2026, 3, 5)


def test_parse_data_iso():
    dt = parse_data("2026-03-05T10:30:00")
    assert dt == datetime(2026, 3, 5, 10, 30)


def test_mes_ano_label():
    assert mes_ano_label("03/2026") == "Mar/2026"
    assert mes_ano_label("12/2025") == "Dez/2025"


def test_normalizar_aproveitamento():
    assert normalizar_aproveitamento("Revisão sem ressalva") == "Revisão sem ressalva"
    assert normalizar_aproveitamento("Revisão com ressalva") == "Revisão com ressalva"
    assert normalizar_aproveitamento("Revisão com acréscimo") == "Revisão com acréscimo"
    assert (
        normalizar_aproveitamento("Revisão com ressalva e acréscimo")
        == "Revisão com ressalva e acréscimo"
    )
    assert normalizar_aproveitamento("Revisão sem aproveitamento") == "Revisão sem aproveitamento"
    assert normalizar_aproveitamento("") == ""
