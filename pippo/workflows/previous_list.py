"""Reading the PREVIOUS list: Handed Off projects take their due date from it."""
from __future__ import annotations

from dataclasses import dataclass

from slack_sdk.errors import SlackApiError

from ..core.rows import read_row_identity
from ..core.text import describe_error
from ..core.types import Log
from ..infra.slack_gateway import SlackGateway

NOTE_NONE = "none"              # no previous list ID on record
NOTE_UNREADABLE = "unreadable"  # Slack wouldn't let Pippo read it


@dataclass
class PreviousDates:
    dates: dict | None          # project name (lowercase) -> due date there (None = no date); None = unusable
    note: str | None = None     # why it is unusable (NOTE_NONE / NOTE_UNREADABLE)


class PreviousListReader:
    def __init__(self, gateway: SlackGateway, log: Log):
        self.gateway = gateway
        self.log = log

    def read(self, prev_list_id: str) -> PreviousDates:
        """A project on several rows takes the EARLIEST date."""
        if not prev_list_id:
            return PreviousDates(None, NOTE_NONE)
        try:
            items = self.gateway.fetch_items(prev_list_id)
            by_id = self.gateway.list_schema(prev_list_id, items)
        except SlackApiError as e:
            self.log(f"Couldn't read the previous list {prev_list_id}:\n{describe_error(e)}", "warn")
            return PreviousDates(None, NOTE_UNREADABLE)
        if items and not by_id:
            return PreviousDates(None, NOTE_UNREADABLE)
        dates: dict = {}
        for it in items:
            r = read_row_identity(it, by_id)
            nm = r.name.strip().lower()
            if nm not in dates or (r.date and (not dates[nm] or r.date < dates[nm])):
                dates[nm] = r.date
        self.log(f"Previous list {prev_list_id}: read {len(dates)} project(s) for Handed Off dates.")
        return PreviousDates(dates)
