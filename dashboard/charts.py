"""Seven-day activity bars (built into Qt, no external plotting dependency)."""
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout


class WeeklyActivityChart(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 20, 22, 22)
        outer.setSpacing(12)
        title = QLabel("Keystrokes - last 7 days")
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        self.bars: list[tuple[QLabel, QProgressBar]] = []
        for _ in range(7):
            row = QHBoxLayout()
            label = QLabel("-")
            label.setMinimumWidth(78)
            bar = QProgressBar()
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setFormat("0")
            bar.setMinimumHeight(23)
            row.addWidget(label)
            row.addWidget(bar, 1)
            outer.addLayout(row)
            self.bars.append((label, bar))

    def display(self, records: list[dict[str, str | int]]) -> None:
        maximum = max((int(r["key_presses"]) for r in records), default=0)
        for (label, bar), record in zip(self.bars, records):
            day = date.fromisoformat(str(record["day"]))
            number = int(record["key_presses"])
            label.setText(day.strftime("%a %d"))
            bar.setRange(0, max(1, maximum))
            bar.setValue(number)
            bar.setFormat(f"{number:,} keys")
