"""Unit tests for worker scheduler registration (W5·D4)."""

from __future__ import annotations

from app.scheduler import JOB_FUNCS, build_scheduler, main


def test_build_scheduler_registers_expected_jobs() -> None:
    sched = build_scheduler()
    ids = sorted(j.id for j in sched.get_jobs())
    assert ids == [
        "daily_profiles",
        "metrics_cadence",
        "narratives_refresh",
        "outbox_relay",
        "profile_events",
        "prune_profiles",
        "regime_log",
        "score_regime_calls",
        "sentiment_refresh",
        "watchdog_check",
        "weekly_scoring",
    ]


def test_job_funcs_cover_registered_ids() -> None:
    assert set(JOB_FUNCS) == {
        "metrics_cadence",
        "regime_log",
        "profile_events",
        "outbox_relay",
        "daily_profiles",
        "prune_profiles",
        "sentiment_refresh",
        "narratives_refresh",
        "score_regime_calls",
        "weekly_scoring",
        "watchdog_check",
    }


def test_main_rejects_unknown_once_job(monkeypatch) -> None:
    # Unknown job name should count as failure without starting the blocking loop
    code = main(["--once", "--jobs", "not_a_real_job"])
    assert code == 1
