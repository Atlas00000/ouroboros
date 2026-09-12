"""Deterministic analytics package — numbers only (no LLM)."""

from app.analytics.correlations import (
    CORR_TIMEFRAME,
    CORR_WINDOW_DAYS,
    CorrelationEntry,
    CorrelationMatrixResult,
    compute_correlation_matrix,
)
from app.analytics.metrics import (
    MODEL_VERSION,
    TIMEFRAMES,
    MetricSnapshot,
    Timeframe,
    compute_metric_snapshot,
    gap_aware_log_returns,
    kaufman_efficiency_ratio,
    realized_vol,
    wilder_atr,
)
from app.analytics.forecast_log import (
    classify_and_log_regimes,
    log_forecast_call,
    log_regime_call,
)
from app.analytics.profile_refresh import (
    collect_refresh_triggers,
    run_event_triggered_refresh,
)
from app.analytics.profile_store import (
    RETENTION_DAYS,
    can_refresh_symbol,
    persist_asset_profile,
    prune_profiles,
)
from app.analytics.profiles import (
    PROFILE_MODEL_VERSION,
    AssetIdentityInput,
    build_asset_profile,
    build_asset_profile_from_session,
)
from app.analytics.regimes import (
    MODEL_VERSION as REGIME_MODEL_VERSION,
)
from app.analytics.regimes import (
    PERSISTENCE_N,
    REGIME_LABELS,
    RegimeSnapshot,
    apply_persistence,
    classify_raw,
    classify_regime,
    soft_regime_probabilities,
)
from app.analytics.universe import (
    DEPTH_GATED_SYMBOLS,
    MIN_CORR_REGIME_DEPTH_DAYS,
    filter_corr_eligible,
    m1_span_days,
    passes_depth_gate,
)

__all__ = [
    "CORR_TIMEFRAME",
    "CORR_WINDOW_DAYS",
    "DEPTH_GATED_SYMBOLS",
    "MIN_CORR_REGIME_DEPTH_DAYS",
    "MODEL_VERSION",
    "PERSISTENCE_N",
    "PROFILE_MODEL_VERSION",
    "REGIME_LABELS",
    "REGIME_MODEL_VERSION",
    "RETENTION_DAYS",
    "TIMEFRAMES",
    "AssetIdentityInput",
    "CorrelationEntry",
    "CorrelationMatrixResult",
    "MetricSnapshot",
    "RegimeSnapshot",
    "Timeframe",
    "apply_persistence",
    "build_asset_profile",
    "build_asset_profile_from_session",
    "can_refresh_symbol",
    "classify_and_log_regimes",
    "classify_raw",
    "classify_regime",
    "collect_refresh_triggers",
    "compute_correlation_matrix",
    "compute_metric_snapshot",
    "filter_corr_eligible",
    "gap_aware_log_returns",
    "kaufman_efficiency_ratio",
    "log_forecast_call",
    "log_regime_call",
    "m1_span_days",
    "passes_depth_gate",
    "persist_asset_profile",
    "prune_profiles",
    "realized_vol",
    "run_event_triggered_refresh",
    "soft_regime_probabilities",
    "wilder_atr",
]
