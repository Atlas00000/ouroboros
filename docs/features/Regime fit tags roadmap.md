# Regime fit tags — build roadmap

> **Living plan** for productizing [`Regime fit tags.md`](./Regime%20fit%20tags.md)  
> **Status:** R0–R4 **shipped**; Desk overlays + fit stickiness scoring shipped 2026-10-06; forward `P(tag)` out of scope  
> **Last updated:** 2026-10-06

## Ship order

`fit.map_v0` → ex-post boards → live gate → persist (`forecast_log` `fit.*`) → `GET /v1/fit`

No forward `P(tag)`, Desk page, or Preset Factory emit in this roadmap.

## Locked choices

| Choice | Value |
| --- | --- |
| Key | `symbol × timeframe × family` |
| Families v0 | `meanrev` · `trendfollow` |
| Tags | `MATCH` · `MISMATCH` · `FRAGILE` |
| Map version | `fit.map_v0` |
| Persist | `forecast_log.call_type` = `fit.meanrev` \| `fit.trendfollow` |
| FRAGILE v0 | `high_volatility` → FRAGILE (both families) |
| Tie-break (boards) | MISMATCH > FRAGILE > MATCH |
| Live gate | `allow_on` iff tag == MATCH |

## Phases & exit tests

| Phase | Deliverable | Exit |
| --- | --- | --- |
| **R0** | Family registry + mapper | `pytest server/tests/test_fit_map_v0.py -q` |
| **R1** | Board builder + CLI | `pytest server/tests/test_fit_boards.py -q` |
| **R2** | Live gate helper | `pytest server/tests/test_fit_gate.py -q` |
| **R3** | Persist + `fit_log` job | `pytest server/tests/test_fit_log.py -q` |
| **R4** | `GET /v1/fit` | `pytest server/tests/test_api_fit.py -q` |
| **R5** | Status sync in `features.md` | Docs only |

## File map

| Path | Role |
| --- | --- |
| `server/app/analytics/fit/` | Mapper, boards, gate, log helpers |
| `server/tests/fixtures/analytics/fit_map_v0.json` | Golden map |
| `ops/analytics/fit_board.py` | CLI board smoke |
| `server/app/api/v1/fit.py` | REST |
| `packages/contracts/contracts/fit_v1.py` | `fit.v1` contract |

## Out of scope (later)

- Forward `P(tag)` @ 7d/30d/60d + Brier gate  
- Calendar-distance FRAGILE overlay  
- Jade Desk overlays  
- Preset Factory emitter wiring  

## Changelog

| Date | Change |
| --- | --- |
| 2026-10-03 | R0–R4 implemented + tests |
| 2026-10-03 | Initial roadmap; R0–R4 implementation plan locked |
