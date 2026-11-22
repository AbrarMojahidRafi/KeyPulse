r"""Milestone 02: practice the complete count -> SQLite pipeline.

This demo does NOT connect to the keyboard or mouse. It simulates counts,
uses a disposable database, and never touches real KeyPulse user data.

From the KeyPulse project root, run:
    .\.venv\Scripts\python.exe -m scripts.milestone02_demo
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from core.activity_tracker import ActivityAccumulator
from database.db_manager import DatabaseManager


def main() -> None:
    # Fixed time keeps the lesson output the same on every computer.
    sample_time = datetime(2026, 11, 22, 14, 30)
    counts = ActivityAccumulator(now=lambda: sample_time)

    # Simulate five key-press callbacks, two mouse-press callbacks,
    # and three scroll callbacks. This is NOT real input monitoring.
    for _ in range(5):
        counts.record_keypress()
    for _ in range(2):
        counts.record_click()
    for _ in range(3):
        counts.record_scroll()

    print("[1] In-memory totals:", counts.peek_today())

    # The database is created in a temporary directory, NOT LocalAppData.
    with TemporaryDirectory(prefix="keypulse_lesson_") as folder:
        db = DatabaseManager(Path(folder) / "lesson.db")
        try:
            db.add_aggregates(counts.drain())
            print("[2] After first save:", db.today_totals(date(2026, 11, 22)))

            # A second save in the same hour updates the existing row.
            counts.record_keypress()
            counts.record_click()
            db.add_aggregates(counts.drain())

            print("[3] After second save:", db.today_totals(date(2026, 11, 22)))
            print("[4] Hourly SQLite rows:", db.all_hourly_rows())
            print("[5] Unsent events after save:", counts.peek_today())
        finally:
            db.close()

    print("Done. Temporary lesson database was deleted.")
    print("No global keyboard or mouse listeners were started.")


if __name__ == "__main__":
    main()
