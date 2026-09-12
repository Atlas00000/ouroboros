# Runbook: Restore from backup

**Owner:** platform / on-call  
**Related:** N9 (RPO/RTO), W2·D4 restore drill  
**Last drilled:** see git history for `ops/backups/restore_drill.py` runs

## Objectives

| Class | Tables | RPO | Recovery path |
| --- | --- | --- | --- |
| Prices | `prices` (+ aggregates) | <= 24h | Restore full dump **or** re-backfill from MT5 |
| Irreplaceable | `sentiment`, `forecast_log`, `outbox`, `profiles`, `insights`, `news`, `states`, `assets`, `source_registry` | <= 1h | Hourly targeted dump → `pg_restore` |

**RTO target:** <= 4 hours to accept traffic again (restore + migrate check + resume API/worker/MT5).

## Prerequisites

- Docker with `ouroboros-postgres` healthy (`docker compose up -d postgres`)
- Latest dumps under `data/backups/full/` and/or `data/backups/targeted/`
- MT5 worker available if prices must be re-backfilled instead of restored

## A. Scratch restore drill (safe)

Does **not** touch the live `ouroboros` database.

```powershell
py -3.12 ops\backups\backup_full.py
py -3.12 ops\backups\restore_drill.py
```

Expect: `restore drill PASSED` and seeded `assets` / `source_registry` counts >= 1.

Note: Timescale may log benign `ALTER TABLE ONLY ... hypertable` errors during `pg_restore`; the drill verifies row counts afterward. The script calls `timescaledb_pre_restore()` / `timescaledb_post_restore()`.

## B. Live database restore (incident)

1. **Stop writers** — API (if writing), worker, MT5 poller/backfill. Freeze schema changes.
2. **Snapshot current volume** if the host allows (Railway volume snapshot / `docker commit` emergency only).
3. **Restore full dump** into a new DB name first when possible; cut over via rename or `DATABASE_URL` flip.
4. Or restore in place (destructive):

```powershell
# Example: recreate DB then restore (DOWNTIME)
docker exec ouroboros-postgres psql -U ouroboros -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='ouroboros' AND pid <> pg_backend_pid();"
docker exec ouroboros-postgres psql -U ouroboros -d postgres -c "DROP DATABASE ouroboros;"
docker exec ouroboros-postgres psql -U ouroboros -d postgres -c "CREATE DATABASE ouroboros;"
docker exec ouroboros-postgres psql -U ouroboros -d ouroboros -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
# copy dump in and pg_restore — prefer ops/backups/restore_drill.py patterns
```

5. Prefer `ops/backups/common.py` helpers (`pg_restore_custom`) over ad-hoc flags.
6. `cd server && alembic current` — confirm head; run `alembic upgrade head` only if dump pre-dates a migration.
7. If prices are older than acceptable:  
   `py -3.12 ops\mt5-worker\backfill.py --years 2` (resumable).
8. If only irreplaceable tables were lost: restore the latest `data/backups/targeted/*.dump` with `pg_restore -t …` / full targeted file.
9. Resume services; confirm `source_registry.last_seen_at` advances (MT5 poller / news later).
10. Write incident note: dump used, RPO realized, RTO clock start/end.

## C. Verification checklist

- [ ] `SELECT count(*) FROM assets;` matches expected universe (~15)
- [ ] `SELECT count(*) FROM source_registry;` ≥ 4
- [ ] `SELECT max(ts) FROM prices;` within RPO or backfill started
- [ ] Health: `GET /v1/health` OK
- [ ] No silent stale feeds (W2·D5 watchdog once live)

## Assumptions (document in incidents)

- **Prices are disposable relative to MT5 history** — full re-backfill is acceptable within 24h RPO.
- **Outbox / sentiment / profiles are not** — hourly targeted dumps are mandatory before staging holds real derived data.
