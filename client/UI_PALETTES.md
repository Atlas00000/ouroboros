# UI palettes — active + alternates

Active implementation lives in `src/design/tokens/color.css`.
Shared product vibe: **Institutional Signal Desk** — quiet luxury, hairlines over boxes, one accent used like a fountain-pen underline. Dark is the primary desk; light is daylight research paper.

To switch light/dark at runtime: set `data-theme="light"` or `data-theme="dark"` on `<html>` (or toggle `.light` / `.dark`). Default is dark.

---

## Active — Jade Desk & Champagne Paper *(hybrid)*

**Composition:** dark from **Ink & Jade Ledger** · light from **Noir & Champagne Brass**.

**Feel:** Night desk is classic jade ledger; day mode is warm champagne paper with matte brass.

| Token | Dark (Jade Ledger) | Light (Champagne Brass) |
| --- | --- | --- |
| canvas | `#090C0B` | `#F7F4EE` |
| canvas-elevated | `#0D1210` | `#F0EBE3` |
| plane | `#111614` | `#FFFDF8` |
| plane-raised | `#171D1A` | `#FFFFFF` |
| ink | `#E4EBE6` | `#1C1A17` |
| ink-muted | `#85948C` | `#6F6A62` |
| ink-faint | `#5A6B63` | `#9A9488` |
| line | `#1C2621` | `#E4DDD2` |
| line-strong | `#2A3630` | `#D0C8BA` |
| signal | `#5F9E86` (jade) | `#9A7B3C` (brass) |
| signal-ink | `#071410` | `#FFFDF8` |
| ok | `#5F9E86` | `#4F6F54` |
| warn | `#B8934E` | `#A67C2E` |
| halt | `#B56A62` | `#9A4540` |
| idle | `#85948C` | `#7A756C` |
| vol | `#B8934E` | `#A67C2E` |

**Risk:** Keep jade muted (no neon mint); keep brass matte (no glossy gold). Accent stays sparse in both modes.

---

## Alternate A — Obsidian & Vermilion Seal

**Feel:** Boardroom severity; one hot accent like a wax seal.

| Token | Dark | Light |
| --- | --- | --- |
| canvas | `#0B0C0E` | `#F4F1EB` |
| plane | `#14161A` | `#FFFFFF` |
| ink | `#ECE8E1` | `#1A1C1F` |
| signal (vermilion) | `#C45C4A` | `#B5483A` |
| warn | `#C4A35A` | `#A67C2E` |
| halt | `#A33B32` | `#8F322A` |
| ok | `#7A9E7E` | `#4F6F54` |

**Risk:** Finance-red if overused — accent &lt;5%.

---

## Alternate B — Ink & Jade Ledger *(full pair)*

**Feel:** Classic ledger modernity; jade both modes.

| Token | Dark | Light |
| --- | --- | --- |
| canvas | `#090C0B` | `#F2F5F3` |
| plane | `#111614` | `#FFFFFF` |
| signal (jade) | `#5F9E86` | `#2F6B55` |
| warn | `#B8934E` | `#9A7B3C` |
| halt | `#B56A62` | `#9A4540` |

---

## Alternate C — Noir & Champagne Brass *(full pair)*

**Feel:** Evening desk / warm paper; brass both modes.

| Token | Dark | Light |
| --- | --- | --- |
| canvas | `#0A0B0D` | `#F7F4EE` |
| plane | `#12141A` | `#FFFDF8` |
| signal (brass) | `#C6A96B` | `#9A7B3C` |
| ok | `#7A9E7E` | `#4F6F54` |
| halt | `#B05A52` | `#9A4540` |

---

## Alternate D — Midnight & Iris Smoke

**Feel:** Editorial research-house; smoky gray-iris.

| Token | Dark | Light |
| --- | --- | --- |
| canvas | `#0A0A0F` | `#F4F3F8` |
| plane | `#13131A` | `#FFFFFF` |
| signal (iris) | `#8B84A8` | `#5C5678` |
| ok | `#6F9A8A` | `#4F6F54` |
| halt | `#B56B72` | `#9A4540` |

---

## Alternate E — Carbon & Arctic Steel

**Feel:** Precision instrument; desaturated steel.

| Token | Dark | Light |
| --- | --- | --- |
| canvas | `#080A0C` | `#F3F5F7` |
| plane | `#101418` | `#FFFFFF` |
| signal (steel) | `#7FA6B8` | `#3F6F82` |
| ok | `#6FA08A` | `#4A7A66` |
| halt | `#C07070` | `#A35555` |

---

## How to activate an alternate later

1. Replace the hex values in `src/design/tokens/color.css` (keep token **names** stable).
2. Or add `[data-palette="…"]` scopes mirroring the dark/light blocks.
3. Do **not** invent one-off colours in page components — always map through `--ds-*` tokens.

Token names (`canvas`, `signal`, `ok`, `warn`, `halt`, …) stay fixed across palettes so primitives and backend maps do not change.
