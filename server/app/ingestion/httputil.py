"""Shared HTTP rate-limit + retry/backoff for ingestion providers."""

from __future__ import annotations

import logging
import random
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

DEFAULT_RETRY_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
DEFAULT_RETRY_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.RemoteProtocolError,
)


@dataclass
class RateLimiter:
    """
    Simple minimum-interval limiter (per-process, thread-safe).

    `min_interval_seconds=0.2` ≈ 5 QPS ceiling for a single limiter instance.
    """

    min_interval_seconds: float = 0.2
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _last_at: float = field(default=0.0, repr=False)

    def wait(self) -> None:
        if self.min_interval_seconds <= 0:
            return
        with self._lock:
            now = time.monotonic()
            delay = self.min_interval_seconds - (now - self._last_at)
            if delay > 0:
                time.sleep(delay)
            self._last_at = time.monotonic()


# Process-wide defaults for provider families.
FINNHUB_LIMITER = RateLimiter(min_interval_seconds=0.25)
FRED_LIMITER = RateLimiter(min_interval_seconds=0.5)
FF_LIMITER = RateLimiter(min_interval_seconds=0.5)


def _retry_after_seconds(response: httpx.Response, attempt: int, backoff_base: float) -> float:
    header = response.headers.get("Retry-After")
    if header:
        try:
            return max(0.0, float(header))
        except ValueError:
            pass
    # Exponential backoff with light jitter.
    return backoff_base * (2**attempt) + random.uniform(0, backoff_base * 0.25)


def request_with_retry(
    method: str,
    url: str,
    *,
    timeout: float = 30.0,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    retries: int = 3,
    backoff_base: float = 0.4,
    retry_statuses: frozenset[int] = DEFAULT_RETRY_STATUSES,
    rate_limiter: RateLimiter | None = None,
    transport: httpx.BaseTransport | None = None,
    client: httpx.Client | None = None,
) -> httpx.Response:
    """
    Perform an HTTP request with rate limiting and retries.

    Retries on transient network errors and selected HTTP statuses.
    Non-retryable 4xx responses are raised immediately via raise_for_status.
    """
    owns_client = client is None
    http = client or httpx.Client(timeout=timeout, transport=transport)
    attempt = 0
    try:
        while True:
            if rate_limiter is not None:
                rate_limiter.wait()
            try:
                response = http.request(method, url, headers=headers, params=params)
            except DEFAULT_RETRY_EXCEPTIONS as exc:
                if attempt >= retries:
                    raise
                sleep_for = backoff_base * (2**attempt) + random.uniform(0, 0.1)
                logger.warning(
                    "http retry network attempt=%s/%s url=%s err=%s sleep=%.2fs",
                    attempt + 1,
                    retries,
                    url,
                    type(exc).__name__,
                    sleep_for,
                )
                time.sleep(sleep_for)
                attempt += 1
                continue

            if response.status_code in retry_statuses and attempt < retries:
                sleep_for = _retry_after_seconds(response, attempt, backoff_base)
                logger.warning(
                    "http retry status attempt=%s/%s url=%s status=%s sleep=%.2fs",
                    attempt + 1,
                    retries,
                    url,
                    response.status_code,
                    sleep_for,
                )
                time.sleep(sleep_for)
                attempt += 1
                continue

            response.raise_for_status()
            return response
    finally:
        if owns_client:
            http.close()


def get_json(
    url: str,
    *,
    timeout: float = 30.0,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    retries: int = 3,
    backoff_base: float = 0.4,
    rate_limiter: RateLimiter | None = None,
    transport: httpx.BaseTransport | None = None,
    client: httpx.Client | None = None,
) -> Any:
    """GET + JSON decode with shared retry/rate-limit policy."""
    response = request_with_retry(
        "GET",
        url,
        timeout=timeout,
        headers=headers,
        params=params,
        retries=retries,
        backoff_base=backoff_base,
        rate_limiter=rate_limiter,
        transport=transport,
        client=client,
    )
    return response.json()
