"""Normalização de nomes / assuntos + mapeamento de grupos.

Paridade 1:1 com `buscarGrupo`, `_isAssuntoExcluido`, `extrairMesAno`, `parseData` do Calculator.js.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime


_DASH_TABLE = str.maketrans(
    {
        "\u2010": "-",  # hyphen
        "\u2011": "-",  # non-breaking hyphen
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2212": "-",  # minus sign
    }
)


def normalize(texto: str | None) -> str:
    """NFD + sem diacríticos + lowercase + trim + dashes Unicode viram hyphen.

    Paridade com `.normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase()` do Calculator.js,
    mais uniformização de en-dash/em-dash (Apps Script falha silenciosamente nesses casos
    — assuntos tipo "Petição Inicial – PREV" ficavam sem pontuação no ranking).
    """
    if not texto:
        return ""
    decomposed = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(c for c in decomposed if not unicodedata.combining(c))
    return sem_acento.translate(_DASH_TABLE).lower().strip()


# ---- Grupos ----

MAPA_GRUPOS: dict[str, str] = {
    # Liderancas
    "Armando Guerini": "Liderancas",
    "Armando Varejão": "Liderancas",
    "Bruna Vidal": "Liderancas",
    "Carol Rigoni": "Liderancas",
    "Luiza Alves": "Liderancas",
    "Lucas Luchi": "Liderancas",
    "Vinicius Oliveira": "Liderancas",
    # Civel Operacional
    "Rafaelle Oliveira": "Civel - Operacional",
    "Andre Murad": "Civel - Operacional",
    "André Murad": "Civel - Operacional",
    "Letycya Cardoso": "Civel - Operacional",
    "Joel Costa": "Civel - Operacional",
    "Guilherme Lube": "Civel - Operacional",
    "Victor Fernandes": "Civel - Operacional",
    # Civel Suporte
    "Nycolle Correia": "Civel - Suporte",
    # Civel Comercial
    "Brenda Catalunha": "Civel - Comercial",
    "Giulia Boscardin": "Civel - Comercial",
    # Trabalhista Operacional
    "Alessandra Sperandio": "Trabalhista - Operacional",
    "Mayara Fardim": "Trabalhista - Operacional",
    "Simone Martins": "Trabalhista - Operacional",
    "Joao Castelo": "Trabalhista - Operacional",
    "João Castelo": "Trabalhista - Operacional",
    "Julia Pitanga": "Trabalhista - Operacional",
    "Ana Demuner": "Trabalhista - Operacional",
    "Matheus Pertence": "Trabalhista - Operacional",
    # Trabalhista Suporte
    "Marcella Xavier": "Trabalhista - Suporte",
    # Previdenciario Operacional
    "Kalebe Prado": "Previdenciario - Operacional",
    "Luiza Machado": "Previdenciario - Operacional",
    "Pedro Moscon": "Previdenciario - Operacional",
    # Previdenciario Suporte
    "Beatriz Galvao": "Previdenciario - Suporte",
    "Beatriz Galvão": "Previdenciario - Suporte",
    # Controladoria
    "Gabriela Capucho": "Controladoria",
    "Ana Beatriz Campos": "Controladoria",
    "Lucas Siqueira": "Controladoria",
    "Julia Milanezi": "Controladoria",
    "Júlia Milanezi": "Controladoria",
    # Financeiro
    "Diego Rangel": "Financeiro",
    # Previdenciario Pos Vendas
    "Maria Eduarda Conti": "Previdenciario - Pos Vendas",
    "Gustavo Guerra": "Previdenciario - Pos Vendas",
    "Marcos Coutinho": "Previdenciario - Pos Vendas",
    "Marcos Vinicius Coutinho": "Previdenciario - Pos Vendas",
}

_MAPA_GRUPOS_NORM: dict[str, str] = {normalize(k): v for k, v in MAPA_GRUPOS.items()}


def buscar_grupo(nome: str | None) -> str:
    """Paridade com `buscarGrupo(nome)` do Calculator.js."""
    if not nome:
        return ""
    s = str(nome).strip()
    if s in MAPA_GRUPOS:
        return MAPA_GRUPOS[s]
    return _MAPA_GRUPOS_NORM.get(normalize(s), "")


# ---- Blacklist global ----

ASSUNTOS_EXCLUIDOS: set[str] = {
    "requisitorio rpv/precatorio",
    "habilitacao",
    "pagamento/garantia da execucao",
    "informar dados bancarios",
    "desistencia",
}


def is_assunto_excluido(assunto: str | None) -> bool:
    return normalize(assunto) in ASSUNTOS_EXCLUIDOS


def is_excluido_por_grupo(
    assunto: str | None,
    grupo: str | None,
    mapa_excluidos: dict[str, set[str]],
) -> bool:
    """Paridade com `_isExcluidoPorGrupo`. `mapa_excluidos[grupo]` = set de assuntos normalizados."""
    if not assunto or not grupo or not mapa_excluidos:
        return False
    nset = mapa_excluidos.get(grupo)
    if not nset:
        return False
    return normalize(assunto) in nset


# ---- Extração mês/ano e parse de data ----

_MESES_NOME = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def mes_ano_label(mes_ano: str) -> str:
    """'03/2026' -> 'Mar/2026'."""
    parts = mes_ano.split("/")
    if len(parts) != 2:
        return mes_ano
    try:
        m = int(parts[0])
        return f"{_MESES_NOME.get(m, parts[0])}/{parts[1]}"
    except ValueError:
        return mes_ano


def parse_data(valor: object) -> datetime | None:
    """Paridade com `parseData`. Aceita datetime, `dd/MM/yyyy[ HH:mm[:ss]]`, `yyyy-MM-dd[...]`."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    s = str(valor).strip()
    if not s:
        return None
    # dd/MM/yyyy[ HH:mm[:ss]]
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        h = int(m.group(4) or 0)
        mi = int(m.group(5) or 0)
        se = int(m.group(6) or 0)
        try:
            return datetime(y, mo, d, h, mi, se)
        except ValueError:
            return None
    # yyyy-MM-dd[THH:mm:ss...]
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        h = int(m.group(4) or 0)
        mi = int(m.group(5) or 0)
        se = int(m.group(6) or 0)
        try:
            return datetime(y, mo, d, h, mi, se)
        except ValueError:
            return None
    return None


