# Watchdog (W2·D5)

```powershell
cd server

# Cadence check → registry status → stale flags → log alerts
py -3.12 ..\ops\watchdog\run.py check

# Simulated kill-feed (does not stop MT5 backfill)
py -3.12 ..\ops\watchdog\run.py kill-feed-drill --source finnhub.news

# M1 integrity gaps (weekday holes only)
py -3.12 ..\ops\watchdog\run.py gap-report
py -3.12 ..\ops\watchdog\run.py gap-report --symbols EURUSD,GBPUSD
```

Exit code `1` from `check` means at least one alert fired (or use in CI with care on weekends for price feeds — weekend price silence is suppressed).
