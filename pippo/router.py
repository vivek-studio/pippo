"""Decides what to do with each Slack event: Good Morning, tag the team, or ignore it."""
from __future__ import annotations

import re
from typing import Callable

from .core.types import Log
from .workflows.good_morning import GOOD_MORNING_RE

MAX_REMEMBERED_EVENTS = 5000


class EventRouter:
    def __init__(self, cfg: dict, log: Log, on_good_morning: Callable[[dict], None],
                 on_tag: Callable[[dict], None]):
        self.cfg = cfg
        self.log = log
        self.on_good_morning = on_good_morning
        self.on_tag = on_tag
        self.bot_user_id: str | None = None
        self._handled: set = set()

    # ---------- Slack event handlers (slack_bolt passes arguments by name: event, body)
    def on_mention(self, event, body):
        self.route(event)

    def on_message(self, event, body):
        if event.get("bot_id") or event.get("subtype") or not event.get("text"):
            return
        tagged = bool(self.bot_user_id and re.search(
            rf"<@{re.escape(self.bot_user_id)}(?:\|[^>]+)?>", event["text"]))
        if tagged:
            self.route(event)

    # ---------- routing
    def route(self, event):
        """@Pippo was tagged. Good-morning greeting -> list workflow. Anything else -> tag everybody."""
        if event.get("bot_id") or (self.bot_user_id and event.get("user") == self.bot_user_id):
            return
        channel_id, text = event.get("channel"), event.get("text", "") or ""
        if GOOD_MORNING_RE.search(text):
            if not self._gm_allowed(channel_id):
                self.log("Good Morning in a channel that isn't in Good Morning channels, ignoring.", "warn")
                return
            if not self._already_handled(event):
                self.on_good_morning(event)
            return
        # Not a greeting -> works in ANY channel / thread Pippo is in, on ANY day.
        if not self._already_handled(event):
            self.on_tag(event)

    def _already_handled(self, event) -> bool:
        key = (event.get("channel"), event.get("ts"))
        if key in self._handled:
            return True
        self._handled.add(key)
        if len(self._handled) > MAX_REMEMBERED_EVENTS:
            self._handled.clear()
        return False

    def _gm_allowed(self, channel_id) -> bool:
        ids = self.cfg.get("good_morning_channel_ids") or []
        return (not ids) or channel_id in ids