def extrair_mes_ano(valor: object) -> str | None:
    """Paridade com `extrairMesAno`. Retorna 'MM/YYYY' ou None (ano entre 2020 e 2030)."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        if 2020 <= valor.year <= 2030:
            return f"{valor.month:02d}/{valor.year}"
        return None
    dt = parse_data(valor)
    if dt and 2020 <= dt.year <= 2030:
        return f"{dt.month:02d}/{dt.year}"
    # Handle "MM/YYYY" puro
    s = str(valor).strip()
    m = re.match(r"^(\d{1,2})/(\d{4})$", s)
    if m:
        mm = int(m.group(1))
        yy = int(m.group(2))
        if 2020 <= yy <= 2030:
            return f"{mm:02d}/{yy}"
    return None


# ---- Aproveitamento ----

PESOS_APROVEITAMENTO: dict[str, int] = {
    "Revisão sem ressalva": 100,
    "Revisão com ressalva": 90,
    "Revisão com acréscimo": 70,
    "Revisão com ressalva e acréscimo": 40,
    "Revisão sem aproveitamento": 0,
}


def normalizar_aproveitamento(valor: str | None) -> str:
    """Paridade com `normalizarAproveitamento`. Retorna chave canônica de PESOS_APROVEITAMENTO."""
    if not valor:
        return ""
    v = str(valor).strip().lower()
    if "sem ressalva" in v and "sem aproveitamento" not in v:
        return "Revisão sem ressalva"
    if "ressalva" in v and "acréscimo" in v:
        return "Revisão com ressalva e acréscimo"
    if "ressalva" in v and "acréscimo" not in v:
        return "Revisão com ressalva"
    if "acréscimo" in v and "ressalva" not in v:
        return "Revisão com acréscimo"
    if "sem aproveitamento" in v:
        return "Revisão sem aproveitamento"
    for tipo in PESOS_APROVEITAMENTO:
        if v == tipo.lower():
            return tipo
    return ""
