"""EURUSD 2y monthly regime audit + asset profile dossier export.

Research-only. Ex-post calendar-month boards via fit.map_v0.
"""

from __future__ import annotations

import calendar
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.fit.boards import board_from_ohlcv, board_from_regimes
from app.analytics.fit.mapper import MODEL_VERSION as FIT_MODEL
from app.analytics.profiles import build_asset_profile_from_session
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL_VERSION, regime_feature_frame
from app.config import get_settings
from app.db.session import get_engine, get_session_factory

SYMBOL = "EURUSD"
LOOKBACK_DAYS = 800


def _month_ends(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[str, pd.Timestamp]]:
    cur = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
    out: list[tuple[str, pd.Timestamp]] = []
    while cur <= end:
        last_day = calendar.monthrange(cur.year, cur.month)[1]
        me = pd.Timestamp(
            year=cur.year, month=cur.month, day=last_day, hour=23, minute=59, tz="UTC"
        )
        out.append((f"{cur.year:04d}-{cur.month:02d}", me))
        if cur.month == 12:
            cur = pd.Timestamp(year=cur.year + 1, month=1, day=1, tz="UTC")
        else:
            cur = pd.Timestamp(year=cur.year, month=cur.month + 1, day=1, tz="UTC")
    return out


def _boards_for(
    feat: pd.DataFrame, tf: str, family: str, months: list[tuple[str, pd.Timestamp]]
) -> list[dict]:
    rows: list[dict] = []
    ts = pd.to_datetime(feat["ts"], utc=True)
    for month_key, me in months:
        ms = me.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mask = (ts >= ms) & (ts <= me)
        sliced = feat.loc[mask]
        regimes = [str(r) for r in sliced["confirmed_regime"].dropna().tolist()]
        board = board_from_regimes(regimes, family, window="calendar_month")
        dom = None
        if board.regime_shares:
            dom = max(board.regime_shares.items(), key=lambda kv: kv[1])[0]
        rows.append(
            {
                "month": month_key,
                "timeframe": tf,
                "family": family,
                "tag": board.tag,
                "bar_count": board.bar_count,
                "shares": board.shares,
                "regime_shares": board.regime_shares,
                "dominant_regime": dom,
            }
        )
    return rows


def _monthly_price(df_d1: pd.DataFrame) -> list[dict]:
    d1 = df_d1.copy()
    d1["ts"] = pd.to_datetime(d1["ts"], utc=True)
    d1["ym"] = d1["ts"].dt.strftime("%Y-%m")
    monthly_px: list[dict] = []
    for ym, g in d1.groupby("ym", sort=True):
        o = float(g["open"].iloc[0])
        c = float(g["close"].iloc[-1])
        monthly_px.append(
            {
                "month": ym,
                "open": round(o, 5),
                "high": round(float(g["high"].max()), 5),
                "low": round(float(g["low"].min()), 5),
                "close": round(c, 5),
                "ret_pct": round((c / o - 1.0) * 100.0, 2) if o else None,
            }
        )
    return monthly_px


