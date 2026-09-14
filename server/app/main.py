"""FastAPI entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app import __version__
from app.api.errors import register_exception_handlers
from app.api.v1 import admin_keys as admin_keys_router
from app.api.v1 import assets as assets_router
from app.api.v1 import bars as bars_router
from app.api.v1 import health as health_router
from app.api.v1 import insights as insights_router
from app.api.v1 import metrics as metrics_router
from app.api.v1 import news as news_router
from app.api.v1 import ops as ops_router
from app.api.v1 import profiles as profiles_router
from app.api.v1 import scoring as scoring_router
from app.api.v1 import sentiment as sentiment_router
from app.api.v1 import states as states_router
from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.auth.roles import Role
from app.config import get_settings
from app.db.session import get_session_factory
from app.observability.logging import configure_logging
from app.observability.metrics_http import mount_metrics
from app.observability.sentry import init_sentry

logger = logging.getLogger(__name__)

# Local SSR / admin UI uses the client bootstrap key at admin+.
_BOOTSTRAP_ROLES: dict[str, Role] = {
    "client": "admin",
    "epg": "viewer",
    "quant": "viewer",
}


def _bootstrap_keys() -> None:
    settings = get_settings()
    triples = settings.bootstrap_api_keys()
    if not triples:
        return
    session = get_session_factory()()
    try:
        keys = [
            BootstrapKey(
                name=n,
                service_name=s,
                raw_key=k,
                role=_BOOTSTRAP_ROLES.get(n, "viewer"),
            )
            for n, s, k in triples
        ]
        n = upsert_bootstrap_keys(session, keys)
        logger.info("api_key_bootstrap upserted=%s", n)
    except Exception:
        logger.exception("api_key_bootstrap_failed")
        session.rollback()
    finally:
        session.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    init_sentry(
        dsn=settings.sentry_dsn_server,
        environment=settings.app_env,
        release=f"ouroboros-server@{__version__}",
    )
    _bootstrap_keys()
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
    register_exception_handlers(application)
    mount_metrics(application)
    application.include_router(health_router.router, prefix="/v1")
    application.include_router(assets_router.router, prefix="/v1")
    application.include_router(profiles_router.router, prefix="/v1")
    application.include_router(states_router.router, prefix="/v1")
    application.include_router(metrics_router.router, prefix="/v1")
    application.include_router(bars_router.router, prefix="/v1")
    application.include_router(sentiment_router.router, prefix="/v1")
    application.include_router(insights_router.router, prefix="/v1")
    application.include_router(news_router.router, prefix="/v1")
    application.include_router(scoring_router.router, prefix="/v1")
    application.include_router(ops_router.router, prefix="/v1")
    application.include_router(admin_keys_router.router, prefix="/v1")

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema
        schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(
            {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Clerk session JWT",
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Hashed machine API key",
                },
            }
        )
        application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi  # type: ignore[method-assign]
    return application


app = create_app()
