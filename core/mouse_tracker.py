"""Mouse hook that deliberately ignores cursor coordinates and button identity."""
from __future__ import annotations

from typing import Callable


def create_mouse_listener(on_click: Callable[[], None], on_scroll: Callable[[], None]):
    from pynput import mouse

    def count_click(_x: int, _y: int, _button: object, pressed: bool) -> None:
        if pressed:
            on_click()

    def count_scroll(_x: int, _y: int, _dx: int, _dy: int) -> None:
        on_scroll()

    return mouse.Listener(on_click=count_click, on_scroll=count_scroll)
