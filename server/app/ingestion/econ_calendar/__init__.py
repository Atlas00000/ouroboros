"""Economic calendar ingestion package."""

from app.ingestion.econ_calendar.client import FinnhubCalendarClient, RawCalendarEvent
from app.ingestion.econ_calendar.impact import FlaggedCalendarEvent, flag_event, normalize_impact
from app.ingestion.econ_calendar.poller import CalendarPollResult, poll_once

__all__ = [
    "CalendarPollResult",
    "FinnhubCalendarClient",
    "FlaggedCalendarEvent",
    "RawCalendarEvent",
    "flag_event",
    "normalize_impact",
    "poll_once",
]
