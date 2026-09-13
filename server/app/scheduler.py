"""APScheduler worker entrypoint — ``python -m app.scheduler`` (Phase 2 W5·D4).

Runs outside the API process so jobs never double-fire with replica scale-out.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from datetime import UTC, datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app import __version__
from app.analytics.bars import load_ohlcv
from app.analytics.forecast_log import classify_and_log_regimes
from app.analytics.metrics import compute_metric_snapshot
from app.analytics.profile_refresh import refresh_symbol_profile, run_event_triggered_refresh
from app.analytics.profile_store import prune_profiles
from app.config import get_settings
from app.db.session import get_session_factory
from app.models.asset import Asset
from app.observability.logging import configure_logging
from app.observability.sentry import init_sentry

logger = logging.getLogger("ouroboros.scheduler")

# Cadences (UTC). Tunable later via settings if needed.
METRICS_INTERVAL_MINUTES = 15
REGIME_LOG_INTERVAL_MINUTES = 15
PROFILE_EVENTS_INTERVAL_MINUTES = 15
OUTBOX_RELAY_INTERVAL_SECONDS = 30
DAILY_PROFILES_CRON_HOUR = 0
DAILY_PROFILES_CRON_MINUTE = 15
PRUNE_CRON_HOUR = 0
PRUNE_CRON_MINUTE = 45
METRICS_TIMEFRAMES = ("H1", "H4", "D1")


def _active_symbols(session) -> list[str]:
    return [
        str(s)
        for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
    ]


def job_metrics_cadence() -> None:
    """Compute metrics.v1 snapshots for active symbols (no persistence yet)."""
    session = get_session_factory()()
    try:
        symbols = _active_symbols(session)
        ok = 0
        empty = 0
        for sym in symbols:
            for tf in METRICS_TIMEFRAMES:
                df = load_ohlcv(session, sym, tf, lookback_days=90)
                if df.empty:
                    empty += 1
                    continue
                compute_metric_snapshot(df, symbol=sym, timeframe=tf)
                ok += 1
        logger.info(
            "metrics_cadence done symbols=%s snapshots=%s empty=%s",
            len(symbols),
            ok,
            empty,
        )
    except Exception:
        logger.exception("metrics_cadence failed")
        raise
    finally:
        session.close()


def job_regime_log() -> None:
    """Classify latest regimes → forecast_log + states (+ regime.changed outbox)."""
    session = get_session_factory()()
    try:
        report = classify_and_log_regimes(session, commit=True)
        logger.info(
            "regime_log inserted=%s dupes=%s errors=%s",
            report.inserted,
            report.skipped_dupes,
            len(report.errors),
        )
    except Exception:
        logger.exception("regime_log failed")
        raise
    finally:
        session.close()


def job_outbox_relay() -> None:
    """Publish unpublished outbox rows to Redis Streams."""
    from app.events.relay import relay_unpublished

    session = get_session_factory()()
    try:
        result = relay_unpublished(session)
        session.commit()
        logger.info(
            "outbox_relay published=%s failed=%s",
            result.published,
            result.failed,
        )
    except Exception:
        logger.exception("outbox_relay failed")
        session.rollback()
        raise
    finally:
        session.close()


def job_profile_events() -> None:
    """Event-triggered profile refresh (regime flip + high-impact calendar)."""
    session = get_session_factory()()
    try:
        report = run_event_triggered_refresh(session, commit=True)
        logger.info(
            "profile_events triggers=%s refreshed=%s",
            len(report.triggers),
            report.refreshed,
        )
    except Exception:
        logger.exception("profile_events failed")
        raise
    finally:
        session.close()


def job_daily_profiles() -> None:
    """Daily 00:15 UTC full-universe profile rebuild (bypasses 1h debounce)."""
    session = get_session_factory()()
    try:
        symbols = _active_symbols(session)
        refreshed = 0
        errors = 0
        for sym in symbols:
            outcome = refresh_symbol_profile(
                session,
                sym,
                reason="manual",
                detail="daily_00:15_utc",
                force=True,
                enqueue_outbox=True,
            )
            if outcome.status == "refreshed":
                refreshed += 1
            elif outcome.status == "skipped_error":
                errors += 1
                logger.warning("daily_profiles %s: %s", sym, outcome.detail)
        session.commit()
        logger.info(
            "daily_profiles refreshed=%s errors=%s symbols=%s",
            refreshed,
            errors,
            len(symbols),
        )
    except Exception:
        logger.exception("daily_profiles failed")
        session.rollback()
        raise
    finally:
        session.close()


def job_prune_profiles() -> None:
    """180d then last-of-day profile retention prune."""
    session = get_session_factory()()
    try:
        result = prune_profiles(session, use_sql_function=True)
        session.commit()
        logger.info(
            "prune_profiles deleted=%s retention_days=%s",
            result.deleted,
            result.retention_days,
        )
    except Exception:
        logger.exception("prune_profiles failed")
        session.rollback()
        raise
    finally:
        session.close()


def job_sentiment_refresh() -> None:
    """Score unseen news + refresh sentiment.v1 aggregates (W7·D3)."""
    from app.intelligence.sentiment import run_sentiment_tick

    session = get_session_factory()()
    try:
        report = run_sentiment_tick(session, commit=True)
        logger.info(
            "sentiment_refresh scored=%s cached=%s symbols=%s spikes=%s high_impact=%s",
            report.articles_scored,
            report.articles_cached,
            report.symbols_updated,
            report.spikes,
            report.high_impact,
        )
    except Exception:
        logger.exception("sentiment_refresh failed")
        raise
    finally:
        session.close()


def job_narratives_refresh() -> None:
    """Generate labeled narratives from latest state/sentiment (W7·D4)."""
    from app.intelligence.narratives import run_narrative_tick

    session = get_session_factory()()
    try:
        symbols = _active_symbols(session)
        report = run_narrative_tick(session, symbols, commit=True)
        logger.info(
            "narratives_refresh generated=%s skipped=%s",
            report.generated,
            report.skipped,
        )
    except Exception:
        logger.exception("narratives_refresh failed")
        raise
    finally:
        session.close()


def job_score_regime_calls() -> None:
    """Fill realized outcomes on due forecast_log regime rows (W8·D1)."""
    from app.scoring.regime_accuracy import score_due_regime_calls

    session = get_session_factory()()
    try:
        report = score_due_regime_calls(session, commit=True)
        logger.info(
            "score_regime_calls scored=%s correct=%s skipped=%s errors=%s",
            report.scored,
            report.correct,
            report.skipped,
            len(report.errors),
        )
    except Exception:
        logger.exception("score_regime_calls failed")
        raise
    finally:
        session.close()


def job_weekly_scoring() -> None:
    """Weekly accuracy tables + Resend digest (W8·D1)."""
    from app.scoring.weekly import run_weekly_scoring

    session = get_session_factory()()
    try:
        result = run_weekly_scoring(session, send_email=True, commit=True)
        logger.info(
            "weekly_scoring report_id=%s accuracy=%s email_ok=%s",
            result.report_row_id,
            result.report.accuracy,
            result.email_ok,
        )
    except Exception:
        logger.exception("weekly_scoring failed")
        raise
    finally:
        session.close()


def job_watchdog_check() -> None:
    """Cadence check → stale propagation → Resend on prolonged staleness (W8·D2)."""
    from app.watchdog.checker import run_check

    session = get_session_factory()()
    try:
        report = run_check(session, propagate=True, notify=True)
        logger.info(
            "watchdog_check stale=%s alerts=%s marked=%s",
            report.stale_count,
            len(report.alerts),
            report.rows_marked_stale,
        )
    except Exception:
        logger.exception("watchdog_check failed")
        raise
    finally:
        session.close()


JOB_FUNCS = {
    "metrics_cadence": job_metrics_cadence,
    "regime_log": job_regime_log,
    "profile_events": job_profile_events,
    "outbox_relay": job_outbox_relay,
    "daily_profiles": job_daily_profiles,
    "prune_profiles": job_prune_profiles,
    "sentiment_refresh": job_sentiment_refresh,
    "narratives_refresh": job_narratives_refresh,
    "score_regime_calls": job_score_regime_calls,
    "weekly_scoring": job_weekly_scoring,
    "watchdog_check": job_watchdog_check,
}


def build_scheduler() -> BlockingScheduler:
    """Register analytics + intelligence + scoring + watchdog jobs (UTC)."""
    settings = get_settings()
    sentiment_minutes = max(1, int(settings.sentiment_interval_minutes))
    narrative_minutes = max(15, sentiment_minutes * 2)
    watchdog_minutes = max(1, int(settings.watchdog_interval_minutes))

    sched = BlockingScheduler(timezone="UTC")
    sched.add_job(
        job_metrics_cadence,
        IntervalTrigger(minutes=METRICS_INTERVAL_MINUTES),
        id="metrics_cadence",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_regime_log,
        IntervalTrigger(minutes=REGIME_LOG_INTERVAL_MINUTES),
        id="regime_log",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_profile_events,
        IntervalTrigger(minutes=PROFILE_EVENTS_INTERVAL_MINUTES),
        id="profile_events",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_outbox_relay,
        IntervalTrigger(seconds=OUTBOX_RELAY_INTERVAL_SECONDS),
        id="outbox_relay",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_sentiment_refresh,
        IntervalTrigger(minutes=sentiment_minutes),
        id="sentiment_refresh",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_narratives_refresh,
        IntervalTrigger(minutes=narrative_minutes),
        id="narratives_refresh",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_score_regime_calls,
        IntervalTrigger(hours=1),
        id="score_regime_calls",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_watchdog_check,
        IntervalTrigger(minutes=watchdog_minutes),
        id="watchdog_check",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_weekly_scoring,
        CronTrigger(day_of_week="mon", hour=8, minute=0, timezone="UTC"),
        id="weekly_scoring",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_daily_profiles,
        CronTrigger(
            hour=DAILY_PROFILES_CRON_HOUR,
            minute=DAILY_PROFILES_CRON_MINUTE,
            timezone="UTC",
        ),
        id="daily_profiles",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    sched.add_job(
        job_prune_profiles,
        CronTrigger(hour=PRUNE_CRON_HOUR, minute=PRUNE_CRON_MINUTE, timezone="UTC"),
        id="prune_profiles",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    return sched


def run_once(job_names: list[str] | None = None) -> int:
    """Pipeline dry-run: execute selected jobs once and exit."""
    names = job_names or list(JOB_FUNCS.keys())
    # Skip expensive / weekly jobs in default once unless explicitly named
    if job_names is None:
        names = [
            n
            for n in names
            if n not in ("daily_profiles", "weekly_scoring")
        ]
    logger.info("scheduler --once jobs=%s at=%s", names, datetime.now(UTC).isoformat())
    failures = 0
    for name in names:
        fn = JOB_FUNCS.get(name)
        if fn is None:
            logger.error("unknown job %s", name)
            failures += 1
            continue
        try:
            fn()
        except Exception:
            failures += 1
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ouroboros analytics worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run jobs once (dry-run) then exit",
    )
    parser.add_argument(
        "--jobs",
        nargs="*",
        default=None,
        help=f"Job ids for --once (default: all except daily_profiles). Options: {list(JOB_FUNCS)}",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings.log_level)
    init_sentry(
        dsn=settings.sentry_dsn_server,
        environment=settings.app_env,
        release=f"ouroboros-worker@{__version__}",
    )

    if args.once:
        return run_once(args.jobs)

    sched = build_scheduler()
    logger.info(
        "worker starting env=%s jobs=%s",
        settings.app_env,
        [j.id for j in sched.get_jobs()],
    )

    def _shutdown(signum: int, _frame: object) -> None:
        logger.info("worker shutdown signal=%s", signum)
        sched.shutdown(wait=False)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("worker stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
