import tempfile
import unittest
from pathlib import Path

from analytics.reports import export_hourly_csv
from database.db_manager import DatabaseManager


class ExportTests(unittest.TestCase):
    def test_csv_has_aggregate_only_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            db = DatabaseManager(Path(folder) / 'test.db')
            db.add_aggregates([{'day': '2026-11-22', 'hour': 13,
                                'key_presses': 2, 'mouse_clicks': 1, 'scroll_events': 0}])
            output = Path(folder) / 'report.csv'
            self.assertEqual(export_hourly_csv(db, output), 1)
            text = output.read_text(encoding='utf-8-sig')
            self.assertIn('date,hour_24h,key_presses,mouse_clicks,scroll_events', text)
            self.assertIn('2026-11-22,13,2,1,0', text)
            db.close()


if __name__ == '__main__':
    unittest.main()
