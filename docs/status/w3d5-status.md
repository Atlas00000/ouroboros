# W3·D5 status — ingestion stabilization / `v0.2-ingestion`

**Date:** 2026-09-12  
**Tag:** `v0.2-ingestion`

## Delivered this day

- Feed-down runbook: `docs/runbooks/feed-down.md`
- Soak tooling: `ops/soak/feed_status.py` (+ README for 24h hourly sampling)
- Phase 1 ingestion stack complete through W3·D4 (MT5, news, calendar, FRED, watchdog, notifications)

## Soak protocol (ops)

True 24h wall-clock soak cannot finish inside a single coding session. Start:

```powershell
py -3.12 ops\soak\feed_status.py --json-out data\soak\feed_status.jsonl
```

Schedule hourly samples for 24h; keep news/calendar/macro polls and (after MT5 backfill) the live price poller running. See `ops/soak/README.md`.

## Known gaps / follow-ups

| Item | Notes |
| --- | --- |
| MT5 2y backfill | Still running through remaining universe symbols; EURUSD may need `--years 2` resume after early smoke-only window |
| USDCHF | Broker returned very thin history (~1.3k bars) — investigate ticker mapping if deeper history is required |
| Resend | Live send returned HTTP 403 until `EMAIL_FROM` domain is verified |
| Staging Railway | Walking skeleton from Phase 0; point workers at staging DB when soak moves off localhost |

## Pass for tag

Tag marks **ingestion feature-complete + operable** (runbooks, soak harness, registry/watchdog/notify). Staging 24h green is an ops checklist item tracked via `data/soak/feed_status.jsonl`, not a blocker for cutting `v0.2-ingestion`.
