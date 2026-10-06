"""Edge-family → regime fit maps (fit.map_v0)."""

from __future__ import annotations

from app.analytics.fit.types import EdgeFamily, FitTag
from app.analytics.regimes import REGIME_LABELS, RegimeLabel

# meanrev: home = ranging; trends adverse; high vol fragile
MEANREV_MAP: dict[RegimeLabel, FitTag] = {
    "ranging": "MATCH",
    "trending_up": "MISMATCH",
    "trending_down": "MISMATCH",
    "high_volatility": "FRAGILE",
}

# trendfollow: home = trending_*; ranging adverse; high vol fragile
TRENDFOLLOW_MAP: dict[RegimeLabel, FitTag] = {
    "trending_up": "MATCH",
    "trending_down": "MATCH",
    "ranging": "MISMATCH",
    "high_volatility": "FRAGILE",
}

FAMILY_MAPS: dict[EdgeFamily, dict[RegimeLabel, FitTag]] = {
    "meanrev": MEANREV_MAP,
    "trendfollow": TRENDFOLLOW_MAP,
}


def family_map(family: EdgeFamily) -> dict[RegimeLabel, FitTag]:
    try:
        return FAMILY_MAPS[family]
    except KeyError as exc:
        raise ValueError(f"unknown edge family: {family}") from exc


def assert_maps_cover_regimes() -> None:
    """Invariant: every family maps all four regime labels."""
    for fam, mapping in FAMILY_MAPS.items():
        missing = set(REGIME_LABELS) - set(mapping)
        if missing:
            raise AssertionError(f"{fam} missing regimes: {sorted(missing)}")
