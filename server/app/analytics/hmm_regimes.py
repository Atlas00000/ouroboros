"""HMM regime spike — ``regimes.hmm_v1`` candidate (Phase 2 W5·D5).

4-state Gaussian HMM on (vol_percentile_30d, Kaufman ER_20). States are mapped
to the same four regime labels as ``regimes.rule_v1`` by interpreting emission
means against the rule grid. Production promotion requires beating flip-rate
budgets without collapsing agreement / interpretability (see ADR-017).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from app.analytics.backtest import count_flips
from app.analytics.metrics import Timeframe, bars_for_calendar_days
from app.analytics.regimes import (
    DEFAULT_PARAMS,
    ER_TREND_ABS,
    MODEL_VERSION as RULE_MODEL_VERSION,
    REGIME_LABELS,
    RegimeLabel,
    RegimeParams,
    VOL_HIGH_PCT,
    apply_persistence,
    regime_feature_frame,
)
from app.calendar.timebase import ensure_utc

MODEL_VERSION = "regimes.hmm_v1"
N_STATES = 4


def hmmlearn_available() -> bool:
    try:
        import hmmlearn  # noqa: F401

        return True
    except ImportError:
        return False


def _require_hmm() -> Any:
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError as exc:
        raise ImportError(
            "hmmlearn is required for the HMM spike. "
            "Install with: pip install 'ouroboros-server[hmm]' or pip install hmmlearn"
        ) from exc
    return GaussianHMM


def feature_matrix(features: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (X, valid_mask) where X is finite rows of [vol_pct, er], z-scored.
    """
    vol = pd.to_numeric(features["vol_percentile"], errors="coerce")
    er = pd.to_numeric(features["efficiency_ratio"], errors="coerce")
    mask = vol.notna() & er.notna() & np.isfinite(vol) & np.isfinite(er)
    raw = np.column_stack([vol.to_numpy(dtype=float), er.to_numpy(dtype=float)])
    valid = raw[mask.to_numpy()]
    if len(valid) < 20:
        return np.empty((0, 2)), mask.to_numpy()
    mu = valid.mean(axis=0)
    sigma = valid.std(axis=0)
    sigma = np.where(sigma < 1e-9, 1.0, sigma)
    z = (raw - mu) / sigma
    z[~mask.to_numpy()] = np.nan
    return z, mask.to_numpy()


def map_state_means_to_labels(
    means_z: np.ndarray,
    *,
    train_mu: np.ndarray,
    train_sigma: np.ndarray,
    vol_high: float = VOL_HIGH_PCT,
    er_abs: float = ER_TREND_ABS,
) -> dict[int, RegimeLabel]:
    """
    Map HMM state index → regime label using denormalized emission means
    and the same hard grid as ``classify_raw``.
    """
    mapping: dict[int, RegimeLabel] = {}
    used: set[RegimeLabel] = set()
    # Rank states by |vol| then |er| for collision resolution
    order = list(range(len(means_z)))
    denorm = means_z * train_sigma + train_mu
    # Prefer assigning high_vol first, then trends, then ranging
    scored: list[tuple[float, int, RegimeLabel]] = []
    for i, (vol, er) in enumerate(denorm):
        if vol >= vol_high:
            lab: RegimeLabel = "high_volatility"
            pri = 0
        elif er >= er_abs:
            lab = "trending_up"
            pri = 1
        elif er <= -er_abs:
            lab = "trending_down"
            pri = 1
        else:
            lab = "ranging"
            pri = 2
        scored.append((pri, i, lab))
    scored.sort(key=lambda t: (t[0], -abs(denorm[t[1]][0])))
    leftovers = [r for r in REGIME_LABELS]
    for _, i, lab in scored:
        if lab not in used:
            mapping[i] = lab
            used.add(lab)
        else:
            # Collision: pick an unused label closest in spirit
            for cand in leftovers:
                if cand not in used:
                    mapping[i] = cand
                    used.add(cand)
                    break
    for i in order:
        if i not in mapping:
            for cand in REGIME_LABELS:
                if cand not in used:
                    mapping[i] = cand
                    used.add(cand)
                    break
    return mapping


@dataclass(frozen=True)
class HmmFitResult:
    model: Any
    state_to_label: dict[int, RegimeLabel]
    train_mu: np.ndarray
    train_sigma: np.ndarray
    n_train: int


def fit_gaussian_hmm(
    features: pd.DataFrame,
    *,
    n_states: int = N_STATES,
    random_state: int = 42,
    n_iter: int = 200,
) -> HmmFitResult:
    """Fit a diagonal GaussianHMM on z-scored (vol_pct, er)."""
    GaussianHMM = _require_hmm()
    vol = pd.to_numeric(features["vol_percentile"], errors="coerce")
    er = pd.to_numeric(features["efficiency_ratio"], errors="coerce")
    mask = vol.notna() & er.notna() & np.isfinite(vol) & np.isfinite(er)
    valid = np.column_stack([vol[mask].to_numpy(dtype=float), er[mask].to_numpy(dtype=float)])
    if len(valid) < max(50, n_states * 10):
        raise ValueError(f"insufficient finite feature rows for HMM: {len(valid)}")

    mu = valid.mean(axis=0)
    sigma = valid.std(axis=0)
    sigma = np.where(sigma < 1e-9, 1.0, sigma)
    z = (valid - mu) / sigma

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="diag",
        n_iter=n_iter,
        random_state=random_state,
        verbose=False,
    )
    model.fit(z)
    state_map = map_state_means_to_labels(model.means_, train_mu=mu, train_sigma=sigma)
    return HmmFitResult(
        model=model,
        state_to_label=state_map,
        train_mu=mu,
        train_sigma=sigma,
        n_train=len(valid),
    )


