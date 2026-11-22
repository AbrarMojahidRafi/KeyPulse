"""Milestone 03 Step 05: analytics data tests (no GUI required)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from analytics.overview_data import build_overview, format_peak_hour
from database.db_manager import DatabaseManager


class Step05OverviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = DatabaseManager(Path(self.temp.name) / "overview.db")
        self.db.add_aggregates([
            {"day": "2026-11-20", "hour": 9, "key_presses": 5, "mouse_clicks": 2, "scroll_events": 1},
            {"day": "2026-11-22", "hour": 15, "key_presses": 8, "mouse_clicks": 3, "scroll_events": 4},
        ])

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_today_summary_and_busiest_hour(self):
        data = build_overview(self.db, 1, date(2026, 11, 22))
        self.assertEqual(data["summary"]["total_events"], 15)
        self.assertEqual(data["active_days"], 1)
        self.assertEqual(data["busiest_hour_today"], 15)

    def test_last_seven_days_includes_empty_days(self):
        data = build_overview(self.db, 7, date(2026, 11, 22))
        self.assertEqual(len(data["daily"]), 7)
        self.assertEqual(data["summary"]["key_presses"], 13)
        self.assertEqual(data["summary"]["total_events"], 23)
        self.assertEqual(data["active_days"], 2)
        self.assertEqual(data["summary"]["average_events_per_day"], 3.29)

    def test_thirty_day_range(self):
        data = build_overview(self.db, 30, date(2026, 11, 22))
        self.assertEqual(len(data["daily"]), 30)
        self.assertEqual(data["summary"]["total_events"], 23)

    def test_empty_date_and_peak_format(self):
        data = build_overview(self.db, 1, date(2026, 11, 23))
        self.assertEqual(data["summary"]["total_events"], 0)
        self.assertIsNone(data["busiest_hour_today"])
        self.assertEqual(format_peak_hour(None), "N/A")
        self.assertEqual(format_peak_hour(9), "09:00")

    def test_invalid_period_does_not_modify_db(self):
        before = self.db.all_hourly_rows()
        with self.assertRaises(ValueError):
            build_overview(self.db, 2, date(2026, 11, 22))
        self.assertEqual(before, self.db.all_hourly_rows())

    def test_only_aggregate_fields_returned(self):
        data = build_overview(self.db, 7, date(2026, 11, 22))
        self.assertEqual(set(data["daily"][0]), {
            "day", "key_presses", "mouse_clicks", "scroll_events"
        })


if __name__ == "__main__":
    unittest.main()
