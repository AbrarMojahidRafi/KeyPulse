"""Application settings. There is deliberately no network configuration."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "KeyPulse"
APP_VERSION = "0.1.0"


def data_directory() -> Path:
    """Return a per-user directory outside the Git repository/install folder."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / ".keypulse"


def database_path() -> Path:
    return data_directory() / "keypulse.db"
