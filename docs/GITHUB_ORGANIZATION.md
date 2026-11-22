# Organize a professional GitHub portfolio for KeyPulse

## Account profile

- Use an identifiable professional GitHub username and a concise bio.
- Add public, non-sensitive links (website/portfolio/YouTube) if available.
- Create a profile README by making a public repository named exactly your
  GitHub username, with its `README.md` at the root. Pin KeyPulse.
- Never put private email, access tokens or credentials in source, commits,
  videos, Issues, or the profile README.

## KeyPulse repository settings

- Repository name: `KeyPulse` (case-sensitive display, Git URLs often case-insensitive).
- About: `Privacy-first, open-source desktop activity analytics for Windows.`
- Topics: `python`, `pyside6`, `sqlite`, `windows`, `productivity`, `desktop-app`.
- Source visibility: Public only when personal and secret data is absent.
- Default branch: `main`; protect it when collaboration begins.
- Enable Issues for bug reports and feature requests.
- Use Releases for `KeyPulseSetup.exe` and portable ZIP, not committed binaries.
- Keep a real `LICENSE`, changelog, privacy, security, contribution docs.
- Show a real product screenshot after the Windows GUI is tested.

## Suggested labels

- `bug`, `enhancement`, `documentation`, `good first issue`, `privacy`,
  `release`, `help wanted`, `testing`.

## Suggested Git workflow

```powershell
git status
git switch -c feature/chart-improvements
# Edit and test files
git add .
git commit -m "feat: improve weekly chart"
git push -u origin feature/chart-improvements
```

Open a pull request and merge into `main` after tests pass.

## Suggested release versions

- `v0.1.0` privacy-first counting starter
- `v0.2.0` reliability, tray and single-instance controls
- `v0.3.0` detailed activity analytics
- `v1.0.0` tested public-ready build

Do not call a release production-ready based solely on green unit tests.
