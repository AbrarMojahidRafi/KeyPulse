"""KeyPulse Step 06: date range analytics using local, aggregate-only SQLite data.

No keyboard listeners, text data, or network calls are involved.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Mapping

from analytics.statistics import most_active_hour, period_summary

if TYPE_CHECKING:
    from database.db_manager import DatabaseManager

MAX_CUSTOM_DAYS = 90


def validate_date_range(start: date, end: date, *, today: date | None = None) -> int:
    """Validate an inclusive, past-or-present range and return its day count."""
    if not isinstance(start, date) or not isinstance(end, date):
        raise ValueError("Choose valid start and end dates.")
    if start > end:
        raise ValueError("Start date must be on or before end date.")
    if end > (today or date.today()):
        raise ValueError("End date cannot be in the future.")
    count = (end - start).days + 1
    if count > MAX_CUSTOM_DAYS:
        raise ValueError(f"Select {MAX_CUSTOM_DAYS} days or fewer at a time.")
    return count


def build_custom_overview(
    db: DatabaseManager,
    start: date,
    end: date,
    *,
    today: date | None = None,
) -> dict[str, Any]:
    """Read daily aggregates for a custom period, plus today's hourly activity."""
    now = today or date.today()
    days = validate_date_range(start, end, today=now)
    daily = db.date_range_totals(start, end)
    hours = db.hourly_totals(now)
    summary = period_summary(daily)
    active_days = sum(
        sum(int(row[k]) for k in ("key_presses", "mouse_clicks", "scroll_events")) > 0
        for row in daily
    )
    return {
        "days": days,
        "as_of": now.isoformat(),
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "daily": daily,
        "hourly_today": hours,
        "summary": summary,
        "active_days": active_days,
        "busiest_hour_today": most_active_hour(hours),
    }


def chart_rows_for_range(
    daily: list[Mapping[str, str | int]],
    *,
    bucket_after: int = 31,
) -> list[dict[str, str | int]]:
    """Use daily bars for <=31 days; aggregate contiguous weeks for longer ranges.

    Chart grouping changes visual presentation only, never underlying statistics.
    """
    measures = ("key_presses", "mouse_clicks", "scroll_events")
    if len(daily) <= bucket_after:
        return [
            {"label": date.fromisoformat(str(row["day"])).strftime("%d/%m"),
             **{k: int(row[k]) for k in measures}}
            for row in daily
        ]
    buckets: list[dict[str, str | int]] = []
    for index in range(0, len(daily), 7):
        group = daily[index:index + 7]
        first = date.fromisoformat(str(group[0]["day"])).strftime("%d/%m")
        last = date.fromisoformat(str(group[-1]["day"])).strftime("%d/%m")
        buckets.append({
            "label": f"{first}-{last}",
            **{key: sum(int(row[key]) for row in group) for key in measures},
        })
    return buckets
