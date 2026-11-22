# Windows installer and publishing guide

## Prerequisites

Windows 10/11 64-bit, Python 3.12, Git, VS Code, and optional NSIS.
NSIS download: https://nsis.sourceforge.io/

PyInstaller is not a cross-compiler. A native Windows `.exe` must be built on
Windows, either locally or using the provided `windows-2022` GitHub Actions job.

## Build locally

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name KeyPulse main.py
```

The folder `dist\KeyPulse` is a portable install. Run `dist\KeyPulse\KeyPulse.exe`.
If NSIS is installed, build an installer from the same repository root:

```powershell
& "${env:ProgramFiles(x86)}\NSIS\makensis.exe" packaging\keypulse.nsi
```

This writes `dist\KeyPulseSetup.exe`. It is a **per-user** installation, so no
admin rights are requested. Uninstall does not erase usage history stored in
`%LOCALAPPDATA%\KeyPulse`.

## Build automatically on GitHub

Push an annotated or lightweight `v0.1.0` tag. The release workflow:

1. Sets up Python 3.12 on a Windows runner.
2. Installs dependencies, runs unit tests and bundles the app with PyInstaller.
3. Compresses a portable ZIP and packages an NSIS installer.
4. Uploads both files to GitHub Releases.

Ensure release files appear and test them before sharing the download URL.
`windows-2022` is a Windows Server build environment, not a substitute for
Windows 10/11 end-user testing.

## Publisher trust

Unsigned executables may trigger Microsoft Defender SmartScreen or other
anti-virus warnings, particularly when newly released. Do not tell users to
disable security software. Provide source, transparent changelog, reproducible
build steps, hash checksums, and optional commercial code-signing later.

## Suggested manual release checklist

- [ ] Run tests on Windows 10 and Windows 11 (x64)
- [ ] Confirm event counts update only after Start
- [ ] Confirm Pause and exit stop listeners
- [ ] Check CSV totals against observed counts
- [ ] Confirm delete and uninstall behavior
- [ ] Test keyboard and mouse hooks in typical desktop applications
- [ ] Verify installer and portable ZIP on a clean test account
- [ ] Review license notices and release artifacts
- [ ] Only then mark the release ready for the public
