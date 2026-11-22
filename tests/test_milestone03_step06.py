"""Backend checks for the Step 06 date range selector (no GUI needed)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from analytics.custom_range import (
    MAX_CUSTOM_DAYS, build_custom_overview, chart_rows_for_range,
    validate_date_range,
)
from database.db_manager import DatabaseManager


class Step06CustomRangeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = DatabaseManager(Path(self.temp.name) / "step06.db")
        self.db.add_aggregates([
            {"day": "2026-11-20", "hour": 9, "key_presses": 5, "mouse_clicks": 2, "scroll_events": 1},
            {"day": "2026-11-22", "hour": 14, "key_presses": 8, "mouse_clicks": 3, "scroll_events": 4},
        ])
        self.now = date(2026, 11, 22)

    def tearDown(self) -> None:
        self.db.close()
        self.temp.cleanup()

    def test_custom_range_inclusive(self) -> None:
        result = build_custom_overview(self.db, date(2026, 11, 20), self.now, today=self.now)
        self.assertEqual(result["days"], 3)
        self.assertEqual(result["summary"]["total_events"], 23)
        self.assertEqual(result["summary"]["average_events_per_day"], 7.67)
        self.assertEqual(result["active_days"], 2)
        self.assertEqual(len(result["daily"]), 3)
        self.assertEqual(result["daily"][1]["key_presses"], 0)

    def test_single_day_including_empty(self) -> None:
        result = build_custom_overview(self.db, date(2026, 11, 21), date(2026, 11, 21), today=self.now)
        self.assertEqual(result["summary"]["total_events"], 0)
        self.assertEqual(result["active_days"], 0)
        self.assertEqual(result["days"], 1)

    def test_invalid_reversed_range_does_not_change_data(self) -> None:
        before = self.db.all_hourly_rows()
        with self.assertRaisesRegex(ValueError, "Start date"):
            build_custom_overview(self.db, self.now, date(2026, 11, 20), today=self.now)
        self.assertEqual(self.db.all_hourly_rows(), before)

    def test_future_date_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "future"):
            validate_date_range(self.now, self.now + timedelta(days=1), today=self.now)

    def test_maximum_range(self) -> None:
        self.assertEqual(validate_date_range(self.now - timedelta(days=MAX_CUSTOM_DAYS - 1), self.now, today=self.now), MAX_CUSTOM_DAYS)
        with self.assertRaisesRegex(ValueError, "fewer"):
            validate_date_range(self.now - timedelta(days=MAX_CUSTOM_DAYS), self.now, today=self.now)

    def test_chart_weekly_grouping_preserves_totals(self) -> None:
        daily = self.db.daily_totals(days=35, today=self.now)
        buckets = chart_rows_for_range(daily)
        self.assertEqual(len(buckets), 5)
        for key in ("key_presses", "mouse_clicks", "scroll_events"):
            self.assertEqual(sum(int(row[key]) for row in daily), sum(int(row[key]) for row in buckets))

    def test_short_range_keeps_daily_bars(self) -> None:
        daily = self.db.daily_totals(days=3, today=self.now)
        buckets = chart_rows_for_range(daily)
        self.assertEqual(len(buckets), 3)
        self.assertEqual(buckets[0]["label"], "20/11")

    def test_hourly_remains_today(self) -> None:
        result = build_custom_overview(self.db, date(2026, 11, 20), date(2026, 11, 20), today=self.now)
        self.assertEqual(result["summary"]["total_events"], 8)
        self.assertEqual(result["busiest_hour_today"], 14)
        self.assertEqual(result["hourly_today"][14]["key_presses"], 8)


if __name__ == "__main__":
    unittest.main()
