# Architecture

```
USER: Start/Pause
        |
        v
PySide6 GUI (main/UI thread) <------ QTimer (2.5s refresh/flush)
        |                                    |
        v                                    v
ActivityMonitor --------------------> ActivityAccumulator
    |                                    ^ thread-safe lock
    |                                    |
    +--> keyboard hook callback -----> increment counter only
    +--> mouse click/scroll callback -> increment counter only
                                             |
                                       drain hourly buckets
                                             |
                                             v
                                   SQLite (hourly_activity)
                                             |
                                  chart cards and CSV export
```

## Safety and scope

The listener callbacks run in their own background threads, but they never
send Qt signals or write to SQLite directly. They merely increment integer
counters under a lock. The main Qt thread drains counters periodically and
writes a single batched SQLite transaction. There are no per-event entries.

## Database schema

Primary key `(day TEXT, hour INTEGER)` with counts `key_presses`,
`mouse_clicks`, `scroll_events`. Calendar day/time is local to the user's PC.
Time zone travel and daylight-saving ambiguity are future considerations;
local wall-clock hours can repeat during DST changes.

## Future extension points

- `core/`: explicitly approved collection categories, with opt-in settings.
- `database/`: forward-only schema migration plus retention controls.
- `analytics/`: weekly and monthly totals, anonymized aggregate reports.
- `dashboard/`: live charts, accessible theme and keyboard heatmap.
- `packaging/`: icons, signature and update strategy after validation.

## Known MVP gaps

- No inter-process lock; opening multiple instances can double-count.
- Hourly local time buckets are not DST-disambiguated.
- The packaged app and hooks must be tested on Windows 10 and Windows 11.
- No autonomous background service or tray menu.
