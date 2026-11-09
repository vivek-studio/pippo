"""Writing rows to a list (shared by the new-list and the normal-day strategies)."""
from __future__ import annotations

import time

from ..core.radio import RadioEntry
from ..core.rows import RowCellPlanner
from ..core.types import Log
from ..infra.slack_gateway import SlackGateway

ROW_PAUSE = 0.3    # seconds between row writes, to stay friendly with Slack's rate limits


class RowWriter:
    def __init__(self, gateway: SlackGateway, planner: RowCellPlanner, log: Log):
        self.gateway = gateway
        self.planner = planner
        self.log = log

    def create_rows(self, list_id, entries: list[RadioEntry], cols, ranks, prev_dates) -> int:
        added = 0
        for entry in entries:
            try:
                self.gateway.create_row(list_id, self.planner.plan(entry, cols, ranks, prev_dates=prev_dates))
                added += 1
                time.sleep(ROW_PAUSE)
            except Exception as e:  # noqa
                self.log(f"New row failed ({entry.name}): {e}", "err")
        return added
