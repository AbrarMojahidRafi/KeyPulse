"""Safely polish the existing KeyPulse Step 05 analytics panel.

Scope: dashboard/analytics_panel.py only. Idempotent; backups and syntax
validation protect the existing project. Uses Python standard library only.
"""
from __future__ import annotations

import ast
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "dashboard" / "analytics_panel.py"
MARKER = "class MouseWheelPassThroughTabBar(QTabBar):"


def change_once(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one '{name}' block, found {count}; aborting safely.")
    return text.replace(old, new, 1)


def build(source: str) -> str:
    if MARKER in source:
        return source
    ast.parse(source, filename=str(TARGET))
    new = source
    new = change_once(
        new, "from PySide6.QtCore import Qt\n",
        "from PySide6.QtCore import QMargins, Qt\n",
        "QtCore imports",
    )
    new = change_once(
        new, "from PySide6.QtGui import QColor, QFont, QPainter\n",
        "from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen\n",
        "QtGui imports",
    )
    new = change_once(
        new,
        "    QTabWidget, QVBoxLayout, QWidget,\n",
        "    QTabBar, QTabWidget, QVBoxLayout, QWidget,\n",
        "QtWidgets imports",
    )
    new = change_once(
        new,
        "\nclass AnalyticsPanel(QWidget):\n",
        """
class MouseWheelPassThroughTabBar(QTabBar):
    \"\"\"Wheel events should scroll the main page, not switch chart tabs.\"\"\"

    def wheelEvent(self, event) -> None:
        event.ignore()


class PageScrollChartView(QChartView):
    \"\"\"Do not use nested mouse-wheel scrolling inside chart views.\"\"\"

    def wheelEvent(self, event) -> None:
        event.ignore()


class PageScrollComboBox(QComboBox):
    \"\"\"Change the date range by clicking, not by mouse wheel.\"\"\"

    def wheelEvent(self, event) -> None:
        event.ignore()


class AnalyticsPanel(QWidget):
""",
        "wheel-safe widget classes",
    )
    new = change_once(
        new,
        """        root.addLayout(cards)

        self.empty_notice""",
        """        root.addLayout(cards)
        self._metric_grid = cards
        self._metric_frames = [
            self.total_value.parentWidget(),
            self.average_value.parentWidget(),
            self.active_value.parentWidget(),
            self.peak_value.parentWidget(),
        ]
        self._wide_card_layout = None

        self.empty_notice""",
        "dashboard responsive cards",
    )
    new = change_once(
        new,
        """        self.period_picker = QComboBox()
""",
        """        self.period_picker = PageScrollComboBox()
""",
        "date range selector wheel handling",
    )
    new = change_once(
        new,
        """        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
""",
        """        self.tabs = QTabWidget()
        self.tabs.setObjectName("KeyPulseAnalyticsTabs")
        self.tabs.setTabBar(MouseWheelPassThroughTabBar(self.tabs))
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.setUsesScrollButtons(False)
        self.tabs.tabBar().setUsesScrollButtons(False)
        self.tabs.tabBar().setExpanding(True)
""",
        "tab setup",
    )
    new = change_once(
        new,
        """        self.period_picker.currentIndexChanged.connect(lambda _index: self.refresh(force=True))
        self.refresh(force=True)
""",
        """        self.period_picker.currentIndexChanged.connect(lambda _index: self.refresh(force=True))
        self._style_tabs()
        self._reflow_cards()
        self.refresh(force=True)
""",
        "panel startup",
    )
    new = change_once(
        new,
        """        view = QChartView()
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        view.setMinimumHeight(350)
        view.setFrameShape(QFrame.Shape.NoFrame)
""",
        """        view = PageScrollChartView()
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        view.setFixedHeight(320)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFrameShape(QFrame.Shape.NoFrame)
""",
        "chart view geometry",
    )
    new = change_once(
        new,
        """    def set_dark_mode(self, dark: bool) -> None:
        self._dark = dark
        self.refresh(force=True)

    def _chart(""",
        """    def set_dark_mode(self, dark: bool) -> None:
        self._dark = dark
        self._style_tabs()
        self.refresh(force=True)

    def _style_tabs(self) -> None:
        if self._dark:
            pane, idle, selected = "#0b1220", "#253652", "#172237"
            ink, muted, border, accent = "#ffffff", "#cbd5e1", "#344b68", "#3b82f6"
        else:
            pane, idle, selected = "#f5f7fc", "#e7edf7", "#ffffff"
            ink, muted, border, accent = "#1b2437", "#44546b", "#cbd5e1", "#245fe6"
        self.tabs.setStyleSheet(f\"\"\"
        QTabWidget#KeyPulseAnalyticsTabs::pane {{
            border: 1px solid {border}; border-radius: 10px;
            background: {pane}; top: -1px;
        }}
        QTabWidget#KeyPulseAnalyticsTabs QTabBar::tab {{
            background: {idle}; color: {muted};
            padding: 11px 8px; margin-right: 3px;
            border: 1px solid {border};
            border-top-left-radius: 8px; border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabWidget#KeyPulseAnalyticsTabs QTabBar::tab:selected {{
            background: {selected}; color: {ink};
            border-bottom: 3px solid {accent};
        }}
        QTabWidget#KeyPulseAnalyticsTabs QTabBar::tab:hover:!selected {{
            background: {selected}; color: {ink};
        }}
        \"\"\")

    def _reflow_cards(self) -> None:
        wide = self.width() >= 1050
        if self._wide_card_layout == wide:
            return
        for card in self._metric_frames:
            self._metric_grid.removeWidget(card)
        for index, card in enumerate(self._metric_frames):
            row, col = (0, index) if wide else divmod(index, 2)
            self._metric_grid.addWidget(card, row, col)
        self._wide_card_layout = wide

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_metric_grid"):
            self._reflow_cards()

    def _chart(""",
        "palette and responsive cards",
    )
    new = change_once(
        new,
        """        chart.setTitle(title)
        chart.setBackgroundRoundness(10)

        bars = QBarSeries()
""",
        """        chart.setTitle(title)
        chart.setBackgroundRoundness(10)
        chart.setDropShadowEnabled(False)
        chart.setMargins(QMargins(12, 12, 12, 6))
        bg = QColor("#172237" if self._dark else "#ffffff")
        foreground = QColor("#e5edf9" if self._dark else "#24334a")
        secondary = QColor("#a6b5ca" if self._dark else "#52647c")
        grid = QColor("#33445c" if self._dark else "#e3eaf2")
        chart.setBackgroundBrush(QBrush(bg))
        chart.setBackgroundPen(QPen(Qt.PenStyle.NoPen))
        chart.setTitleBrush(QBrush(foreground))
        chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))

        bars = QBarSeries()
""",
        "chart background and typography",
    )
    new = change_once(
        new,
        """        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        bars.attachAxis(x_axis)

        y_axis = QValueAxis()
""",
        """        x_axis.setLabelsBrush(QBrush(secondary))
        x_axis.setLinePen(QPen(grid))
        x_axis.setGridLineVisible(False)
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        bars.attachAxis(x_axis)

        y_axis = QValueAxis()
""",
        "chart x axis",
    )
    new = change_once(
        new,
        """        y_axis.setTickCount(5)
        y_axis.setLabelFormat("%.0f")
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        bars.attachAxis(y_axis)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        return chart
""",
        """        y_axis.setTickCount(5)
        y_axis.setLabelFormat("%.0f")
        y_axis.setLabelsBrush(QBrush(secondary))
        y_axis.setLinePen(QPen(grid))
        y_axis.setGridLinePen(QPen(grid))
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        bars.attachAxis(y_axis)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        for marker in chart.legend().markers():
            marker.setLabelBrush(QBrush(foreground))
        return chart
""",
        "chart y axis and legend",
    )
    ast.parse(new, filename=str(TARGET))
    return new


def main() -> int:
    if not TARGET.is_file():
        print("ERROR: analytics_panel.py missing. Copy this script into the existing KeyPulse scripts folder.")
        return 1
    original = TARGET.read_text(encoding="utf-8")
    try:
        revised = build(original)
    except (ValueError, SyntaxError) as exc:
        print(f"ABORTED without changes: {exc}")
        return 1
    if revised == original:
        print("Already polished. No changes made.")
        return 0
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET.with_name(f"analytics_panel.py.before_ui_polish_{stamp}.bak")
    if backup.exists():
        print(f"ABORTED: backup exists: {backup}")
        return 1
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(revised, encoding="utf-8")
    print("SUCCESS: Step 05 UI polish applied to dashboard/analytics_panel.py")
    print(f"Backup: {backup.name}")
    print("Next: python -m py_compile dashboard/analytics_panel.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
