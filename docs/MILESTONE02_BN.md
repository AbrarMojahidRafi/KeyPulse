# KeyPulse Milestone 02 — Core Tracking & SQLite (বাংলা)

**লক্ষ্য:** নতুন project না বানিয়ে আগের `KeyPulse` starter-এর `core/` এবং `database/` বোঝা, event-to-database pipeline পরীক্ষা করা, এবং GitHub-এ শেখার কাজ নথিভুক্ত করা।

## 0. শুরু করার আগে

VS Code-এ **যে folder-এর মধ্যে `main.py` আছে**, সেটি খোলা থাকতে হবে। Windows PowerShell terminal-এ চালাও:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

প্রথমে আগের tests পাস করা নিশ্চিত করো। Add-on-এর `scripts/`, `tests/` ও `docs/` folder-গুলো একই নামের existing folder-এর সঙ্গে **merge** করবে। `core/`, `database/`, `main.py`, `config.py` পরিবর্তন করার দরকার নেই।

## 1. Source code map

| File                             | কাজ                                                                             |
| -------------------------------- | ------------------------------------------------------------------------------- |
| `main.py`                        | PySide6 application ও window চালু                                               |
| `dashboard/main_window.py`       | Start/Pause, 2.5-second timer, database flush, dashboard refresh                |
| `core/keyboard_tracker.py`       | `pynput.keyboard.Listener` বানায়; key-এর পরিচয় ব্যবহার করে না                   |
| `core/mouse_tracker.py`          | Button press-এ click count এবং scroll callback-এ scroll count                   |
| `core/activity_tracker.py`       | `ActivityMonitor` start/pause; `ActivityAccumulator` thread-safe hourly buckets |
| `database/db_manager.py`         | SQLite schema, insert/upsert, totals/read/delete                                |
| `config.py`                      | Database path: `%LOCALAPPDATA%\KeyPulse\keypulse.db`                            |
| `tests/test_milestone02_core.py` | Fake keyboard/mouse events এবং SQLite test; real hooks চালায় না                 |
| `scripts/milestone02_demo.py`    | Fake counts দিয়ে pipeline দেখায়; temporary database ব্যবহার করে                 |

## 2. Keyboard Tracking বোঝো

`core/keyboard_tracker.py` খুলে এই অংশ দেখো:

```python
def count_without_reading_key(_key: object) -> None:
    on_press()
```

প্রতিবার `pynput` যখন একটি press callback দেয়, KeyPulse **শুধু counter বাড়ায়**। `_key`-এর নাম, text বা password সংরক্ষণ করে না। Keyboard auto-repeat-এর কারণে key ধরে রাখলে count আরও বাড়তে পারে। Listener callback-এর মধ্যে SQLite write বা UI update করা হয় না।

**নিজে চিন্তা করে উত্তর দাও:** `_key` parameter-এর নামের আগে `_` থাকার মানে কী? (ইঙ্গিত: এটি একটি Python naming convention; compiler-level privacy guarantee নয়।)

## 3. Mouse Tracking বোঝো

`core/mouse_tracker.py`-এ দেখো:

```python
def count_click(_x, _y, _button, pressed: bool) -> None:
    if pressed:
        on_click()

def count_scroll(_x, _y, _dx, _dy) -> None:
    on_scroll()
```

`pressed` `True` হলে ১টি click গোনা হয়; `False` (release) হলে নয়। Scroll-এর **callback সংখ্যা** গোনা হয়, pixel বা wheel-distance নয়। Coordinates বা button identity database-এ লেখা হয় না।

## 4. ActivityAccumulator বোঝো

`core/activity_tracker.py`-এ `ActivityAccumulator`-এর `_record()` method-এ:

- `now.date().isoformat()` দিন বোঝায় (যেমন `2026-11-22`)
- `now.hour` ঘণ্টা বোঝায় (`0`–`23`)
- `threading.Lock` একাধিক listener callback একসঙ্গে count পরিবর্তন করলেও counter ঠিক রাখে
- `peek_today()` আজকের এখনো save না হওয়া totals দেখায়
- `drain()` pending counts নিয়ে accumulator খালি করে
- `restore()` database save ব্যর্থ হলে counts ফেরত দেয়

`ActivityMonitor` Start করলে নতুন keyboard/mouse listener তৈরি করে এবং Pause করলে দুটো বন্ধ করে। `pynput` listener থামানোর পরে সেই **একই listener object** restart করা যায় না। তাই আবার Start করলে নতুন listener তৈরি করার ব্যবস্থা রয়েছে।

## 5. SQLite Table ও UPSERT

`database/db_manager.py`-এ `hourly_activity` table-এর columns:

```text
day | hour | key_presses | mouse_clicks | scroll_events
```

