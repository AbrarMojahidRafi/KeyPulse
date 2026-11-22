# Run on Windows with NSIS installed, from the repository root.
$ErrorActionPreference = 'Stop'
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m PyInstaller --noconfirm --clean --onedir --windowed --name KeyPulse main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
Copy-Item LICENSE, PRIVACY.md, THIRD_PARTY_NOTICES.md -Destination dist\KeyPulse\
$nsis = "${env:ProgramFiles(x86)}\NSIS\makensis.exe"
if (Test-Path $nsis) {
    & $nsis packaging\keypulse.nsi
    if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }
    Write-Host 'Installer: dist\KeyPulseSetup.exe'
} else {
    Write-Host 'NSIS not installed: portable app is under dist\KeyPulse\'
}
