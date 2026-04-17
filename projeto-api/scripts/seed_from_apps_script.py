"""Seed inicial a partir dos valores hard-coded em `Config.js` e `Calculator.js` legados.

Popula: grupo, pessoa (sem id DataJuri ainda — será completado pelo ETL),
pontuacao_ranking, assunto_excluido, feriado, parametro.

Idempotente: usa upserts.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db import get_session_factory
from app.models import (
    AssuntoExcluido,
    Feriado,
    Grupo,
    Parametro,
    Pessoa,
    PontuacaoRanking,
)
from app.services.normalize import normalize

logger = logging.getLogger("seed")

# ---------- Grupos e pessoas ---------- (extraídos de Calculator.js:26-79)

MAPA_GRUPOS: dict[str, str] = {
    "Armando Guerini": "Liderancas",
    "Armando Varejão": "Liderancas",
    "Bruna Vidal": "Liderancas",
    "Carol Rigoni": "Liderancas",
    "Luiza Alves": "Liderancas",
    "Lucas Luchi": "Liderancas",
    "Vinicius Oliveira": "Liderancas",
    "Rafaelle Oliveira": "Civel - Operacional",
    "Andre Murad": "Civel - Operacional",
    "André Murad": "Civel - Operacional",
    "Letycya Cardoso": "Civel - Operacional",
    "Joel Costa": "Civel - Operacional",
    "Guilherme Lube": "Civel - Operacional",
    "Victor Fernandes": "Civel - Operacional",
    "Nycolle Correia": "Civel - Suporte",
    "Brenda Catalunha": "Civel - Comercial",
    "Giulia Boscardin": "Civel - Comercial",
    "Alessandra Sperandio": "Trabalhista - Operacional",
    "Mayara Fardim": "Trabalhista - Operacional",
    "Simone Martins": "Trabalhista - Operacional",
    "Joao Castelo": "Trabalhista - Operacional",
    "João Castelo": "Trabalhista - Operacional",
    "Julia Pitanga": "Trabalhista - Operacional",
    "Ana Demuner": "Trabalhista - Operacional",
    "Matheus Pertence": "Trabalhista - Operacional",
    "Marcella Xavier": "Trabalhista - Suporte",
    "Kalebe Prado": "Previdenciario - Operacional",
    "Luiza Machado": "Previdenciario - Operacional",
    "Pedro Moscon": "Previdenciario - Operacional",
    "Beatriz Galvao": "Previdenciario - Suporte",
    "Beatriz Galvão": "Previdenciario - Suporte",
    "Gabriela Capucho": "Controladoria",
    "Ana Beatriz Campos": "Controladoria",
    "Lucas Siqueira": "Controladoria",
    "Julia Milanezi": "Controladoria",
    "Júlia Milanezi": "Controladoria",
    "Diego Rangel": "Financeiro",
    "Maria Eduarda Conti": "Previdenciario - Pos Vendas",
    "Gustavo Guerra": "Previdenciario - Pos Vendas",
    "Marcos Coutinho": "Previdenciario - Pos Vendas",
    "Marcos Vinicius Coutinho": "Previdenciario - Pos Vendas",
}

# ---------- Pontuações por grupo ---------- (Config.js)

PONTUACAO_RANKING_PREV: dict[str, int] = {
    "analise de viabilidade - beneficios": 9,
    "recurso inominado": 8,
    "mf laudo": 8,
    "agravos": 8,
    "apelacao": 8,
    "agravo interno": 8,
    "mf aos esclarecimentos do perito": 8,
    "embargos de declaracao": 7,
    "peticao inicial - prev": 6,
    "revisao": 6,
    "manifestacao a excecao de incompetencia": 5,
    "cred": 4,
    "crri": 4,
    "requerimento administrativo": 4,
    "contrarrazoes de apelacao": 4,
    "cumprimento de sentenca - prev": 3,
    "analise de viabilidade - restituicao de inss": 3,
    "peticao de meio - prev": 2,
    "emenda a inicial - prev": 2,
    "juntada de documentos": 2,
    "mf aos calculos": 2,
    "mf sobre a impugnacao": 2,
    "razoes finais": 2,
    "especificar provas": 2,
    "peticao de juntada - prev": 2,
    "replica": 1,
    "quesitos": 1,
    "peticao inicial - restituicao": 1,
    "cumprimento de exigencia": 1,
    "conversao audiencia": 1,
}

PONTUACAO_RANKING_CIVEL: dict[str, int] = {
    "acao rescisoria": 8, "acompanhar processo": 2, "acompanhar processo administrativo": 2,
    "acordo": 2, "aditamento a inicial": 3, "agravo": 8, "agravo de instrumento": 8,
    "agravo interno": 8, "analise de custas/multa": 4, "analise de viabilidade - atipicas - civel": 6,
    "apelacao": 7, "audiencia conciliacao": 5, "audiencia de instrucao e julgamento": 5,
    "avisar cliente": 3, "chamada": 2, "cobrar cliente": 2, "contestacao": 6,
    "contrarrazoes de apelacao": 7, "conversao audiencia": 3, "cr puil": 5, "crain": 5,
    "cred": 5, "crresp": 5, "crrex": 5, "crri": 4, "cumprimento de sentenca": 5,
    "desistencia": 1, "despachar": 5, "embargos a execucao": 8, "embargos de declaracao": 5,
    "emenda a inicial - civel": 2, "especificar provas": 1, "gerar custas": 4,
    "juntada de documentos": 2, "mandado de seguranca": 5, "mandado de seguranca - fies": 5,
    "manifestacao a excecao de incompetencia": 7, "manifestacao preliminar": 7, "memoriais": 4,
    "mf aos calculos": 5, "mf sobre a impugnacao": 5, "notificacao extrajudicial": 4,
    "parecer": 4, "peticao de meio - civel": 3, "peticao inicial - atipica - civel": 6,
    "peticao inicial - civel": 4, "preparacao de audiencia": 1, "protocolo": 1, "puil": 8,
    "reclamacao": 8, "recurso especial": 8, "recurso extra ou puil": 8,
    "recurso extraordinario": 8, "recurso inominado": 6, "replica - civel": 3,
    "requerimento administrativo": 3, "restituicao de custas": 5, "revisao": 5,
    "substabelecimento": 1, "substabelecimento - correspondente": 1, "sustentacao oral": 5,
}  # fmt: skip

PONTUACAO_RANKING_TRAB: dict[str, int] = {
    "reclamacao trabalhista": 9, "substabelecimento": 1, "acompanhar processo": 3,
    "despachar": 3, "carta convite": 3, "emenda a inicial": 6, "aditamento": 6,
    "nova rt": 7, "mf a excecao de incompetencia": 3, "preparacao de audiencia": 8,
    "audiencia": 10, "acompanhar audiencia (capacitacao)": 4, "impugnacao da ata": 3,
    "degravacao de audiencia": 3, "especificacao de provas": 5, "quesitos": 3,
    "juntada de documentos": 4, "protestos antipreclusivos": 4, "chamada": 3,
    "replica": 8, "peticao de meio": 5, "manifestacao ao laudo": 7,
    "mf laudo - trab": 7, "manifestacao aos esclarecimentos": 7,
    "mf aos esclarecimentos do perito": 7, "impugnacao aos honorarios periciais": 3,
    "solicitar calculos": 1, "manifestacao aos calculos": 4, "mf aos calculos": 4,
    "manifestacao sobre impugnacao": 5, "mf sobre a impugnacao": 5,
    "recurso ordinario": 9, "contrarrazoes ao ro": 7, "crro": 7, "recurso de revista": 10,
    "contrarrazoes ao rr": 9, "agravo de instrumento (tst)": 10, "contraminuta ao ai": 8,
    "agravo de peticao": 9, "contraminuta ao ap": 8, "embargos de declaracao": 7,
    "mandado de seguranca": 7, "sustentacao oral": 10, "ro adesivo": 9, "cred": 6,
    "agravo interno": 8, "razoes finais": 6, "memoriais": 6, "parecer tecnico": 8,
    "liquidar inicial": 8, "impugnacao a sentenca de liquidacao": 7,
    "cumprimento de sentenca": 5, "pagamento / garantia": 3, "informar pagamento de guia": 2,
    "proposta de acordo": 5, "minuta de acordo": 6, "discriminar acordo": 3,
    "analisar / avaliar repasse": 7,
}  # fmt: skip

PONTUACAO_POR_GRUPO: dict[str, dict[str, int]] = {
    "Previdenciario - Operacional": PONTUACAO_RANKING_PREV,
    "Civel - Operacional": PONTUACAO_RANKING_CIVEL,
    "Trabalhista - Operacional": PONTUACAO_RANKING_TRAB,
}

# ---------- Blacklist global ---------- (Calculator.js:14)

ASSUNTOS_EXCLUIDOS: list[str] = [
    "requisitorio rpv/precatorio",
    "habilitacao",
    "pagamento/garantia da execucao",
    "informar dados bancarios",
    "desistencia",
]

# ---------- Pesos + fatores ---------- (Config.js:128, 241)

PESOS_APROVEITAMENTO: dict[str, float] = {
    "Revisão sem ressalva": 100,
    "Revisão com ressalva": 90,
    "Revisão com acréscimo": 70,
    "Revisão com ressalva e acréscimo": 40,
    "Revisão sem aproveitamento": 0,
}

FATORES_APROVEITAMENTO: dict[str, float] = {
    "revisao sem ressalva": 1.00,
    "revisao com ressalva": 0.90,
    "revisao com acrescimo": 0.70,
    "revisao com ressalva e acrescimo": 0.40,
    "revisao sem aproveitamento": 0.00,
}

# ---------- Feriados ---------- (Config.js:80)

FERIADOS: dict[int, list[tuple[str, str]]] = {
    2025: [
        ("2025-01-01", "Confraternização Universal"),
        ("2025-03-03", "Carnaval"),
        ("2025-03-04", "Carnaval"),
        ("2025-03-05", "Quarta-feira de Cinzas"),
        ("2025-04-18", "Paixão de Cristo"),
        ("2025-04-21", "Tiradentes"),
        ("2025-05-01", "Dia do Trabalho"),
        ("2025-06-19", "Corpus Christi"),
        ("2025-09-07", "Independência do Brasil"),
        ("2025-10-12", "Nossa Sra Aparecida"),
        ("2025-11-02", "Finados"),
        ("2025-11-15", "Proclamação da República"),
        ("2025-11-20", "Consciência Negra"),
        ("2025-12-25", "Natal"),
    ],
    2026: [
        ("2026-01-01", "Confraternização Universal"),
        ("2026-02-16", "Carnaval"),
        ("2026-02-17", "Carnaval"),
        ("2026-02-18", "Quarta-feira de Cinzas"),
        ("2026-04-03", "Paixão de Cristo"),
        ("2026-04-21", "Tiradentes"),
        ("2026-05-01", "Dia do Trabalho"),
        ("2026-06-04", "Corpus Christi"),
        ("2026-09-07", "Independência do Brasil"),
        ("2026-10-12", "Nossa Sra Aparecida"),
        ("2026-11-02", "Finados"),
        ("2026-11-15", "Proclamação da República"),
        ("2026-11-20", "Consciência Negra"),
        ("2026-12-25", "Natal"),
    ],
}


async def seed() -> None:
    factory = get_session_factory()
    async with factory() as db:
        # grupos
        grupos_unicos = sorted(set(MAPA_GRUPOS.values()))
        for nome in grupos_unicos:
            stmt = pg_insert(Grupo).values(nome=nome).on_conflict_do_nothing()
            await db.execute(stmt)
        await db.commit()

        result = await db.execute(select(Grupo))
        grupo_by_nome = {g.nome: g.id for g in result.scalars().all()}
        logger.info("Grupos: %d", len(grupo_by_nome))

        # pessoas — sem id DataJuri ainda (será atualizado pelo ETL).
        # Usamos hash estável do nome como id temporário negativo.
        for nome, grupo_nome in MAPA_GRUPOS.items():
            stmt = (
                pg_insert(Pessoa)
                .values(
                    id=-abs(hash(nome)) % (2**31),
                    nome=nome,
                    grupo_id=grupo_by_nome[grupo_nome],
                    ativo=True,
                )
                .on_conflict_do_update(
                    index_elements=["nome"],
                    set_={"grupo_id": grupo_by_nome[grupo_nome]},
                )
            )
            await db.execute(stmt)
        await db.commit()

        # pontuacao_ranking
        for grupo_nome, tabela in PONTUACAO_POR_GRUPO.items():
            gid = grupo_by_nome[grupo_nome]
            for assunto_norm, pontos in tabela.items():
                stmt = (
                    pg_insert(PontuacaoRanking)
                    .values(grupo_id=gid, assunto_norm=normalize(assunto_norm), pontos=pontos)
                    .on_conflict_do_update(
                        index_elements=["grupo_id", "assunto_norm"],
                        set_={"pontos": pontos},
                    )
                )
                await db.execute(stmt)
        await db.commit()
        logger.info("Pontuações semeadas")

        # Blacklist global (ASSUNTOS_EXCLUIDOS) fica hardcoded em app/services/normalize.py
        # — é usada via is_assunto_excluido() em todos os services. A tabela
        # `assunto_excluido` é só para blacklists POR GRUPO (com grupo_id definido).
        logger.info("Skip seed global — is_assunto_excluido() usa lista hardcoded")

        # feriados
        for _, itens in FERIADOS.items():
            for data_str, descricao in itens:
                dt = date.fromisoformat(data_str)
                stmt = (
                    pg_insert(Feriado)
                    .values(data=dt, descricao=descricao)
                    .on_conflict_do_nothing()
                )
                await db.execute(stmt)
        await db.commit()

        # parâmetros
        for chave, valor in [
            ("pesos_aproveitamento", PESOS_APROVEITAMENTO),
            ("fatores_aproveitamento", FATORES_APROVEITAMENTO),
            ("horario_atualizacao_1", 8),
            ("horario_atualizacao_2", 14),
        ]:
            stmt = (
                pg_insert(Parametro)
                .values(chave=chave, valor=valor)
                .on_conflict_do_update(index_elements=["chave"], set_={"valor": valor})
            )
            await db.execute(stmt)
        await db.commit()

        logger.info("Seed concluído.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(seed())
