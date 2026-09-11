"""Sentry initialization (no-op when DSN is empty)."""

from __future__ import annotations

import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

logger = logging.getLogger(__name__)


def init_sentry(*, dsn: str | None, environment: str, release: str | None = None) -> None:
    if not dsn:
        logger.info("sentry_disabled", extra={"reason": "no_dsn"})
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=0.1 if environment != "local" else 0.0,
        send_default_pii=False,
    )
    logger.info("sentry_initialized", extra={"environment": environment})
