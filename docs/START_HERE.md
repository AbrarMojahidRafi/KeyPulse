# Start here - First successful KeyPulse run

1. On Windows, install Python 3.12 (64-bit), Visual Studio Code and Git.
2. Extract the ZIP to `Documents\KeyPulse`.
3. Open the folder in Visual Studio Code.
4. Use Terminal > New Terminal and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

5. Confirm the dashboard opens **PAUSED** by default.
6. Click **Start tracking**, press a few keys, and test the mouse.
7. Click **Pause tracking** and verify numbers stop increasing.
8. Click **Export CSV**, inspect the summarized data, and test **Delete all**.
9. Run tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

10. Use the README GitHub push guide after you confirm your project works.

Common issues:

- `py` not found: reinstall Python using the official Windows installer and
  enable its launcher/PATH options, then reopen the terminal.
- `No module named PySide6`: check that you installed requirements into the
  same `.venv` Python used to start the program.
- PowerShell activation restricted: the commands above do not require
  `Activate.ps1`, so no execution-policy changes are needed.
- Installer warning: don't disable anti-virus. Check source/build transparency,
  and test the downloaded binary before publishing it to others.
