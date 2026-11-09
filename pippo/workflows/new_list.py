"""First working day of the month: a brand-new list, built from scratch."""
from __future__ import annotations

from ..core.columns import COL_SORT, STATUS_HANDED_OFF
from ..core.radio import pick_per_project
from ..core.rules import sort_ranks, status_for
from ..core.schema import build_schema_from_template
from ..core.text import date_text, fmt
from ..core.types import Log
from ..infra.resources import load_template
from ..infra.slack_gateway import SlackGateway
from .contracts import ListContext, ListOutcome
from .row_writer import RowWriter


class NewListStrategy:
    """Brand-new list built from scratch (template columns, no rows), filled from the radio.
    Only radio projects end up in it (the template has no rows). Never needs an old list ID."""
    is_new = True

    def __init__(self, cfg: dict, gateway: SlackGateway, rows: RowWriter, log: Log,
                 template_loader=load_template):
        self.cfg = cfg
        self.gateway = gateway
        self.rows = rows
        self.log = log
        self.template_loader = template_loader

    def title_for(self, ctx: ListContext) -> str:
        today = ctx.today
        return fmt(self.cfg["list_title_format"], date=date_text(today), client=self.cfg["client_name"],
                   month=today.strftime("%B"), year=today.year)

    def run(self, ctx: ListContext) -> ListOutcome | None:
        title = self.title_for(ctx)
        self.log(f"First working day → creating new list '{title}'.", "info")
        schema = build_schema_from_template(self.template_loader(self.cfg))
        resp = self.gateway.create_list(title, schema)
        if not resp:
            return None
        list_id = resp["list_id"]
        cols = {c["name"]: c for c in (resp.get("list_metadata") or {}).get("schema") or []}
        self.log(f"New list {list_id}; columns: {list(cols)}")
        entries = list(pick_per_project(ctx.radio).values())
        ranks = sort_ranks([e for e in entries if status_for(e) != STATUS_HANDED_OFF])
        added = self.rows.create_rows(list_id, entries, cols, ranks, ctx.prev_dates)
        self.log(f"{added} row(s) added from the Daily Radio.", "ok")
        return ListOutcome(list_id, sort_missing=COL_SORT not in cols)