def _regime_month_table(boards: list[dict], tf: str) -> list[dict]:
    """One row per month: dominant H1/D1 regime + both family tags."""
    by_month: dict[str, dict] = {}
    for b in boards:
        if b["timeframe"] != tf or b["bar_count"] <= 0:
            continue
        row = by_month.setdefault(
            b["month"],
            {
                "month": b["month"],
                "bar_count": b["bar_count"],
                "dominant_regime": b["dominant_regime"],
                "regime_shares": b["regime_shares"],
            },
        )
        row[f"{b['family']}_tag"] = b["tag"]
        row[f"{b['family']}_shares"] = b["shares"]
    return [by_month[k] for k in sorted(by_month)]


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    eng = get_engine()
    try:
        profile = build_asset_profile_from_session(
            session, SYMBOL, lookback_days=LOOKBACK_DAYS
        )
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=LOOKBACK_DAYS)
        df_d1 = load_ohlcv(session, SYMBOL, "D1", lookback_days=LOOKBACK_DAYS)
        feat_h1 = regime_feature_frame(df_h1, "H1")
        feat_d1 = regime_feature_frame(df_d1, "D1")

        start = pd.to_datetime(feat_h1["ts"].iloc[0], utc=True)
        end = pd.to_datetime(feat_h1["ts"].iloc[-1], utc=True)
        months = _month_ends(start, end)

        all_boards: list[dict] = []
        for tf, feat in (("H1", feat_h1), ("D1", feat_d1)):
            for fam in ("meanrev", "trendfollow"):
                all_boards.extend(_boards_for(feat, tf, fam, months))

        summary: dict[tuple[str, str], Counter] = defaultdict(Counter)
        for b in all_boards:
            if b["bar_count"] > 0:
                summary[(b["timeframe"], b["family"])][b["tag"]] += 1

        with eng.connect() as c:
            st = c.execute(
                text(
                    """
                    SELECT timeframe, regime, probabilities_json, volatility_percentile,
                           trend_strength, as_of, model_version, confidence, stale
                    FROM states
                    WHERE symbol = :s AND timeframe = 'H1'
                    ORDER BY as_of DESC LIMIT 1
                    """
                ),
                {"s": SYMBOL},
            ).mappings().first()
            sent = c.execute(
                text(
                    """
                    SELECT score, item_count, window_hours, top_drivers_json, as_of,
                           model_version, confidence, stale
                    FROM sentiment WHERE symbol = :s
                    ORDER BY as_of DESC LIMIT 1
                    """
                ),
                {"s": SYMBOL},
            ).mappings().first()
            insight = c.execute(
                text(
                    """
                    SELECT insight_type, title, body, tags_json, related_refs_json,
                           as_of, model_version, confidence, stale
                    FROM insights WHERE symbol = :s
                    ORDER BY as_of DESC LIMIT 1
                    """
                ),
                {"s": SYMBOL},
            ).mappings().first()
            news_sample = c.execute(
                text(
                    """
                    SELECT headline, source, url, published_at, event_type, impact
                    FROM news WHERE symbol = :s
                    ORDER BY published_at DESC LIMIT 12
                    """
                ),
                {"s": SYMBOL},
            ).mappings().all()
            news_count = c.execute(
                text("SELECT count(*) FROM news WHERE symbol = :s"), {"s": SYMBOL}
            ).scalar()

        fit_mr = board_from_ohlcv(df_h1, "meanrev", timeframe="H1", window="30d")
        fit_tf = board_from_ohlcv(df_h1, "trendfollow", timeframe="H1", window="30d")

        out = {
            "symbol": SYMBOL,
            "generated_at": datetime.now(UTC).isoformat(),
            "disclaimer": (
                "Research / advisory only. Ex-post monthly MATCH boards are not "
                "profit claims. fit.map_v0 gates research books — not execution."
            ),
            "models": {
                "fit": FIT_MODEL,
                "regime": REGIME_MODEL_VERSION,
                "profile": profile.provenance.model_version,
            },
            "data_range": {
                "h1_start": str(df_h1["ts"].iloc[0]),
                "h1_end": str(df_h1["ts"].iloc[-1]),
                "d1_start": str(df_d1["ts"].iloc[0]),
                "d1_end": str(df_d1["ts"].iloc[-1]),
                "m1_depth_days": m1_depth_days(session, SYMBOL),
                "months": [m[0] for m in months],
                "month_count": len(months),
            },
            "profile": json.loads(profile.model_dump_json()),
            "nowcast": {
                "state": dict(st) if st else None,
                "fit_30d_h1": {
                    "meanrev": {
                        "tag": fit_mr.tag,
                        "shares": fit_mr.shares,
                        "regime_shares": fit_mr.regime_shares,
                        "bar_count": fit_mr.bar_count,
                    },
                    "trendfollow": {
                        "tag": fit_tf.tag,
                        "shares": fit_tf.shares,
                        "regime_shares": fit_tf.regime_shares,
                        "bar_count": fit_tf.bar_count,
                    },
                },
                "sentiment": dict(sent) if sent else None,
                "insight": dict(insight) if insight else None,
            },
            "news_count": int(news_count or 0),
            "recent_news": [dict(n) for n in news_sample],
            "monthly_boards": all_boards,
            "monthly_regime_table_h1": _regime_month_table(all_boards, "H1"),
            "monthly_regime_table_d1": _regime_month_table(all_boards, "D1"),
            "monthly_price": _monthly_price(df_d1),
            "tag_summary": {
                f"{tf}|{fam}": dict(summary[(tf, fam)]) for tf, fam in summary
            },
        }

        repo = Path(__file__).resolve().parents[2]
        out_dir = repo / "research" / "assets" / "EURUSD"
        out_dir.mkdir(parents=True, exist_ok=True)
        raw_path = out_dir / "audit.json"
        raw_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(f"wrote {raw_path} ({raw_path.stat().st_size} bytes)")
        print("tag_summary", out["tag_summary"])
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
