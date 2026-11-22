"""SQLite persistence of hourly aggregates only."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Mapping

from config import database_path


class DatabaseManager:
    def __init__(self, db_file: str | Path | None = None) -> None:
        self.path = Path(db_file) if db_file is not None else database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(self.path), timeout=10.0)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS hourly_activity (
                day TEXT NOT NULL,
                hour INTEGER NOT NULL CHECK(hour BETWEEN 0 AND 23),
                key_presses INTEGER NOT NULL DEFAULT 0,
                mouse_clicks INTEGER NOT NULL DEFAULT 0,
                scroll_events INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (day, hour)
            )"""
        )
        self._db.commit()

    def add_aggregates(self, records: Iterable[Mapping[str, str | int]]) -> None:
        rows = [
            (
                str(r["day"]), int(r["hour"]), int(r["key_presses"]),
                int(r["mouse_clicks"]), int(r["scroll_events"]),
            )
            for r in records
        ]
        if not rows:
            return
        with self._db:
            self._db.executemany(
                """INSERT INTO hourly_activity
                   (day, hour, key_presses, mouse_clicks, scroll_events)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(day, hour) DO UPDATE SET
                     key_presses = key_presses + excluded.key_presses,
                     mouse_clicks = mouse_clicks + excluded.mouse_clicks,
                     scroll_events = scroll_events + excluded.scroll_events""",
                rows,
            )

    def today_totals(self, today: date | None = None) -> dict[str, int]:
        day = (today or date.today()).isoformat()
        row = self._db.execute(
            """SELECT COALESCE(SUM(key_presses), 0),
                      COALESCE(SUM(mouse_clicks), 0),
                      COALESCE(SUM(scroll_events), 0)
               FROM hourly_activity WHERE day = ?""",
            (day,),
        ).fetchone()
        return {"key_presses": row[0], "mouse_clicks": row[1], "scroll_events": row[2]}

    def daily_totals(self, days: int = 7, today: date | None = None) -> list[dict[str, str | int]]:
        end = today or date.today()
        start = end - timedelta(days=days - 1)
        rows = self._db.execute(
            """SELECT day, SUM(key_presses), SUM(mouse_clicks), SUM(scroll_events)
               FROM hourly_activity WHERE day BETWEEN ? AND ? GROUP BY day""",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        by_day = {day: (keys, clicks, scrolls) for day, keys, clicks, scrolls in rows}
        output = []
        for offset in range(days):
            current = (start + timedelta(days=offset)).isoformat()
            keys, clicks, scrolls = by_day.get(current, (0, 0, 0))
            output.append({"day": current, "key_presses": keys,
                           "mouse_clicks": clicks, "scroll_events": scrolls})
        return output
    def date_range_totals(self, start: date, end: date):
        """Get daily activity within a selected date range."""

        if start > end:
            raise ValueError("Start date cannot be after end date")

        number_of_days = (end - start).days + 1

        return self.daily_totals(
            days=number_of_days,
            today=end
        )

    def hourly_totals(self, selected_day: date):
        """Get activity for all 24 hours of a day."""

        rows = self._db.execute(
            """
            SELECT hour, key_presses, mouse_clicks, scroll_events
            FROM hourly_activity
            WHERE day = ?
            ORDER BY hour
            """,
            (selected_day.isoformat(),)
        ).fetchall()

        lookup = {
            hour: (keys, clicks, scrolls)
            for hour, keys, clicks, scrolls in rows
        }

        results = []

        for hour in range(24):
            keys, clicks, scrolls = lookup.get(hour, (0, 0, 0))

            results.append({
                "hour": hour,
                "key_presses": keys,
                "mouse_clicks": clicks,
                "scroll_events": scrolls
            })

        return results
    def all_hourly_rows(self) -> list[tuple[str, int, int, int, int]]:
        return self._db.execute(
            """SELECT day, hour, key_presses, mouse_clicks, scroll_events
               FROM hourly_activity ORDER BY day, hour"""
        ).fetchall()

    def delete_all(self) -> None:
        with self._db:
            self._db.execute("DELETE FROM hourly_activity")

    def close(self) -> None:
        self._db.close()
