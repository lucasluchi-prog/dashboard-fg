"""Testes do Ranking Gamificado."""

from app.services.ranking import buscar_pontuacao_ranking, calcular_ranking
from tests.unit.fixtures.atividades_sample import ATIVIDADES

PONTUACAO_PREV = {
    "peticao inicial - prev": 6,
    "emenda a inicial - prev": 2,
    "replica": 1,
    "recurso inominado": 8,
}
POR_GRUPO = {"Previdenciario - Operacional": PONTUACAO_PREV}


def test_buscar_pontuacao_match_exato():
    assert buscar_pontuacao_ranking("Réplica", "Previdenciario - Operacional", POR_GRUPO) == 1
    assert (
        buscar_pontuacao_ranking("Recurso Inominado", "Previdenciario - Operacional", POR_GRUPO)
        == 8
    )


def test_buscar_pontuacao_match_substring():
    # "Petição Inicial – PREV" contém "peticao inicial - prev"
    assert (
        buscar_pontuacao_ranking(
            "Petição Inicial – PREV", "Previdenciario - Operacional", POR_GRUPO
        )
        > 0
    )


def test_buscar_pontuacao_grupo_desconhecido():
    assert buscar_pontuacao_ranking("Réplica", "Grupo Inexistente", POR_GRUPO) == 0


def test_ranking_pedro_kalebe_ordenados():
    rows = calcular_ranking(
        ATIVIDADES, pontuacao_por_grupo=POR_GRUPO, taxa_aprov_map={}
    )
    # Pedro: Réplica (1) + Recurso Inominado (8) = 9 brutos, sem habilitação (blacklist)
    # Kalebe: Petição Inicial – PREV (6, match substring) + Emenda à Inicial - PREV (2)
    #         -> 8 brutos. Autorrevisão dele é filtrada.
    pedro = [r for r in rows if r["responsavel"] == "Pedro Moscon"]
    kalebe = [r for r in rows if r["responsavel"] == "Kalebe Prado"]

    assert len(pedro) == 1
    assert len(kalebe) == 1
    assert pedro[0]["pontos_brutos"] == 9
    assert kalebe[0]["pontos_brutos"] == 8

    # Sem taxa -> taxa_aprov = 100, pontos_validos == brutos
    assert pedro[0]["taxa_aprov"] == 100
    assert pedro[0]["pontos_validos"] == 9

    # Pedro ocupa posição 1 (9 > 8)
    assert pedro[0]["posicao"] == 1
    assert kalebe[0]["posicao"] == 2


def test_ranking_aplica_taxa_aproveitamento():
    taxa = {"kalebe prado|03/2026": 50.0}
    rows = calcular_ranking(
        ATIVIDADES, pontuacao_por_grupo=POR_GRUPO, taxa_aprov_map=taxa
    )
    kalebe = next(r for r in rows if r["responsavel"] == "Kalebe Prado")
    # 8 * 50% = 4
    assert kalebe["taxa_aprov"] == 50.0
    assert kalebe["pontos_validos"] == 4


def test_ranking_ignora_assunto_sem_pontuacao():
    # Se removermos "Recurso Inominado" da tabela, Pedro cai para 1 ponto.
    tabela = {"replica": 1}
    rows = calcular_ranking(
        ATIVIDADES,
        pontuacao_por_grupo={"Previdenciario - Operacional": tabela},
        taxa_aprov_map={},
    )
    pedro = next(r for r in rows if r["responsavel"] == "Pedro Moscon")
    assert pedro["pontos_brutos"] == 1
    assert pedro["total_atividades"] == 1
