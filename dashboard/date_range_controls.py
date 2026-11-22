"""Click-based, accessible date range controls for KeyPulse's analytics panel."""
from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit, QFrame, QGridLayout, QLabel, QPushButton,
)


class PageScrollDateEdit(QDateEdit):
    """Mouse wheel scrolls the dashboard, rather than changing a date."""

    def wheelEvent(self, event) -> None:
        event.ignore()


class DateRangeControls(QFrame):
    applyRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        grid = QGridLayout(self)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        start_label = QLabel("Start date")
        end_label = QLabel("End date")
        self.start_edit = PageScrollDateEdit()
        self.end_edit = PageScrollDateEdit()
        for edit, label in ((self.start_edit, "Start date"), (self.end_edit, "End date")):
            edit.setCalendarPopup(True)
            edit.setDisplayFormat("dd MMM yyyy")
            edit.setAccessibleName(label)
            edit.setMinimumWidth(126)
            edit.setMaximumDate(QDate.currentDate())

        today = date.today()
        first = today - timedelta(days=6)
        self.start_edit.setDate(QDate(first.year, first.month, first.day))
        self.end_edit.setDate(QDate(today.year, today.month, today.day))

        self.apply_button = QPushButton("Apply dates")
        self.apply_button.setAccessibleName("Apply selected date range")
        self.apply_button.clicked.connect(lambda _checked=False: self.applyRequested.emit())
        self.feedback = QLabel("")
        self.feedback.setWordWrap(True)
        self.feedback.setVisible(False)

        grid.addWidget(start_label, 0, 0)
        grid.addWidget(end_label, 0, 1)
        grid.addWidget(self.start_edit, 1, 0)
        grid.addWidget(self.end_edit, 1, 1)
        grid.addWidget(self.apply_button, 1, 2)
        grid.addWidget(self.feedback, 2, 0, 1, 3)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

    @staticmethod
    def _as_date(value: QDate) -> date:
        return date(value.year(), value.month(), value.day())

    def selected_dates(self) -> tuple[date, date]:
        return self._as_date(self.start_edit.date()), self._as_date(self.end_edit.date())

    def set_feedback(self, message: str, *, error: bool = False, dark: bool = True) -> None:
        self.feedback.setText(message)
        if error:
            ink = "#ff9ea1" if dark else "#b42318"
        else:
            ink = "#91e4b2" if dark else "#067647"
        self.feedback.setStyleSheet(f"color: {ink};")
        self.feedback.setVisible(bool(message))
