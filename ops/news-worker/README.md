# News worker (W3·D1)

Uses `NEWS_API_KEY` / `NEWS_PROVIDER` from `server/.env`.

```powershell
cd server
py -3.12 ..\ops\news-worker\poll.py
py -3.12 ..\ops\news-worker\poll.py --categories forex,general
```

Safe to re-run: articles are deduped by `finnhub:{id}` (+ per-symbol rows). Successful polls heartbeat `finnhub.news` on the source registry.
