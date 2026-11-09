"""The list rules: stars, status and sort order of a row, decided from the Daily Radio."""
from __future__ import annotations

from .columns import FAR_DATE, STATUS_HANDED_OFF, STATUS_NOT_STARTED
from .radio import SECTION_DUE_TODAY, SECTION_KICKING_OFF, SECTION_PIPELINE, RadioEntry

# Daily Radio sections whose projects get status "Not Started".
# Every other project in the list (feedback awaited, not in today's radio, ...) becomes "Handed Off".
NOT_STARTED_SECTIONS = {SECTION_DUE_TODAY, SECTION_KICKING_OFF, SECTION_PIPELINE}


def stars_for(entry: RadioEntry | None) -> int:
    """Due today + AM HO = 2 stars, due today only = 1 star, otherwise none."""
    if not entry or not entry.due_today:
        return 0
    return 2 if entry.am_ho else 1


def status_for(entry: RadioEntry | None) -> str:
    return STATUS_NOT_STARTED if entry and entry.section in NOT_STARTED_SECTIONS else STATUS_HANDED_OFF


def sort_ranks(active: list[RadioEntry]) -> dict[int, int]:
    """
    Order of the NOT-handed-off rows (Handed Off rows always get HANDED_OFF_SORT instead):
      1) due today + AM HO   2) due today   3) everything else by date (no date = last)
    Ties keep the Daily Radio order. Returns {id(entry): 1, 2, 3, ...}.
    """
    def key(e: RadioEntry):
        g = 0 if (e.due_today and e.am_ho) else 1 if e.due_today else 2
        return (g, (e.date or FAR_DATE) if g == 2 else "", e.idx)

    return {id(e): n for n, e in enumerate(sorted(active, key=key), start=1)}
