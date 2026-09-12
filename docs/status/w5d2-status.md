# W5·D2 status — event-triggered profile refresh + retention

**Date:** 2026-09-12  
**Models:** `profiles.v1` · outbox `profile.updated`

## Delivered

- **Persist + versioning** — `app/analytics/profile_store.py`
  - Monotonic `profile_version` per symbol → `profiles` table
  - Optional transactional `profile.updated` outbox enqueue
  - Debounce helper: ≤1 refresh / hour / symbol
- **Event triggers** — `app/analytics/profile_refresh.py`
  - `regime.changed` on confirmed H4/D1 last-bar flip
  - High-impact calendar (`news.is_calendar` + `impact=high`) in ± window
  - `run_event_triggered_refresh` orchestration
- **Retention** — migration `0006_profile_retention`
  - Index `ix_profiles_symbol_created`
  - SQL `prune_profiles_retention(180)` — full history 180d, then last-of-day
  - ORM fallback + pure `ids_to_prune_beyond_retention` for tests
- CLI: `ops/analytics/refresh_profiles.py` (`--force`, `--prune`)
- Smoke: `scripts/smoke_profile_refresh.py`
- Tests: `tests/test_profile_refresh.py`

## Smoke notes

- Forced EURUSD → `profiles` v1 + outbox row
- Immediate re-refresh → `skipped_cooldown`
- Live calendar triggers fired for EUR* (ECB Lagarde) during smoke

## Next

**W5·D3** — done; see `docs/status/w5d3-status.md`. Next: **W5·D4** scheduler worker.
