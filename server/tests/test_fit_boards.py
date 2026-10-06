"""Ex-post fit board builder tests (R1)."""

from __future__ import annotations

from app.analytics.fit.boards import board_from_regimes


def test_empty_window_safe_mismatch() -> None:
    board = board_from_regimes([], "meanrev", window="30d")
    assert board.tag == "MISMATCH"
    assert board.bar_count == 0
    assert board.shares["MATCH"] == 0.0


def test_meanrev_ranging_dominant() -> None:
    regimes = ["ranging"] * 7 + ["trending_up"] * 3
    board = board_from_regimes(regimes, "meanrev", window="7d")
    assert board.tag == "MATCH"
    assert board.bar_count == 10
    assert abs(board.shares["MATCH"] - 0.7) < 1e-9
    assert abs(board.shares["MISMATCH"] - 0.3) < 1e-9


def test_trendfollow_inverts_ranging() -> None:
    regimes = ["ranging"] * 10
    board = board_from_regimes(regimes, "trendfollow", window="30d")
    assert board.tag == "MISMATCH"
    assert board.shares["MISMATCH"] == 1.0


def test_high_vol_fragile_both_families() -> None:
    regimes = ["high_volatility"] * 5
    assert board_from_regimes(regimes, "meanrev").tag == "FRAGILE"
    assert board_from_regimes(regimes, "trendfollow").tag == "FRAGILE"


def test_tie_prefers_mismatch() -> None:
    # 50/50 MATCH vs MISMATCH for meanrev: ranging vs trending_up
    regimes = ["ranging", "trending_up"]
    board = board_from_regimes(regimes, "meanrev", window="7d")
    assert abs(board.shares["MATCH"] - 0.5) < 1e-9
    assert abs(board.shares["MISMATCH"] - 0.5) < 1e-9
    assert board.tag == "MISMATCH"
