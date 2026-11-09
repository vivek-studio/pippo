"""Row logic: who an existing row is, which radio entry it matches, and every cell Pippo sets on it."""
from __future__ import annotations

from dataclasses import dataclass, field

from .columns import (COL_ASSETS, COL_DATE, COL_NAME, COL_ROUND, COL_SORT, COL_STARS, COL_STATUS,
                      FAR_DATE, HANDED_OFF_SORT, STATUS_HANDED_OFF)
from .radio import RadioEntry
from .rules import stars_for, status_for
from .schema import choice_value, flatten_rich_text, rich_text_value
from .types import Log


# ---------------------------------------------------------------- reading an existing row
@dataclass
class RowIdentity:
    """Project name / round / due date / has-stars of an existing row."""
    id: str | None
    name: str = ""
    round: str = ""
    date: str | None = None
    stars: bool = False


def read_row_identity(item: dict, by_id: dict) -> RowIdentity:
    info = RowIdentity(id=item.get("id"))
    for f in item.get("fields", []):
        col = by_id.get(f.get("column_id") or f.get("key"), {})
        cname = col.get("name")
        if cname == COL_NAME:
            info.name = (flatten_rich_text(f.get("rich_text")) if f.get("rich_text")
                         else (f.get("text") or f.get("value") or ""))
        elif cname == COL_ROUND and f.get("select"):
            choices = (col.get("options") or {}).get("choices", [])
            label = next((c["label"] for c in choices if c["value"] == f["select"][0]), None)
            info.round = label or f.get("text") or ""
        elif cname == COL_DATE and f.get("date"):
            info.date = f["date"][0]
        elif cname == COL_STARS and f.get("rating"):
            info.stars = True
    return info


# ---------------------------------------------------------------- cells straight from the radio
def radio_fields(item: RadioEntry, cols: dict, with_round: bool = True, with_date: bool = True,
                 current_name: str | None = None) -> list[dict]:
    """Cells straight from one Daily Radio entry. An empty radio value never produces a cell.
    current_name: the name already in the row - when equal, the name cell is skipped (keeps its formatting)."""
    fields = []
    c = cols.get(COL_NAME)
    if c and item.name and item.name != current_name:
        fields.append({"column_id": c["id"], "rich_text": rich_text_value(item.name)})

    c = cols.get(COL_ROUND)
    v = choice_value(c, item.round) if with_round and c and item.round else None
    if v:
        fields.append({"column_id": c["id"], "select": [v]})

    c = cols.get(COL_DATE)
    if with_date and c and item.date:
        fields.append({"column_id": c["id"], "date": [item.date]})

    c = cols.get(COL_ASSETS)
    if c and item.assets is not None:
        fields.append({"column_id": c["id"], "number": [item.assets]})
    return fields


# ---------------------------------------------------------------- every cell of one row
class RowCellPlanner:
    """
    Every cell Pippo sets on a row, from today's radio. Used for NEW rows (row=None) and for
    EXISTING rows (row = its identity), so the rules live in one place:
      project name (existing rows: only if it changed), round, due date, assets,
      Status, Due Today stars, Sort Order.
    entry=None means the project isn't in today's radio -> Handed Off.
    Handed Off rows have no round (an existing round is emptied) and sort order 999.
    Their due date never comes from the radio: it is the one the project had in the PREVIOUS list
    (prev_dates), or empty if it wasn't there. If the previous list couldn't be read (prev_dates
    is None) a Handed Off row's date isn't touched - a new row simply has none.
    """

    def __init__(self, log: Log):
        self.log = log

    def plan(self, entry: RadioEntry | None, cols: dict, ranks: dict, row: RowIdentity | None = None,
             prev_dates: dict | None = None) -> list[dict]:
        status = status_for(entry)
        handed = status == STATUS_HANDED_OFF
        cells = radio_fields(entry, cols, with_round=not handed, with_date=not handed,
                             current_name=row.name if row else None) if entry else []
        cells += self._handed_off_date(entry, cols, handed, row, prev_dates)
        cells += self._round(entry, cols, handed, row)
        cells += self._status(cols, status)
        cells += self._stars(entry, cols, row)
        cells += self._sort(entry, cols, ranks, handed)
        return cells

    @staticmethod
    def _handed_off_date(entry, cols, handed, row, prev_dates) -> list[dict]:
        c = cols.get(COL_DATE)
        if not (c and handed and prev_dates is not None):
            return []
        d = prev_dates.get((entry.name if entry else row.name).strip().lower())
        current = row.date if row else None
        if d and d != current:
            return [{"column_id": c["id"], "date": [d]}]
        if not d and current:
            return [{"column_id": c["id"], "date": []}]
        return []

    def _round(self, entry, cols, handed, row) -> list[dict]:
        c = cols.get(COL_ROUND)
        if c and handed and row and row.round:
            return [{"column_id": c["id"], "select": []}]
        if c and entry and not handed and entry.round and not choice_value(c, entry.round):
            self.log(f"Round '{entry.round}' isn't an option in the list ({entry.name}).", "warn")
        return []

    def _status(self, cols, status) -> list[dict]:
        c = cols.get(COL_STATUS)
        if not c:
            return []
        v = choice_value(c, status)
        if v:
            return [{"column_id": c["id"], "select": [v]}]
        self.log(f"Status '{status}' isn't an option in the list.", "warn")
        return []

    @staticmethod
    def _stars(entry, cols, row) -> list[dict]:
        c = cols.get(COL_STARS)
        if not c:
            return []
        n = stars_for(entry)
        if n:
            return [{"column_id": c["id"], "rating": [n]}]
        if row and row.stars:
            return [{"column_id": c["id"], "rating": []}]
        return []

    @staticmethod
    def _sort(entry, cols, ranks, handed) -> list[dict]:
        c = cols.get(COL_SORT)
        if not c:
            return []
        rank = HANDED_OFF_SORT if handed else ranks.get(id(entry), HANDED_OFF_SORT)
        return [{"column_id": c["id"], "number": [rank]}]


# ---------------------------------------------------------------- which row is which project
@dataclass
class RowMatch:
    groups: dict[str, list[RowIdentity]]
    target: dict[str, RadioEntry]                  # row id -> the radio entry that updates it
    dupes: list[str] = field(default_factory=list)  # project names found on 2+ rows


def match_rows_to_radio(rows: list[RowIdentity], picked: dict[str, RadioEntry], log: Log) -> RowMatch:
    """
    * rows are matched to radio entries by PROJECT NAME only;
    * a project on 2+ rows: the row with the same round wins, then the one due EARLIER;
    * a project on 2+ rows is reported (it should never happen).
    """
    groups: dict[str, list[RowIdentity]] = {}
    for r in rows:
        groups.setdefault(r.name.strip().lower(), []).append(r)

    match = RowMatch(groups=groups, target={})
    for nm, g in groups.items():
        if len(g) > 1 and nm not in picked:
            match.dupes.append(g[0].name)
            log(f"'{g[0].name}' is on {len(g)} rows of the list (not in today's radio).", "warn")

    for nm, entry in picked.items():
        cands = groups.get(nm) or []
        if not cands:
            continue
        same_round = [c for c in cands if entry.round and c.round.lower() == entry.round.lower()]
        pool = same_round or cands
        best = min(pool, key=lambda c: c.date or FAR_DATE)
        if len(cands) > 1:
            match.dupes.append(entry.name)
            log(f"'{entry.name}' is on {len(cands)} rows; updating the one with "
                f"round '{best.round or '-'}' / date '{best.date or '-'}'.", "warn")
        match.target[best.id] = entry
    return match
