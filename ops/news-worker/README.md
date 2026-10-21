# News worker (W3·D1 + dossier parity)

Uses `NEWS_API_KEY` / `NEWS_PROVIDER` from `server/.env`.

## Market news (`/news`)

```powershell
cd server
py -3.12 ..\ops\news-worker\poll.py
py -3.12 ..\ops\news-worker\poll.py --categories forex,general,merger
```

Default categories: `forex,general,merger`.

## Equity company-news (`/company-news`)

On by default for all active `asset_class=equity` symbols (14d lookback):

```powershell
py -3.12 ..\ops\news-worker\poll.py --company-equities --lookback-days 14
py -3.12 ..\ops\news-worker\poll.py --company-equities --symbols AAPL,MSFT --lookback-days 7
# market only:
py -3.12 ..\ops\news-worker\poll.py --no-company-equities --categories general,merger
```

Company-news rows are force-mapped to the polled ticker. Safe to re-run: dedupe on `finnhub:{id}` (+ per-symbol rows). Successful polls heartbeat `finnhub.news`.

## Economic calendar (W3·D2)

```powershell
py -3.12 ..\ops\news-worker\poll_calendar.py
py -3.12 ..\ops\news-worker\poll_calendar.py --days-back 2 --days-forward 14
```

Stores rows in `news` with `is_calendar=true`, impact `high|medium|low`, and country→symbol fan-out. Heartbeats `finnhub.calendar`.

If Finnhub returns 401/403 (economic calendar often requires a paid plan), the poller falls back to the public Forex Factory weekly JSON feed.

## Parity runbook

See [`docs/runbooks/local-dossier-parity.md`](../../docs/runbooks/local-dossier-parity.md).
