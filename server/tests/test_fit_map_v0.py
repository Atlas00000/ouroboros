"""Golden fixtures for fit.map_v0 (R0)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.analytics.fit.families import assert_maps_cover_regimes
from app.analytics.fit.mapper import MODEL_VERSION, call_type_for_family, map_regime_to_fit
from app.analytics.regimes import REGIME_LABELS

FIXTURE = Path(__file__).parent / "fixtures" / "analytics" / "fit_map_v0.json"


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_model_version() -> None:
    assert _load()["model_version"] == MODEL_VERSION


def test_maps_cover_all_regimes() -> None:
    assert_maps_cover_regimes()


@pytest.mark.parametrize("family", ["meanrev", "trendfollow"])
@pytest.mark.parametrize("regime", list(REGIME_LABELS))
def test_matrix_matches_fixture(family: str, regime: str) -> None:
    expected = _load()["matrix"][family][regime]
    assert map_regime_to_fit(regime, family) == expected


def test_unknown_regime_raises() -> None:
    with pytest.raises(ValueError, match="unknown regime"):
        map_regime_to_fit("sideways", "meanrev")


def test_unknown_family_raises() -> None:
    with pytest.raises(ValueError, match="unknown edge family"):
        map_regime_to_fit("ranging", "scalp")


def test_call_type_encoding() -> None:
    assert call_type_for_family("meanrev") == "fit.meanrev"
    assert call_type_for_family("trendfollow") == "fit.trendfollow"
