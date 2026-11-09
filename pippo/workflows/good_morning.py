"""The Good Morning workflow, start to finish.

  1. Pippo works out today's date (from the time of the Slack message).
  2. Not a working day?  -> a cute "non-working day" reply. Nothing else happens.
  3. Reads the latest Daily Radio ("Project Status") post.
  4. First working day of the month?  -> a NEW list (NewListStrategy).
     Any other working day?           -> the month's list, updated (DailyUpdateStrategy).
  5. Restructuring runs on BOTH paths (a placeholder for now).
  6. New list -> share it. Always -> announce it.
  7. Pippo remembers the list IDs.
"""
from __future__ import annotations

import re

from slack_sdk.errors import SlackApiError

from ..core.radio import parse_header_date, parse_status_message
from ..core.text import date_text, describe_error, event_date, fmt
from ..core.types import Log
from ..core.work_calendar import WorkCalendar
from ..infra.slack_gateway import SlackGateway
from ..messaging.picker import NON_WORKING, MessagePicker
from . import notices
from .announce import Announcer, list_url
from .contracts import ListContext, ListStrategy, Restructurer
from .previous_list import PreviousListReader

GOOD_MORNING_RE = re.compile(r"\bgood\s+morning\b", re.IGNORECASE)
FORCE_NEW_RE = re.compile(r"\bforce\s+new\b", re.IGNORECASE)


class GoodMorningWorkflow:
    def __init__(self, cfg: dict, gateway: SlackGateway, picker: MessagePicker, log: Log, save,
                 new_list: ListStrategy, daily: ListStrategy, previous: PreviousListReader,
                 restructurer: Restructurer, announcer: Announcer):
        self.cfg = cfg
        self.gateway = gateway
        self.picker = picker
        self.log = log
        self.save = save
        self.new_list = new_list
        self.daily = daily
        self.previous = previous
        self.restructurer = restructurer
        self.announcer = announcer

    def run(self, event: dict) -> None:
        cfg = self.cfg
        user_id, channel_id = event.get("user"), event.get("channel")
        thread_ts = event.get("thread_ts")
        today = event_date(event)
        calendar = WorkCalendar.from_config(cfg)

        def reply(text):
            self.gateway.post(channel_id, text, thread_ts, "Reply failed")

        self.log(f"🐾 Good Morning from {user_id} on {date_text(today)}", "info")

        # 1) Working day?
        if not calendar.is_working_day(today):
            reason = calendar.non_working_reason(today)
            self.log(f"Non-working day ({reason}) - cute reply only.", "warn")
            reply(fmt(self.picker.pick(NON_WORKING), user=user_id, date=date_text(today), reason=reason))
            return

        # 2) Daily Radio
        radio = self._read_radio(today, reply)
        if radio is None:
            return

        # 3) New list (first working day) or the month's list (any other working day)
        last = (cfg.get("last_list_id") or "").strip()
        make_new = self._should_make_new_list(today, calendar, last, event)
        if not make_new and not last:
            reply("🐾 I don't know which list to use yet. Please put the current list's ID in "
                  "*Last list ID* in Pippo's Settings.")
            self.log("No last_list_id set on a non-first working day - stopped, nothing created.", "err")
            return

        # Previous list = where Handed Off dates come from.
        #   new list     -> the list I was using until now (Last list ID)
        #   normal day   -> the list saved as Previous list ID when this month's list was created
        prev = self.previous.read(last if make_new else (cfg.get("previous_list_id") or "").strip())
        ctx = ListContext(today=today, radio=radio, last_list_id=last, prev_dates=prev.dates)
        strategy = self.new_list if make_new else self.daily
        try:
            outcome = strategy.run(ctx)
        except SlackApiError as e:
            self.log(f"Slack API error:\n{describe_error(e)}", "err")
            reply("🐾 Slack returned an error while working on the list. Check Pippo's log.")
            return
        if not outcome or not outcome.list_id:
            reply("🐾 I couldn't get the list ready. Check Pippo's log.")
            return
        list_id = outcome.list_id

        # 4) Restructuring - runs on BOTH paths
        self.restructurer.restructure(list_id, radio, new_list=make_new)

        # 5) Share (new list only) + announce
        if make_new:
            self.gateway.share(list_id, cfg["target_channel_id"])
        self.announcer.announce(user_id, today, list_id)
        if outcome.sort_missing:
            reply(notices.sort_missing_notice())
        if prev.note:
            reply(notices.previous_list_notice(prev.note, make_new))
        dupes = sorted(set(outcome.dupes)) if not make_new else []
        if dupes:
            reply(notices.duplicates_notice(dupes))

        # 6) Remember my own list ID - and, on a new list, the one it replaces
        if make_new:
            cfg["previous_list_id"] = last
        cfg["last_list_id"] = list_id
        cfg["last_run_date"] = today.isoformat()
        self.save()
        self.log(f"✅ Done. List {list_id} → {list_url(cfg, list_id)}", "ok")

    # ---------- steps
    def _read_radio(self, today, reply):
        """Today's parsed Daily Radio, or None (after telling the person why) when it can't be used."""
        try:
            status_text = self.gateway.latest_status_text(self.cfg["source_channel_id"])
        except SlackApiError as e:
            self.log(f"Could not read source channel: {e.response.get('error')}", "err")
            reply("🐾 I couldn't read the source channel. Check Pippo's log.")
            return None
        if not status_text:
            reply("🐾 I couldn't find a recent *Project Status* message in the source channel.")
            return None
        radio = parse_status_message(status_text)
        self.log(f"Parsed {len(radio)} Daily Radio entries.")
        if not radio:
            reply("🐾 I found the status message but couldn't parse any projects.")
            return None
        radio_date = parse_header_date(status_text)
        if radio_date and radio_date != today:
            self.log(f"Heads-up: the latest Daily Radio is dated {date_text(radio_date)}, "
                     f"not today.", "warn")
        return radio

    def _should_make_new_list(self, today, calendar: WorkCalendar, last: str, event: dict) -> bool:
        """First working day -> new list (if I already made today's list, a second 'good morning' re-uses it)."""
        first_day = calendar.is_first_working_day_of_month(today)
        already_ran_today = self.cfg.get("last_run_date") == today.isoformat() and bool(last)
        make_new = first_day and not already_ran_today
        # Testing hook: "good morning force new" (any case) behaves like a first working day.
        if FORCE_NEW_RE.search(event.get("text", "") or ""):
            make_new = True
            self.log("TEST MODE: 'force new' found in the message -> acting as the first working day.", "warn")
        return make_new
