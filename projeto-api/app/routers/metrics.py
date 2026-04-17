"""Prometheus metrics endpoint + instrumentação de latência por rota."""

from __future__ import annotations

import time

from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

router = APIRouter(tags=["metrics"])


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5, 10),
)

ETL_ATIVIDADES_COLETADAS = Counter(
    "etl_atividades_coletadas_total",
    "Atividades coletadas do DataJuri pelo ETL",
)

ETL_RUN_DURATION = Histogram(
    "etl_run_duration_seconds",
    "Duração de uma execução ETL completa",
    buckets=(5, 15, 30, 60, 120, 300, 600, 900, 1800),
)


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def record_metrics(request: Request, call_next):
    """Middleware que mede latência e conta requests."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    path_label = request.url.path if request.url.path.startswith("/api") else "/other"
    REQUEST_COUNT.labels(
        method=request.method, path=path_label, status=str(response.status_code)
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, path=path_label).observe(elapsed)
    return response
