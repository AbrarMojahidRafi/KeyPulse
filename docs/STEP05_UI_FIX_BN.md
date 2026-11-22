# KeyPulse Step 05 UI Polish

This is a small patch for the Step 05 AnalyticsPanel. It does not replace
main_window.py, the SQLite database, or the keyboard/mouse trackers.

## What it fixes

- Three chart tabs fill the whole row (no wide empty strip on the right).
- Mouse-wheel movement over tabs no longer changes the selected tab.
- Mouse-wheel movement over the chart does not trigger nested scrolling.
- Date range selection only changes when the user explicitly selects an item.
- The chart has a fixed, compact height and hides internal scrollbars.
- Dark and Light chart colors, axes, title, and legend are more consistent.
- The four summary cards occupy one row on wide windows, two rows on smaller windows.

The main KeyPulse page remains vertically scrollable. The tabs still work
with mouse clicks and normal keyboard accessibility.

## Step by step (VS Code PowerShell)

1. Close the running KeyPulse app.
2. Check branch: git branch --show-current
   Expected: feature/milestone-03-analytics
3. Copy scripts/polish_step05_ui.py into your existing KeyPulse/scripts folder.
4. Copy docs/STEP05_UI_FIX_BN.md into the existing KeyPulse/docs folder.
5. Run:

   python scripts/polish_step05_ui.py

   Expected: SUCCESS: Step 05 UI polish applied ...
   This creates a backup in dashboard/ with a .bak extension.
   Re-running the script prints "Already polished" and makes no changes.
   If ABORTED appears, do not overwrite the code manually. Share the error.

6. Run syntax check:

   python -m py_compile dashboard/analytics_panel.py

7. Run all tests:

   python -m unittest discover -s tests -v

   If you installed the Step 05 add-on, 22 tests should pass.
   The patch was syntax-checked but not run on a real Windows GUI here.

8. Run the app:

   python main.py

9. Check:

   - Hover over Activity trend and use the wheel: selected tab stays unchanged.
   - Click Mouse activity and Hourly today: they still switch properly.
   - Hover over any chart and wheel: the page scrolls, not the chart itself.
   - Tabs now use the full width and have clearer background colors.
   - Wide screen: four cards in a row; narrow screen: two by two.
   - Repeat in Light theme and with Today/7 Days/30 Days.

## GitHub

Run only after GUI testing succeeds:

   git status
   git diff --check
   git add dashboard/analytics_panel.py scripts/polish_step05_ui.py docs/STEP05_UI_FIX_BN.md
   git diff --cached --name-only
   git commit -m "style: polish analytics tabs and prevent accidental wheel switching"
   git push origin feature/milestone-03-analytics

If your original Step 05 files are not committed yet, stage and commit those
Step 05 files too. Do not use git add . blindly: the backup .bak should never
be committed. You can add *.bak to .gitignore to prevent mistakes.

## Rollback

If the changes are not satisfactory, close KeyPulse and restore the saved
backup from dashboard/analytics_panel.py.before_ui_polish_YYYYMMDD_HHMMSS.bak
as dashboard/analytics_panel.py. Then rerun your tests.
