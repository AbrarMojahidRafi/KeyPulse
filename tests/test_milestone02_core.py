"""Milestone 02: tests without global input hooks or GUI requirements."""
from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from core.activity_tracker import ActivityAccumulator, ActivityMonitor
from core.keyboard_tracker import create_keyboard_listener
from core.mouse_tracker import create_mouse_listener
from database.db_manager import DatabaseManager


class TrackerAdapterTests(unittest.TestCase):
    def test_keyboard_event_identity_is_not_forwarded(self):
        # Inject a fake pynput module. The test never starts OS listeners.
        fake = ModuleType("pynput")
        fake.keyboard = SimpleNamespace(Listener=lambda **kwargs: SimpleNamespace(**kwargs))
        events = []
        with patch.dict(sys.modules, {"pynput": fake}):
            listener = create_keyboard_listener(lambda: events.append("press"))
        listener.on_press("do_not_capture_this_key")
        self.assertEqual(events, ["press"])

    def test_mouse_counts_press_and_scroll_but_not_release(self):
        fake = ModuleType("pynput")
        fake.mouse = SimpleNamespace(Listener=lambda **kwargs: SimpleNamespace(**kwargs))
        events = []
        with patch.dict(sys.modules, {"pynput": fake}):
            listener = create_mouse_listener(
                lambda: events.append("click"),
                lambda: events.append("scroll"),
            )
        listener.on_click(11, 22, "left", True)
        listener.on_click(11, 22, "left", False)
        listener.on_scroll(11, 22, 0, -1)
        self.assertEqual(events, ["click", "scroll"])


class AccumulatorTests(unittest.TestCase):
    def test_events_are_grouped_into_separate_hours(self):
        current = [datetime(2026, 11, 22, 14, 59)]
        acc = ActivityAccumulator(now=lambda: current[0])
        acc.record_keypress()
        current[0] = datetime(2026, 11, 22, 15, 0)
        acc.record_click()
        rows = sorted(acc.drain(), key=lambda row: row["hour"])
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0]["hour"], rows[0]["key_presses"]), (14, 1))
        self.assertEqual((rows[1]["hour"], rows[1]["mouse_clicks"]), (15, 1))
        self.assertEqual(acc.peek_today().key_presses, 0)

    def test_monitor_only_records_while_started(self):
        class FakeListener:
            def __init__(self):
                self.started = False
                self.stopped = False

            def start(self):
                self.started = True

            def stop(self):
                self.stopped = True

        acc = ActivityAccumulator(now=lambda: datetime(2026, 11, 22, 14))
        monitor = ActivityMonitor(acc)
        monitor._key_pressed()
        self.assertEqual(acc.peek_today().key_presses, 0)

        listeners = []
        def new_listener(*_args):
            listener = FakeListener()
            listeners.append(listener)
            return listener

        with patch("core.keyboard_tracker.create_keyboard_listener", side_effect=new_listener), \
             patch("core.mouse_tracker.create_mouse_listener", side_effect=new_listener):
            monitor.start()
            monitor._key_pressed()
            monitor._clicked()
            monitor._scrolled()
            monitor.pause()
            monitor._key_pressed()

            # Starting a second time creates fresh listener objects.
            monitor.start()
            monitor._key_pressed()
            monitor.pause()

        self.assertTrue(all(item.started and item.stopped for item in listeners))
        self.assertEqual(len(listeners), 4)
        self.assertEqual(acc.peek_today().key_presses, 2)
        self.assertEqual(acc.peek_today().mouse_clicks, 1)
        self.assertEqual(acc.peek_today().scroll_events, 1)


class SQLitePipelineTests(unittest.TestCase):
    def test_same_hour_upsert_updates_only_aggregate_columns(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "lesson.db"
            db = DatabaseManager(path)
            try:
                db.add_aggregates([{
                    "day": "2026-11-22", "hour": 14,
                    "key_presses": 5, "mouse_clicks": 2, "scroll_events": 3,
                }])
                db.add_aggregates([{
                    "day": "2026-11-22", "hour": 14,
                    "key_presses": 1, "mouse_clicks": 1, "scroll_events": 0,
                }])
                self.assertEqual(db.today_totals(date(2026, 11, 22)), {
                    "key_presses": 6,
                    "mouse_clicks": 3,
                    "scroll_events": 3,
                })
                self.assertEqual(db.all_hourly_rows(), [
                    ("2026-11-22", 14, 6, 3, 3)
                ])
                cols = [col[1] for col in db._db.execute("PRAGMA table_info(hourly_activity)")]
                self.assertEqual(cols, [
                    "day", "hour", "key_presses", "mouse_clicks", "scroll_events"
                ])
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
