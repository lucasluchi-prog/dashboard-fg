"""Testes unitários do client DataJuri (sem bater na API real)."""

from app.services.datajuri_client import nested_value


def test_nested_simples():
    assert nested_value({"a": 1}, "a") == 1


def test_nested_profundo():
    payload = {"processo": {"pasta": "12345", "tipoProcesso": "Judicial"}}
    assert nested_value(payload, "processo.pasta") == "12345"
    assert nested_value(payload, "processo.tipoProcesso") == "Judicial"


def test_nested_ausente():
    assert nested_value({"a": 1}, "a.b.c") == ""


def test_nested_none():
    assert nested_value({"a": None}, "a.b") == ""
