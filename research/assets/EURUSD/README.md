# EURUSD research dossier

Living asset profile + 2y regime audit + BMRG / EPG M15 sleeves from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Asset profile dossier |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 fit tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG geometry + P0/P1/P2 blotter notes |
| [`EPG_M15_chart_preset.md`](./EPG_M15_chart_preset.md) | EPG deep-pullback P0 geometry |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15* probe |
| [`epg_m15_6m_audit.json`](./epg_m15_6m_audit.json) | EPG M15* probe |
| [`tester_magic_26101815_score.json`](./tester_magic_26101815_score.json) | BMRG P0 blotter (WR &lt; BWR) |
| [`tester_magic_26101816_score.json`](./tester_magic_26101816_score.json) | BMRG P1 blotter (starved tip) |

**BMRG Tester:** `…/MQL5/Profiles/Tester/BMRG/EURUSD/`

| Sleeve | Magic | Status |
| --- | ---: | --- |
| P0 balanced | 26101815 | WR &lt; BWR |
| P1 selective | 26101816 | reject — tip n≈6 |
| **P2 light** | **26101817** | **NEXT** — BB 2.3 · CD 3 · ATR≤74 · BBw off |

**EPG Tester:** `…/MQL5/Profiles/Tester/EPG/EURUSD/`

| Sleeve | Magic | Status |
| --- | ---: | --- |
| P0 deep L1 | 26101821 | reject — 135/135 EMA50 scratch · WR 0% |
| P1 hard stops | 26101822 | exit OK · tip WR 40.6% &lt; BWR |
| P2 light | 26101823 | reject tip — WR 37.5% &lt; P1; longer windows EF&lt;0 |

Canvas: [epg-eurusd-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/epg-eurusd-m15-preset.canvas.tsx)
