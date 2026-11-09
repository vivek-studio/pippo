"""Pippo's internal working-day calendar."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Mapping


@dataclass(frozen=True)
class WorkCalendar:
    """
    holidays          {"2026-11-12": "Diwali"}        weekdays that are days off
    working_weekends  {"2026-11-14": "Special shift"}  Saturdays / Sundays that are worked
    """
    holidays: Mapping[str, str] = field(default_factory=dict)
    working_weekends: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_config(cls, cfg: dict) -> "WorkCalendar":
        return cls(cfg["holidays"], cfg.get("working_weekends") or {})

    @staticmethod
    def is_weekend(d: date) -> bool:
        return d.weekday() >= 5  # Sat, Sun

    def is_holiday(self, d: date) -> bool:
        return d.isoformat() in self.holidays

    def is_marked_working(self, d: date) -> bool:
        return bool(self.working_weekends) and d.isoformat() in self.working_weekends

    def is_working_day(self, d: date) -> bool:
        """Weekdays work unless marked as a holiday. Sat/Sun rest unless marked as a working weekend."""
        if self.is_holiday(d):
            return False
        if self.is_weekend(d):
            return self.is_marked_working(d)
        return True

    def first_working_day(self, year: int, month: int) -> date | None:
        d = date(year, month, 1)
        while d.month == month:
            if self.is_working_day(d):
                return d
            d += timedelta(days=1)
        return None  # whole month is off

    def is_first_working_day_of_month(self, d: date) -> bool:
        return self.first_working_day(d.year, d.month) == d

    def non_working_reason(self, d: date) -> str:
        if self.is_holiday(d):
            return self.holidays.get(d.isoformat()) or "a holiday"
        if self.is_weekend(d):
            return d.strftime("%A")  # "Saturday" / "Sunday"
        return ""
