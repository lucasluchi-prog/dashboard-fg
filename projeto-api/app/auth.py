"""OAuth Google restrito ao domínio configurado."""

from __future__ import annotations

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status

from app.config import get_settings


def build_oauth() -> OAuth:
    settings = get_settings()
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


def validate_google_user(userinfo: dict[str, Any]) -> dict[str, Any]:
    """Valida que o user pertence ao domínio permitido e devolve payload de sessão."""
    settings = get_settings()
    email = str(userinfo.get("email", ""))
    hd = str(userinfo.get("hd", ""))

    if settings.allowed_domain and hd != settings.allowed_domain and not email.endswith(
        f"@{settings.allowed_domain}"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso restrito ao domínio @{settings.allowed_domain}",
        )

    return {
        "email": email,
        "name": userinfo.get("name", ""),
        "picture": userinfo.get("picture", ""),
        "hd": hd,
    }


def current_user(request: Request) -> dict[str, Any]:
    """Dependência FastAPI — exige sessão válida."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
        )
    return user
