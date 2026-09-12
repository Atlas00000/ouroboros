#!/usr/bin/env python3
"""Phase 1 (Weeks 2–3) ingestion verification — run from repo root.

Usage:
  py -3.12 scripts/test_phase1.py
  py -3.12 scripts/test_phase1.py --skip-live     # pytest + structure only
  py -3.12 scripts/test_phase1.py --with-mt5      # also smoke_connect (conflicts with running backfill)

Skips live MT5 poll/backfill by default so an in-progress historical backfill is not interrupted.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server"
IS_WIN = os.name == "nt"
PY = [sys.executable]


class StepError(RuntimeError):
    pass


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print(f"\n>> {' '.join(args)}" + (f"  (cwd={cwd})" if cwd else ""))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        env=merged,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        err = result.stderr.rstrip()
        if err:
            print(err)
    if check and result.returncode != 0:
        raise StepError(f"Command failed ({result.returncode}): {' '.join(args)}")
    return result


def step_structure() -> None:
    required = [
        ROOT / "server" / "app" / "calendar",
        ROOT / "server" / "app" / "ingestion" / "mt5",
        ROOT / "server" / "app" / "ingestion" / "news",
        ROOT / "server" / "app" / "ingestion" / "econ_calendar",
        ROOT / "server" / "app" / "ingestion" / "macro",
        ROOT / "server" / "app" / "ingestion" / "registry.py",
        ROOT / "server" / "app" / "ingestion" / "httputil.py",
        ROOT / "server" / "app" / "watchdog",
        ROOT / "server" / "app" / "notifications",
        ROOT / "ops" / "mt5-worker" / "backfill.py",
        ROOT / "ops" / "mt5-worker" / "poll.py",
        ROOT / "ops" / "news-worker" / "poll.py",
        ROOT / "ops" / "news-worker" / "poll_calendar.py",
        ROOT / "ops" / "macro-worker" / "poll.py",
        ROOT / "ops" / "watchdog" / "run.py",
        ROOT / "ops" / "notifications" / "send_test.py",
        ROOT / "ops" / "soak" / "feed_status.py",
        ROOT / "ops" / "backups" / "backup_full.py",
        ROOT / "docs" / "runbooks" / "feed-down.md",
        ROOT / "docs" / "runbooks" / "restore-from-backup.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise StepError(f"Missing Phase 1 paths: {missing}")
    print("structure OK")


def step_migrate() -> None:
    run([*PY, "-m", "alembic", "upgrade", "head"], cwd=SERVER)


def step_pytest_phase1() -> None:
    tests = [
        "tests/test_calendar.py",
        "tests/test_symbol_mapper.py",
        "tests/test_price_writer.py",
        "tests/test_poller_gaps.py",
        "tests/test_registry.py",
        "tests/test_watchdog.py",
        "tests/test_news_ingestion.py",
        "tests/test_w3d2_calendar_macro.py",
        "tests/test_httputil.py",
        "tests/test_ingestion_fixtures.py",
        "tests/test_notifications.py",
    ]
    run([*PY, "-m", "pytest", *tests, "-q"], cwd=SERVER)


def step_live_news() -> None:
    run([*PY, str(ROOT / "ops" / "news-worker" / "poll.py")], cwd=SERVER)


def step_live_calendar() -> None:
    run([*PY, str(ROOT / "ops" / "news-worker" / "poll_calendar.py")], cwd=SERVER)


def step_live_macro() -> None:
    # Short lookback — proves FRED path without re-pulling full history.
    run(
        [*PY, str(ROOT / "ops" / "macro-worker" / "poll.py"), "--lookback-days", "30", "--series", "DFF"],
        cwd=SERVER,
    )


def step_feed_status() -> None:
    # Exit 1 if stale is allowed during soak; still print snapshot.
    result = run(
        [*PY, str(ROOT / "ops" / "soak" / "feed_status.py")],
        cwd=SERVER,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise StepError(f"feed_status failed ({result.returncode})")


def step_watchdog() -> None:
    result = run(
        [*PY, str(ROOT / "ops" / "watchdog" / "run.py"), "check"],
        cwd=SERVER,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise StepError(f"watchdog check failed ({result.returncode})")


def step_notify_log() -> None:
    run(
        [*PY, str(ROOT / "ops" / "notifications" / "send_test.py"), "--channel", "log"],
        cwd=SERVER,
    )


def step_backup_targeted() -> None:
    run([*PY, str(ROOT / "ops" / "backups" / "backup_targeted.py")], cwd=ROOT)


def step_mt5_smoke() -> None:
    run([*PY, str(ROOT / "ops" / "mt5-worker" / "smoke_connect.py")], cwd=SERVER)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 ingestion verification")
    parser.add_argument("--skip-live", action="store_true", help="Skip live HTTP feed smokes")
    parser.add_argument(
        "--with-mt5",
        action="store_true",
        help="Run MT5 smoke_connect (do not use while backfill/poller holds IPC)",
    )
    args = parser.parse_args()

    steps: list[tuple[str, Callable[[], None]]] = [
        ("structure", step_structure),
        ("migrate", step_migrate),
        ("pytest_phase1", step_pytest_phase1),
    ]
    if not args.skip_live:
        steps.extend(
            [
                ("live_news", step_live_news),
                ("live_calendar", step_live_calendar),
                ("live_macro", step_live_macro),
                ("feed_status", step_feed_status),
                ("watchdog", step_watchdog),
                ("notify_log", step_notify_log),
                ("backup_targeted", step_backup_targeted),
            ]
        )
    if args.with_mt5:
        steps.append(("mt5_smoke", step_mt5_smoke))

    failed: list[str] = []
    for name, fn in steps:
        print(f"\n== {name} ==")
        try:
            fn()
            print(f"PASS {name}")
        except StepError as exc:
            print(f"FAIL {name}: {exc}")
            failed.append(name)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {name}: {exc}")
            failed.append(name)

    print("\n" + "=" * 60)
    if failed:
        print(f"PHASE 1 RESULT: FAILED ({len(failed)}) — {', '.join(failed)}")
        return 1
    print(f"PHASE 1 RESULT: ALL PASSED ({len(steps)} steps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
