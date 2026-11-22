"""KeyPulse v0.1: privacy-first, manually controlled desktop UI."""
from __future__ import annotations
from datetime import date
from PySide6.QtWidgets import QTabWidget

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QVBoxLayout,
    QWidget,
)

from analytics.reports import export_hourly_csv
from config import APP_VERSION
from core.activity_tracker import ActivityAccumulator, ActivityMonitor
from dashboard.charts import ActivityRangeChart, WeeklyActivityChart
from dashboard.widgets import MetricCard
from database.db_manager import DatabaseManager


DARK_STYLE = """
QWidget { background: #0b1220; color: #edf2fb; font-family: 'Segoe UI'; font-size: 11pt; }
QLabel#Heading { font-size: 26pt; font-weight: 700; }
QLabel#Subtitle, QLabel#CardHeading, QLabel#Footer { color: #a5b4c8; }
QLabel#CardNumber { font-size: 27pt; font-weight: 700; }
QLabel#SectionTitle { font-size: 13pt; font-weight: 600; }
QFrame#MetricCard, QFrame#Panel { background: #172237; border: 1px solid #273b58; border-radius: 13px; }
QFrame#MetricCard QLabel, QFrame#Panel QLabel, QFrame#Panel QProgressBar { background: transparent; }
QPushButton { background: #253652; border: 1px solid #39506f; border-radius: 9px; padding: 9px 16px; font-weight: 600; }
QPushButton:hover { background: #324a70; }
QPushButton#PrimaryButton { background: #2563eb; border: 1px solid #3b82f6; color: white; }
QPushButton#PrimaryButton:hover { background: #1d4ed8; }
QPushButton#DangerButton { background: #431f2c; color: #ffd3d9; border: 1px solid #8e4558; }
QComboBox { background: #253652; border: 1px solid #39506f; border-radius: 7px; padding: 8px; }
QComboBox QAbstractItemView { background: #172237; }
QProgressBar { background: #28364e; border: 0; border-radius: 6px; text-align: center; color: white; font-size: 9pt; }
QProgressBar::chunk { background: #3b82f6; border-radius: 6px; }
QScrollArea { border: none; }

QTabWidget::pane {
    background: #0b1220;
    border: 1px solid #273b58;
    border-radius: 9px;
}

QTabBar::tab {
    background: #253652;
    color: #cbd5e1;
    padding: 10px 18px;
    margin-right: 4px;
    border: 1px solid #39506f;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #172237;
    color: #ffffff;
    border-bottom: 2px solid #3b82f6;
}

QTabBar::tab:hover:!selected {
    background: #324a70;
}

"""
LIGHT_STYLE = """
QWidget { background: #f5f7fc; color: #1b2437; font-family: 'Segoe UI'; font-size: 11pt; }
QLabel#Heading { font-size: 26pt; font-weight: 700; }
QLabel#Subtitle, QLabel#CardHeading, QLabel#Footer { color: #5f6c81; }
QLabel#CardNumber { font-size: 27pt; font-weight: 700; }
QLabel#SectionTitle { font-size: 13pt; font-weight: 600; }
QFrame#MetricCard, QFrame#Panel { background: #ffffff; border: 1px solid #dee5ef; border-radius: 13px; }
QFrame#MetricCard QLabel, QFrame#Panel QLabel, QFrame#Panel QProgressBar { background: transparent; }
QPushButton { background: #e9edf6; border: 1px solid #d0d9e5; border-radius: 9px; padding: 9px 16px; font-weight: 600; }
QPushButton:hover { background: #dce5f4; }
QPushButton#PrimaryButton { background: #245fe6; border: 1px solid #245fe6; color: white; }
QPushButton#PrimaryButton:hover { background: #174dc2; }
QPushButton#DangerButton { background: #fff0f0; color: #9e253c; border: 1px solid #ffc0cb; }
QComboBox { background: #ffffff; border: 1px solid #ccd7e5; border-radius: 7px; padding: 8px; }
QComboBox QAbstractItemView { background: #ffffff; }
QProgressBar { background: #e5ebf5; border: 0; border-radius: 6px; text-align: center; color: #18243a; font-size: 9pt; }
QProgressBar::chunk { background: #75a0ff; border-radius: 6px; }
QScrollArea { border: none; }

QTabWidget::pane {
    background: #f5f7fc;
    border: 1px solid #dee5ef;
    border-radius: 9px;
}

QTabBar::tab {
    background: #e9edf6;
    color: #344054;
    padding: 10px 18px;
    margin-right: 4px;
    border: 1px solid #d0d9e5;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #174dc2;
    border-bottom: 2px solid #245fe6;
}

QTabBar::tab:hover:!selected {
    background: #dce5f4;
}

"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"KeyPulse v{APP_VERSION} - Personal Activity Analytics")
        self.setMinimumSize(760, 590)
        self.resize(950, 710)
        self.db = DatabaseManager()
        self.accumulator = ActivityAccumulator()
        self.monitor = ActivityMonitor(self.accumulator)
        self._build_ui()
        self._apply_theme("Dark")
        self._refresh()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(2500)

    def _build_ui(self) -> None:
        scroller = QScrollArea(self)
        scroller.setWidgetResizable(True)
        content = QWidget()
        container = QVBoxLayout(content)
        container.setContentsMargins(32, 30, 32, 24)
        container.setSpacing(22)

        heading = QLabel("KeyPulse")
        heading.setObjectName("Heading")
        subtitle = QLabel("Your personal desktop activity dashboard - local data only")
        subtitle.setObjectName("Subtitle")
        container.addWidget(heading)
        container.addWidget(subtitle)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.status_label = QLabel("● PAUSED - no activity is being recorded")
        controls.addWidget(self.status_label, 1)
        self.theme_picker = QComboBox()
        self.theme_picker.addItems(["Dark", "Light"])
        self.theme_picker.currentTextChanged.connect(self._apply_theme)
        controls.addWidget(self.theme_picker)
        container.addLayout(controls)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self.record_button = QPushButton("Start tracking")
        self.record_button.setObjectName("PrimaryButton")
        self.record_button.clicked.connect(self._toggle_tracking)
        export_button = QPushButton("Export CSV")
        export_button.clicked.connect(self._export_csv)
        erase_button = QPushButton("Delete all saved data")
        erase_button.setObjectName("DangerButton")
        erase_button.clicked.connect(self._delete_all)
        action_row.addWidget(self.record_button)
        action_row.addWidget(export_button)
        action_row.addStretch(1)
        action_row.addWidget(erase_button)
        container.addLayout(action_row)

        metrics = QGridLayout()
        metrics.setSpacing(14)
        self.keys_card = MetricCard("Today's keystrokes")
        self.clicks_card = MetricCard("Today's mouse clicks")
        self.scrolls_card = MetricCard("Today's scroll events")
        metrics.addWidget(self.keys_card, 0, 0)
        metrics.addWidget(self.clicks_card, 0, 1)
        metrics.addWidget(self.scrolls_card, 0, 2)
        container.addLayout(metrics)

        
        chart_tabs = QTabWidget()

        self.chart = WeeklyActivityChart()

        self.month_chart = ActivityRangeChart(
            "Keystrokes - last 30 days",
            30,
            "key_presses"
        )

        self.hour_chart = ActivityRangeChart(
            "All events - today by hour",
            24,
            "total",
            axis="hour"
        )

        self.mouse_chart = ActivityRangeChart(
            "Mouse clicks - last 7 days",
            7,
            "mouse_clicks"
        )

        chart_tabs.addTab(self.chart, "7 Days")
        chart_tabs.addTab(self.month_chart, "30 Days")
        chart_tabs.addTab(self.hour_chart, "Hourly")
        chart_tabs.addTab(self.mouse_chart, "Mouse")

        container.addWidget(chart_tabs)


        privacy_panel = QFrame()
        privacy_panel.setObjectName("Panel")
        privacy_layout = QVBoxLayout(privacy_panel)
        privacy_layout.setContentsMargins(20, 18, 20, 18)
        privacy_layout.setSpacing(9)
        label = QLabel("Privacy by design")
        label.setObjectName("SectionTitle")
        text = QLabel(
            "Tracking is OFF when the application opens. This version counts key presses, "
            "mouse clicks and scroll events only. It never saves typed words, passwords, "
            "key identity, window titles, screenshots or cursor positions. "
            "It writes hourly summaries to SQLite on this PC; no cloud connection is used. "
            "Global activity counts can include typing in password fields."
        )
        text.setWordWrap(True)
        privacy_layout.addWidget(label)
        privacy_layout.addWidget(text)
        container.addWidget(privacy_panel)

        footer = QLabel(f"KeyPulse v{APP_VERSION}  |  Open source starter  |  You control when tracking starts and stops")
        footer.setObjectName("Footer")
        container.addWidget(footer)
        container.addStretch(1)
        scroller.setWidget(content)
        self.setCentralWidget(scroller)

    def _apply_theme(self, theme: str) -> None:
        self.setStyleSheet(DARK_STYLE if theme == "Dark" else LIGHT_STYLE)

    def _toggle_tracking(self) -> None:
        if self.monitor.is_running:
            self.monitor.pause()
            self._flush()
        else:
            try:
                self.monitor.start()
            except Exception as exc:
                QMessageBox.critical(self, "Unable to start tracking", str(exc))
        self._update_controls()
        self._refresh()

    def _update_controls(self) -> None:
        if self.monitor.is_running:
            self.status_label.setText("● TRACKING - keyboard and mouse events are counted")
            self.record_button.setText("Pause tracking")
        else:
            self.status_label.setText("● PAUSED - no activity is being recorded")
            self.record_button.setText("Start tracking")

    def _flush(self) -> None:
        batch = self.accumulator.drain()
        try:
            self.db.add_aggregates(batch)
        except Exception as exc:
            self.accumulator.restore(batch)
            self.monitor.pause()
            self._update_controls()
            QMessageBox.critical(self, "Data could not be saved", f"Tracking is paused.\n{exc}")

    def _refresh(self) -> None:
        today = self.db.today_totals()
        pending = self.accumulator.peek_today()
        self.keys_card.set_value(today["key_presses"] + pending.key_presses)
        self.clicks_card.set_value(today["mouse_clicks"] + pending.mouse_clicks)
        self.scrolls_card.set_value(today["scroll_events"] + pending.scroll_events)
        last_seven_days = self.db.daily_totals(7)

        self.chart.display(last_seven_days)
        self.mouse_chart.display(last_seven_days)

        self.month_chart.display(
            self.db.daily_totals(30)
        )

        self.hour_chart.display(
            self.db.hourly_totals(date.today())
        )

    def _tick(self) -> None:
        self._flush()
        self._refresh()

    def _export_csv(self) -> None:
        self._flush()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export hourly summary", "KeyPulse-activity.csv", "CSV file (*.csv)"
        )
        if not path:
            return
        try:
            count = export_hourly_csv(self.db, path)
            QMessageBox.information(self, "CSV exported", f"Saved {count} aggregate hourly rows.")
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _delete_all(self) -> None:
        answer = QMessageBox.question(
            self, "Delete all activity history?",
            "This permanently deletes your saved local activity counts. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.monitor.pause()
        self.accumulator.drain()  # Discard unsaved counts; do not flush them.
        self.db.delete_all()
        self._update_controls()
        self._refresh()

    def closeEvent(self, event) -> None:
        self.timer.stop()
        self.monitor.pause()
        self._flush()
        self.db.close()
        super().closeEvent(event)
