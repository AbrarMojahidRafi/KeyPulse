import unittest

from analytics.statistics import period_summary, most_active_hour


class StatisticsTests(unittest.TestCase):

    def test_period_summary(self):
        rows = [
            {
                "key_presses": 5,
                "mouse_clicks": 2,
                "scroll_events": 1
            },
            {
                "key_presses": 0,
                "mouse_clicks": 0,
                "scroll_events": 0
            },
            {
                "key_presses": 8,
                "mouse_clicks": 3,
                "scroll_events": 4
            }
        ]

        result = period_summary(rows)

        self.assertEqual(result["key_presses"], 13)
        self.assertEqual(result["total_events"], 23)
        self.assertEqual(result["average_events_per_day"], 7.67)

    def test_empty_period(self):
        result = period_summary([])

        self.assertEqual(result["total_events"], 0)
        self.assertEqual(result["average_events_per_day"], 0.0)

    def test_most_active_hour(self):
        hours = [
            {
                "hour": 9,
                "key_presses": 2,
                "mouse_clicks": 0,
                "scroll_events": 1
            },
            {
                "hour": 10,
                "key_presses": 4,
                "mouse_clicks": 2,
                "scroll_events": 0
            }
        ]

        self.assertEqual(most_active_hour(hours), 10)
        self.assertIsNone(most_active_hour([]))


if __name__ == "__main__":
    unittest.main()