# Contributing to KeyPulse

Thank you for helping. Keep privacy as a non-negotiable design constraint.

1. Open an Issue describing the bug or feature. Do not post private usage
   history, credentials, or screenshots of sensitive information.
2. Create a focused branch from `main`, e.g. `feature/weekly-summary`.
3. Make changes and run `python -m unittest discover -s tests -v`.
4. Include tests for collection, storage and export changes.
5. Open a Pull Request explaining the change and its privacy implications.

Commit format examples:

- `feat: add weekly aggregate overview`
- `fix: prevent duplicate hourly writes`
- `docs: clarify installation requirements`
- `test: cover paused-state behavior`

Do not introduce hidden background collection, remote analytics, raw keyboard
logging, silent persistence, or uncontrolled auto-start.
