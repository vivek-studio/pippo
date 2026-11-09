"""The small interfaces the workflows share (so each part can be swapped or tested on its own)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from ..core.radio import RadioEntry


@dataclass
class ListContext:
    """Everything a list strategy needs for today's run."""
    today: date
    radio: list[RadioEntry]
    last_list_id: str
    prev_dates: dict | None      # project (lowercase) -> due date in the previous list; None = unreadable


@dataclass
class ListOutcome:
    """What a list strategy reports back."""
    list_id: str
    sort_missing: bool = False                       # the list has no "Sort Order" column
    dupes: list[str] = field(default_factory=list)   # projects found on 2+ rows


class ListStrategy(Protocol):
    """One way of getting today's list ready. Add a new strategy without touching the workflow."""
    is_new: bool

    def run(self, ctx: ListContext) -> ListOutcome | None: ...


class Restructurer(Protocol):
    def restructure(self, list_id: str, radio: list[RadioEntry], new_list: bool) -> None: ...
