# W5·D4 status — analytics worker (`python -m app.scheduler`)

**Date:** 2026-09-12  
**Entrypoint:** `python -m app.scheduler`

## Delivered

- `app/scheduler.py` — APScheduler (UTC) BlockingScheduler
  | Job | Cadence |
  | --- | --- |
  | `metrics_cadence` | every 15m (H1/H4/D1 snapshots) |
  | `regime_log` | every 15m → `forecast_log` |
  | `profile_events` | every 15m (regime/calendar triggers) |
  | `daily_profiles` | cron **00:15 UTC** (force refresh all active) |
  | `prune_profiles` | cron 00:45 UTC (180d → last-of-day) |
- `--once [--jobs …]` pipeline dry-run
- Compose: `--profile worker` service (`ouroboros-worker`)
- Docker: monorepo-root build context; installs `packages/contracts`
- Railway: `server/railway.toml` (API) + `server/railway.worker.toml` (worker)
- Docs: `ops/railway/STAGING.md` updated
- Dep: `apscheduler>=3.10`
- Tests: `tests/test_scheduler.py`

## Local

```powershell
# native dry-run (uses local Docker DB)
cd server
py -3.12 -m pip install "apscheduler>=3.10"
py -3.12 -m app.scheduler --once --jobs regime_log prune_profiles

# compose worker
docker-compose --profile worker up -d --build
```

## Railway

Second service, same Dockerfile, start command `python -m app.scheduler`.  
Root Directory = **repo root** (contracts in build context).

## Next

**W5·D5** — done; see `docs/status/w5d5-status.md` + ADR-017. Phase 2 analytics complete pending `v0.3-analytics` tag after commit.
