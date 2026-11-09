"""The only place that talks to Slack's Web API (messages, history and Lists)."""
from __future__ import annotations

import time

from slack_sdk.errors import SlackApiError

from ..core.text import describe_error
from ..core.types import Log


class SlackGateway:
    """Thin, logged wrapper around slack_sdk.WebClient. Workflows depend on THIS, not on slack_sdk."""

    def __init__(self, client, log: Log):
        self.client = client
        self.log = log

    # ---------- plumbing
    def _lists(self, method_name, api_name, **kwargs):
        """Slack Lists call; on a 429 wait Retry-After and try again."""
        for _ in range(4):
            try:
                m = getattr(self.client, method_name, None)
                return m(**kwargs) if m else self.client.api_call(api_name, json=kwargs)
            except SlackApiError as e:
                if getattr(e.response, "status_code", 0) == 429:
                    wait = int(e.response.headers.get("Retry-After", 2))
                    self.log(f"Rate limited, waiting {wait}s…", "warn")
                    time.sleep(wait + 1)
                    continue
                raise
        raise RuntimeError("Too many rate-limit retries.")

    # ---------- messages
    def post(self, channel, text, thread_ts=None, failed_msg="Message failed", **kw):
        """chat.postMessage; logs `failed_msg: <slack error>` and returns None on failure."""
        try:
            return self.client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text, **kw)
        except SlackApiError as e:
            self.log(f"{failed_msg}: {e.response.get('error')}", "err")
            return None

    def latest_status_text(self, source_channel_id: str):
        r = self.client.conversations_history(channel=source_channel_id, limit=50)
        for msg in r.get("messages", []):
            if "project status" in msg.get("text", "").lower():
                return msg["text"]
        return None

    # ---------- lists: writing
    def create_list(self, title: str, schema: list[dict]):
        """slackLists.create. Returns Slack's response, or None (and logs why) when it failed."""
        try:
            r = self._lists("slackLists_create", "slackLists.create", name=title, schema=schema)
            if r.get("ok"):
                self.log("List created from the template's columns", "ok")
                return r
            self.log(f"List creation failed: {r}", "err")
        except SlackApiError as e:
            self.log(f"List creation failed:\n{describe_error(e)}", "err")
        return None

    def create_row(self, list_id, fields):
        r = self._lists("slackLists_items_create", "slackLists.items.create",
                        list_id=list_id, initial_fields=fields)
        if not r.get("ok"):
            raise RuntimeError(str(r))
        return (r.get("item") or {}).get("id")

    def update_cells(self, list_id, row_id, cells):
        """cells: [{column_id, <type>: value}]  ->  one items.update call for that row."""
        if not cells:
            return
        payload = [dict(c, row_id=row_id) for c in cells]
        r = self._lists("slackLists_items_update", "slackLists.items.update",
                        list_id=list_id, cells=payload)
        if not r.get("ok"):
            raise RuntimeError(str(r))

    def share(self, list_id, channel_id) -> bool:
        r = self._lists("slackLists_access_set", "slackLists.access.set",
                        list_id=list_id, access_level="write", channel_ids=[channel_id])
        if not r.get("ok"):
            self.log(f"List sharing failed: {r}", "err")
        return bool(r.get("ok"))

    # ---------- lists: reading
    def fetch_items(self, list_id) -> list[dict]:
        items, cursor = [], None
        while True:
            kw = {"list_id": list_id, "limit": 100}
            if cursor:
                kw["cursor"] = cursor
            r = self._lists("slackLists_items_list", "slackLists.items.list", **kw)
            items += r.get("items", [])
            cursor = (r.get("response_metadata") or {}).get("next_cursor")
            if not cursor:
                return items

    def list_schema(self, list_id, items) -> dict:
        """column_id -> column dict for an existing list (read via items.info)."""
        if not items:
            return {}
        try:
            r = self._lists("slackLists_items_info", "slackLists.items.info",
                            list_id=list_id, id=items[0]["id"])
            meta = (r.get("list") or {}).get("list_metadata") or {}
            return {c["id"]: c for c in meta.get("schema", [])}
        except SlackApiError as e:
            self.log(f"Couldn't read the list's columns: {describe_error(e)}", "warn")
            return {}