একদিনের একই ঘণ্টায় শুধু একটি row থাকে, কারণ `(day, hour)` primary key। `ON CONFLICT ... DO UPDATE` আগের সংখ্যার সঙ্গে নতুন সংখ্যা যোগ করে। Password, typed content, key identity, app names, mouse positions সংরক্ষিত হয় না।

Windows-এ আসল database থাকে `%LOCALAPPDATA%\KeyPulse\keypulse.db`-তে। **সরাসরি delete/edit কোরো না**; app-এর Delete Data control ব্যবহার করবে।

## 6. প্রথম practical demo

VS Code terminal থেকে:

```powershell
.\.venv\Scripts\python.exe -m scripts.milestone02_demo
```

এটি **বাস্তব keyboard/mouse monitor করবে না**। Fixed date/time-এ ৫ key press, ২ click, ৩ scroll event simulate করবে, SQLite-এ save করবে; এরপর আরও ১ key ও ১ click যোগ করবে। প্রত্যাশিত totals:

```text
[2] After first save: {'key_presses': 5, 'mouse_clicks': 2, 'scroll_events': 3}
[3] After second save: {'key_presses': 6, 'mouse_clicks': 3, 'scroll_events': 3}
[4] Hourly SQLite rows: [('2026-11-22', 14, 6, 3, 3)]
```

Database TemporaryDirectory-তে তৈরি হয় এবং শেষ হলে মুছে যায়। তোমার আগের activity history অপরিবর্তিত থাকবে।

## 7. Automated tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

এই add-on ৫টি নতুন test যোগ করে:

1. Keyboard callback identity ব্যবহার করছে না
2. Mouse press, release ও scroll সঠিক count হচ্ছে
3. Events দুই ঘণ্টায় ভাগ হচ্ছে
4. Pause-এ count হয় না এবং Restart-এ নতুন listener তৈরি হয়
5. SQLite UPSERT একই ঘণ্টার aggregate সংখ্যা যোগ করে, private fields রাখে না

**একটি test-ও ফেল করলে সঙ্গে সঙ্গে GitHub-এ push নয়**—আগে error log দেখে সমস্যা ঠিক করবে।

## 8. Real app smoke test (নিজের PC-তে)

```powershell
.\.venv\Scripts\python.exe main.py
```

1. Startup-এ `PAUSED` আছে কি না দেখো।
2. Start Tracking চাপো; test করার জন্য text editor-এ ৫–১০ বার `a` চাপতে পারো।
3. Mouse click ও scroll করো; dashboard count বাড়ছে কি না দেখো।
4. Pause Tracking চাপো; count স্থির থাকা উচিত।
5. App বন্ধ করে আবার চালাও; saved counters থাকা উচিত।
6. Export CSV করলে aggregate columns আছে কি না দেখো।

**Privacy:** ব্যক্তিগত password, chat বা banking input-এর সময় tracking pause রাখবে। Windows-এ system-wide global listener password-field typing-এর _count_ করতে পারে, যদিও কোনো text save করে না।

## 9. GitHub workflow — শেখার পরিবর্তন সংরক্ষণ

সাধারণ path (আগের milestone-এ Git remote ও main branch setup করা আছে ধরে):

```powershell
git status
git switch -c feature/milestone-02-core-tests
git add scripts/milestone02_demo.py tests/test_milestone02_core.py docs/MILESTONE02_BN.md
git commit -m "test: verify KeyPulse core tracking and SQLite pipeline"
git push -u origin feature/milestone-02-core-tests
```

GitHub-এ branch-এর **Compare & pull request** দিয়ে `main`-এ merge করবে। `git switch -c` চালানোর আগে আগের uncommitted changes থাকলে সেগুলো যাচাই করো; কাজ না বুঝে discard/overwrite করবে না।

## 10. Exercise — নিজে পরিবর্তন করো

`milestone02_demo.py`-তে এই তিনটি loop-এর সংখ্যা পাল্টাও:

```python
for _ in range(5):
    counts.record_keypress()
for _ in range(2):
    counts.record_click()
for _ in range(3):
    counts.record_scroll()
```

ধরো তুমি (8, 4, 2) করেছ। দ্বিতীয় save-এ (1, 1, 0) যোগ হয়, তাই final হবে (9, 5, 2)। Script চালিয়ে নিজের হিসাবের সঙ্গে মিলিয়ে দেখো। এরপর tests আবার চালাও।

## Completion definition

- [ ] ৩টি core module এবং database manager-এর কাজ বোঝাতে পারি
- [ ] Test-safe simulated demo চালিয়েছি
- [ ] Automated tests pass করেছে
- [ ] Start / Pause / Save / Restart real app-এ পরীক্ষা করেছি
- [ ] `feature/milestone-02-core-tests` branch GitHub-এ push করেছি
- [ ] Pull request main-এ merge করেছি

পরবর্তী milestone: daily/weekly reports, richer analytics ও visualization।
