"""Advanced KeyPulse charts and date-range cards, using PySide6 QtCharts.

Drop-in widget used by the existing MainWindow. It does not change tracking.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCharts import (
    QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis,
)
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QSizePolicy,
    QTabBar, QTabWidget, QVBoxLayout, QWidget,
)

from analytics.overview_data import build_overview, format_peak_hour


class MouseWheelPassThroughTabBar(QTabBar):
    """Wheel events should scroll the main page, not switch chart tabs."""

    def wheelEvent(self, event) -> None:
        event.ignore()


class PageScrollChartView(QChartView):
    """Do not use nested mouse-wheel scrolling inside chart views."""

    def wheelEvent(self, event) -> None:
        event.ignore()


class PageScrollComboBox(QComboBox):
    """Change the date range by clicking, not by mouse wheel."""

    def wheelEvent(self, event) -> None:
        event.ignore()


class AnalyticsPanel(QWidget):
    """Period filter, activity summary and three graphical chart tabs."""

    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self.db = db
        self._dark = True
        self._last_signature = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        controls = QHBoxLayout()
        heading = QLabel("Advanced analytics")
        heading.setObjectName("SectionTitle")
        controls.addWidget(heading)
        controls.addStretch(1)

        self.period_picker = PageScrollComboBox()
        self.period_picker.setAccessibleName("Analytics date range")
        self.period_picker.addItem("Today", 1)
        self.period_picker.addItem("Last 7 Days", 7)
        self.period_picker.addItem("Last 30 Days", 30)
        self.period_picker.setCurrentIndex(1)
        controls.addWidget(self.period_picker)
        root.addLayout(controls)

        cards = QGridLayout()
        cards.setSpacing(12)
        self.total_value = self._card(cards, 0, 0, "Total events")
        self.average_value = self._card(cards, 0, 1, "Daily average")
        self.active_value = self._card(cards, 1, 0, "Days with activity")
        self.peak_value = self._card(cards, 1, 1, "Busiest hour today")
        root.addLayout(cards)
        self._metric_grid = cards
        self._metric_frames = [
            self.total_value.parentWidget(),
            self.average_value.parentWidget(),
            self.active_value.parentWidget(),
            self.peak_value.parentWidget(),
        ]
        self._wide_card_layout = None

        self.empty_notice = QLabel("No recorded activity for this date range yet.")
        self.empty_notice.setObjectName("Subtitle")
        self.empty_notice.setWordWrap(True)
        root.addWidget(self.empty_notice)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("KeyPulseAnalyticsTabs")
        self.tabs.setTabBar(MouseWheelPassThroughTabBar(self.tabs))
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.setUsesScrollButtons(False)
        self.tabs.tabBar().setUsesScrollButtons(False)
        self.tabs.tabBar().setExpanding(True)
        self.trend_view = self._chart_view()
        self.mouse_view = self._chart_view()
        self.hourly_view = self._chart_view()
        self.tabs.addTab(self.trend_view, "Activity trend")
        self.tabs.addTab(self.mouse_view, "Mouse activity")
        self.tabs.addTab(self.hourly_view, "Hourly today")
        root.addWidget(self.tabs)

        tip = QLabel("Trend/Mouse follow the selected range. Hourly always shows today. No raw keys are stored.")
        tip.setObjectName("Subtitle")
        tip.setWordWrap(True)
        root.addWidget(tip)

        self.period_picker.currentIndexChanged.connect(lambda _index: self.refresh(force=True))
        self._style_tabs()
        self._reflow_cards()
        self.refresh(force=True)

    @staticmethod
    def _card(grid: QGridLayout, row: int, column: int, label: str) -> QLabel:
        frame = QFrame()
        frame.setObjectName("MetricCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 12, 18, 12)
        caption = QLabel(label)
        caption.setObjectName("CardHeading")
        number = QLabel("—")
        number.setObjectName("CardNumber")
        number.setMinimumWidth(0)
        layout.addWidget(caption)
        layout.addWidget(number)
        grid.addWidget(frame, row, column)
        return number

    @staticmethod
    def _chart_view() -> QChartView:
        view = PageScrollChartView()
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        view.setFixedHeight(320)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFrameShape(QFrame.Shape.NoFrame)
        return view

    def set_dark_mode(self, dark: bool) -> None:
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
        self.tabs.setStyleSheet(f"""
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
        """)

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

    def _chart(self, title: str, labels: list[str], sets: list[tuple[str, list[int], str]]) -> QChart:
        chart = QChart()
        chart.setTheme(
            QChart.ChartThemeDark
            if self._dark else QChart.ChartThemeLight
        )
        chart.setAnimationOptions(QChart.NoAnimation)
        chart.setTitle(title)
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
        bars.setBarWidth(0.75)
        highest = 0
        for name, values, color in sets:
            bar_set = QBarSet(name)
            bar_set.append([float(value) for value in values])
            bar_set.setColor(QColor(color))
            bars.append(bar_set)
            highest = max(highest, max(values, default=0))
        chart.addSeries(bars)

        x_axis = QBarCategoryAxis()
        x_axis.append(labels)
        if len(labels) > 7:
            x_axis.setLabelsAngle(-60)
            x_axis.setLabelsFont(QFont("Segoe UI", 8))
        x_axis.setLabelsBrush(QBrush(secondary))
        x_axis.setLinePen(QPen(grid))
        x_axis.setGridLineVisible(False)
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        bars.attachAxis(x_axis)

        y_axis = QValueAxis()
        ceiling = max(4, ((highest + 3) // 4) * 4)
        y_axis.setRange(0, ceiling)
        y_axis.setTickCount(5)
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

    @staticmethod
    def _replace_chart(view: QChartView, new_chart: QChart) -> None:
        old_chart = view.chart()
        view.setChart(new_chart)
        if old_chart is not None:
            old_chart.deleteLater()  # QChartView releases the previous chart.

    def refresh(self, force: bool = False) -> None:
        days = int(self.period_picker.currentData())
        data = build_overview(self.db, days)
        daily = data["daily"]
        hours = data["hourly_today"]
        summary = data["summary"]
        signature = (
            days, self._dark, data["as_of"],
            tuple((r["day"], r["key_presses"], r["mouse_clicks"], r["scroll_events"]) for r in daily),
            tuple((r["hour"], r["key_presses"], r["mouse_clicks"], r["scroll_events"]) for r in hours),
        )
        if not force and signature == self._last_signature:
            return
        self._last_signature = signature

        self.total_value.setText(f"{summary['total_events']:,}")
        self.average_value.setText(f"{summary['average_events_per_day']:,.2f}")
        self.active_value.setText(str(data["active_days"]))
        self.peak_value.setText(format_peak_hour(data["busiest_hour_today"]))
        self.empty_notice.setVisible(summary["total_events"] == 0)

        day_labels = [date.fromisoformat(str(r["day"])).strftime("%d/%m") for r in daily]
        hour_labels = [f"{r['hour']:02d}:00" for r in hours]
        blue = "#3b82f6"
        green = "#19b6a0"
        amber = "#f59e0b"

        self._replace_chart(self.trend_view, self._chart(
            "Keyboard & mouse clicks", day_labels,
            [("Keypresses", [int(r["key_presses"]) for r in daily], blue),
             ("Clicks", [int(r["mouse_clicks"]) for r in daily], green)],
        ))
        self._replace_chart(self.mouse_view, self._chart(
            "Mouse clicks & scroll events", day_labels,
            [("Clicks", [int(r["mouse_clicks"]) for r in daily], green),
             ("Scrolls", [int(r["scroll_events"]) for r in daily], amber)],
        ))
        self._replace_chart(self.hourly_view, self._chart(
            "Today's activity by hour", hour_labels,
            [("Keypresses", [int(r["key_presses"]) for r in hours], blue),
             ("Clicks", [int(r["mouse_clicks"]) for r in hours], green),
             ("Scrolls", [int(r["scroll_events"]) for r in hours], amber)],
        ))
