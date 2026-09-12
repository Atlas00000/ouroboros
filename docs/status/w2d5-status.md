# W2·D5 status note — 2026-09-12

## Done

- **Watchdog v1** (`server/app/watchdog/checker.py`): cadence refresh → `source_registry.status`, stale propagation onto derived tables (`states`/`profiles` for prices; `sentiment`/`insights` for news), structured log alerts (`ERROR` / `FEED STALE`).
- Weekend FX price silence is **not** alerted (`is_fx_weekend_closed`).
- **Kill-feed drill** (`kill_feed_drill.py`): simulates a silenced `finnhub.news` heartbeat without stopping MT5 backfill — **PASSED** locally.
- **Gap report** (`gap_report.py` + `ops/watchdog/run.py gap-report`): weekday M1 hole scan per active symbol.
- CLI + README: `ops/watchdog/`.

## Parallel / deferred

- Full-universe **2y MT5 backfill** still running (single IPC) — live poller and a real process-kill drill deferred until it finishes.
- Email/Telegram alerts wait for **W3·D4** (Resend). Watchdog logs only for now.

## How to re-verify

```powershell
cd server
py -3.12 ..\ops\watchdog\run.py check
py -3.12 ..\ops\watchdog\run.py kill-feed-drill
py -3.12 ..\ops\watchdog\run.py gap-report --symbols EURUSD,GBPUSD
```
