# Runbook: Feed down

**Owner:** platform / on-call  
**Related:** W2·D5 watchdog, W3·D4 notifications, source registry  
**Goal:** Detect a silent/stale feed within ~2× cadence, restore data flow, clear stale flags.

## Symptoms

- `ops/registry_status.py` shows `status=stale` or `error`
- Watchdog logs `FEED STALE source_id=...`
- Optional: email/Telegram/webhook via `ALERT_CHANNEL` (`check --notify`)
- Downstream rows may have `stale=true` (states/profiles/sentiment/insights)

## Quick triage

```powershell
cd server
py -3.12 ..\ops\registry_status.py
py -3.12 ..\ops\watchdog\run.py check
py -3.12 ..\ops\soak\feed_status.py
```

| `source_id` | Expected cadence | Typical failure | First action |
| --- | --- | --- | --- |
| `mt5.prices` | 60s | MT5 IPC down, terminal closed, Windows worker stopped | Restart `terminal64`, wait 30–45s, `smoke_connect.py`, then `poll.py --once` |
| `finnhub.news` | 60s | API key / rate limit / network | `poll.py` news worker; check `NEWS_API_KEY` |
| `finnhub.calendar` | 300s | Finnhub 403 (plan) — FF fallback should still work | `poll_calendar.py`; if FF URL blocked, check network |
| `fred.macro` | 86400s | Bad `FRED_API_KEY` or FRED outage | `macro-worker\poll.py`; verify key |

Weekend FX price silence is **expected** — watchdog suppresses `mt5.prices` alerts when `is_fx_weekend_closed`.

## Recovery steps

### 1. MT5 prices

1. Confirm MetaTrader 5 is logged in (Algo Trading on).
2. `py -3.12 ops\mt5-worker\smoke_connect.py`
3. If IPC timeout: kill all `terminal64`, reopen, wait ~45s, retry.
4. Catch-up: `py -3.12 ops\mt5-worker\poll.py --once` (or resume backfill).
5. Confirm `mt5.prices` heartbeat advances in `registry_status.py`.

**Do not** run backfill and live poller at the same time (single MT5 IPC).

### 2. News

```powershell
py -3.12 ops\news-worker\poll.py
```

Idempotent; heartbeats `finnhub.news` on success.

### 3. Economic calendar

```powershell
py -3.12 ops\news-worker\poll_calendar.py
```

Finnhub paid calendar → automatic Forex Factory weekly JSON fallback.

### 4. FRED macro

```powershell
py -3.12 ops\macro-worker\poll.py
```

Daily cadence; safe to re-run (upsert).

### 5. Clear derived stale flags (after feed is healthy)

Once the source is `ok` again, either wait for the next analytics refresh or:

```sql
UPDATE states SET stale = false WHERE stale = true;
UPDATE profiles SET stale = false WHERE stale = true;
UPDATE sentiment SET stale = false WHERE stale = true;
UPDATE insights SET stale = false WHERE stale = true;
```

(Prefer letting the next successful compute job clear these once Phase 2 is live.)

## Notify humans

```powershell
py -3.12 ops\watchdog\run.py check --notify
py -3.12 ops\notifications\send_test.py   # path check only
```

If Resend returns **403**, verify the sending domain for `EMAIL_FROM` in the Resend dashboard (code path is fine; domain auth is not).

## Escalation

1. Capture `registry_status` + last 50 log lines from the failing worker.
2. Note last good `last_seen_at` and RPO impact (prices re-backfillable ≤24h; news/calendar/macro less so).
3. If DB restore needed → [restore-from-backup.md](./restore-from-backup.md).
