"""Little text and date helpers used all over Pippo."""
from __future__ import annotations

import json
import re
from datetime import date, datetime


def fmt(template: str, **kw) -> str:
    """Safe {placeholder} formatting - unknown placeholders stay as typed."""
    return re.sub(r"\{(\w+)\}",
                  lambda m: str(kw[m.group(1)]) if m.group(1) in kw else m.group(0),
                  template)


def date_text(d: date) -> str:
    return f"{d.day} {d.strftime('%B')}, {d.year}"      # 5 November, 2026


def event_date(event: dict) -> date:
    """The date the 'good morning' message was actually sent (falls back to today)."""
    try:
        return datetime.fromtimestamp(float(event["ts"])).date()
    except Exception:
        return date.today()


def describe_error(e) -> str:
    try:
        return json.dumps(e.response.data, indent=2)[:1500]
    except Exception:
        return str(e)
