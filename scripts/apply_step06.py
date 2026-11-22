"""Patch the polished KeyPulse Step 05 AnalyticsPanel to add custom date ranges.

Standard-library-only patcher: strict anchors, AST validation, backup to the
user home directory, and idempotence. It does not touch tracking or SQLite.
"""
from __future__ import annotations

import ast
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "dashboard" / "analytics_panel.py"
REQUIRED = [
    ROOT / "analytics" / "custom_range.py",
    ROOT / "dashboard" / "date_range_controls.py",
]
MARKER = "# KeyPulse Step 06 custom date ranges"


def replace_one(source: str, old: str, new: str, description: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(
            f"Could not find the unique {description} block "
            f"(found {count}); no files changed."
        )
    return source.replace(old, new, 1)


def build(original: str) -> str:
    if MARKER in original:
        return original  # patch was already applied
    if "class MouseWheelPassThroughTabBar" not in original or "def _reflow_cards" not in original:
        raise ValueError("Step 05 UI Polish code was not found; apply that first.")

    revised = replace_one(
        original,
        "from analytics.overview_data import build_overview, format_peak_hour\n",
        "from analytics.overview_data import build_overview, format_peak_hour\n"
        "from analytics.custom_range import (\n"
        "    build_custom_overview, chart_rows_for_range, validate_date_range,\n"
        ")\n"
        "from dashboard.date_range_controls import DateRangeControls\n"
        f"{MARKER}\n",
        "new imports",
    )
    revised = replace_one(
        revised,
        '        self.period_picker.addItem("Last 30 Days", 30)\n'
        '        self.period_picker.setCurrentIndex(1)\n'
        '        controls.addWidget(self.period_picker)\n'
        '        root.addLayout(controls)\n',
        '        self.period_picker.addItem("Last 30 Days", 30)\n'
        '        self.period_picker.addItem("Custom range", "custom")\n'
        '        self.period_picker.setCurrentIndex(1)\n'
        '        controls.addWidget(self.period_picker)\n'
        '        root.addLayout(controls)\n'
        '\n'
        '        self.custom_controls = DateRangeControls()\n'
        '        self.custom_controls.setVisible(False)\n'
        '        self._applied_custom_range = self.custom_controls.selected_dates()\n'
        '        root.addWidget(self.custom_controls)\n'
        '        self.range_caption = QLabel("")\n'
        '        self.range_caption.setObjectName("Subtitle")\n'
        '        self.range_caption.setWordWrap(True)\n'
        '        root.addWidget(self.range_caption)\n',
        "period selector controls",
    )
    revised = replace_one(
        revised,
        '        self.period_picker.currentIndexChanged.connect(lambda _index: self.refresh(force=True))\n'
        '        self._style_tabs()\n'
        '        self._reflow_cards()\n'
        '        self.refresh(force=True)\n',
        '        self.period_picker.currentIndexChanged.connect(self._on_period_changed)\n'
        '        self.custom_controls.applyRequested.connect(self._apply_custom_dates)\n'
        '        self._style_tabs()\n'
        '        self._reflow_cards()\n'
        '        self._on_period_changed()\n',
        "panel startup wiring",
    )
    revised = replace_one(
        revised,
        '    @staticmethod\n'
        '    def _card(grid: QGridLayout, row: int, column: int, label: str) -> QLabel:\n',
        '    def _on_period_changed(self, _index: int | None = None) -> None:\n'
        '        custom = self.period_picker.currentData() == "custom"\n'
        '        self.custom_controls.setVisible(custom)\n'
        '        self._last_signature = None\n'
        '        self.refresh(force=True)\n'
        '\n'
        '    def _apply_custom_dates(self) -> None:\n'
        '        start, end = self.custom_controls.selected_dates()\n'
        '        try:\n'
        '            validate_date_range(start, end)\n'
        '        except ValueError as error:\n'
        '            self.custom_controls.set_feedback(\n'
        '                str(error), error=True, dark=self._dark\n'
        '            )\n'
        '            return\n'
        '        self._applied_custom_range = (start, end)\n'
        '        self.custom_controls.set_feedback(\n'
        '            f"Applied: {start.isoformat()} to {end.isoformat()}", dark=self._dark\n'
        '        )\n'
        '        self._last_signature = None\n'
        '        self.refresh(force=True)\n'
        '\n'
        '    @staticmethod\n'
        '    def _card(grid: QGridLayout, row: int, column: int, label: str) -> QLabel:\n',
        "custom date event handlers",
    )
    revised = replace_one(
        revised,
        '    def refresh(self, force: bool = False) -> None:\n'
        '        days = int(self.period_picker.currentData())\n'
        '        data = build_overview(self.db, days)\n',
        '    def refresh(self, force: bool = False) -> None:\n'
        '        selection = self.period_picker.currentData()\n'
        '        if selection == "custom":\n'
        '            start, end = self._applied_custom_range\n'
        '            data = build_custom_overview(self.db, start, end)\n'
        '            selection_key = ("custom", start.isoformat(), end.isoformat())\n'
        '        else:\n'
        '            days = int(selection)\n'
        '            data = build_overview(self.db, days)\n'
        '            selection_key = ("preset", days)\n',
        "period-aware refresh start",
    )
    revised = replace_one(
        revised,
        '            days, self._dark, data["as_of"],\n',
        '            selection_key, self._dark, data["as_of"],\n',
        "refresh signature",
    )
    revised = replace_one(
        revised,
        '        self.empty_notice.setVisible(summary["total_events"] == 0)\n'
        '\n'
        '        day_labels = [date.fromisoformat(str(r["day"])).strftime("%d/%m") for r in daily]\n',
        '        self.empty_notice.setVisible(summary["total_events"] == 0)\n'
        '        self.range_caption.setText(\n'
        '            f"Showing {daily[0][\'day\']} to {daily[-1][\'day\']} "\n'
        '            f"({len(daily)} days). Hourly tab always shows today."\n'
        '        )\n'
        '\n'
        '        chart_daily = chart_rows_for_range(daily)\n'
        '        day_labels = [str(r["label"]) for r in chart_daily]\n',
        "chart date labels and range caption",
    )
    # Only replace values used in the trend and mouse graphs, not hourly data.
    for field in ("key_presses", "mouse_clicks", "scroll_events"):
        old = f'[int(r["{field}"]) for r in daily]'
        new = f'[int(r["{field}"]) for r in chart_daily]'
        count = revised.count(old)
        if count not in (1, 2):
            raise ValueError(f"Could not locate the expected chart data for {field} ({count} occurrences).")
        revised = revised.replace(old, new)

    ast.parse(revised, filename=str(TARGET))
    return revised


def main() -> int:
    if not TARGET.is_file():
        print("ERROR: dashboard/analytics_panel.py is missing. Open your existing KeyPulse project.")
        return 1
    for path in REQUIRED:
        if not path.is_file():
            print(f"ERROR: Missing required file: {path.relative_to(ROOT)}")
            return 1
    source = TARGET.read_text(encoding="utf-8")
    try:
        output = build(source)
    except (ValueError, SyntaxError) as error:
        print(f"ABORTED without changes: {error}")
        return 1
    if output == source:
        print("Already applied. Step 06 code has not been changed again.")
        return 0
    backup_root = Path.home() / ".keypulse_dev_backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = backup_root / f"analytics_panel.before_step06.{stamp}.py"
    backup.write_text(source, encoding="utf-8")
    TARGET.write_text(output, encoding="utf-8")
    print("SUCCESS: Step 06 custom date range integrated into dashboard/analytics_panel.py")
    print(f"Backup: {backup}")
    print("Next: python -m py_compile dashboard/analytics_panel.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
