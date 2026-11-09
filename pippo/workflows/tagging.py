"""@Pippo tagged in anything that isn't a Good Morning: tag the team."""
from __future__ import annotations

from ..core.text import fmt
from ..core.types import Log
from ..infra.slack_gateway import SlackGateway
from ..messaging.picker import TAG, MessagePicker


class TagResponder:
    def __init__(self, cfg: dict, gateway: SlackGateway, picker: MessagePicker, log: Log):
        self.cfg = cfg
        self.gateway = gateway
        self.picker = picker
        self.log = log

    def mentions(self) -> str:
        return " ".join(f"<@{u['id']}>" for u in self.cfg.get("tag_users") or [])

    def respond(self, event: dict) -> None:
        users = self.cfg.get("tag_users") or []
        channel_id, user_id = event.get("channel"), event.get("user")
        thread_ts = event.get("thread_ts") or event.get("ts")
        if not users:
            self.log("Tagged in a non-greeting message but nobody is in Settings → Who can Pippo tag.", "warn")
            self.gateway.post(channel_id, "🐾 I'd tag the team, but nobody is set up in my Settings yet.",
                              thread_ts, "Reply failed")
            return
        text = fmt(self.picker.pick(TAG), mentions=self.mentions(), user=user_id)
        if self.gateway.post(channel_id, text, thread_ts, f"Tag-everybody message failed in {channel_id}"):
            self.log(f"Tagged {len(users)} person(s) in {channel_id} (asked by {user_id}).", "ok")
