"""Basic statistics over daily aggregate rows."""
from __future__ import annotations

from typing import Mapping


def total_events(days: list[Mapping[str, str | int]]) -> int:
    return sum(
        int(day["key_presses"]) + int(day["mouse_clicks"]) + int(day["scroll_events"])
        for day in days
    )

def period_summary(days: list[Mapping[str, str | int]]) -> dict[str, int | float]:
    """Calculate totals and daily average for a period."""

    keys = sum(int(day["key_presses"]) for day in days)
    clicks = sum(int(day["mouse_clicks"]) for day in days)
    scrolls = sum(int(day["scroll_events"]) for day in days)

    total = keys + clicks + scrolls

    return {
        "days": len(days),
        "key_presses": keys,
        "mouse_clicks": clicks,
        "scroll_events": scrolls,
        "total_events": total,
        "average_events_per_day": round(total / len(days), 2) if days else 0.0
    }


def most_active_hour(hours: list[Mapping[str, int]]) -> int | None:
    """Find the hour with the highest total activity."""

    if not hours:
        return None

    def activity_count(row):
        return (
            row["key_presses"]
            + row["mouse_clicks"]
            + row["scroll_events"]
        )

    busiest = max(hours, key=activity_count)

    if activity_count(busiest) == 0:
        return None

    return int(busiest["hour"])