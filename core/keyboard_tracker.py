"""Keyboard hook that deliberately ignores which key was pressed."""
from __future__ import annotations

from typing import Callable


def create_keyboard_listener(on_press: Callable[[], None]):
    from pynput import keyboard

    def count_without_reading_key(_key: object) -> None:
        # Do not inspect, stringify, log, or persist _key.
        on_press()

    return keyboard.Listener(on_press=count_without_reading_key)
