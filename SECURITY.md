# Security Policy

KeyPulse v0.1 is an experimental starter release; production security support
is not guaranteed. If you find a vulnerability, do not publish sensitive
technical exploit details or user data in public Issues. Use the repository's
GitHub private vulnerability reporting feature if enabled, or contact the
maintainer through a non-public channel configured by the repository owner.

Basic principles:

- No internet communication or remote data upload.
- Never persist per-key events or human-readable content.
- No hidden tracking or silent startup.
- Test every packaged Windows build with Windows Defender and a clean VM.
- Audit dependencies and build logs before distribution.
