"""Smoke: build profile.v1 AssetProfile for EURUSD from local DB."""

from __future__ import annotations

import json
import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from app.analytics.profiles import build_asset_profile_from_session
from app.config import get_settings
from app.db.session import get_session_factory


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        # Limit peers for speed; full-universe corrs still available via API later
        profile = build_asset_profile_from_session(
            session,
            "EURUSD",
            peer_symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "SPX500"],
        )
        data = profile.model_dump(mode="json")
        print(f"schema_id={data['schema_id']} version={data['profile_version']}")
        print(f"symbol={data['identity']['symbol']} as_of={data['as_of']}")
        print(
            f"vol atr_pct={data['volatility']['atr_percentile_30d']} "
            f"rv_pct={data['volatility']['realized_vol_percentile_30d']} "
            f"typical_range={data['volatility']['typical_daily_range']}"
        )
        print(f"liquidity notes={data['liquidity']['notes']}")
        print(f"correlations={len(data['correlations'])}")
        for c in data["correlations"][:5]:
            print(f"  {c['symbol']}: {c['coefficient']:.3f} ({c['window_days']}d)")
        print("regime_distribution:")
        for d in data["regime_distribution"]:
            print(f"  {d['regime']}: {d['share']:.3f}")
        print(
            f"provenance model={data['provenance']['model_version']} "
            f"confidence={data['provenance']['confidence']}"
        )
        # Compact JSON for piping
        print("---")
        print(json.dumps({"ok": True, "symbol": data["identity"]["symbol"]}, indent=2))
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
