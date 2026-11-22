"""Seven-day activity bars (built into Qt, no external plotting dependency)."""
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QVBoxLayout, QWidget
)


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


class ActivityRangeChart(QFrame):
    """Scrollable bars for daily or hourly activity."""

    def __init__(
        self, heading: str, row_count: int,
        metric: str, axis: str = "day", parent=None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.metric = metric
        self.axis = axis

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)

        title = QLabel(heading)
        title.setObjectName("SectionTitle")
        outer.addWidget(title)

        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFixedHeight(330)
        scroller.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        rows_layout = QVBoxLayout(inner)
        rows_layout.setSpacing(8)

        self.bars = []

        for _ in range(row_count):
            line = QHBoxLayout()

            label = QLabel("-")
            label.setMinimumWidth(75)

            bar = QProgressBar()
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setFormat("0")

            line.addWidget(label)
            line.addWidget(bar, 1)
            rows_layout.addLayout(line)

            self.bars.append((label, bar))

        scroller.setWidget(inner)
        outer.addWidget(scroller)

    def _count(self, row):
        if self.metric == "total":
            return sum(int(row[k]) for k in (
                "key_presses",
                "mouse_clicks",
                "scroll_events"
            ))

        return int(row[self.metric])

    def display(self, records):
        maximum = max(
            (self._count(row) for row in records),
            default=0
        )

        unit = "events" if self.metric == "total" else "counts"

        for index, (label, bar) in enumerate(self.bars):
            if index >= len(records):
                label.setText("-")
                bar.setRange(0, 1)
                bar.setValue(0)
                bar.setFormat("0")
                continue

            row = records[index]

            if self.axis == "hour":
                label.setText(
                    f"{int(row['hour']):02d}:00"
                )
            else:
                day = date.fromisoformat(str(row["day"]))
                label.setText(day.strftime("%d %b"))

            count = self._count(row)

            bar.setRange(0, max(1, maximum))
            bar.setValue(count)
            bar.setFormat(f"{count:,} {unit}")
