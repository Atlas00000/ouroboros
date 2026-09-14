# W10 status — Asset detail panels (local)

**Date:** 2026-09-14  
**Scope:** W10·D1–D5  
**Verified:** live smoke against restarted Docker + uvicorn

## Delivered

### API
- `GET /v1/bars?symbol=&timeframe=&lookback_days=` — OHLCV for charts (`bars.v1`)
- Staleness map includes `"bars"` → `mt5.prices`

### Client (baseline §3 section order)
- Sticky symbol chrome on `/assets/[symbol]`
- `PriceChart` + `RegimeBands` (SVG close series; tint by current regime — Lightweight Charts deferred)
- `ProfileCard` · `CorrelationHeatmap` · `StatePanel`
- `SentimentTrend` (+ `SentimentGauge`) · `DriverHeadlines`
- `InsightFeed` (narrative label + disclaimer)
- Stale badges across panels; honesty footers (`model_version`, `as_of`)

## Live smoke (2026-09-14)

Infra: `docker-compose up -d postgres redis` (containers recreated; volumes preserved)  
API: uvicorn on `127.0.0.1:8000` with process-env bootstrap keys (not written to `.env`)

| Endpoint | Result |
|----------|--------|
| `GET /v1/health` | ok |
| `GET /v1/assets` | 200 · 15 symbols |
| `GET /v1/bars?symbol=EURUSD&timeframe=H1` | 200 · 480 bars · stale=true (poller idle) |
| `GET /v1/state?symbol=EURUSD&timeframe=H1` | 200 · ranging |
| `GET /v1/assets/EURUSD/profile` | 200 |
| `GET /v1/metrics?symbol=EURUSD` | 200 |
| `GET /v1/news?limit=5` | 200 · 5 items |
| `GET /v1/insights?symbol=EURUSD` | 200 |
| `GET /v1/sentiment?symbol=EURUSD` | 404 (empty window — expected when feed quiet) |

Unit: `tests/test_w8.py` + `tests/test_api_w7.py` → 13 passed.

## Client SSR note

`OUROBOROS_SERVER_API_KEY` must match a bootstrapped server key (`OUROBOROS_API_KEY_CLIENT` or EPG) in `client/.env.local` for Next SSR. Keys were not persisted to disk this session — set locally before `pnpm dev` if the detail page shows empty panels.

## Next

**W11** — System, Scoring, Admin keys + RoleGate; tag `v0.5-client`.
