"""Shared Phase 3 API test auth — one key so lifespan bootstrap cannot desync modules."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Force before Settings / app import in any test module that uses this fixture.
PHASE3_API_KEY = "test-epg-key-phase3"
PHASE3_JWT_SECRET = "phase3-test-secret-32bytes-min!!"

os.environ["CLERK_TEST_JWT_SECRET"] = PHASE3_JWT_SECRET
os.environ["OUROBOROS_API_KEY_EPG"] = PHASE3_API_KEY
os.environ["CLERK_JWKS_URL"] = ""
os.environ.setdefault("LLM_PROVIDERS", "mock")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("ALERT_CHANNEL", "log")


@pytest.fixture
def phase3_api_key() -> str:
    return PHASE3_API_KEY


@pytest.fixture
def phase3_client() -> TestClient:
    """TestClient with bootstrap key matching PHASE3_API_KEY."""
    from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
    from app.config import get_settings
    from app.db.session import get_session_factory
    from app.main import app

    get_settings.cache_clear()
    os.environ["OUROBOROS_API_KEY_EPG"] = PHASE3_API_KEY
    os.environ["CLERK_TEST_JWT_SECRET"] = PHASE3_JWT_SECRET
    os.environ["CLERK_JWKS_URL"] = ""

    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="epg",
                    service_name="epg",
                    raw_key=PHASE3_API_KEY,
                    role="viewer",
                )
            ],
        )
    finally:
        session.close()

    get_settings.cache_clear()
    with TestClient(app) as c:
        yield c
