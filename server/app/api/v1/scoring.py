"""GET /v1/scoring/weekly — stored weekly regime accuracy reports (W11)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.scoring_report import ScoringWeeklyReport

router = APIRouter(tags=["scoring"])


class SymbolTfAccuracy(BaseModel):
    symbol: str
    timeframe: str
    model_version: str | None = None
    n: int = 0
    correct: int = 0
    accuracy: float | None = None


class WeeklyReportItem(BaseModel):
    id: int
    week_start: datetime
    week_end: datetime
    n_scored: int
    n_correct: int
    accuracy: float | None
    by_symbol_tf: list[SymbolTfAccuracy] = Field(default_factory=list)
    scoring_model: str | None = None
    email_sent_at: datetime | None = None
    created_at: datetime


class WeeklyScoringResponse(BaseModel):
    items: list[WeeklyReportItem]


def _parse_report(row: ScoringWeeklyReport) -> WeeklyReportItem:
    raw: dict[str, Any] = {}
    try:
        parsed = json.loads(row.report_json or "{}")
        if isinstance(parsed, dict):
            raw = parsed
    except json.JSONDecodeError:
        raw = {}

    by: list[SymbolTfAccuracy] = []
    for entry in raw.get("by_symbol_tf") or []:
        if not isinstance(entry, dict):
            continue
        by.append(
            SymbolTfAccuracy(
                symbol=str(entry.get("symbol") or ""),
                timeframe=str(entry.get("timeframe") or ""),
                model_version=entry.get("model_version"),
                n=int(entry.get("n") or 0),
                correct=int(entry.get("correct") or 0),
                accuracy=float(entry["accuracy"]) if entry.get("accuracy") is not None else None,
            )
        )

    acc = float(row.accuracy) if row.accuracy is not None else None
    return WeeklyReportItem(
        id=row.id,
        week_start=row.week_start,
        week_end=row.week_end,
        n_scored=row.n_scored,
        n_correct=row.n_correct,
        accuracy=acc,
        by_symbol_tf=by,
        scoring_model=raw.get("scoring_model"),
        email_sent_at=row.email_sent_at,
        created_at=row.created_at,
    )


@router.get("/scoring/weekly", response_model=WeeklyScoringResponse)
def list_weekly_scoring(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=52)] = 8,
) -> WeeklyScoringResponse:
    rows = list(
        db.scalars(
            select(ScoringWeeklyReport)
            .order_by(ScoringWeeklyReport.week_start.desc())
            .limit(limit)
        ).all()
    )
    return WeeklyScoringResponse(items=[_parse_report(r) for r in rows])
