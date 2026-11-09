"""The Good Morning post in the target channel."""
from __future__ import annotations

from datetime import date

from ..core.text import date_text, fmt
from ..infra.slack_gateway import SlackGateway
from ..messaging.picker import GREETING, MessagePicker


def list_url(cfg: dict, list_id) -> str:
    return f"https://{cfg['workspace_domain']}.slack.com/lists/{cfg['workspace_id']}/{list_id}"


class Announcer:
    """One message: a rotating greeting line, then @channel, date, client, list link
    (bare URL so Slack unfurls it)."""

    def __init__(self, cfg: dict, gateway: SlackGateway, picker: MessagePicker):
        self.cfg = cfg
        self.gateway = gateway
        self.picker = picker

    def announce(self, user_id: str, today: date, list_id) -> None:
        cfg = self.cfg
        greeting = self.picker.pick(GREETING)
        text = fmt(f"{greeting}\n\n{cfg['msg_announcement_body']}", user=user_id, date=date_text(today),
                   client=cfg["client_name"], url=list_url(cfg, list_id),
                   month=today.strftime("%B"), year=today.year)
        self.gateway.post(cfg["target_channel_id"], text, failed_msg="Announcement failed", mrkdwn=True)
