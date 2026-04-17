"""Configurações da aplicação via pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://dashboard:dashboard@localhost:5433/dashboard_fg"
    database_url_sync: str = (
        "postgresql+psycopg2://dashboard:dashboard@localhost:5433/dashboard_fg"
    )

    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = "http://localhost:8080/auth/callback"
    allowed_domain: str = "furtadoguerini.com.br"
    session_secret: str = Field(
        default="dev-secret-change-me-at-least-32-chars-long-please",
        min_length=32,
    )

    datajuri_base_url: str = "https://api.datajuri.com.br"
    datajuri_tenant: str = "furtadoguerini"
    datajuri_user: str = ""
    datajuri_password: str = ""
    datajuri_token_endpoint: str = "/oauth/token"
    datajuri_page_size: int = 1000
    datajuri_data_inicio: str = "2025-09-01"

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
