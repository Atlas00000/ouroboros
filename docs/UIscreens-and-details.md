# UI screens and details — Phase 4 baseline

**Status:** Accepted baseline for client IA (2026-09-14)  
**Product:** Ouroboros — asset intelligence, research context only (no trade execution)  
**Build from:** this document + live API `v0.4-api`  
**Roadmap:** Phase 4 (Weeks 9–11)

---

## Primary users

| User | Goal |
|------|------|
| Analyst / viewer | What’s the state of this asset right now? |
| Ops | Are feeds healthy? Is freshness honest? |
| Admin | Machine API keys, org; light scoring visibility |
| Machines | No screens — API + Redis Streams only |

---

## Navigation (dense, market-tool style)

Top nav:

`Dashboard` · `News` · `Scoring` · `System` (ops+) · `Admin` (admin+)

Asset detail is **not** top-nav — entered from the dashboard grid (or deep links).

---

## Core screens (must-have)

### 1. Sign-in / invite gate

- Clerk only; invite-only org (no public signup in production).
- Tone: research product, not a trading terminal.
- Routes: `/sign-in`, `/sign-up` (invite flow only).

### 2. Dashboard (home) — `/`

**One job:** scan the universe.

| Element | Content | Primary API |
|---------|---------|-------------|
| Asset grid | Symbol, sparkline, regime badge, vol percentile, sentiment gauge, stale badge | `GET /v1/assets` (+ per-symbol state/metrics/sentiment as needed) |
| Market strip | Risk tone / top movers / high-impact news ticker | news + derived summary |
| Honesty | `generated_at`, model version, stale — never pretend fresher than feeds | provenance on envelopes |

Composition rule: one scan composition, not a widget dump.

### 3. Asset detail — `/assets/[symbol]`

**One job:** deep dive on one symbol. Sections in order:

| Section | Content | Primary API |
|---------|---------|-------------|
| Price + regime bands | Chart with regime overlay | prices via metrics/state history; `GET /v1/state` |
| Profile | Identity, peers, correlations | `GET /v1/assets/{symbol}/profile` |
| State panel | Regime probs, confidence, model version, `generated_at` | `GET /v1/state` |
| Sentiment | Gauge/trend + driver headlines | `GET /v1/sentiment` |
| Insights | Narrative feed; **labeled generative**; disclaimer always visible | `GET /v1/insights` |

Sticky symbol chrome recommended (power users live here after the scan).

### 4. System / health — `/system` (ops+)

**One job:** trust the pipe.

| Element | Content | Source |
|---------|---------|--------|
| Feed registry | Cadence, last_seen, status | registry / health |
| Watchdog alerts | Prolonged stale digests | watchdog / alerts |
| Pipe health | Outbox / stream depth (human-readable) | `/metrics` (ops view, not raw Prometheus page) |
| LLM spend | Day spend strip (optional) | `/metrics` |

Role-gated via `RoleGate` (ops / admin).

---

## Supporting screens

### 5. News / calendar — `/news`

- Filterable list: symbol, impact, calendar vs article.
- Entry from market ticker; exits to asset detail.
- Useful when sentiment is empty because news feeds went quiet.
- API: `GET /v1/news`.

### 6. Scoring / accuracy — `/scoring`

- Weekly regime hit-rate tables (same story as Resend weekly digest).
- Builds trust in `regimes.rule_v1` without claiming foresight.
- API / tables: scoring weekly reports + `forecast_log` aggregates.

### 7. Admin: API keys — `/admin/keys` (admin+)

- Mint / revoke machine keys for quant platforms.
- Humans never see machine keys in main chrome outside this page.
- Browser never embeds machine keys for data calls (Clerk JWT only).

---

## Use cases → screens

| Use case | Path |
|----------|------|
| Morning scan | Dashboard → 2–3 asset details |
| Why is EURUSD ranging? | Asset detail: state + profile + drivers |
| Is this stale? | Any panel stale badge → System |
| High-impact event | News ticker → News → Asset |
| Weekly model check | Scoring (or email → Scoring) |
| Onboard quant consumer | Admin keys (+ contracts docs, not UI) |

---

## Explicit non-screens (v1)

Do **not** ship as first-class product pages:

- Trade tickets / order books / P&L
- Portfolio construction
- Chat-with-the-market as home
- Raw Prometheus UI for analysts (ops may link out later; System stays human-readable)

---

## Design decisions (locked for Phase 4)

1. **Dashboard-first** for scan; **asset detail** as the real work surface.
2. **Stale is a feature** — important surfaces must be able to look “off” when feeds die.
3. **Narratives are labeled** — generative copy never mixed into numeric panels.
4. **Disclaimer** on insights (and product chrome): research only, not investment advice, no execution.
5. **Dark-mode-first**; regime colors: trending-up green, trending-down red, ranging zinc, high-vol amber.

---

## Phase 4 build mapping

| Week | Screens / focus |
|------|-----------------|
| W9 | Shell, Clerk, Dashboard grid + strip + news ticker head start |
| W10 | Full Asset detail sections |
| W11 | System, Scoring, Admin keys; a11y; Playwright; tag `v0.5-client` |

Component-level day plan remains in `roadmap.md` Phase 4; this file is the **screen IA baseline**.
