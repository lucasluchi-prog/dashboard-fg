"""Entry point do Cloud Run Job ETL.

Uso:
    python -m app.etl                  # pipeline completo
    python -m app.etl --incremental    # apenas últimos N dias
    python -m app.etl --dry-run        # sem gravar
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from app.etl.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incremental", action="store_true", help="Coleta incremental")
    parser.add_argument("--dry-run", action="store_true", help="Não grava no banco")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(run_pipeline(incremental=args.incremental, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
