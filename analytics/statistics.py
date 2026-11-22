"""Basic statistics over daily aggregate rows."""
from __future__ import annotations

from typing import Mapping


def total_events(days: list[Mapping[str, str | int]]) -> int:
    return sum(
        int(day["key_presses"]) + int(day["mouse_clicks"]) + int(day["scroll_events"])
        for day in days
    )
