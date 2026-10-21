"""Verification report for universe expansion phases 1–5."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select, text

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.profiles import _trading_hours_default, build_asset_profile_from_session
from app.analytics.universe import (
    DEPTH_GATED_SYMBOLS,
    EQUITY_INDEX_ANCHORS,
    MIN_CORR_REGIME_DEPTH_DAYS,
    default_peer_symbols,
    passes_depth_gate,
)
from app.db.session import get_engine, get_session_factory
from app.ingestion.econ_calendar.impact import map_country_symbols
from app.ingestion.news.client import DEFAULT_CATEGORIES
from app.ingestion.news.mapping import NewsAssetMapper
from app.models.asset import Asset


EQUITIES = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "JPM",
    "AVGO",
    "XOM",
]
MATERIALS = ["XTIUSD", "XBRUSD"]
EXTRA_INDICES = ["DE40", "UK100", "JP225"]
HARDEN = ["XAUUSD", "XAGUSD", "US500", "US30", "NAS100"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class PhaseReport:
    title: str
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.ok)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.ok)


def _check(name: str, ok: bool, detail: str = "") -> Check:
    return Check(name=name, ok=bool(ok), detail=detail)


def main() -> int:
    engine = get_engine()
    session = get_session_factory()()
    reports: list[PhaseReport] = []

    with engine.connect() as conn:
        alembic = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        active = conn.execute(text("SELECT count(*) FROM assets WHERE is_active")).scalar_one()
        by_class = {
            r[0]: r[1]
            for r in conn.execute(
                text(
                    "SELECT asset_class, count(*) FROM assets WHERE is_active "
                    "GROUP BY asset_class ORDER BY asset_class"
                )
            )
        }
        depth_rows = {
            r[0]: (int(r[1] or 0), r[2], r[3])
            for r in conn.execute(
                text(
                    """
                    SELECT a.symbol, count(p.ts), min(p.ts), max(p.ts)
                    FROM assets a
                    LEFT JOIN prices p ON p.symbol = a.symbol
                    WHERE a.is_active
                    GROUP BY a.symbol
                    """
                )
            )
        }
        h1_counts = {
            r[0]: int(r[1])
            for r in conn.execute(text("SELECT symbol, count(*) FROM prices_h1 GROUP BY symbol"))
        }
        profile_syms = {
            r[0]
            for r in conn.execute(
                text("SELECT DISTINCT symbol FROM profiles ORDER BY 1")
            ).fetchall()
        }

    rows = session.scalars(select(Asset).where(Asset.is_active.is_(True))).all()
    assets = {r.symbol.upper(): r for r in rows}

    # --- Phase 1 ---
    p1 = PhaseReport("Phase 1 — Harden metals & indices")
    for sym in HARDEN:
        bars, _mn, mx = depth_rows.get(sym, (0, None, None))
        p1.checks.append(_check(f"{sym} in assets", sym in assets, assets.get(sym) and assets[sym].asset_class))
        p1.checks.append(_check(f"{sym} has M1 bars", bars > 100_000, f"bars={bars} max={mx}"))
        p1.checks.append(_check(f"{sym} has profile", sym in profile_syms))
    metal_h = _trading_hours_default(asset_class="metal")
    index_h = _trading_hours_default(asset_class="index")
    p1.checks.append(_check("metal session notes set", bool(metal_h.notes and metal_h.open_utc)))
    p1.checks.append(_check("index session notes set", bool(index_h.notes)))
    reports.append(p1)

    # --- Phase 2 ---
    p2 = PhaseReport("Phase 2 — Equity plumbing")
    p2.checks.append(_check("news categories include merger", "merger" in DEFAULT_CATEGORIES, str(DEFAULT_CATEGORIES)))
    eq_h = _trading_hours_default(asset_class="equity")
    p2.checks.append(
        _check(
            "equity RTH defaults",
            eq_h.timezone == "America/New_York" and "new_york" in eq_h.sessions,
            f"tz={eq_h.timezone} sessions={eq_h.sessions}",
        )
    )
    for sym in EQUITIES + MATERIALS + EXTRA_INDICES:
        p2.checks.append(_check(f"{sym} depth-gated", sym in DEPTH_GATED_SYMBOLS))
    peers = default_peer_symbols(session, "AAPL", asset_class="equity")
    p2.checks.append(_check("equity peers exclude FX", "EURUSD" not in peers, f"peers={peers}"))
    p2.checks.append(
        _check(
            "equity peers include index anchors",
            all(a in peers for a in EQUITY_INDEX_ANCHORS),
            f"peers={peers}",
        )
    )
    fx_peers = default_peer_symbols(session, "EURUSD", asset_class="fx")
    p2.checks.append(_check("FX peers stay FX", "AAPL" not in fx_peers, f"peers={fx_peers}"))
    mapper = NewsAssetMapper(set(assets))
    from datetime import UTC, datetime

    from app.ingestion.news.client import RawNewsArticle

    art = RawNewsArticle(
        provider="test",
        provider_id="1",
        headline="Apple and NVIDIA rise; WTI crude soft",
        summary=None,
        url=None,
        source_name="t",
        published_at=datetime.now(UTC),
        related=None,
        category="merger",
        raw={},
    )
    mapped = mapper.map_article(art).symbols
    p2.checks.append(_check("news maps AAPL", "AAPL" in mapped, str(mapped)))
    p2.checks.append(_check("news maps NVDA", "NVDA" in mapped, str(mapped)))
    p2.checks.append(_check("news maps XTIUSD", "XTIUSD" in mapped, str(mapped)))
    us_syms = map_country_symbols("US", set(assets))
    p2.checks.append(_check("US calendar omits equities", "AAPL" not in us_syms, str(us_syms[:8])))
    reports.append(p2)

    # --- Phase 3 ---
    p3 = PhaseReport("Phase 3 — Ten equities live")
    p3.checks.append(_check("active universe >= 30", active >= 30, f"active={active} by_class={by_class}"))
    p3.checks.append(_check("alembic >= 0014", str(alembic) >= "0014", f"alembic={alembic}"))
    for sym in EQUITIES:
        row = assets.get(sym)
        bars, _mn, mx = depth_rows.get(sym, (0, None, None))
        span = m1_depth_days(session, sym)
        h1 = h1_counts.get(sym, 0)
        p3.checks.append(_check(f"{sym} seeded equity", row is not None and row.asset_class == "equity", row and row.mt5_ticker))
        p3.checks.append(_check(f"{sym} has M1", bars > 10_000, f"bars={bars} max={mx}"))
        p3.checks.append(
            _check(
                f"{sym} depth gate",
                passes_depth_gate(sym, m1_span_days_value=span),
                f"span={span:.1f}d need>={MIN_CORR_REGIME_DEPTH_DAYS}",
            )
        )
        p3.checks.append(_check(f"{sym} H1 CAGG", h1 > 0, f"h1_rows={h1}"))
        p3.checks.append(_check(f"{sym} profile row", sym in profile_syms))
        try:
            profile = build_asset_profile_from_session(session, sym)
            p3.checks.append(
                _check(
                    f"{sym} peer corrs",
                    len(profile.correlations) >= 5,
                    f"corrs={len(profile.correlations)} tz={profile.trading_hours.timezone}",
                )
            )
        except Exception as exc:  # noqa: BLE001
            p3.checks.append(_check(f"{sym} build profile", False, str(exc)))
    reports.append(p3)

    # --- Phase 4 ---
    p4 = PhaseReport("Phase 4 — Energy materials")
    for sym in MATERIALS:
        row = assets.get(sym)
        bars, _mn, mx = depth_rows.get(sym, (0, None, None))
        p4.checks.append(_check(f"{sym} seeded metal", row is not None and row.asset_class == "metal", row and row.display_name))
        p4.checks.append(_check(f"{sym} has M1", bars > 100_000, f"bars={bars} max={mx}"))
        p4.checks.append(_check(f"{sym} profile", sym in profile_syms))
        try:
            profile = build_asset_profile_from_session(session, sym)
            peer_syms = {c.symbol for c in profile.correlations}
            p4.checks.append(
                _check(
                    f"{sym} metal-cluster peers",
                    len(profile.correlations) >= 2 and "EURUSD" not in peer_syms,
                    f"peers={sorted(peer_syms)}",
                )
            )
        except Exception as exc:  # noqa: BLE001
            p4.checks.append(_check(f"{sym} build profile", False, str(exc)))
    reports.append(p4)

    # --- Phase 5 ---
    p5 = PhaseReport("Phase 5 — Extra indices")
    for sym in EXTRA_INDICES:
        row = assets.get(sym)
        bars, _mn, mx = depth_rows.get(sym, (0, None, None))
        p5.checks.append(_check(f"{sym} seeded index", row is not None and row.asset_class == "index", row and row.mt5_ticker))
        p5.checks.append(_check(f"{sym} has M1", bars > 50_000, f"bars={bars} max={mx}"))
        p5.checks.append(_check(f"{sym} profile", sym in profile_syms))
    de = map_country_symbols("DE", set(assets))
    gb = map_country_symbols("GB", set(assets))
    jp = map_country_symbols("JP", set(assets))
    p5.checks.append(_check("DE calendar maps DE40", "DE40" in de, str(de)))
    p5.checks.append(_check("GB calendar maps UK100", "UK100" in gb, str(gb)))
    p5.checks.append(_check("JP calendar maps JP225", "JP225" in jp, str(jp)))
    for sym in EXTRA_INDICES:
        try:
            profile = build_asset_profile_from_session(session, sym)
            peer_syms = {c.symbol for c in profile.correlations}
            p5.checks.append(
                _check(
                    f"{sym} index peers",
                    len(profile.correlations) >= 3 and "AAPL" not in peer_syms,
                    f"peers={sorted(peer_syms)}",
                )
            )
        except Exception as exc:  # noqa: BLE001
            p5.checks.append(_check(f"{sym} build profile", False, str(exc)))
    reports.append(p5)

    session.close()

    # Print report
    total_ok = total_fail = 0
    print("=" * 72)
    print("UNIVERSE EXPANSION VERIFICATION REPORT")
    print("=" * 72)
    for rep in reports:
        total_ok += rep.passed
        total_fail += rep.failed
        status = "PASS" if rep.failed == 0 else "FAIL"
        print(f"\n## {rep.title}  [{status}]  {rep.passed}/{rep.passed + rep.failed}")
        for c in rep.checks:
            mark = "OK" if c.ok else "XX"
            extra = f" — {c.detail}" if c.detail else ""
            print(f"  [{mark}] {c.name}{extra}")

    print("\n" + "=" * 72)
    print(f"TOTAL  ok={total_ok}  fail={total_fail}  alembic={alembic}  active_assets={active}")
    print("=" * 72)
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
