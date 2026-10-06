"""Deterministic regime → fit tag mapper — model tag ``fit.map_v0``."""

from __future__ import annotations

from app.analytics.fit.families import family_map
from app.analytics.fit.types import EdgeFamily, FitTag
from app.analytics.regimes import REGIME_LABELS, RegimeLabel

MODEL_VERSION = "fit.map_v0"


def map_regime_to_fit(regime: RegimeLabel | str, family: EdgeFamily | str) -> FitTag:
    """
    Map a confirmed regime label onto MATCH / MISMATCH / FRAGILE for an edge family.

    Pure function — no I/O. Raises ``ValueError`` on unknown regime or family.
    """
    fam = str(family)
    if fam not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown edge family: {family}")
    reg = str(regime)
    if reg not in REGIME_LABELS:
        raise ValueError(f"unknown regime: {regime}")
    return family_map(fam)[reg]  # type: ignore[index]


def call_type_for_family(family: EdgeFamily | str) -> str:
    """forecast_log.call_type encoding: ``fit.{family}``."""
    fam = str(family)
    if fam not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown edge family: {family}")
    return f"fit.{fam}"


def family_from_call_type(call_type: str) -> EdgeFamily:
    if not call_type.startswith("fit."):
        raise ValueError(f"not a fit call_type: {call_type}")
    fam = call_type.removeprefix("fit.")
    if fam not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown fit family in call_type: {call_type}")
    return fam  # type: ignore[return-value]
