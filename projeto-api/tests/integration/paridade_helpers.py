"""Helpers para teste de paridade — leitura da planilha Sheets via gspread (opt-in)."""

from __future__ import annotations

import os
from typing import Any

SPREADSHEET_ID = os.environ.get(
    "SHEETS_SPREADSHEET_ID", "1fe6yHUub8hm8zdLIlm0KxVUiyRXzaU-ANcoSv07JT4E"
)


def get_gspread_client():  # pragma: no cover - ambiente externo
    """Retorna cliente gspread autenticado via service account.

    Requer env `SHEETS_SERVICE_ACCOUNT` apontando para JSON de credenciais
    ou `GOOGLE_APPLICATION_CREDENTIALS`.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as e:
        raise RuntimeError(
            "Instale: pip install '.[paridade]' (gspread + google-auth)."
        ) from e

    path = os.environ.get("SHEETS_SERVICE_ACCOUNT") or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if not path or not os.path.exists(path):
        raise FileNotFoundError(
            "SHEETS_SERVICE_ACCOUNT não encontrada. Aponte para credentials.json."
        )
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(path, scopes=scopes)
    return gspread.authorize(creds)


def read_sheet(aba: str) -> list[dict[str, Any]]:  # pragma: no cover
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(aba)
    return [dict(row) for row in ws.get_all_records()]


def read_atividades_raw() -> list[dict[str, Any]]:  # pragma: no cover
    """Atividades_Raw — shape já é o que os services Python consomem."""
    return read_sheet("Atividades_Raw")


def comparar(
    esperado: list[dict[str, Any]],
    atual: list[dict[str, Any]],
    *,
    chaves: list[str],
    numericos: list[str],
    tol_int: int = 0,
    tol_float: float = 0.01,
) -> list[dict[str, Any]]:
    """Compara duas listas de dicts. Retorna divergências como lista."""
    def _chave(r: dict[str, Any]) -> tuple:
        return tuple(str(r.get(k, "")).strip() for k in chaves)

    esp_por_chave = {_chave(r): r for r in esperado}
    atual_por_chave = {_chave(r): r for r in atual}

    divergencias: list[dict[str, Any]] = []
    # Faltantes / extras
    for k in esp_por_chave.keys() - atual_por_chave.keys():
        divergencias.append({"chave": k, "motivo": "faltante_python", "esperado": esp_por_chave[k]})
    for k in atual_por_chave.keys() - esp_por_chave.keys():
        divergencias.append({"chave": k, "motivo": "extra_python", "atual": atual_por_chave[k]})

    # Comuns
    for k in esp_por_chave.keys() & atual_por_chave.keys():
        e = esp_por_chave[k]
        a = atual_por_chave[k]
        for campo in numericos:
            ve = e.get(campo)
            va = a.get(campo)
            try:
                ve_f = float(ve) if ve not in (None, "", "N/A") else 0.0
                va_f = float(va) if va not in (None, "", "N/A") else 0.0
            except (TypeError, ValueError):
                continue
            delta = abs(ve_f - va_f)
            tol = tol_int if float(ve_f).is_integer() and float(va_f).is_integer() else tol_float
            if delta > tol:
                divergencias.append({
                    "chave": k,
                    "campo": campo,
                    "esperado": ve_f,
                    "atual": va_f,
                    "delta": delta,
                })
    return divergencias
