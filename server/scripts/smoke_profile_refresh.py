"""Smoke: event-triggered profile refresh + retention prune for EURUSD."""

from __future__ import annotations

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from app.analytics.profile_refresh import refresh_symbol_profile, run_event_triggered_refresh
from app.analytics.profile_store import prune_profiles
from app.config import get_settings
from app.db.session import get_session_factory


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        # Force one refresh for EURUSD (bypass trigger scan) with limited peers
        peers = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
        forced = refresh_symbol_profile(
            session,
            "EURUSD",
            reason="manual",
            detail="w5d2-smoke",
            peer_symbols=peers,
            force=True,
            enqueue_outbox=True,
        )
        session.commit()
        print(
            f"forced: status={forced.status} version={forced.profile_version} "
            f"detail={forced.detail}"
        )

        # Second call within cooldown should skip
        skipped = refresh_symbol_profile(
            session,
            "EURUSD",
            reason="manual",
            peer_symbols=peers,
            force=False,
        )
        session.commit()
        print(f"cooldown: status={skipped.status}")

        report = run_event_triggered_refresh(
            session,
            symbols=["EURUSD"],
            peer_symbols=peers,
            force=False,
            commit=True,
        )
        print(
            f"triggers={len(report.triggers)} outcomes={len(report.outcomes)} "
            f"refreshed={report.refreshed}"
        )
        for t in report.triggers:
            print(f"  trigger {t.symbol} {t.reason} {t.detail}")

        pruned = prune_profiles(session, retention_days=180, use_sql_function=True)
        session.commit()
        print(f"prune deleted={pruned.deleted} cutoff={pruned.cutoff.isoformat()}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
