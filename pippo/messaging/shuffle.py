"""Hands out messages in shuffled order."""
from __future__ import annotations

import random


class ShuffleBag:
    """Every message is used once before any repeats, and the same one never comes twice in a row."""

    def __init__(self):
        self._bag: list[int] = []
        self._for: tuple = ()
        self._last = None

    def pick(self, items: list[str]) -> str:
        if tuple(items) != self._for:           # the list was edited in Settings -> start over
            self._for, self._bag, self._last = tuple(items), [], None
        if not self._bag:
            self._bag = list(range(len(items)))
            random.shuffle(self._bag)
            if len(items) > 1 and self._bag[-1] == self._last:
                self._bag[0], self._bag[-1] = self._bag[-1], self._bag[0]
        self._last = self._bag.pop()
        return items[self._last]
