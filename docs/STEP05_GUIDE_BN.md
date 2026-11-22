# KeyPulse Milestone 03 — Step 05 (বাংলা নির্দেশিকা)

## উদ্দেশ্য
- PySide6 QtCharts ব্যবহার করে actual bar charts (axes + legends)
- Today / Last 7 Days / Last 30 Days filter
- Total events, daily average, active days, today's busiest hour cards
- আগের tracking, SQLite database, CSV export ও privacy logic অক্ষত

## 1. প্রথমে Commit/Backup
```powershell
git branch --show-current
git status
python -m unittest discover -s tests -v
```
বর্তমান branch `feature/milestone-03-analytics` হতে হবে। আগের changes commit করা আছে কি না যাচাই করুন।

## 2. Package থেকে Copy করুন
নিচের চারটি code file copy করতে হবে:

- `analytics/overview_data.py`
- `dashboard/analytics_panel.py`
- `tests/test_milestone03_step05.py`
- `scripts/apply_step05.py`

আপনার আগের `database/db_manager.py`, `analytics/statistics.py`, `main.py` **overwrite করবেন না**।

## 3. QtCharts Availability Check
```powershell
python -c "from PySide6.QtCharts import QChartView; print('QtCharts OK')"
```
যদি `ModuleNotFoundError` আসে:
```powershell
python -m pip install "PySide6-Addons<6.13"
```
প্রথমে আপনার `PySide6` package version মিলিয়ে দেখুন; version conflict হলে force upgrade না করে error দেখুন।

## 4. সহজ পদ্ধতি: Safe Auto-Integration (প্রথমে চেষ্টা করুন)

নিচের script আগে বর্তমান `main_window.py`-এর একটি `.bak` backup রাখবে এবং কেবল পুরোনো Step 04 chart block শনাক্ত করতে পারলেই পরিবর্তন করবে।

```powershell
python scripts/apply_step05.py
```

`Step 05 integration applied successfully` দেখালে manual editing লাগবে না।

যদি `ABORTED` দেখায়, কোনো ফাইল পরিবর্তিত হবে না। তখন নিচের manual edits ব্যবহার করুন; অথবা বর্তমান `main_window.py`-এর প্রাসঙ্গিক অংশ দেখে পরিবর্তন ঠিক করুন।

## 4A. Manual fallback: `dashboard/main_window.py`-এ চারটি ছোট Edit

### Edit A: Import
আগের dashboard imports-এর সঙ্গে যুক্ত করুন:
```python
from dashboard.analytics_panel import AnalyticsPanel
```
`WeeklyActivityChart`, `ActivityRangeChart` unused import সরাতে পারেন।

### Edit B: `_build_ui()`
`chart_tabs = QTabWidget()` থেকে `container.addWidget(chart_tabs)` পর্যন্ত পুরোনো chart-tab block **শুধু এই block** Replace করুন:
```python
        self.analytics_panel = AnalyticsPanel(self.db)
        container.addWidget(self.analytics_panel)
```

### Edit C: `_refresh()`
আগের `last_seven_days = ...` থেকে `self.hour_chart.display(...)` পর্যন্ত chart-refresh block Replace করুন:
```python
        self.analytics_panel.refresh()
```

### Edit D: `_apply_theme()`
এই method-এ `self.setStyleSheet(...)` লাইনের ঠিক পরে যুক্ত করুন:
```python
        self.analytics_panel.set_dark_mode(theme == "Dark")
```
`_build_ui()` আগে `self.analytics_panel` তৈরি করছে, তাই theme সেট করার সময় এটি থাকবে।

## 5. Syntax, Backend Tests, Run
```powershell
python -m py_compile analytics/overview_data.py dashboard/analytics_panel.py dashboard/main_window.py
python -m unittest discover -s tests -v
python main.py
```
নতুন **৬টি** backend tests রয়েছে। পুরোনো **১৬টি** থাকলে মোট **২২টি** পাস হওয়ার কথা।
GUI-এর actual appearance Windows PC-তে manually verify করুন।

## 6. Manual QA
- Tracking OFF থাকে যখন window খোলে
- Start/Pause কাজ করে; আজকের ৩টি পুরোনো cards ঠিক থাকে
- Today / Last 7 Days / Last 30 Days filter-এ totals ও trends বদলায়
- Activity trend / Mouse activity / Hourly today tab switch হয়
- Dark/Light theme-এ chart title/legend/axes পড়া যায়
- Window ছোট-বড় করলে chart layout ব্যবহারযোগ্য থাকে
- App Restart করলেও SQLite summary data থাকে
- Export CSV, Delete Saved Data কাজ করে (Delete test-এর আগে optional backup নিন)

**টীকা:** "Busiest hour today" শুধু আজকের ডেটা থেকে আসে; দিন বেছে বদলালেও সেটি আজকের মানই দেখায়। Daily average-এর denominator selected range-এর সব calendar days, শূন্য activity-র দিনসহ।

## 7. GitHub Push
```powershell
git status
git diff --check
git add analytics/overview_data.py dashboard/analytics_panel.py dashboard/main_window.py tests/test_milestone03_step05.py scripts/apply_step05.py docs/STEP05_GUIDE_BN.md
git commit -m "feat: build QtCharts analytics dashboard with date filters"
git push origin feature/milestone-03-analytics
```
পরে documentation-ও commit করুন যদি `docs/STEP05_GUIDE_BN.md` project-এ copy করে থাকেন। Milestone 03-এর শেষ Step 08-এর আগে `main`-এ Merge করবেন না।

## Rollback (প্রয়োজন হলে)
আলাদা ফাইল হিসেবে backup তৈরি হয়েছে, `main_window.py` পুরোনো অবস্থায় ফেরাতে:
```powershell
Copy-Item .\dashboard\main_window.py.before_step05.bak .\dashboard\main_window.py -Force
```
এই `.bak` ফাইল GitHub-এ commit করবেন না।
