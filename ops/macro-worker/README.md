# Macro worker (W3·D2)

Uses `FRED_API_KEY` and optional `FRED_SERIES` from `server/.env`.

```powershell
cd server
py -3.12 ..\ops\macro-worker\poll.py
py -3.12 ..\ops\macro-worker\poll.py --series DFF,UNRATE --lookback-days 365
```

Default series: `DFF,T10Y2Y,DTWEXBGS,CPIAUCSL,UNRATE,GDP`.
Heartbeats `fred.macro` on success.
