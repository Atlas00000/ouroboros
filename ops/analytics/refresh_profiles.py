"""CLI: run event-triggered profile refresh + optional retention prune."""

from __future__ import annotations

import argparse
import os
import sys

# Allow `py -3.12 ops/analytics/refresh_profiles.py` from repo root
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SERVER = os.path.join(_REPO, "server")
if _SERVER not in sys.path:
    sys.path.insert(0, _SERVER)
os.chdir(_SERVER)

from app.analytics.profile_refresh import run_event_triggered_refresh  # noqa: E402
from app.analytics.profile_store import prune_profiles  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Event-triggered AssetProfile refresh")
    parser.add_argument("--symbols", nargs="*", default=None, help="Limit to symbols")
    parser.add_argument("--force", action="store_true", help="Ignore 1h cooldown")
    parser.add_argument("--prune", action="store_true", help="Run 180d last-of-day prune")
    parser.add_argument("--no-outbox", action="store_true")
    args = parser.parse_args()

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        report = run_event_triggered_refresh(
            session,
            symbols=args.symbols,
            force=args.force,
            enqueue_outbox=not args.no_outbox,
            commit=True,
        )
        print(
            f"triggers={len(report.triggers)} refreshed={report.refreshed} "
            f"outcomes={len(report.outcomes)}"
        )
        for o in report.outcomes:
            print(f"  {o.symbol} {o.status} v={o.profile_version} ({o.reason}) {o.detail}")
        if args.prune:
            result = prune_profiles(session, use_sql_function=True)
            session.commit()
            print(f"prune deleted={result.deleted}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
