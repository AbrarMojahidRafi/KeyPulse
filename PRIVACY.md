# KeyPulse Privacy Notice (v0.1.0)

KeyPulse is intended for **your own PC** with your knowledge and control.

## Collection

Only when you click **Start tracking**, KeyPulse counts each system-wide key
press, pressed-state mouse click, and scroll callback. This includes activity
in other programs and may include typing in password fields. It intentionally
never reads or saves key identity; it stores no typed text, character sequences,
window titles, mouse coordinates, URLs, screenshots, audio, or clipboard text.

## Storage

In memory, counts are grouped by local **calendar day and hour**. Every 2.5
seconds, the app batches them into a local SQLite database:

`%LOCALAPPDATA%\KeyPulse\keypulse.db` (Windows)

A stored row is a date, hour, and three numeric counts. It is not a log of
individual events. This project includes no server, telemetry, remote access,
auto-start, or auto-update feature. Closing or pausing stops listeners.

## Control

- **Start** begins counting only after an intentional click.
- **Pause** stops the keyboard and mouse listeners.
- **Export CSV** saves user-selected aggregate data to a user-selected path.
- **Delete all saved data** removes the database's aggregate rows after
  confirmation and pauses tracking. SQLite database storage internals may
  retain historical bytes until vacuumed or overwritten; this feature is not
  a forensic secure erase. For high-assurance deletion, consider full-disk
  encryption and operating-system secure-deletion procedures.

## Known limitations

The operating system does not reliably expose whether *another program's*
focused field is a password field to a generic global keyboard listener.
KeyPulse therefore cannot claim to exclude password-related counts; it does
not record the underlying character content. Multiple simultaneously running
KeyPulse instances can double-count events. Users should not install KeyPulse
on other people's computers without informed permission.

## Data retention

The local data remains until the user deletes it. Uninstalling KeyPulse does
not automatically delete the separate database. No external account is needed.
