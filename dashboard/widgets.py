"""Reusable, lightweight dashboard cards."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    def __init__(self, heading: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setMinimumWidth(175)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        heading_label = QLabel(heading)
        heading_label.setObjectName("CardHeading")
        self.number = QLabel("0")
        self.number.setObjectName("CardNumber")
        self.number.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(heading_label)
        layout.addWidget(self.number)

    def set_value(self, value: int) -> None:
        self.number.setText(f"{value:,}")
