"""Read-only analytics data for the KeyPulse dashboard.

No keyboard listener access, no typed text, and no database writes.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from analytics.statistics import most_active_hour, period_summary

if TYPE_CHECKING:
    from database.db_manager import DatabaseManager

PERIODS = (1, 7, 30)


def build_overview(db: DatabaseManager, days: int, today: date | None = None) -> dict[str, Any]:
    """Return a selected-period summary, daily trend, and today's 24h data."""
    if days not in PERIODS:
        raise ValueError("days must be 1, 7, or 30")

    selected_day = today or date.today()
    daily = db.daily_totals(days=days, today=selected_day)
    hourly_today = db.hourly_totals(selected_day)
    summary = period_summary(daily)
    active_days = sum(
        1 for row in daily
        if sum(int(row[k]) for k in ("key_presses", "mouse_clicks", "scroll_events")) > 0
    )

    return {
        "days": days,
        "as_of": selected_day.isoformat(),
        "daily": daily,
        "hourly_today": hourly_today,
        "summary": summary,
        "active_days": active_days,
        "busiest_hour_today": most_active_hour(hourly_today),
    }


def format_peak_hour(hour: int | None) -> str:
    """Return a readable hour label, or N/A if no events were recorded today."""
    return "N/A" if hour is None else f"{hour:02d}:00"
