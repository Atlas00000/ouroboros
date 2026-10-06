# Pages — Ouroboros client IA

**Role:** Living tracker of client **pages** and **sections**. Update this file when pages or sections are added, removed, or renamed.  
**Audience:** product / design / frontend  
**Sources:** [`concept.md`](../concept.md), [`roadmap.md`](../roadmap.md) §5, [`architecture.md`](./architecture.md), [`UIscreens-and-details.md`](./UIscreens-and-details.md), [`preset-factory-roadmap.md`](../preset-factory-roadmap.md)  
**Non-goals:** no trade execution, no order routing, no public marketing site

---

## How to maintain

| Change | Update |
| --- | --- |
| Add a page | New row in **Pages** + short page subsection + nav if needed |
| Remove a page | Delete row / subsection; note date in **Changelog** |
| Add/remove a section | **Sections** table + composition matrix |
| Ship / stub status | Set **Status** column (`planned` · `chrome` · `stub` · `live`) |

---

## Build plan (2026-10-02)

1. Chrome + nav — done  
2. Restore query helpers (`asset-detail`, `system`) — done  
3. Home — Market pulse · Universe · Signal desk — done  
4. Asset dossier — done  
5. News — done  
6. Scoring — done  
7. Desk (role-gated) — done  

---

## Product in one line

Ouroboros is an **independent asset-intelligence desk**: it builds living profiles, regimes, sentiment, and insights from market and news context, and shares that research awareness with sibling platforms. It is **advisory / research only** — never an execution engine.

Forward-facing capabilities (what people use):

| Capability | User-facing meaning |
| --- | --- |
| Universe awareness | Scan which assets matter right now and how they feel |
| Living dossiers | Deep context on one instrument — character, peers, regime |
| News digestion | Headlines and calendar context that shape sentiment |
| Regime honesty | How well regime calls have been holding up |
| Desk integrity | Whether the research desk’s view is fresh and trustworthy |
| Machine consumers | Sibling platforms receive context; humans never manage that in main chrome |

Auth gate (invite-only sign-in) sits **outside** the main pages below.

Preset Factory (sibling roadmap) **consumes** Ouroboros context later; it is **not** a v1 Ouroboros page.

---

## Pages

| # | Page | Route (intent) | One job | Who | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | **Home** | `/` | Scan the universe at a glance | All signed-in roles | live |
| 2 | **Asset** | `/assets/[symbol]` | Deep-dive one instrument’s living dossier | All signed-in roles | live |
| 3 | **News** | `/news` | Read and filter market/news context | All signed-in roles | live |
| 4 | **Scoring** | `/scoring` | Review regime call quality over time | Analyst+ (visible to all; denser for power users) | live |
| 5 | **Desk** | `/system` | Trust the research desk — freshness & alerts | Ops / admin | live |

**Nav (dense, market-tool style):**  
`Home` · `News` · `Scoring` · `Desk` (content role-gated)  

Asset is **not** top-nav — entered from Home (or deep link).

**Related, not a main page:** invite sign-in / sign-up; admin key management for sibling machines (admin-only, secondary surface).

---

### 1. Home

**Job:** one scan composition — what is alive in the book right now?

- Universe of instruments with regime tone, volatility character, sentiment, freshness cues  
- Short market pulse (counts, high-impact context, honesty stamps)  
- Side signal desk of recent headlines  

Not a widget dump; not a trading blotter.

---

### 2. Asset

**Job:** one symbol’s living research dossier.

- Price view with regime character  
- Profile (identity, peers, correlations, liquidity/vol character)  
- Current state / regime confidence  
- Sentiment with driver headlines  
- Labeled generative insights + persistent research disclaimer  

Power users live here after the Home scan.

---

### 3. News

**Job:** when context matters more than a single card.

- Filterable headlines / calendar-style events  
- Symbol and impact orientation  
- Paths into Asset when a story points at an instrument  

Useful when sentiment is quiet or the desk needs the raw narrative layer.

---

### 4. Scoring

