"""Export aggregate-only usage data, with no event-level rows."""
from __future__ import annotations

import csv
from pathlib import Path

from database.db_manager import DatabaseManager


def export_hourly_csv(db: DatabaseManager, output: str | Path) -> int:
    rows = db.all_hourly_rows()
    with Path(output).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("date", "hour_24h", "key_presses", "mouse_clicks", "scroll_events"))
        writer.writerows(rows)
    return len(rows)
