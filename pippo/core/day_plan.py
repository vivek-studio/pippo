"""What would Good Morning do today?  (shown on the Home page - no Slack calls)"""
from __future__ import annotations

from datetime import date

from .work_calendar import WorkCalendar

MODE_OFF, MODE_FIRST, MODE_DAILY = "off", "first", "daily"


def describe_today(cfg: dict, today: date | None = None) -> dict:
    today = today or date.today()
    cal = WorkCalendar.from_config(cfg)
    if not cal.is_working_day(today):
        return {"mode": MODE_OFF,
                "text": f"Non-working day ({cal.non_working_reason(today)}). "
                        "Pippo will only reply that it's a non-working day."}
    if cal.is_first_working_day_of_month(today):
        return {"mode": MODE_FIRST,
                "text": "First working day of the month! Pippo will create a NEW list from today's "
                        "Daily Radio (no old list ID needed) and post it."}
    last = cfg.get("last_list_id") or ""
    which = f"list {last}" if last else "the last list (NOT SET - add its ID in Settings)"
    return {"mode": MODE_DAILY,
            "text": f"Normal working day. Pippo will reuse {which}, add anything new from "
                    "the Daily Radio, update status/dates/rounds/assets and post it."}
