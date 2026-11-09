"""Every setting Pippo has, with its starting value."""
from __future__ import annotations

from ..messaging.defaults import DEFAULT_GREETINGS, DEFAULT_NON_WORKING, DEFAULT_TAG_REPLIES

DEFAULT_CONFIG = {
    # Slack
    "bot_token": "",
    "app_token": "",
    "workspace_id": "T017Y1A3T6G",
    "workspace_domain": "esga-india",
    # Channels
    "source_channel_id": "C0CENFBMMH9",       # where the Daily Radio is posted
    "target_channel_id": "C0CELEHEX45",       # where the list is shared + announced
    "good_morning_channel_ids": ["C0CENFBMMH9", "C0CELEHEX45"],
    # List
    "client_name": "Sephora",
    "template_json_path": "",
    "list_title_format": "{month} - {year}",
    "last_list_id": "",                       # Pippo overwrites this every time it creates a list
    "previous_list_id": "",                   # the list before it (saved when a new list is created)
    "last_run_date": "",
    # People Pippo is ALLOWED to tag when someone tags @Pippo  [{"id": "U123", "name": "Asha"}]
    "tag_users": [],
    # Messages
    # Good Morning post in the target channel = ONE greeting (picked in shuffled order) + this fixed part
    "msg_greetings": list(DEFAULT_GREETINGS),
    "msg_announcement_body": (
        "<!channel> *{date} Project Status*\n"
        "*{client}*\n"
        "{url}"
    ),
    # Sent whenever @Pippo is tagged in anything that is NOT a good-morning greeting. One is picked
    # each time, in shuffled order (none repeats until all have been used).
    "msg_tag_replies": list(DEFAULT_TAG_REPLIES),
    "msg_non_working_replies": list(DEFAULT_NON_WORKING),
    # Calendar: {"2026-11-12": "Diwali"}
    "holidays": {},
    # Weekend days that are marked as WORKING days: {"2026-11-14": "Special shift"}
    "working_weekends": {},
}
