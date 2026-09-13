# W6 status — API routes + outbox → Redis Streams (local)

**Date:** 2026-09-13  
**Scope:** W6·D2–D5 (local Docker)

## Delivered

### W6·D2
- `GET /v1/state` — `state.v1` (persist on refresh; `regime.changed` outbox on flip)
- `GET /v1/metrics` — on-demand `metrics.v1` (+ provenance)
- `GET /v1/news` — cursor list + filters
- `GET /v1/ops/ping` — ops role stub (403 for viewer)
- `app/analytics/state_store.py`

### W6·D3
- `app/events/relay.py` — outbox → Redis Stream `ouroboros:events`
- Consumer group: `quant-platforms`
- Scheduler job `outbox_relay` every 30s
- `classify_and_log_regimes` also persists state + enqueues `regime.changed`

### W6·D4
- OpenAPI security schemes already on app (`bearerAuth` + `apiKeyAuth`)
- Integration tests cover both auth paths on new routes

### W6·D5
- `scripts/smoke_quant_consumer.py` — quant API key pull + stream subscribe/ack

## Tests / smoke

```powershell
cd server
py -3.12 -m pytest tests/test_api_w6d2.py tests/test_events_relay.py tests/test_scheduler.py -q
py -3.12 scripts/smoke_quant_consumer.py
```

## Next

**W7·D1** — multi-model `intelligence/llm_client.py` + daily budget.
