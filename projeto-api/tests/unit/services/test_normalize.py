"""Paridade com `.normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase()`."""

from app.services.normalize import normalize


def test_remove_acentos():
    # en-dash é uniformizado para hyphen para bater com as chaves de pontuação.
    assert normalize("Petição Inicial – PREV") == "peticao inicial - prev"


def test_lowercase():
    assert normalize("RECURSO INOMINADO") == "recurso inominado"


def test_trim():
    assert normalize("  Réplica  ") == "replica"


def test_none():
    assert normalize(None) == ""


def test_vazio():
    assert normalize("") == ""


def test_mista():
    # paridade com "João Castelo" e "Joao Castelo" — ambos caem no mesmo slug.
    assert normalize("João Castelo") == normalize("Joao Castelo")


def test_preserva_separadores():
    assert normalize("Mandado de Segurança - FIES") == "mandado de seguranca - fies"
