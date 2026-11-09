"""Chooses the next message of each kind from the Settings lists (built-ins when a list is empty)."""
from __future__ import annotations

from dataclasses import dataclass

from .defaults import DEFAULT_GREETINGS, DEFAULT_NON_WORKING, DEFAULT_TAG_REPLIES
from .shuffle import ShuffleBag


@dataclass(frozen=True)
class MessageKind:
    cfg_key: str            # which Settings list holds the messages
    defaults: list[str]     # used when that list is empty


TAG = "tag"
GREETING = "greeting"
NON_WORKING = "non_working"

MESSAGE_KINDS = {
    TAG: MessageKind("msg_tag_replies", DEFAULT_TAG_REPLIES),
    GREETING: MessageKind("msg_greetings", DEFAULT_GREETINGS),
    NON_WORKING: MessageKind("msg_non_working_replies", DEFAULT_NON_WORKING),
}


class MessagePicker:
    """One shuffle bag per kind. Add a new kind by adding one entry to MESSAGE_KINDS."""

    def __init__(self, cfg: dict, kinds: dict[str, MessageKind] | None = None):
        self.cfg = cfg
        self.kinds = kinds or MESSAGE_KINDS
        self._bags = {name: ShuffleBag() for name in self.kinds}

    def pick(self, kind: str) -> str:
        k = self.kinds[kind]
        items = [m.strip() for m in self.cfg.get(k.cfg_key) or [] if m.strip()] or k.defaults
        return self._bags[kind].pick(items)
