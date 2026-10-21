"""Render research/assets/AAPL markdown from audit.json."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    return f"{100 * float(x):.{digits}f}%"


def fnum(x: object | None, digits: int = 2) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{digits}f}"


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    out = repo / "research" / "assets" / "AAPL"
    d = json.loads((out / "audit.json").read_text(encoding="utf-8"))
    prof = d["profile"]
    nc = d["nowcast"]
    dr = d["data_range"]
    id_ = prof["identity"]
    vol = prof["volatility"]
    liq = prof["liquidity"]
    hours = prof["trading_hours"]
    rd = prof["regime_distribution"]
    fit30 = nc["fit_30d_h1"]
    st = nc["state"]
    sent = nc["sentiment"]
    ins = nc.get("insight") or {}
    px = d["monthly_price"]
    tot_ret = (px[-1]["close"] / px[0]["open"] - 1) * 100 if px else None
    h1_rows = d["monthly_regime_table_h1"]
    d1_rows = d["monthly_regime_table_d1"]
    dom_h1 = Counter(r["dominant_regime"] for r in h1_rows)
    dom_d1 = Counter(r["dominant_regime"] for r in d1_rows)
    tsum = d["tag_summary"]

    lines: list[str] = []
    A = lines.append
    A("# AAPL — Asset profile dossier")
    A("")
    A(
        "> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  "
    )
    A(
        f"> Generated `{d['generated_at'][:19]}Z` · data `{dr['d1_start'][:10]}` → "
        f"`{dr['d1_end'][:10]}` ({dr['month_count']} calendar months, "
        f"M1 depth ≈ {dr['m1_depth_days']:.0f}d)"
    )
    A("")
    A(
        "Canvas cover (open beside chat): "
        "`canvases/aapl-asset-profile.canvas.tsx` in the Cursor project."
    )
    A("")
    A("---")
    A("")
    A("## Identity")
    A("")
    A("| Field | Value |")
    A("| --- | --- |")
    A(f"| Symbol | `{id_['symbol']}` |")
    A(f"| Display | {id_['display_name']} |")
    A(f"| Class | {id_['asset_class']} |")
    A(f"| Quote | {id_['quote_currency']} |")
    A(f"| MT5 ticker | `{id_['mt5_ticker']}` |")
    A(
        f"| Sessions | {', '.join(hours['sessions'])} · `{hours['timezone']}` · "
        f"UTC {hours['open_utc'][:5]}–{hours['close_utc'][:5]} |"
    )
    A("")
    A(hours["notes"])
    A("")
    A("---")
    A("")
    A("## Two clocks")
    A("")
    A("### Nowcast (H1 state)")
    A("")
    A("| Metric | Value |")
    A("| --- | --- |")
    A(f"| Confirmed regime | **{st['regime']}** |")
    A(f"| Vol percentile | {fnum(st['volatility_percentile'], 1)} |")
    A(f"| Trend ER | {fnum(st['trend_strength'], 3)} |")
    A(f"| Confidence | {fnum(st['confidence'], 3)} |")
    A(f"| As-of | {st['as_of']} |")
    A(f"| Stale | {st['stale']} |")
    A("")
    probs = json.loads(st["probabilities_json"])
    A(
        "Soft probabilities (nowcast — may disagree with confirmed label when "
        "confidence is low):"
    )
    A("")
    A("| Regime | P |")
    A("| --- | ---: |")
    for p in probs:
        A(f"| {p['regime']} | {pct(p['probability'])} |")
    A("")
    A("### Live fit gate (ex-post 30d H1 shares → dominant tag)")
    A("")
    A("| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |")
    A("| --- | --- | ---: | ---: | ---: | ---: |")
    for fam in ("meanrev", "trendfollow"):
        b = fit30[fam]
        s = b["shares"]
        A(
            f"| `{fam}` | **{b['tag']}** | {pct(s['MATCH'])} | "
            f"{pct(s['MISMATCH'])} | {pct(s['FRAGILE'])} | {b['bar_count']} |"
        )
    A("")
    A(
        "Interpretation: last ~30d H1 mass is **ranging-led** → mean-reversion "
        "research gate ON (MATCH), trend-follow OFF (MISMATCH). High-vol share "
        "still ~26% → FRAGILE weight is material."
    )
    A("")
    A("---")
    A("")
    A("## Character (`profile.v1`)")
    A("")
    A("### Volatility & liquidity")
    A("")
    A("| Field | Value |")
    A("| --- | --- |")
    A(f"| ATR pctile 30d | {fnum(vol['atr_percentile_30d'], 1)} |")
    A(f"| Realized vol pctile 30d | {fnum(vol['realized_vol_percentile_30d'], 1)} |")
    A(f"| Typical daily range | {fnum(vol['typical_daily_range'], 2)} USD |")
    A(f"| Range pctile 30d (liq proxy) | {fnum(liq['spread_percentile_30d'], 1)} |")
    A("| True spread | deferred |")
    A("")
    A(f"_{liq['notes']}_")
    A("")
    A("### Regime distribution (history clock)")
    A("")
    A(
        "Confirmed-label share over the profile sample "
        "(H1 preferred when depth gate passes):"
    )
    A("")
    A("| Regime | Share |")
    A("| --- | ---: |")
    for r in rd:
        A(f"| {r['regime']} | {pct(r['share'])} |")
    A("")
    A(
        "**Read:** ranging (~38%) + high_volatility (~32%) dominate the 2y "
        "character. Net trending (up+down) ≈ 31%. This is a **meanrev-leaning** "
        "equity on H1 history — with a large fragile/high-vol sleeve."
    )
    A("")
    A("### Peer correlations (H1 ~30d)")
    A("")
    A("| Peer | ρ |")
    A("| --- | ---: |")
    for c in prof["correlations"]:
        A(f"| {c['symbol']} | {c['coefficient']:+.3f} |")
    A("")
    A(
        "Beta-to-index is mild (~0.30 vs US500/NAS100). Closest single-name peers "
        "in this window: GOOGL / NVDA / AMZN / AVGO. XOM is the only notable "
        "negative sleeve (~−0.20)."
    )
    A("")
    A("### Event sensitivities")
    A("")
    A(
        "Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — "
        "calendar hits scored for AAPL are below the ≥3-window gate. Honest gap "
        "until equity event windows are scored."
    )
    A("")
    A("---")
    A("")
    A("## Path")
    A("")
    A(
        f"Monthly D1 path return over the window: **{tot_ret:+.1f}%** "
        f"(open {px[0]['open']:.2f} → last close {px[-1]['close']:.2f})."
    )
    A("")
    A("| Month | Ret % | Close |")
    A("| --- | ---: | ---: |")
    for r in px:
        A(f"| {r['month']} | {r['ret_pct']:+.2f} | {r['close']:.2f} |")
    A("")
    A("---")
    A("")
    A("## Narrative pressure")
    A("")
    if sent:
        A(
            f"- Sentiment score: **{fnum(sent['score'], 3)}** on [−1, +1] · "
            f"{sent['item_count']} items · {sent['window_hours']}h window"
        )
        A(f"- As-of: {sent['as_of']} · stale={sent['stale']}")
    A(f"- Mapped news articles: **{d['news_count']}**")
    if ins:
        body = str(ins.get("body") or "")[:280]
        A(f"- Insight: _{ins.get('title')}_ — {body}")
    A("")
    A("Recent headlines:")
    A("")
    for n in d["recent_news"][:8]:
        A(
            f"- {str(n.get('published_at') or '')[:10]} · "
            f"{n.get('source') or '?'} — {n.get('headline')}"
        )
    A("")
    A("---")
    A("")
    A("## Provenance")
    A("")
    A(
        f"- Models: `{d['models']['regime']}` · `{d['models']['fit']}` · "
        f"`{d['models']['profile']}`"
    )
    A(
        f"- Profile confidence: {prof['provenance']['confidence']} · "
        f"stale={prof['provenance']['stale']}"
    )
    A(f"- Sources: {', '.join(prof['provenance']['sources'])}")
    A(
        "- Raw export: [`audit.json`](./audit.json) · monthly boards: "
        "[`regime-audit.md`](./regime-audit.md)"
    )
    A("")
    A(d["disclaimer"])
    A("")
    (out / "PROFILE.md").write_text("\n".join(lines), encoding="utf-8")

    L: list[str] = []
    B = L.append
    B("# AAPL — Regime audit & fit tagging (monthly, 2y)")
    B("")
    B(
        f"> Ex-post calendar-month boards · `{d['models']['regime']}` labels → "
        f"`{d['models']['fit']}`  "
    )
    B(
        f"> Window: {dr['months'][0]} → {dr['months'][-1]} "
        f"({len(h1_rows)} H1 months with confirmed bars after warmup)"
    )
    B("")
    B("## Method")
    B("")
    B("1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).")
    B("2. Run `regime_feature_frame` → confirmed regime per bar.")
    B(
        "3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE "
        "per edge family."
    )
    B(
        "4. Dominant tag = largest fit-share "
        "(ties break MISMATCH > FRAGILE > MATCH)."
    )
    B("")
    B(
        "Families: **meanrev** home=`ranging`; **trendfollow** "
        "home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE."
    )
    B("")
    B("## Tag summary (months with bars)")
    B("")
    B("| TF × family | MATCH | MISMATCH | FRAGILE |")
    B("| --- | ---: | ---: | ---: |")
    for key in (
        "H1|meanrev",
        "H1|trendfollow",
        "D1|meanrev",
        "D1|trendfollow",
    ):
        s = tsum[key]
        B(
            f"| `{key}` | {s.get('MATCH', 0)} | {s.get('MISMATCH', 0)} | "
            f"{s.get('FRAGILE', 0)} |"
        )
    B("")
    B(f"Dominant-regime months (H1): {dict(dom_h1)}")
    B(f"Dominant-regime months (D1): {dict(dom_d1)}")
    B("")
    B("## H1 monthly board")
    B("")
    B(
        "| Month | Dominant regime | meanrev | trendfollow | Bars | "
        "ranging | trend↑ | trend↓ | high_vol |"
    )
    B("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for r in h1_rows:
        rs = r["regime_shares"]
        B(
            f"| {r['month']} | {r['dominant_regime']} | "
            f"**{r.get('meanrev_tag')}** | **{r.get('trendfollow_tag')}** | "
            f"{r['bar_count']} | {pct(rs.get('ranging', 0))} | "
            f"{pct(rs.get('trending_up', 0))} | "
            f"{pct(rs.get('trending_down', 0))} | "
            f"{pct(rs.get('high_volatility', 0))} |"
        )
    B("")
    B("## D1 monthly board")
    B("")
    B(
        "| Month | Dominant regime | meanrev | trendfollow | Bars | "
        "ranging | trend↑ | trend↓ | high_vol |"
    )
    B("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for r in d1_rows:
        rs = r["regime_shares"]
        B(
            f"| {r['month']} | {r['dominant_regime']} | "
            f"**{r.get('meanrev_tag')}** | **{r.get('trendfollow_tag')}** | "
            f"{r['bar_count']} | {pct(rs.get('ranging', 0))} | "
            f"{pct(rs.get('trending_up', 0))} | "
            f"{pct(rs.get('trending_down', 0))} | "
            f"{pct(rs.get('high_volatility', 0))} |"
        )
    B("")
    B("## Audit takeaways")
    B("")
    B(
        "1. **H1 meanrev MATCH in 12/24 months** vs trendfollow MATCH in 5/24 — "
        "ranging is the modal month regime (14/24 H1)."
    )
    B(
        "2. **Fragile clusters:** Jan–Apr 2025 and Jan–Apr 2026 are high-vol "
        "dominant on H1 (both families FRAGILE for most of those months)."
    )
    B(
        "3. **Trend windows are rare but sharp:** Dec 2024 and May 2026 flip to "
        "trending_up-led MATCH for trendfollow."
    )
    B(
        "4. **TF disagreement is expected:** e.g. May 2025 H1 dominant=ranging "
        "but meanrev=MISMATCH because trend shares outvote ranging on the fit map."
    )
    B(
        "5. **2024-10** may appear in price but drop from confirmed boards "
        "(regime warmup). Partial **2026-10** has fewer bars."
    )
    B(
        "6. Monthly MATCH is **ex-post**, not a forward signal. Live research "
        "gate should use nowcast + 30d shares, not calendar-month prophecy."
    )
    B("")
    B(d["disclaimer"])
    B("")
    (out / "regime-audit.md").write_text("\n".join(L), encoding="utf-8")

    (out / "profile.json").write_text(json.dumps(prof, indent=2), encoding="utf-8")

    readme = f"""# AAPL research dossier

Living asset profile + 2-year monthly regime / fit audit produced from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas cover:** open `aapl-asset-profile.canvas.tsx` beside chat (Cursor managed `canvases/` directory).

Models: `{d['models']['regime']}` · `{d['models']['fit']}` · `{d['models']['profile']}`  
Range: {dr['d1_start'][:10]} → {dr['d1_end'][:10]} · regenerated via `server/scripts/aapl_regime_audit.py`
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print("wrote", out)
    for f in sorted(out.iterdir()):
        print(f"  {f.name} {f.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