def decode_hmm_labels(
    features: pd.DataFrame,
    fit: HmmFitResult,
    *,
    persistence_n: int = 3,
) -> pd.Series:
    """Viterbi decode → mapped labels; optional persistence for fair flip comparison."""
    vol = pd.to_numeric(features["vol_percentile"], errors="coerce")
    er = pd.to_numeric(features["efficiency_ratio"], errors="coerce")
    mask = (vol.notna() & er.notna() & np.isfinite(vol) & np.isfinite(er)).to_numpy()
    raw = np.column_stack([vol.to_numpy(dtype=float), er.to_numpy(dtype=float)])
    z = (raw - fit.train_mu) / fit.train_sigma

    labels: list[RegimeLabel | None] = [None] * len(features)
    if mask.sum() < 10:
        return pd.Series(labels, index=features.index, dtype=object)

    # Decode only contiguous finite segments to avoid NaN in hmmlearn
    idx = np.where(mask)[0]
    # Single segment of all valid rows (drop gaps by decoding valid-only then scatter)
    z_valid = z[mask]
    states = fit.model.predict(z_valid)
    mapped = [fit.state_to_label[int(s)] for s in states]
    for pos, lab in zip(idx, mapped, strict=True):
        labels[int(pos)] = lab

    if persistence_n > 1:
        labels = apply_persistence(labels, n=persistence_n)
    return pd.Series(labels, index=features.index, dtype=object)


@dataclass(frozen=True)
class HmmCompareResult:
    symbol: str
    timeframe: Timeframe
    rule_flips_per_day: float
    hmm_flips_per_day: float
    rule_flips_per_week: float
    hmm_flips_per_week: float
    agreement: float
    bars_compared: int
    rule_within_budget: bool
    hmm_within_budget: bool
    state_map: dict[int, str]
    rule_model: str = RULE_MODEL_VERSION
    hmm_model: str = MODEL_VERSION


def compare_hmm_vs_rule(
    df: pd.DataFrame,
    *,
    symbol: str,
    timeframe: Timeframe,
    params: RegimeParams = DEFAULT_PARAMS,
    warmup_days: int = 30,
    persistence_n: int = 3,
    random_state: int = 42,
) -> HmmCompareResult:
    """Fit HMM on the series, decode, compare flip-rate + agreement to rule_v1."""
    from app.analytics.backtest import (
        FLIP_BUDGET_D1_PER_WEEK,
        FLIP_BUDGET_H1_PER_DAY,
        measure_flip_rate,
    )

    feats = regime_feature_frame(df, timeframe, params=params)
    rule = measure_flip_rate(
        df, symbol=symbol, timeframe=timeframe, params=params, warmup_days=warmup_days
    )

    fit = fit_gaussian_hmm(feats, random_state=random_state)
    hmm_labels = decode_hmm_labels(feats, fit, persistence_n=persistence_n)

    warmup = bars_for_calendar_days(timeframe, warmup_days)
    work = feats.iloc[warmup:].copy()
    work["hmm"] = hmm_labels.iloc[warmup:].to_numpy()
    work["rule"] = feats["confirmed_regime"].iloc[warmup:].to_numpy()
    both = work[work["hmm"].notna() & work["rule"].notna()]
    agree = float((both["hmm"] == both["rule"]).mean()) if len(both) else 0.0

    hmm_lab_list = list(both["hmm"])
    flips = count_flips(hmm_lab_list)
    if len(both) >= 2:
        first = ensure_utc(pd.to_datetime(both["ts"].iloc[0], utc=True).to_pydatetime())
        last = ensure_utc(pd.to_datetime(both["ts"].iloc[-1], utc=True).to_pydatetime())
        span = max((last - first).total_seconds() / 86400.0, 1.0 / 24.0)
    else:
        span = 0.0
    per_day = flips / span if span > 0 else 0.0
    per_week = per_day * 7.0
    if timeframe == "D1":
        hmm_ok = per_week <= FLIP_BUDGET_D1_PER_WEEK
    else:
        hmm_ok = per_day <= FLIP_BUDGET_H1_PER_DAY

    return HmmCompareResult(
        symbol=symbol.upper(),
        timeframe=timeframe,
        rule_flips_per_day=rule.flips_per_day,
        hmm_flips_per_day=per_day,
        rule_flips_per_week=rule.flips_per_week,
        hmm_flips_per_week=per_week,
        agreement=agree,
        bars_compared=len(both),
        rule_within_budget=rule.within_budget,
        hmm_within_budget=hmm_ok,
        state_map={int(k): str(v) for k, v in fit.state_to_label.items()},
    )
