"""The little heads-up messages Pippo posts when something about the list needs a human."""
from __future__ import annotations

from ..core.columns import COL_SORT
from .previous_list import NOTE_NONE


def sort_missing_notice() -> str:
    return (f"⚠️ I can't find a number column called *{COL_SORT}* in the list, so I couldn't sort it. "
            "Please add it (type: Number) and save a view sorted by it, ascending. Stars were still set. 🐾")


def previous_list_notice(note: str, new_list: bool) -> str:
    what_now = ("I still made the new list, but every *Handed Off* project has an empty due date."
                if new_list else
                "I still updated today's list, but I left the due dates of *Handed Off* projects exactly as they were.")
    if note == NOTE_NONE:
        why = ("🔍 I went looking for last month's list to copy the due dates of Handed Off projects, "
               "but I don't have one on record. 🙈")
        fix = "To fix it, put last month's list ID in *Previous list ID* in my Settings."
    else:
        why = ("🔒 I tried to open last month's list to copy the due dates of Handed Off projects, "
               "but Slack wouldn't let me read it. 🙈")
        fix = ("Please check that the list still exists and that I have access to it, "
               "or update *Previous list ID* in my Settings.")
    return f"🐾 Tiny hiccup! {why} {what_now} {fix}"


def duplicates_notice(dupes: list[str]) -> str:
    return ("⚠️ Heads-up: these projects appear on more than one row in the list, which should never "
            "happen: " + ", ".join(f"*{d}*" for d in dupes) + ". Please check and delete the extra row(s). 🐾")
