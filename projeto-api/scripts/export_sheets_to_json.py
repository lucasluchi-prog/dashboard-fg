"""Exporta as abas `Atividades_Raw` e `*_Calculado` do Sheets para JSON local.

Útil para:
- alimentar o Postgres local com dados reais antes do ETL DataJuri estar configurado
- servir de fixture congelada para o teste de paridade em CI (sem bater em Sheets)

Uso:
    SHEETS_SERVICE_ACCOUNT=/path/creds.json \
    python scripts/export_sheets_to_json.py --out tests/integration/snapshots/sheets
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger("export_sheets")

ABAS = [
    "Atividades_Raw",
    "Produtividade_Calculado",
    "Aproveitamento_Calculado",
    "Aproveitamento_Individual",
    "Aproveitamento_Peticao",
    "Desempenho_Revisor",
    "Distribuicao_Horario",
    "Distribuicao_Assunto",
    "Ranking_Gamificado",
    "Config_Assuntos",
    "Assuntos_Excluidos_Por_Grupo",
]


def _gspread():
    try:
        import gspread  # noqa: F401
        from google.oauth2.service_account import Credentials
    except ImportError:
        sys.exit("pip install '.[paridade]'")

    path = os.environ.get("SHEETS_SERVICE_ACCOUNT") or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if not path:
        sys.exit("Defina SHEETS_SERVICE_ACCOUNT ou GOOGLE_APPLICATION_CREDENTIALS")
    creds = Credentials.from_service_account_file(
        path,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ],
    )
    import gspread

    return gspread.authorize(creds)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spreadsheet-id",
        default=os.environ.get(
            "SHEETS_SPREADSHEET_ID", "1fe6yHUub8hm8zdLIlm0KxVUiyRXzaU-ANcoSv07JT4E"
        ),
    )
    parser.add_argument(
        "--out",
        default="tests/integration/snapshots/sheets",
        help="Diretório onde gravar os JSONs",
    )
    parser.add_argument("--aba", action="append", help="Limitar a abas específicas")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    gc = _gspread()
    sh = gc.open_by_key(args.spreadsheet_id)

    alvo = args.aba or ABAS
    for aba in alvo:
        try:
            ws = sh.worksheet(aba)
        except Exception as e:  # noqa: BLE001
            logger.warning("Aba %s indisponível: %s", aba, e)
            continue
        rows = ws.get_all_records()
        path = out_dir / f"{aba}.json"
        path.write_text(
            json.dumps(rows, ensure_ascii=False, default=str, indent=2),
            encoding="utf-8",
        )
        logger.info("%s -> %s (%d linhas)", aba, path, len(rows))


if __name__ == "__main__":
    main()
