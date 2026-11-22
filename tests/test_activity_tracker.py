import unittest
from datetime import datetime

from core.activity_tracker import ActivityAccumulator


class ActivityTrackerTests(unittest.TestCase):
    def test_hourly_aggregate_and_drain(self):
        clock = lambda: datetime(2026, 11, 22, 15, 30)
        tracker = ActivityAccumulator(now=clock)
        tracker.record_keypress()
        tracker.record_keypress()
        tracker.record_click()
        tracker.record_scroll()
        self.assertEqual(tracker.peek_today().key_presses, 2)
        rows = tracker.drain()
        self.assertEqual(rows, [{
            'day': '2026-11-22', 'hour': 15,
            'key_presses': 2, 'mouse_clicks': 1, 'scroll_events': 1,
        }])
        self.assertEqual(tracker.peek_today().key_presses, 0)
        tracker.restore(rows)
        self.assertEqual(tracker.peek_today().key_presses, 2)

    def test_never_captures_character_identity(self):
        tracker = ActivityAccumulator(now=lambda: datetime(2026, 11, 22, 15))
        tracker.record_keypress()
        self.assertEqual(set(tracker.drain()[0]), {
            'day', 'hour', 'key_presses', 'mouse_clicks', 'scroll_events'
        })


if __name__ == '__main__':
    unittest.main()
