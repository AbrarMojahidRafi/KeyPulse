# KeyPulse — Milestone 03 / Step 06: Custom Date Range & Dashboard Interaction

## Objective

Use the **same** KeyPulse project and the `feature/milestone-03-analytics` branch. Add a calendar-based Start / End selection to the Step 05 Analytics Panel, while preserving keyboard/mouse tracking, SQLite data, scroll behavior, charts, and dark/light themes.

**Prerequisite:** Step 05 + UI Polish already working and committed to the feature branch.

## 1. Verify branch (in VS Code PowerShell)

```powershell
git branch --show-current
git status
```

Expected branch: `feature/milestone-03-analytics`. Make sure prior work is committed. Don't make a new repository or overwrite `main.py`, `db_manager.py`, `main_window.py`, or `analytics_panel.py` manually.

## 2. Copy the add-on files

Extract the Step 06 ZIP. Copy **the contents** of these folders into your existing KeyPulse folders:

| Source in ZIP | Destination in existing project |
| --- | --- |
| `analytics/custom_range.py` | `KeyPulse/analytics/custom_range.py` |
| `dashboard/date_range_controls.py` | `KeyPulse/dashboard/date_range_controls.py` |
| `scripts/apply_step06.py` | `KeyPulse/scripts/apply_step06.py` |
| `tests/test_milestone03_step06.py` | `KeyPulse/tests/test_milestone03_step06.py` |
| `docs/STEP06_GUIDE_BN.md` | `KeyPulse/docs/STEP06_GUIDE_BN.md` |

Do **not** overwrite your existing `dashboard/analytics_panel.py`: the script will update only targeted sections after checking the expected Step 05 UI Polish structure.

## 3. Apply integration patch

Close the KeyPulse window. From the original project root:

```powershell
python scripts/apply_step06.py
```

Expected:

```
SUCCESS: Step 06 custom date range integrated into dashboard/analytics_panel.py
Backup: ...
Next: python -m py_compile dashboard/analytics_panel.py
```

It backs up your `analytics_panel.py` under `%USERPROFILE%\.keypulse_dev_backups`, *outside* the repository. If it displays `ABORTED`, **do not modify the file manually**; inspect the message and ask for a targeted update. If it displays `Already applied`, it was already run successfully; you do not need to run it again.

## 4. Run syntax and unit tests

```powershell
python -m py_compile analytics/custom_range.py dashboard/date_range_controls.py dashboard/analytics_panel.py
python -m unittest discover -s tests -v
```

Expected in the previously tested starter: `Ran 30 tests ... OK` (22 original + 8 new tests).

These are primarily backend tests. Your Windows PC must still verify the PySide6 UI.

## 5. Launch the UI

```powershell
python main.py
```

In **Advanced analytics** select the dropdown:

- `Today` -> today's data
- `Last 7 Days` -> past seven calendar dates including today
- `Last 30 Days` -> past 30 calendar dates including today
- `Custom range` -> Start date and End date calendars appear

In Custom range, select the dates and click **Apply dates**. Choosing dates alone does not change the charts. Only the Apply button commits the selection. Allow at most **90 days**, inclusive, and do not select future dates. An invalid range shows an on-screen message while preserving the last applied data.

**Important:** `Activity trend` and `Mouse activity` follow the selected date range. `Hourly today` and `Busiest hour today` always describe **today**, even when Custom range shows historic days. This deliberate distinction is displayed in the UI text. For longer than 31 days, weekly groups make the graphical chart readable; totals and daily average still come from the full selected period.

### Manual UI acceptance checklist

- [ ] Three presets give the correct date window
- [ ] Custom start/end calendars open
- [ ] Applying one historic day shows that day's activity (or all zeros)
- [ ] Invalid Start > End shows an error; previous results remain
- [ ] Date editing does **not** unexpectedly switch chart tabs
- [ ] Mouse wheel scrolls the page, not the date spinbox or tabs
- [ ] Dark/Light theme both remain readable
- [ ] Keyboard/Mouse Start/Pause still works
- [ ] Existing SQLite data and CSV export are unchanged
- [ ] Quit and relaunch retains stored statistics

Note: switching away and back to Custom range preserves its last successfully applied dates **during that app session**. Persistent date-filter preferences are not part of Step 06.

## 6. Commit and push only after testing

```powershell
git status
git diff --check
git add analytics/custom_range.py dashboard/date_range_controls.py dashboard/analytics_panel.py scripts/apply_step06.py tests/test_milestone03_step06.py docs/STEP06_GUIDE_BN.md
git diff --cached --name-only
git commit -m "feat: add custom analytics date ranges and chart refresh"
git push origin feature/milestone-03-analytics
```

Do not stage `.venv`, `__pycache__`, local SQLite database, screenshots with personal data, or backups. **Do not merge the feature branch into main yet.** Step 07 is final tests/privacy verification and Step 08 is PR merge.

## Troubleshooting

- `ModuleNotFoundError` on a new module: confirm you copied files to the correct folder; run commands from project root.
- `ABORTED`: the currently installed AnalyticsPanel differs from the expected Step 05 UI Polish code. Don't force-edit it; provide the exact abort message.
- `Ran 30 tests ... OK` but GUI error: unit tests do not validate QtCharts rendering; share the full GUI traceback.
- Saved activity seems different: compare filter selection, date boundaries, and local PC date/time. No data is modified by analytics queries.
