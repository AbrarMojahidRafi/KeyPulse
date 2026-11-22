import tempfile
import unittest

from datetime import date
from pathlib import Path
from database.db_manager import DatabaseManager


class Milestone03Tests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.db = DatabaseManager(
            Path(self.temp.name) / "test.db"
        )

        self.db.add_aggregates([
            {
                "day": "2026-11-20",
                "hour": 9,
                "key_presses": 5,
                "mouse_clicks": 2,
                "scroll_events": 1
            },
            {
                "day": "2026-11-22",
                "hour": 15,
                "key_presses": 8,
                "mouse_clicks": 3,
                "scroll_events": 4
            }
        ])

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_date_range(self):
        result = self.db.date_range_totals(
            date(2026, 11, 20),
            date(2026, 11, 22)
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(
            [day["key_presses"] for day in result],
            [5, 0, 8]
        )

    def test_hourly_activity(self):
        result = self.db.hourly_totals(
            date(2026, 11, 22)
        )

        self.assertEqual(len(result), 24)
        self.assertEqual(result[15]["mouse_clicks"], 3)
        self.assertEqual(result[14]["key_presses"], 0)

    def test_invalid_date_range(self):
        before = self.db.all_hourly_rows()

        with self.assertRaises(ValueError):
            self.db.date_range_totals(
                date(2026, 11, 23),
                date(2026, 11, 22)
            )

        self.assertEqual(
            self.db.all_hourly_rows(),
            before
        )


if __name__ == "__main__":
    unittest.main()