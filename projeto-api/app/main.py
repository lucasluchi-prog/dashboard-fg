"""Aplicação FastAPI — factory + middlewares + routers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.logging_config import configure_logging, get_logger
from app.routers import (
    admin,
    aproveitamento,
    auth,
    dashboard,
    health,
    metrics,
    produtividade,
    ranking,
)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    logger = get_logger("dashboard-fg")

    app = FastAPI(
        title="Dashboard FG",
        version="0.1.0",
        description="Backend do Dashboard de Produtividade — Furtado Guerini Advocacia",
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        https_only=settings.is_prod,
        same_site="lax",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(metrics.record_metrics)

    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(produtividade.router)
    app.include_router(ranking.router)
    app.include_router(aproveitamento.router)
    app.include_router(admin.router)

    logger.info("dashboard_fg_started", env=settings.env)
    return app


app = create_app()
