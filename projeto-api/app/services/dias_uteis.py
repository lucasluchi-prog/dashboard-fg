"""Dias úteis — paridade com `isDiaUtil`, `calcularDiasUteisMes`, `calcularDiasUteisQuinzena`."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feriado import Feriado


# Conjunto estático — o ETL carrega do banco uma vez e passa como argumento.
# Em testes, usar o `FERIADOS_HARDCODED` abaixo para manter paridade determinística.
FERIADOS_HARDCODED: set[date] = {
    # 2025
    date(2025, 1, 1), date(2025, 3, 3), date(2025, 3, 4), date(2025, 3, 5),
    date(2025, 4, 18), date(2025, 4, 21), date(2025, 5, 1), date(2025, 6, 19),
    date(2025, 9, 7), date(2025, 10, 12), date(2025, 11, 2), date(2025, 11, 15),
    date(2025, 11, 20), date(2025, 12, 25),
    # 2026
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 4, 3), date(2026, 4, 21), date(2026, 5, 1), date(2026, 6, 4),
    date(2026, 9, 7), date(2026, 10, 12), date(2026, 11, 2), date(2026, 11, 15),
    date(2026, 11, 20), date(2026, 12, 25),
}


async def load_feriados(db: AsyncSession, ano: int | None = None) -> set[date]:
    stmt = select(Feriado.data)
    if ano is not None:
        from sqlalchemy import extract
        stmt = stmt.where(extract("year", Feriado.data) == ano)
    result = await db.execute(stmt)
    return set(result.scalars().all())


def eh_dia_util(d: date | datetime, feriados: set[date]) -> bool:
    if isinstance(d, datetime):
        d = d.date()
    if d.weekday() >= 5:  # sábado/domingo
        return False
    return d not in feriados


def dias_uteis_mes(mes_ano: str, feriados: set[date], hoje: date | None = None) -> int:
    """Paridade com `calcularDiasUteisMes`.

    Se `mes_ano` for o mês atual (`hoje`), conta só até hoje.
    """
    parts = mes_ano.split("/")
    if len(parts) != 2:
        return 0
    try:
        mes = int(parts[0])
        ano = int(parts[1])
    except ValueError:
        return 0
    hoje = hoje or date.today()

    # último dia do mês
    proximo_mes = date(ano, 12, 31) if mes == 12 else date(ano, mes + 1, 1) - timedelta(days=1)
    if mes == 12:
        ultimo_dia = 31
    else:
        ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day
    if ano == hoje.year and mes == hoje.month:
        ultimo_dia = min(ultimo_dia, hoje.day)

    total = 0
    for dia in range(1, ultimo_dia + 1):
        try:
            d = date(ano, mes, dia)
        except ValueError:
            continue
        if eh_dia_util(d, feriados):
            total += 1
    return total


def dias_uteis_quinzena(
    mes_ano: str,
    quinzena: str,
    feriados: set[date],
    hoje: date | None = None,
) -> int:
    """Paridade com `calcularDiasUteisQuinzena`.

    Q1 = dias 1..15; Q2 = dias 16..fim do mês.
    """
    parts = mes_ano.split("/")
    if len(parts) != 2:
        return 0
    try:
        mes = int(parts[0])
        ano = int(parts[1])
    except ValueError:
        return 0
    hoje = hoje or date.today()

    if mes == 12:
        ultimo_dia_mes = 31
    else:
        ultimo_dia_mes = (date(ano, mes + 1, 1) - timedelta(days=1)).day

    dia_inicio = 1 if quinzena == "Q1" else 16
    dia_fim = 15 if quinzena == "Q1" else ultimo_dia_mes
    if ano == hoje.year and mes == hoje.month:
        dia_fim = min(dia_fim, hoje.day)

    total = 0
    for dia in range(dia_inicio, dia_fim + 1):
        try:
            d = date(ano, mes, dia)
        except ValueError:
            continue
        if eh_dia_util(d, feriados):
            total += 1
    return total


def dias_uteis_entre(inicio: date, fim: date, feriados: set[date]) -> int:
    if inicio > fim:
        return 0
    total = 0
    cur = inicio
    while cur <= fim:
        if eh_dia_util(cur, feriados):
            total += 1
        cur += timedelta(days=1)
    return total
