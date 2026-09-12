# Ingestion HTTP helpers (W3·D3)

Shared module: `server/app/ingestion/httputil.py`

- `RateLimiter` — min-interval throttle (Finnhub / FRED / FF defaults)
- `request_with_retry` / `get_json` — retries on 408/429/5xx + network errors, honors `Retry-After`

Recorded fixtures live under `server/tests/fixtures/ingestion/` and are exercised by `tests/test_ingestion_fixtures.py` via `httpx.MockTransport` (no live network).
