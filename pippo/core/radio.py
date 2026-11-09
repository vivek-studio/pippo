"""Reading the Daily Radio ("Project Status") post."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from .columns import FAR_DATE

SECTION_DUE_TODAY = "DUE TODAY"
SECTION_KICKING_OFF = "PROJECTS KICKING OFF"
SECTION_PIPELINE = "IN PIPELINE"
SECTION_FEEDBACK = "FEEDBACK AWAITED"
SECTION_HEADERS = {SECTION_DUE_TODAY, SECTION_KICKING_OFF, SECTION_PIPELINE, SECTION_FEEDBACK}

ROUND_RE = re.compile(r"\b(Additional Revisions|SKU Swaps|RD\d[a-z]?|KO)\b", re.IGNORECASE)
DUE_RE = re.compile(r"due\s+(?:on|by)\s+(\d{1,2})/(\d{1,2})", re.IGNORECASE)
ASSETS_RE = re.compile(r"\((\d+)\s+assets?\)", re.IGNORECASE)
AMHO_RE = re.compile(r"\(\s*AM\s+HO\s*\)", re.IGNORECASE)
HEADER_DATE_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})")
LINE_RE = re.compile(r"^\d+[.)]\s*(.+)$")
SKIP_NAMES = {"na", "n/a", "none", "-"}


@dataclass
class RadioEntry:
    """One numbered line of the Daily Radio."""
    idx: int                  # position in the radio (ties keep radio order)
    name: str
    round: str | None
    date: str | None          # YYYY-MM-DD
    assets: int | None
    am_ho: bool
    due_today: bool
    section: str | None


def parse_header_date(text: str) -> date | None:
    m = HEADER_DATE_RE.search(text or "")
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %B %Y").date()
    except ValueError:
        return None


class RadioParser:
    """
    Date rules:
      DUE TODAY section      -> the post's header date
      FEEDBACK AWAITED       -> ONLY the "due on" date (never the "awaited by" date); None if absent
      everything else        -> the "due on" date after the round
    """

    def parse(self, text: str) -> list[RadioEntry]:
        header = parse_header_date(text)
        year, header_iso = (header.year, header.isoformat()) if header else (datetime.now().year, None)

        items: list[RadioEntry] = []
        section = None
        for raw in text.splitlines():
            line = raw.strip().replace("*", "")
            if not line:
                continue
            if line.upper() in SECTION_HEADERS:
                section = line.upper()
                continue
            m = LINE_RE.match(line)
            if not m or not section:
                continue
            entry = self._entry(len(items), m.group(1).strip(), section, year, header_iso)
            if entry:
                items.append(entry)
        return items

    def _entry(self, idx: int, body: str, section: str, year: int, header_iso: str | None):
        name, _, rest = body.partition(" - ")
        name = name.strip().rstrip(".")
        if name.lower() in SKIP_NAMES:
            return None
        round_label, date_iso = self._round_and_date(rest, section, year)
        due_today = section == SECTION_DUE_TODAY
        if due_today:
            date_iso = header_iso or date_iso
        am = ASSETS_RE.search(body)
        return RadioEntry(idx=idx, name=name, round=round_label, date=date_iso,
                          assets=int(am.group(1)) if am else None,
                          am_ho=bool(AMHO_RE.search(body)),
                          due_today=due_today, section=section)

    @staticmethod
    def _to_iso(year: int, mm: str, dd: str) -> str | None:
        try:
            return datetime(year, int(mm), int(dd)).strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _round_and_date(self, rest: str, section: str, year: int):
        round_label, date_iso = None, None
        rm = ROUND_RE.search(rest)
        if not rm and section == SECTION_FEEDBACK:
            # Feedback lines carry no round; still read ONLY the "due on/by" date ("awaited by" is never used)
            dm = DUE_RE.search(rest)
            if dm:
                date_iso = self._to_iso(year, dm.group(1), dm.group(2))
        if rm:
            round_label = rm.group(1)
            if round_label.upper() == "KO":
                round_label = "KO"
            elif round_label.upper().startswith("RD"):
                round_label = "RD" + rm.group(1)[2:]
            dm = DUE_RE.search(rest, rm.end())
            if dm:
                date_iso = self._to_iso(year, dm.group(1), dm.group(2))
        return round_label, date_iso


def parse_status_message(text: str) -> list[RadioEntry]:
    return RadioParser().parse(text)


def pick_per_project(radio: list[RadioEntry]) -> dict[str, RadioEntry]:
    """One radio entry per project name (case-insensitive). Earliest due date wins; no date = last.
    Used by BOTH the new-list path and the normal-day path, so a project is never listed twice."""
    picked: dict[str, RadioEntry] = {}
    for it in radio:
        nm = (it.name or "").strip().lower()
        cur = picked.get(nm)
        if cur is None or (it.date or FAR_DATE) < (cur.date or FAR_DATE):
            picked[nm] = it
    return picked
