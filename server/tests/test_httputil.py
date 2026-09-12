"""Unit tests for shared rate-limit / retry helper."""

from __future__ import annotations

import json
from unittest.mock import patch

import httpx
import pytest

from app.ingestion.httputil import RateLimiter, get_json, request_with_retry


def test_rate_limiter_enforces_interval() -> None:
    limiter = RateLimiter(min_interval_seconds=0.05)
    with patch("app.ingestion.httputil.time.sleep") as sleep:
        # wait1: now=0.0 → sleep 0.05 → last=0.0
        # wait2: now=0.01 → sleep 0.04 → last=0.05
        with patch(
            "app.ingestion.httputil.time.monotonic",
            side_effect=[0.0, 0.0, 0.01, 0.05],
        ):
            limiter.wait()
            limiter.wait()
        assert sleep.call_count == 2
        assert sleep.call_args_list[0].args[0] == pytest.approx(0.05)
        assert sleep.call_args_list[1].args[0] == pytest.approx(0.04)



def test_request_retries_on_429_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    transport = httpx.MockTransport(handler)
    with patch("app.ingestion.httputil.time.sleep"):
        resp = request_with_retry(
            "GET",
            "https://example.test/x",
            transport=transport,
            retries=2,
            backoff_base=0.01,
            rate_limiter=None,
        )
    assert resp.status_code == 200
    assert calls["n"] == 2


def test_get_json_raises_on_non_retryable_4xx() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": "forbidden"}, request=request)

    with pytest.raises(httpx.HTTPStatusError):
        get_json("https://example.test/forbidden", transport=httpx.MockTransport(handler), retries=1)


def test_get_json_parses_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=json.dumps([1, 2, 3]), request=request)

    data = get_json("https://example.test/list", transport=httpx.MockTransport(handler))
    assert data == [1, 2, 3]
