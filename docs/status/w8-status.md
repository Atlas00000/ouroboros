# W8 status — scoring, staleness, load poll, observability (local)

**Date:** 2026-09-13  
**Scope:** W8·D1–D5 (local Docker)

## Delivered

### W8·D1 — Scoring
- `app/scoring/regime_accuracy.py` — score due `forecast_log` regime calls (realized re-classify at horizon)
- `app/scoring/weekly.py` — previous-UTC-week accuracy tables + Resend/log digest
- Migration `0010_scoring_weekly` → `scoring_weekly_reports`
- Scheduler: `score_regime_calls` (hourly), `weekly_scoring` (Mon 08:00 UTC)

### W8·D2 — Staleness → API
- `app/api/staleness.py` — feed map → `provenance.stale` on assets/metrics/news/state/profiles/sentiment/insights
- Scheduler: `watchdog_check` every `WATCHDOG_INTERVAL_MINUTES` with Resend notify on prolonged stale feeds

### W8·D3 — Local load
- `scripts/load_poll_local.py` — universe poll of `/v1/assets` + per-symbol state/metrics + `/metrics`
- Pool knobs: `DB_POOL_SIZE` / `DB_MAX_OVERFLOW`

### W8·D4 — Observability
- **`GET /metrics`** Prometheus text (not `/v1/metrics`) — HTTP latency, auth methods, ingestion lag, outbox depth, LLM spend/day
- ADR-018 documents the path split; ADR-015/016 already cover dual-auth + Resend catch-up
- Sentry release tagging already wired in `main` / worker (`ouroboros-server@` / `ouroboros-worker@`)

### W8·D5 — Freeze checklist (local)
Tag `v0.4-api` **when you sign off** (not auto-tagged). Before tag:

1. `alembic upgrade head`
2. `pytest tests/test_w8.py tests/test_api_w8.py tests/test_scheduler.py tests/test_intelligence_w7.py -q`
3. API + worker up; `load_poll_local.py` error rate &lt; 10%
4. Spot-check `/v1/health`, `/metrics`, auth on data routes
5. Confirm `ALERT_CHANNEL=log` or Resend keys for weekly/watchdog digests

## Tests / migrate

```powershell
cd server
py -3.12 -m alembic upgrade head
py -3.12 -m pytest tests/test_w8.py tests/test_api_w8.py tests/test_scheduler.py -q
# optional (API up + key):
py -3.12 scripts/load_poll_local.py --rounds 2
```

## Next

**Phase 4 / W9** — Next.js client hugging this API. Railway soak only after explicit sign-off.