**Job:** build trust in regimes without claiming foresight.

- Weekly / rolling accuracy of regime calls  
- By symbol and timeframe where available  
- Same story the research digests tell — visible in-product  

This is honesty about the brain, not a performance marketing page.

---

### 5. Desk

**Job:** ops trust the pipe feeding the research UI.

- Source / feed status and expected cadence  
- Prolonged-staleness alerts  
- Human-readable desk health (depth, lag cues, spend strip if useful)  

Role-gated (`admin`+). Analysts should not need this for daily scan/deep-dive.

---

## Sections

Reusable **content sections** composed into pages. Named for Ouroboros product language — not generic “hero / features / CTA.”

| # | Section | What it shows | Typically on | Status |
| --- | --- | --- | --- | --- |
| 1 | **Universe** | Instrument **grid**: symbol, last/change, regime, Recharts series + TF selector, vol ring, sentiment | Home | live |
| 2 | **Market pulse** | Desk-level summary: asset count, high-impact pressure, freshness / “as of”, research-only reminder | Home | live |
| 3 | **Price & regime** | Recharts close path + D3 regime wash + TF selector | Asset | live |
| 4 | **Profile** | Living dossier identity: peers, D3 correlation heat strip, liquidity & volatility character | Asset | live |
| 5 | **Sentiment & drivers** | Recharts sentiment scale + headlines; Home rail = signal tape; News impact mix | Asset, Home rail, News | live |
| 6 | **Insights & honesty** | Narratives + Scoring Recharts accuracy / Desk lag+outbox charts | Asset; Scoring; Desk; all pages (stale / disclaimer) | live |

### Section composition by page

| Page | Sections in play |
| --- | --- |
| Home | **Universe** (instrument grid + Recharts) · **Market pulse** · **Sentiment & drivers** (signal desk tape) · Insights & honesty |
| Asset | **Price & regime** (Recharts+D3) · Profile · Sentiment & drivers · Insights & honesty |
| News | Sentiment & drivers (list + impact mix chart) · Insights & honesty (freshness) · links into Asset |
| Scoring | Insights & honesty (Recharts accuracy + honesty tables) |
| Desk | Insights & honesty (desk integrity) · Pipe lag/outbox charts |

---

## Explicit exclusions

- Execution, order tickets, position managers, broker login  
- Public signup / marketing landing as part of this IA  
- Preset Factory emitter UI (sibling workstream)  
- Exposing feed plumbing, keys, or infrastructure in analyst chrome  

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-10-02 | Created as living **pages** tracker. Five pages + six sections. Home chrome-only. |
| 2026-10-02 | Built all five routes on design system; nav Home/News/Scoring/Desk; sections marked live. |
| 2026-10-02 | Home **Market pulse** overhauled — modular `design/patterns/market-pulse/*` (atmosphere, rail, metrics, honesty; not boxed MetricStrip). |
| 2026-10-02 | Home **Universe** overhauled — modular `design/patterns/universe/*` (ledger rows, regime filter, signal paths; not equal card grid). |
| 2026-10-02 | Home **News ticker / Signal desk** overhauled — modular `design/patterns/news-ticker/*` (impact tape, focus strip; not boxed list). |
| 2026-10-02 | Home **Universe** → professional **grid** with Recharts H1 series + vol rings (real `/v1/bars`, not placeholder paths). |
| 2026-10-02 | Chart revamp — shared `design/patterns/charts` + Recharts/D3 across Asset, Scoring, Desk, News; deleted Sparkline placeholder. |

---

## Doc map

| Doc | Role |
| --- | --- |
| This file | Living **pages + sections** tracker for the client |
| [`UIscreens-and-details.md`](./UIscreens-and-details.md) | Earlier Phase 4 screen baseline |
| [`../client/UI_PHILOSOPHY.md`](../client/UI_PHILOSOPHY.md) | Visual system (Jade Desk & Champagne Paper) |
| [`../client/UI_PALETTES.md`](../client/UI_PALETTES.md) | Palette alternates |
