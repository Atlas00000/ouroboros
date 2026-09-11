"""FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import health as health_router
from app.config import get_settings
from app.observability.logging import configure_logging
from app.observability.sentry import init_sentry


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    init_sentry(
        dsn=settings.sentry_dsn_server,
        environment=settings.app_env,
        release=f"ouroboros-server@{__version__}",
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Ouroboros API",
        version=__version__,
        description="Asset-intelligence API — research only, no trade execution.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router.router, prefix="/v1")
    return application


app = create_app()
