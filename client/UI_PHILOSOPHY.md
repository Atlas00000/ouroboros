# UI Philosophy — Jade Desk & Champagne Paper

## North star

Ouroboros should feel like an **institutional signal desk**: jade ink for the night desk, champagne paper for daylight research. Professional and unmistakably branded — FAANG-grade craft without crypto-neon, neon mint, teal-on-black, or generic admin chrome. Motion explains state. Colour carries backend truth. Every later page inherits this language; it does not invent its own.

## Feel adjectives

- Executive, ledger-like, precise
- Dual-mode: ink-jade dark / warm brass light
- Asymmetric, staged, signal-forward
- Calm under load; sharp on change

## Kill list (do not ship)

- Equal Bootstrap-style card stacks as the default grammar
- Purple / indigo “AI” gradients, glow stacks, neon cyan / mint on black
- Neon mint / fintech-green glow; glossy gold / crypto-brass gradients
- Saturated SaaS blue (`#3B82F6` and kin) as the accent
- Clip art, emojis, illustration placeholders, decorative Lorem
- Inter-as-default “SaaS dark mode” with blue primary buttons only
- Motion that entertains (bounce, confetti, endless pulse)
- One-off page art that bypasses tokens/primitives
- Mega CSS dumps inside individual pages

## System name

**Jade Desk & Champagne Paper** (active hybrid)

- **Dark** = Ink & Jade Ledger
- **Light** = Noir & Champagne Brass

Alternates documented in [`UI_PALETTES.md`](./UI_PALETTES.md).

| Layer | Role |
| --- | --- |
| Jade Desk (dark) | Ink-green canvas; muted jade signal |
| Champagne Paper (light) | Warm paper canvas; matte brass signal |
| Sage / Clay | `ok` / `halt` — sparse semantics, not decoration |

## Palette tokens (names = code)

| Token | Intent |
| --- | --- |
| `canvas` | App background (ambient gradient sits here) |
| `canvas-elevated` | Subtle lift band under chrome |
| `plane` | Primary content plane |
| `plane-raised` | Nested / interactive plane |
| `ink` | Primary text |
| `ink-muted` | Secondary text |
| `ink-faint` | Tertiary / meta |
| `line` | Hairline borders |
| `line-strong` | Emphasis rules |
| `signal` | Jade (dark) / Brass (light) — CTA, focus, live signal |
| `signal-soft` | Accent wash / selected |
| `warn` | Stale / caution |
| `halt` | Error / deny / trending_down severity |
| `ok` | Healthy / trending_up |
| `idle` | Ranging / neutral |
| `vol` | High volatility |

Regime / ops colours are **aliases** of the semantic set above (see backend map).

## Typography

| Role | Face | Use |
| --- | --- | --- |
| Display | Instrument Sans | Page titles, brand wordmark |
| UI | IBM Plex Sans | Body, labels, chrome |
| Numeric | IBM Plex Mono | Metrics, symbols, IDs — always `tabular-nums` |

Scale (tokenized): `display`, `title`, `body`, `label`, `micro`.

## Motion grammar

| Primitive | When | Rule |
| --- | --- | --- |
| `PageEnter` | Route / shell mount | Staged opacity + small Y; 1–2 steps max |
| `NumberTick` | Metric value change | Brief digit settle; no bounce |
| `StateCrossfade` | Enum / badge change | Crossfade 120–180ms |

- Durations: `instant` 80ms · `swift` 160ms · `pace` 280ms · `stage` 420ms
- Easing: `out-soft` (decelerate), `in-out-soft`
- **Always** honour `prefers-reduced-motion: reduce` → opacity-only or none

## Layout grammar (shell-level)

- Canvas full-bleed; content planes lifted, not boxed equally
- Asymmetric: primary column + narrower rail (ActionRail / context)
- Hairlines for structure; elevation via plane colour + soft shadow, not thick borders
- Section content layouts: **out of scope this phase**

## Modular file map

```
client/UI_PHILOSOPHY.md          ← this doc
client/UI_PALETTES.md            ← active + alternate palettes (dark/light)
client/src/design/
  tokens/
    color.css
    space.css
    type.css
    motion.css
    elevation.css
    index.css
  map/
    backend-visual.ts            ← API enums → token classes
  primitives/
    Surface.tsx · Text.tsx · Button.tsx · Input.tsx
    Badge.tsx · Icon.tsx
  motion/
    PageEnter.tsx · NumberTick.tsx · StateCrossfade.tsx
  shells/
    AppShell.tsx · PageHeader.tsx · ActionRail.tsx
  patterns/
    MetricStrip.tsx · EmptyState.tsx · Skeleton.tsx
    charts/          ← Recharts + D3 shared kit (ChartFrame, theme)
    market-pulse/ · universe/ · news-ticker/ · price-regime/ …
  index.ts
```

Pages compose shells + patterns. They do not redefine tokens.

## Charts

| Library | Role |
| --- | --- |
| **Recharts** | Declarative series, bars, rings, gauges |
| **D3** | Custom scales/overlays (regime bands, correlation heat, lag horizons) |

Rules: real API series only (or honest empty). No decorative placeholder paths, clip art, or emoji. Honour `prefers-reduced-motion`. Token colours via `design/patterns/charts/theme` + `backend-visual`.

## Backend ↔ UI mapping

| Backend concept | UI token / primitive |
| --- | --- |
| `regime: trending_up` | `ok` + Badge |
| `regime: trending_down` | `halt` + Badge |
| `regime: ranging` | `idle` + Badge |
| `regime: high_volatility` | `vol` + Badge |
| `provenance.stale` / feed stale | `warn` |
| Feed / source `status` healthy | `ok` |
| Feed / source `status` degraded/error | `warn` / `halt` |
| Gate decision `allow` (reserved) | `ok` / `signal` |
| Gate decision `skip` (reserved) | `idle` + muted Badge |
| Lifecycle phases (reserved) | `lifecycle-*` aliases on color tokens |

Zone / lifecycle / allow|skip slots exist in `backend-visual.ts` even if the API does not emit them yet — so later pages hug the backend without inventing new colours.

## Out of scope (later workstreams)

- New product features or routes
- Illustration systems, marketing landing
- Full component library parity with every form control
- Lightweight Charts / TradingView widgets

## Acceptance for this phase

- Global chrome/theme obviously different in &lt;2s
- Primitives reusable by later section tasks
- Token names in this doc match CSS / TS exports
- No feature scope creep
