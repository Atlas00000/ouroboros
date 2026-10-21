"""Rebuild asset profiles for a symbol list (ops helper for universe expansion)."""

from __future__ import annotations

import argparse
import sys

from app.analytics.profile_store import next_profile_version, persist_asset_profile
from app.analytics.profiles import build_asset_profile_from_session
from app.db.session import get_session_factory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--symbols",
        required=True,
        help="Comma-separated canonical symbols",
    )
    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    session = get_session_factory()()
    try:
        for sym in symbols:
            ver = next_profile_version(session, sym)
            profile = build_asset_profile_from_session(session, sym, profile_version=ver)
            persist_asset_profile(session, profile, enqueue_outbox=False)
            print(
                f"{sym} ok v={ver} corrs={len(profile.correlations)} "
                f"class={profile.identity.asset_class} "
                f"tz={profile.trading_hours.timezone}"
            )
        session.commit()
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
