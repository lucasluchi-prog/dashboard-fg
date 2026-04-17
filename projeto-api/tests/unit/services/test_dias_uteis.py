"""Dias úteis — sábado, domingo e feriados não contam."""

from datetime import date

from app.services.dias_uteis import dias_uteis_entre, eh_dia_util


FERIADOS_2026 = {
    date(2026, 2, 16),  # Carnaval seg
    date(2026, 4, 21),  # Tiradentes
}


def test_segunda_util():
    assert eh_dia_util(date(2026, 4, 13), FERIADOS_2026) is True


def test_sabado_nao_util():
    assert eh_dia_util(date(2026, 4, 18), FERIADOS_2026) is False


def test_domingo_nao_util():
    assert eh_dia_util(date(2026, 4, 19), FERIADOS_2026) is False


def test_feriado_fixo():
    assert eh_dia_util(date(2026, 4, 21), FERIADOS_2026) is False


def test_intervalo_semana():
    # seg 06/04 a sex 10/04 = 5 dias úteis
    dias = dias_uteis_entre(date(2026, 4, 6), date(2026, 4, 10), FERIADOS_2026)
    assert dias == 5


def test_intervalo_com_feriado():
    # seg 13/04 a sex 24/04 = 10 dias - 1 tiradentes = 9
    dias = dias_uteis_entre(date(2026, 4, 13), date(2026, 4, 24), FERIADOS_2026)
    assert dias == 9
