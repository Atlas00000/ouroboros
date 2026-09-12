# 24h feed soak (W3·D5)

Stabilization means every registered feed keeps heartbeating for a full day on staging/local with watchdog + optional notify.

## Baseline + hourly sample

```powershell
cd server

# One-shot health snapshot
py -3.12 ..\ops\soak\feed_status.py

# Append JSONL samples during the soak window (gitignored under data/)
py -3.12 ..\ops\soak\feed_status.py --json-out ..\data\soak\feed_status.jsonl
```

### Windows Task Scheduler (example)

Hourly for 24 hours:

```powershell
schtasks /Create /TN OuroborosFeedSoak /SC HOURLY /MO 1 /TR "py -3.12 C:\path\to\Ouroboros\ops\soak\feed_status.py --json-out C:\path\to\Ouroboros\data\soak\feed_status.jsonl"
```

Also keep workers cycling (separate tasks / terminals):

| Feed | Command | Cadence |
| --- | --- | --- |
| Prices | `ops\mt5-worker\poll.py` (after backfill finishes) | 60s loop |
| News | `ops\news-worker\poll.py` | ≤60s |
| Calendar | `ops\news-worker\poll_calendar.py` | ≤5m |
| Macro | `ops\macro-worker\poll.py` | daily |
| Watchdog | `ops\watchdog\run.py check --notify` | 1–5m |

## Pass criteria

- No unexplained `stale`/`error` on `mt5.prices`, `finnhub.news`, `finnhub.calendar`, `fred.macro` during market-relevant hours
- Weekend price silence alone is OK
- JSONL soak file covers ≥24h wall clock
- Feed-down drill documented in [docs/runbooks/feed-down.md](../../docs/runbooks/feed-down.md)

## After soak

Tag is cut at `v0.2-ingestion` when tooling + runbooks land; re-verify soak log before calling staging "green" for Phase 2.
