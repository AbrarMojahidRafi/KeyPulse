"""Safely integrate the Step 05 analytics panel into an existing KeyPulse MainWindow.

Creates an untracked backup and aborts without writing if the old chart-tabs
block doesn't match the expected Step 04 structure. Repeat execution is safe.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "dashboard" / "main_window.py"
BACKUP = ROOT / "dashboard" / "main_window.py.before_step05.bak"


def one_replace(original: str, pattern: str, replacement: str, description: str) -> str:
    new, matches = re.subn(pattern, replacement, original, flags=re.MULTILINE | re.DOTALL)
    if matches != 1:
        raise ValueError(f"Expected 1 {description}; found {matches}. No file changed.")
    return new


def main() -> int:
    if not MAIN.is_file():
        print("ERROR: Run from the KeyPulse project where dashboard/main_window.py exists.")
        return 1

    source = MAIN.read_text(encoding="utf-8")
    if "self.analytics_panel = AnalyticsPanel(self.db)" in source:
        print("Step 05 is already integrated. No changes made.")
        return 0

    for relative in (
        "analytics/overview_data.py",
        "dashboard/analytics_panel.py",
        "tests/test_milestone03_step05.py",
    ):
        if not (ROOT / relative).is_file():
            print(f"ERROR: Missing {relative}. Copy the add-on files first.")
            return 1

    try:
        updated = source
        if "from dashboard.analytics_panel import AnalyticsPanel" not in updated:
            updated = one_replace(
                updated,
                r"^(from dashboard\.charts import [^\n]+\n)",
                r"\1from dashboard.analytics_panel import AnalyticsPanel\n",
                "dashboard.charts import",
            )

        updated = one_replace(
            updated,
            r"^        chart_tabs = QTabWidget\(\)[^\n]*\n.*?^        container\.addWidget\(chart_tabs\)[^\n]*\n",
            "        self.analytics_panel = AnalyticsPanel(self.db)\n"
            "        container.addWidget(self.analytics_panel)\n",
            "Step 04 QTabWidget chart block",
        )

        updated = one_replace(
            updated,
            r"^        last_seven_days = self\.db\.daily_totals\(7\)[^\n]*\n.*?^        self\.hour_chart\.display\(\s*self\.db\.hourly_totals\(date\.today\(\)\)\s*\)[^\n]*\n",
            "        self.analytics_panel.refresh()\n",
            "Step 04 chart refresh block",
        )

        updated = one_replace(
            updated,
            r"^(    def _apply_theme\(self, theme: str\) -> None:\n        self\.setStyleSheet\(DARK_STYLE if theme == \"Dark\" else LIGHT_STYLE\)\n)",
            r'\1        self.analytics_panel.set_dark_mode(theme == "Dark")\n',
            "theme method",
        )
        ast.parse(updated)
    except (ValueError, SyntaxError) as exc:
        print(f"ABORTED: {exc}")
        print("Your current main_window.py was not modified. See manual instructions in docs/STEP05_GUIDE_BN.md.")
        return 1

    if BACKUP.exists():
        print(f"ABORTED: Backup already exists: {BACKUP}")
        print("Please review it and move it aside before running again.")
        return 1
    BACKUP.write_text(source, encoding="utf-8")
    MAIN.write_text(updated, encoding="utf-8")
    print("Step 05 integration applied successfully.")
    print(f"Backup: {BACKUP}")
    print("Next: python -m py_compile dashboard/main_window.py dashboard/analytics_panel.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
