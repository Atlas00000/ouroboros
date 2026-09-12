"""CLI: watchdog check, kill-feed drill, gap report."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402
from app.watchdog.checker import run_check  # noqa: E402
from app.watchdog.gap_report import build_gap_report  # noqa: E402
from app.watchdog.kill_feed_drill import run_kill_feed_drill  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ouroboros watchdog / integrity tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    check = sub.add_parser("check", help="Cadence check + stale propagation + log alerts")
    check.add_argument(
        "--notify",
        action="store_true",
        help="Also send alert digest via ALERT_CHANNEL (Resend/Telegram/webhook)",
    )

    drill = sub.add_parser("kill-feed-drill", help="Simulate a silenced feed (no MT5 stop)")
    drill.add_argument("--source", default="finnhub.news")
    drill.add_argument(
        "--notify",
        action="store_true",
        help="Send notification digest if drill produces alerts",
    )

    gaps = sub.add_parser("gap-report", help="M1 backfill integrity gap scan")
    gaps.add_argument("--symbols", default="", help="Comma-separated subset (default: all active)")
    gaps.add_argument("--min-hole-minutes", type=int, default=2)

    args = parser.parse_args()
    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    session = get_session_factory()()
    try:
        if args.cmd == "check":
            report = run_check(session, notify=args.notify)
            print(
                f"watchdog check sources={len(report.sources)} "
                f"stale={report.stale_count} alerts={len(report.alerts)} "
                f"propagated={report.rows_marked_stale}"
            )
            for s in report.sources:
                age = f"{s.age_seconds:.0f}s" if s.age_seconds is not None else "never"
                print(
                    f"  {s.source_id:20} status={s.status:8} age={age} stale={s.stale}"
                )
            for a in report.alerts:
                print(f"ALERT {a.message}")
            return 1 if report.alerts else 0

        if args.cmd == "kill-feed-drill":
            result = run_kill_feed_drill(session, source_id=args.source)
            print(f"kill-feed drill passed={result.passed} {result.detail}")
            if args.notify and result.report.alerts:
                from app.watchdog.notify import notify_watchdog_report

                nr = notify_watchdog_report(result.report)
                print(f"notify ok={nr.ok if nr else None} detail={nr.detail if nr else None}")
            return 0 if result.passed else 1

        if args.cmd == "gap-report":
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None
            report = build_gap_report(
                session,
                symbols=symbols,
                min_hole_minutes=args.min_hole_minutes,
            )
            print(
                f"gap report symbols={len(report.symbols)} "
                f"with_gaps={report.symbols_with_gaps} at={report.generated_at.isoformat()}"
            )
            for s in report.symbols:
                print(
                    f"  {s.symbol:8} bars={s.bar_count:>8} gaps={s.gap_count:>3} "
                    f"missing_min={s.missing_minutes_total} "
                    f"range={s.min_ts} .. {s.max_ts}"
                )
                for g in s.gaps[:5]:
                    print(
                        f"    hole {g.from_ts} -> {g.to_ts} missing={g.missing_minutes}m"
                    )
                if s.gap_count > 5:
                    print(f"    ... {s.gap_count - 5} more holes")
            return 0
    finally:
        session.close()

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
