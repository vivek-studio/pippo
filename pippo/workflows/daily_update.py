"""Any other working day: the month's list is kept and updated from today's Daily Radio."""
from __future__ import annotations

import time

from slack_sdk.errors import SlackApiError

from ..core.columns import (CLEAR_COLUMNS, COL_SORT, COL_STATUS, STATUS_HANDED_OFF,
                            STATUS_NOT_STARTED)
from ..core.radio import pick_per_project
from ..core.rows import RowCellPlanner, match_rows_to_radio, read_row_identity
from ..core.rules import sort_ranks, status_for
from ..core.text import date_text, describe_error
from ..core.types import Log
from ..infra.slack_gateway import SlackGateway
from .contracts import ListContext, ListOutcome
from .row_writer import ROW_PAUSE, RowWriter


class DailyUpdateStrategy:
    """
    NORMAL WORKING DAY - same list, updated from today's Daily Radio:
      * match rows to radio entries by PROJECT NAME only;
      * same project twice in the radio -> the entry due EARLIER wins;
      * matched row: name, round, due date, asset count taken from today's radio
        (an empty radio value never wipes the old one - no round / no due-on date /
        no asset count -> the old cell is left as it is);
      * Status: Not Started if the project is in today's radio under DUE TODAY /
        PROJECTS KICKING OFF / IN PIPELINE, otherwise Handed Off
        (rows missing from the radio stay in the list as Handed Off);
      * Handed Off rows get their Round emptied and their due date taken from the PREVIOUS list
        (empty if the project wasn't there; left untouched if that list couldn't be read);
      * a project on 2+ list rows is flagged in a Slack reply (never expected to happen);
      * Assignee, Currently Working, Design Lead, Copy Leads, Functional Lead cleared on every row;
      * Due Today stars (2 = due today + AM HO, 1 = due today, else empty) and the helper
        "Sort Order" number are set from today's radio (Handed Off rows = 999);
      * radio projects that aren't in the list yet are added as new rows.
    """
    is_new = False

    def __init__(self, gateway: SlackGateway, planner: RowCellPlanner, rows: RowWriter, log: Log):
        self.gateway = gateway
        self.planner = planner
        self.rows = rows
        self.log = log

    def run(self, ctx: ListContext) -> ListOutcome | None:
        list_id = ctx.last_list_id
        self.log(f"Today ({date_text(ctx.today)}) is NOT the first working day of the month, so: "
                 f"no new list. Using list {list_id}. "
                 "(To test the new-list path, send: good morning force new)", "info")
        try:
            items = self.gateway.fetch_items(list_id)
        except SlackApiError as e:
            self.log(f"Couldn't read list {list_id}:\n{describe_error(e)}", "err")
            return None
        by_id = self.gateway.list_schema(list_id, items)
        if not by_id:
            self.log("Couldn't read the list's columns (is the list empty?).", "err")
            return None
        cols = {c["name"]: c for c in by_id.values()}
        if not cols.get(COL_STATUS):
            self.log("No 'Status' column found in the list - statuses cannot be set.", "err")

        picked = pick_per_project(ctx.radio)                       # one entry per project (earlier date wins)
        rows = [read_row_identity(i, by_id) for i in items]
        raw = {i.get("id"): i for i in items}
        match = match_rows_to_radio(rows, picked, self.log)

        new_entries = [e for nm, e in picked.items() if nm not in match.groups]
        ranks = sort_ranks([e for e in list(match.target.values()) + new_entries
                            if status_for(e) != STATUS_HANDED_OFF])

        updated = handed = started = cleared = failed = 0
        for r in rows:
            entry = match.target.get(r.id)
            status = status_for(entry)
            cells = self.planner.plan(entry, cols, ranks, r, ctx.prev_dates)
            # clear the people columns (only the ones that actually hold someone)
            for f in raw[r.id].get("fields", []):
                cn = (by_id.get(f.get("column_id") or f.get("key")) or {}).get("name")
                if cn in CLEAR_COLUMNS and f.get("user"):
                    cells.append({"column_id": f.get("column_id") or f.get("key"), "user": []})
                    cleared += 1
            try:
                self.gateway.update_cells(list_id, r.id, cells)
                updated += 1
                started += status == STATUS_NOT_STARTED
                handed += status == STATUS_HANDED_OFF
                time.sleep(ROW_PAUSE)
            except Exception as e:  # noqa
                failed += 1
                self.log(f"Row update failed ({r.name}): {e}", "err")

        # radio projects that aren't in the list yet -> new rows (same builder as a new list)
        added = self.rows.create_rows(list_id, new_entries, cols, ranks, ctx.prev_dates)
        self.log(f"{updated} row(s) updated ({started} Not Started, {handed} Handed Off, "
                 f"{cleared} people cell(s) cleared, {failed} failed), {added} new row(s) added.", "ok")
        return ListOutcome(list_id, sort_missing=COL_SORT not in cols, dupes=list(match.dupes))
