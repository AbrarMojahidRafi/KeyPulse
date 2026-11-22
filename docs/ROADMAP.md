# KeyPulse development roadmap

## v0.1 - Local-first core (included in this starter)

- [x] Explicit opt-in tracking and Pause button
- [x] Event *counts* without key contents or event sequence
- [x] Hourly SQLite aggregation
- [x] Today metrics and 7-day keystroke chart
- [x] Dark/light UI and CSV export
- [x] Delete stored activity counts
- [x] Unit tests and GitHub Actions build configuration
- [ ] Validate GUI and installer on real Windows 10 and Windows 11 hardware

## v0.2 - Reliability

- [ ] Single-instance safeguard
- [ ] System tray icon with visible tracking state
- [ ] Graceful exception reporting without sensitive data
- [ ] Local data retention policy (30/90/365 days; default user choice)
- [ ] Daylight-saving-aware hour bucketing
- [ ] Verified accessibility, high-DPI layout and low-CPU use

## v0.3 - Better analytics

- [ ] Daily/weekly/monthly breakdown
- [ ] Hour-of-day activity timeline
- [ ] Mouse analytics over time
- [ ] CSV/XLSX export and print-friendly summaries
- [ ] Optional keyboard heatmap design review

## v0.4 - Opt-in key frequency (requires privacy review)

- [ ] Separate consent screen, OFF by default, easy disable/erase
- [ ] Aggregate by day only; never store ordered keys or event timestamps
- [ ] Avoid observing/storing key identity in known sensitive contexts
- [ ] Explain clearly that perfect password-field detection is impossible
- [ ] Independent privacy/security review before public release

## v1.0 - Public distribution

- [ ] Windows 10/11 regression tests and uninstall checks
- [ ] Reproducible/pinned release dependencies and dependency audit
- [ ] Source, binaries, licenses and third-party notices together
- [ ] Screenshots, signed SHA-256 checksums and release notes
- [ ] Code signing if sustainable (optional paid enhancement)
- [ ] Tutorial playlist and issue/feature request workflow
