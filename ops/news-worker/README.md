# News worker (W3·D1)

Uses `NEWS_API_KEY` / `NEWS_PROVIDER` from `server/.env`.

```powershell
cd server
py -3.12 ..\ops\news-worker\poll.py
py -3.12 ..\ops\news-worker\poll.py --categories forex,general
```

Safe to re-run: articles are deduped by `finnhub:{id}` (+ per-symbol rows). Successful polls heartbeat `finnhub.news` on the source registry.

## Economic calendar (W3·D2)

```powershell
py -3.12 ..\ops\news-worker\poll_calendar.py
py -3.12 ..\ops\news-worker\poll_calendar.py --days-back 2 --days-forward 14
```

Stores rows in `news` with `is_calendar=true`, impact `high|medium|low`, and country→symbol fan-out. Heartbeats `finnhub.calendar`.

If Finnhub returns 401/403 (economic calendar often requires a paid plan), the poller falls back to the public Forex Factory weekly JSON feed.
