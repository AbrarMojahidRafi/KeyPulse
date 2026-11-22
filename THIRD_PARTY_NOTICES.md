# Third-party licensing and distribution reminders

This starter does not change the licenses of its dependencies.

- Python: https://docs.python.org/3/license.html
- PySide6 / Qt for Python: LGPLv3/GPLv3 or commercial licensing options;
  https://doc.qt.io/qtforpython-6/
- pynput: consult the installed package's LICENSE and dependency license files.
- PyInstaller: https://pyinstaller.org/ (build tool licensing terms apply)
- NSIS: https://nsis.sourceforge.io/License (installer builder license)

Before shipping binaries: inspect and include the actual license notices of
bundled components and comply with LGPL requirements where applicable,
including providing applicable notices and permitting replacement of linked
libraries when required. `--onedir` packaging makes bundled Qt dynamic
libraries accessible, but compliance still needs review. License this
project's original source separately as MIT.
