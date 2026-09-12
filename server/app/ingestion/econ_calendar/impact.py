"""High-impact flagging + country → asset mapping for calendar events."""

from __future__ import annotations

from dataclasses import dataclass

from app.ingestion.econ_calendar.client import RawCalendarEvent

# Country codes Finnhub uses → primary FX/metal/index symbols in our universe.
_COUNTRY_SYMBOLS: dict[str, tuple[str, ...]] = {
    "US": ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "XAUUSD", "US500", "US30", "NAS100"),
    "EU": ("EURUSD", "EURGBP", "EURJPY"),
    "EZ": ("EURUSD", "EURGBP", "EURJPY"),
    "DE": ("EURUSD", "EURGBP", "EURJPY"),
    "GB": ("GBPUSD", "EURGBP", "GBPJPY"),
    "UK": ("GBPUSD", "EURGBP", "GBPJPY"),
    "JP": ("USDJPY", "EURJPY", "GBPJPY"),
    "CH": ("USDCHF",),
    "AU": ("AUDUSD",),
    "CA": ("USDCAD",),
    "NZ": ("NZDUSD",),
    "CN": ("AUDUSD", "USDJPY"),  # risk proxy
}

# Event-name substrings that force high impact regardless of provider label.
_HIGH_IMPACT_EVENTS = (
    "non-farm",
    "nonfarm",
    "nfp",
    "fomc",
    "interest rate decision",
    "fed interest",
    "cpi",
    "consumer price",
    "gdp",
    "unemployment rate",
    "payroll",
    "ecb",
    "boe",
    "boj",
    "rba",
    "snb",
    "pce",
    "ism manufacturing",
)


@dataclass(frozen=True)
class FlaggedCalendarEvent:
    event: RawCalendarEvent
    impact: str  # high|medium|low|unknown
    symbols: tuple[str, ...]
    high_impact: bool


def normalize_impact(raw: str | None, event_name: str) -> str:
    base = (raw or "").strip().lower()
    if base in {"high", "medium", "low"}:
        impact = base
    elif base in {"1", "2", "3"}:
        impact = {"1": "low", "2": "medium", "3": "high"}[base]
    else:
        impact = "unknown"

    name = event_name.lower()
    if any(token in name for token in _HIGH_IMPACT_EVENTS):
        return "high"
    return impact


def map_country_symbols(country: str, active: set[str] | None = None) -> tuple[str, ...]:
    candidates = _COUNTRY_SYMBOLS.get(country.upper(), ())
    if active is None:
        return candidates
    return tuple(s for s in candidates if s in active)


def flag_event(
    event: RawCalendarEvent,
    *,
    active_symbols: set[str] | None = None,
) -> FlaggedCalendarEvent:
    impact = normalize_impact(event.impact_raw, event.event)
    symbols = map_country_symbols(event.country, active_symbols)
    return FlaggedCalendarEvent(
        event=event,
        impact=impact,
        symbols=symbols,
        high_impact=(impact == "high"),
    )
