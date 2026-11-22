"""Thread-safe, aggregate-only activity counting and global listener lifecycle.

This application never stores individual key events, key names, window titles,
clipboard content, mouse positions, or typed text.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import Event, Lock
from typing import Callable


@dataclass
class ActivityCounts:
    key_presses: int = 0
    mouse_clicks: int = 0
    scroll_events: int = 0

    def as_record(self, day: str, hour: int) -> dict[str, str | int]:
        return {
            "day": day,
            "hour": hour,
            "key_presses": self.key_presses,
            "mouse_clicks": self.mouse_clicks,
            "scroll_events": self.scroll_events,
        }


class ActivityAccumulator:
    """Keep only per-hour counters in memory, with no event history."""

    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or datetime.now
        self._lock = Lock()
        self._buckets: dict[tuple[str, int], ActivityCounts] = {}

    def _record(self, field: str) -> None:
        now = self._now()
        key = (now.date().isoformat(), now.hour)
        with self._lock:
            bucket = self._buckets.setdefault(key, ActivityCounts())
            setattr(bucket, field, getattr(bucket, field) + 1)

    def record_keypress(self) -> None:
        self._record("key_presses")

    def record_click(self) -> None:
        self._record("mouse_clicks")

    def record_scroll(self) -> None:
        self._record("scroll_events")

    def peek_today(self) -> ActivityCounts:
        today = self._now().date().isoformat()
        with self._lock:
            rows = [count for (day, _), count in self._buckets.items() if day == today]
            return ActivityCounts(
                sum(row.key_presses for row in rows),
                sum(row.mouse_clicks for row in rows),
                sum(row.scroll_events for row in rows),
            )

    def drain(self) -> list[dict[str, str | int]]:
        """Atomically transfer aggregate counters for batched SQLite writes."""
        with self._lock:
            records = [v.as_record(*key) for key, v in self._buckets.items()]
            self._buckets.clear()
        return records

    def restore(self, records: list[dict[str, str | int]]) -> None:
        """Restore counts if a database transaction failed."""
        with self._lock:
            for record in records:
                key = (str(record["day"]), int(record["hour"]))
                bucket = self._buckets.setdefault(key, ActivityCounts())
                bucket.key_presses += int(record["key_presses"])
                bucket.mouse_clicks += int(record["mouse_clicks"])
                bucket.scroll_events += int(record["scroll_events"])


class ActivityMonitor:
    """Explicitly started/stopped global keyboard and mouse listeners."""

    def __init__(self, accumulator: ActivityAccumulator) -> None:
        self.accumulator = accumulator
        self._active = Event()
        self._keyboard = None
        self._mouse = None

    @property
    def is_running(self) -> bool:
        return self._active.is_set()

    def _key_pressed(self) -> None:
        if self._active.is_set():
            self.accumulator.record_keypress()

    def _clicked(self) -> None:
        if self._active.is_set():
            self.accumulator.record_click()

    def _scrolled(self) -> None:
        if self._active.is_set():
            self.accumulator.record_scroll()

    def start(self) -> None:
        if self.is_running:
            return
        from core.keyboard_tracker import create_keyboard_listener
        from core.mouse_tracker import create_mouse_listener

        self._keyboard = create_keyboard_listener(self._key_pressed)
        self._mouse = create_mouse_listener(self._clicked, self._scrolled)
        self._active.set()
        try:
            self._keyboard.start()
            self._mouse.start()
        except Exception:
            self.pause()
            raise

    def pause(self) -> None:
        self._active.clear()
        for listener in (self._keyboard, self._mouse):
            if listener is not None:
                try:
                    listener.stop()
                except Exception:
                    pass
        self._keyboard = None
        self._mouse = None
