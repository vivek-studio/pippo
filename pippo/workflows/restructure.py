"""Restructuring hook (re-ordering rows, changing values, modifying columns)."""
from __future__ import annotations

from ..core.radio import RadioEntry
from ..core.types import Log


class NoopRestructurer:
    """
    PLACEHOLDER - restructuring goes here. Called on BOTH paths: first working
    day (new list) and every other day (existing list).

    Write another class with the same `restructure` method and hand it to the
    GoodMorningWorkflow to add rules - nothing else has to change.
    """

    def __init__(self, log: Log):
        self.log = log

    def restructure(self, list_id, radio: list[RadioEntry], new_list: bool) -> None:
        self.log("Restructuring: nothing to do yet (rules pending).", "info")
