"""Unit tests for profile store + event-triggered refresh (W5·D2)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from app.analytics.profile_refresh import confirmed_regime_flipped_on_last_bar
from app.analytics.profile_store import (
    ids_to_prune_beyond_retention,
    within_refresh_cooldown,
)


def test_within_refresh_cooldown_enforces_one_per_hour() -> None:
    now = datetime(2026, 9, 12, 12, 0, tzinfo=UTC)
    assert within_refresh_cooldown(None, now=now) is False
    assert (
        within_refresh_cooldown(now - timedelta(minutes=59), now=now) is True
    )
    assert (
        within_refresh_cooldown(now - timedelta(hours=1), now=now) is False
    )


def test_ids_to_prune_keeps_last_of_day_beyond_180d() -> None:
    now = datetime(2026, 9, 12, tzinfo=UTC)
    cutoff = now - timedelta(days=180)
    # Within retention — never pruned by this helper
    recent = (1, "EURUSD", now - timedelta(days=10))
    # Old day with 3 versions — keep latest only
    old_day = cutoff - timedelta(days=5)
    rows = [
        recent,
        (10, "EURUSD", old_day.replace(hour=8)),
        (11, "EURUSD", old_day.replace(hour=14)),
        (12, "EURUSD", old_day.replace(hour=20)),  # keep
        (20, "GBPUSD", old_day.replace(hour=9)),
        (21, "GBPUSD", old_day.replace(hour=18)),  # keep
    ]
    doomed = set(ids_to_prune_beyond_retention(rows, cutoff=cutoff))
    assert doomed == {10, 11, 20}
    assert 12 not in doomed
    assert 21 not in doomed
    assert 1 not in doomed


def test_confirmed_regime_flip_on_last_bar() -> None:
    ts0 = datetime(2026, 9, 11, 0, tzinfo=UTC)
    ts1 = datetime(2026, 9, 12, 0, tzinfo=UTC)
    features = pd.DataFrame(
        {
            "ts": [ts0, ts1],
            "confirmed_regime": ["ranging", "trending_up"],
        }
    )
    flip = confirmed_regime_flipped_on_last_bar(features)
    assert flip is not None
    prev, new, as_of = flip
    assert prev == "ranging"
    assert new == "trending_up"
    assert as_of == ts1

    same = pd.DataFrame(
        {"ts": [ts0, ts1], "confirmed_regime": ["ranging", "ranging"]}
    )
    assert confirmed_regime_flipped_on_last_bar(same) is None
