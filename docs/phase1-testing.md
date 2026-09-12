# Phase 1 (Ingestion) test automation

## One command

```powershell
py -3.12 scripts\test_phase1.py
```

Offline / CI-friendly (no live Finnhub/FRED calls):

```powershell
py -3.12 scripts\test_phase1.py --skip-live
```

MT5 connect smoke (only when no backfill/poller is using IPC):

```powershell
py -3.12 scripts\test_phase1.py --with-mt5
```

## What it covers

| Step | Checks |
| --- | --- |
| structure | calendar, MT5/news/calendar/macro/watchdog/notifications, ops CLIs, runbooks |
| migrate | `alembic upgrade head` (incl. `macro_observations`) |
| pytest_phase1 | W2–W3 unit + fixture tests |
| live_news / calendar / macro | Real provider polls + registry heartbeats |
| feed_status | Soak snapshot of all sources + row counts |
| watchdog | Cadence check |
| notify_log | Shared notifier path (`--channel log`) |
| backup_targeted | Irreplaceable-table dump |
| mt5_smoke | Optional `smoke_connect.py` |

Live MT5 **poll/backfill** are intentionally not in this suite while a long backfill may hold the terminal IPC.
