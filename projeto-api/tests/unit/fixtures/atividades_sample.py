"""Fixture de atividades sintéticas para testar os services.

Cobre cenários-chave:
- atividade concluída no prazo por pessoa de grupo mapeado
- atividade fora do prazo
- revisão com ressalva / sem ressalva / acréscimo
- autorrevisão (filtrada)
- assunto blacklistado (filtrado)
- assunto sem pontuação no ranking (filtrado do ranking)
"""

from __future__ import annotations

from typing import Any

ATIVIDADES: list[dict[str, Any]] = [
    # Kalebe (Previdenciario - Operacional) concluiu petição no prazo
    {
        "Pasta": "10001",
        "Assunto": "Petição Inicial – PREV",
        "Assunto Atividade Principal": "Petição Inicial – PREV",
        "Status": "Concluído",
        "Data": "02/03/2026 09:00",
        "Data Conclusao": "05/03/2026 10:30",
        "Data Prazo Fatal": "06/03/2026 23:59",
        "Responsavel": "Kalebe Prado",
        "ConcluidoPor": "Kalebe Prado",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Kalebe concluiu fora do prazo
    {
        "Pasta": "10002",
        "Assunto": "Emenda à Inicial - PREV",
        "Assunto Atividade Principal": "Emenda à Inicial - PREV",
        "Status": "Concluído",
        "Data": "03/03/2026 08:00",
        "Data Conclusao": "15/03/2026 18:00",
        "Data Prazo Fatal": "10/03/2026 23:59",
        "Responsavel": "Kalebe Prado",
        "ConcluidoPor": "Kalebe Prado",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Luiza Machado revisou Kalebe — sem ressalva
    {
        "Pasta": "10001",
        "Assunto": "Revisão",
        "Assunto Atividade Principal": "Petição Inicial – PREV",
        "Status": "Concluído",
        "Data": "05/03/2026 15:00",
        "Data Conclusao": "05/03/2026 15:30",
        "Data Prazo Fatal": "",
        "Responsavel": "Luiza Machado",
        "ConcluidoPor": "Luiza Machado",
        "Responsavel Atividade Principal": "Kalebe Prado",
        "Aproveitamento": "Revisão sem ressalva",
        "Natureza": "Judicial",
    },
    # Kalebe fez uma autorrevisão — deve ser filtrado
    {
        "Pasta": "10002",
        "Assunto": "Revisão com acréscimo",
        "Assunto Atividade Principal": "Emenda à Inicial - PREV",
        "Status": "Concluído",
        "Data": "15/03/2026 18:00",
        "Data Conclusao": "15/03/2026 18:10",
        "Data Prazo Fatal": "",
        "Responsavel": "Kalebe Prado",
        "ConcluidoPor": "Kalebe Prado",
        "Responsavel Atividade Principal": "Kalebe Prado",
        "Aproveitamento": "Revisão com acréscimo",
        "Natureza": "Judicial",
    },
    # Pedro Moscon concluiu assunto blacklistado — deve ser filtrado
    {
        "Pasta": "10003",
        "Assunto": "Habilitação",
        "Assunto Atividade Principal": "Habilitação",
        "Status": "Concluído",
        "Data": "07/03/2026 10:00",
        "Data Conclusao": "07/03/2026 10:30",
        "Data Prazo Fatal": "",
        "Responsavel": "Pedro Moscon",
        "ConcluidoPor": "Pedro Moscon",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Pedro Moscon concluiu Réplica — pontua 1 no ranking Prev
    {
        "Pasta": "10004",
        "Assunto": "Réplica",
        "Assunto Atividade Principal": "Réplica",
        "Status": "Concluído",
        "Data": "08/03/2026 14:00",
        "Data Conclusao": "08/03/2026 14:30",
        "Data Prazo Fatal": "",
        "Responsavel": "Pedro Moscon",
        "ConcluidoPor": "Pedro Moscon",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Pedro Moscon concluiu Recurso Inominado — pontua 8 no ranking Prev
    {
        "Pasta": "10005",
        "Assunto": "Recurso Inominado",
        "Assunto Atividade Principal": "Recurso Inominado",
        "Status": "Concluído",
        "Data": "09/03/2026 11:00",
        "Data Conclusao": "09/03/2026 11:30",
        "Data Prazo Fatal": "",
        "Responsavel": "Pedro Moscon",
        "ConcluidoPor": "Pedro Moscon",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Atividade fora do período (2020) — rejeitada por extrair_mes_ano
    {
        "Pasta": "10006",
        "Assunto": "Réplica",
        "Assunto Atividade Principal": "Réplica",
        "Status": "Concluído",
        "Data": "01/03/2019 10:00",
        "Data Conclusao": "01/03/2019 10:30",
        "Data Prazo Fatal": "",
        "Responsavel": "Pedro Moscon",
        "ConcluidoPor": "Pedro Moscon",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
    # Atividade "Pendente" — filtrada
    {
        "Pasta": "10007",
        "Assunto": "Réplica",
        "Assunto Atividade Principal": "Réplica",
        "Status": "Pendente",
        "Data": "10/03/2026 10:00",
        "Data Conclusao": "",
        "Data Prazo Fatal": "",
        "Responsavel": "Kalebe Prado",
        "ConcluidoPor": "",
        "Responsavel Atividade Principal": "",
        "Aproveitamento": "",
        "Natureza": "Judicial",
    },
]
