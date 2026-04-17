"""Cliente DataJuri — reimplementa `ApiClient.js` em Python async.

Correções especiais (vide manual interno, não documentação oficial):
- Página inicial 0 (não 1)
- Dados na chave `rows` (não `data`/`content`)
- `removerHtml` como string `true`
- Basic Auth para obter token, depois Bearer nas chamadas
"""

from __future__ import annotations

import asyncio
import base64
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings


class DataJuriError(RuntimeError):
    pass


class DataJuriClient:
    """Cliente async com paginação e retry exponencial."""

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        secret: str | None = None,
        username: str | None = None,
        password: str | None = None,
        tenant: str | None = None,
        page_size: int | None = None,
    ) -> None:
        s = get_settings()
        self.base_url = (base_url or s.datajuri_base_url).rstrip("/")
        self.client_id = client_id or s.datajuri_client_id
        self.secret = secret or s.datajuri_secret
        self.username = username or s.datajuri_username
        self.password = password or s.datajuri_password
        self.tenant = tenant or s.datajuri_tenant
        self.page_size = page_size or s.datajuri_page_size
        self.token_endpoint = s.datajuri_token_endpoint
        self._token: str | None = None
        self._client = httpx.AsyncClient(timeout=60)

    async def __aenter__(self) -> DataJuriClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        # Basic Auth "client_id:secret" + grant_type=password (username/password)
        # Paridade com scripts/discovery.py do MCP DataJuri local.
        creds = f"{self.client_id}:{self.secret}".encode()
        auth = base64.b64encode(creds).decode()
        url = f"{self.base_url}{self.token_endpoint}"
        resp = await self._client.post(
            url,
            headers={"Authorization": f"Basic {auth}"},
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            },
        )
        if resp.status_code != 200:
            raise DataJuriError(f"Falha ao obter token: {resp.status_code} {resp.text[:200]}")
        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise DataJuriError(f"Token ausente no payload: {payload}")
        self._token = token
        return token

    def _clear_token(self) -> None:
        self._token = None

    async def fetch_page(
        self, modulo: str, campos: str, page: int = 0, criterio: str | None = None
    ) -> dict[str, Any]:
        url = (
            f"{self.base_url}/v1/entidades/{modulo}"
            f"?campos={httpx.QueryParams({'_': campos})['_']}"
            f"&page={page}&pageSize={self.page_size}&removerHtml=true"
        )
        if criterio:
            url += f"&criterio={httpx.QueryParams({'_': criterio})['_']}"

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=8),
            retry=retry_if_exception_type((httpx.HTTPError, DataJuriError)),
            reraise=True,
        ):
            with attempt:
                token = await self._get_token()
                resp = await self._client.get(
                    url, headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code == 401:
                    self._clear_token()
                    raise DataJuriError("401 — token expirado, retentando")
                if resp.status_code != 200:
                    raise DataJuriError(
                        f"HTTP {resp.status_code}: {resp.text[:200]}"
                    )
                return resp.json()
        raise DataJuriError("Retry exausto")  # pragma: no cover

    async def fetch_all(
        self, modulo: str, campos: str, criterio: str | None = None
    ) -> list[dict[str, Any]]:
        page = 0
        rows: list[dict[str, Any]] = []
        while True:
            payload = await self.fetch_page(modulo, campos, page, criterio)
            batch = payload.get("rows", []) or []
            rows.extend(batch)
            if len(batch) < self.page_size:
                break
            page += 1
            await asyncio.sleep(0.5)
        return rows


def nested_value(obj: dict[str, Any], path: str) -> Any:
    """Acessa `a.b.c` dentro de um dict JSON aninhado — paridade com `getNestedValue`."""
    value: Any = obj
    for part in path.split("."):
        if value is None:
            return ""
        value = value.get(part) if isinstance(value, dict) else None
    return value if value is not None else ""
