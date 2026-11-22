import tempfile
import unittest
from datetime import date
from pathlib import Path

from database.db_manager import DatabaseManager


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = DatabaseManager(Path(self.tmp.name) / 'usage.db')

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_upsert_and_daily_aggregation(self):
        record = {'day': '2026-11-22', 'hour': 15,
                  'key_presses': 3, 'mouse_clicks': 1, 'scroll_events': 2}
        self.db.add_aggregates([record, record])
        totals = self.db.today_totals(date(2026, 11, 22))
        self.assertEqual(totals, {'key_presses': 6, 'mouse_clicks': 2, 'scroll_events': 4})
        weekly = self.db.daily_totals(2, date(2026, 11, 22))
        self.assertEqual(len(weekly), 2)
        self.assertEqual(weekly[-1]['key_presses'], 6)

    def test_delete_all(self):
        self.db.add_aggregates([{'day': '2026-11-22', 'hour': 9,
                                 'key_presses': 1, 'mouse_clicks': 0, 'scroll_events': 0}])
        self.db.delete_all()
        self.assertEqual(self.db.all_hourly_rows(), [])


if __name__ == '__main__':
    unittest.main()
