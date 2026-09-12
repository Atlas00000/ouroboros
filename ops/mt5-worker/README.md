# MT5 Windows worker

Runs on a Windows host with MetaTrader 5 installed (cannot run on Railway).

## Env

Uses `server/.env`:

- `MT5_PATH` — path to `terminal64.exe`
- `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` — account (server must match MT5 dropdown exactly)
- `MT5_BROKER` — optional label
- `DATABASE_URL` — Timescale target (local or Railway)

## Smoke connect

```powershell
cd server
python ..\ops\mt5-worker\smoke_connect.py
```

## Later (W2·D2+)

Backfill + live poller entrypoints will live here and call `app.ingestion.mt5.*`.
