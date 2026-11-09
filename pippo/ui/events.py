"""A tiny publish/subscribe bus, so pages never need to know about each other."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable

# Topics
LOG = "log"                      # (message, level)
STATUS = "status"                # ("online" | "starting" | "offline")
STATE = "state"                  # engine changed the config (list IDs ...)
CALENDAR_CHANGED = "calendar"    # holidays / working weekends were edited
SETTINGS_SAVED = "settings"      # the Settings page was saved
TICK = "tick"                    # once a minute (keeps "today" fresh)


class EventBus:
    def __init__(self):
        self._subs: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Callable) -> None:
        self._subs[topic].append(fn)

    def publish(self, topic: str, *args) -> None:
        for fn in list(self._subs[topic]):
            fn(*args)
