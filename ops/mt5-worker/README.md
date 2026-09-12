# MT5 Windows worker

Runs on a Windows host with MetaTrader 5 installed (cannot run on Railway).

## Env

Uses `server/.env`:

- `MT5_PATH` — path to `terminal64.exe`
- `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` — account (server must match MT5 dropdown exactly)
- `MT5_BROKER` — optional label
- `DATABASE_URL` — Timescale target (local or Railway)

## Smoke connect

1. Leave MetaTrader 5 running and logged in (or let the script restart it).
2. From `server/`:

```powershell
py -3.12 ..\ops\mt5-worker\smoke_connect.py
```

Expected: `OK connected ... server='YWO-Trade'`.

If you see `IPC timeout (-10005)`, fully restart MT5 (close all `terminal64` processes, open again, wait ~30–45s), then retry.

## Historical backfill (W2·D2)

```powershell
# Short smoke (7 days ≈ 0.02 years) for one symbol
py -3.12 ..\ops\mt5-worker\backfill.py --symbols EURUSD --years 0.02

# Resume-safe 2y backfill for full universe (long-running)
py -3.12 ..\ops\mt5-worker\backfill.py --years 2
```

Re-running is safe: continues from each symbol's latest `prices.ts`.
