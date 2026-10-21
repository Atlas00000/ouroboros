# Local dossier parity (FX-quality planes)

Keep equities, energy, and regional indices at the same desk depth as FX majors: **price · profile · H1 state · mapped news · sentiment · insight**.

## Stack

| Process | Command | Role |
| --- | --- | --- |
| Compose | `docker-compose up -d` | Postgres/Timescale `:5433`, Redis `:6380` |
| API | `cd server && py -3.12 -m uvicorn app.main:app --reload --port 8000` | `/v1/*` |
| Client | `cd client && pnpm dev` | Desk UI `:3000` |
| Worker | `cd server && py -3.12 -m app.scheduler` | regime/fit/sentiment/narratives/profiles |
| News poll | `py -3.12 ops/news-worker/poll.py` | Finnhub market + equity company-news |
| MT5 prices | `py -3.12 ops/mt5-worker/poll.py --interval 60` | Live M1 (Windows + MT5) |

News and MT5 pollers stay **CLI processes** (not inside the API). Leave the worker running so `states` / sentiment stay current after expansion.

## One-shot catch-up (after adding symbols)

```powershell
cd server
# If H1/D1 empty for new symbols:
py -3.12 scripts/refresh_m15_h4_caggs.py

py -3.12 -m app.scheduler --once --jobs regime_log fit_log

cd ..
py -3.12 ops/news-worker/poll.py --categories forex,general,merger --company-equities --lookback-days 14

cd server
py -3.12 -m app.scheduler --once --jobs sentiment_refresh narratives_refresh
# Sentiment scores max 40 articles/tick — re-run until backlog clears:
py -3.12 -m app.scheduler --once --jobs sentiment_refresh

py -3.12 scripts/verify_dossier_parity.py
```

## Continuous

```powershell
# Terminal A — analytics worker
cd server
py -3.12 -m app.scheduler

# Terminal B — news (hourly is enough for research desk)
py -3.12 ops/news-worker/poll.py --company-equities --lookback-days 2

# Terminal C — MT5 live bars (optional if backfill is fresh)
py -3.12 ops/mt5-worker/poll.py --interval 60
```

## Acceptance

`server/scripts/verify_dossier_parity.py` checks the thin set (10 equities + WTI/Brent + DE40/UK100/JP225):

- H1 `states` row required  
- Equities: `news` count &gt; 0 (Finnhub company-news)  
- Energy/indices: group news total &gt; 0 (market keywords; some symbols may stay sparse)  
- Sentiment required when the symbol has news  

JP225 may stay news-empty when Finnhub general feed has no Nikkei headlines — state + insight still populate from regime.

## Related

- Universe expansion verify: `server/scripts/verify_universe_expansion.py`  
- Asset profile honesty: `docs/features/Asset profile.md`  
