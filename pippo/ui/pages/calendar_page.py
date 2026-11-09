"""Calendar: mark holidays and working weekends."""
from __future__ import annotations

import calendar
from datetime import date, datetime

import customtkinter as ctk

from ...core.work_calendar import WorkCalendar
from .. import events
from .. import theme as t
from ..widgets import accent_button, card, page_header, quiet_button
from .base import AppContext, Page

WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


class CalendarPage(Page):
    key, nav_label = "calendar", "Calendar"

    def __init__(self, parent, ctx: AppContext):
        super().__init__(parent, ctx)
        self.year, self.month = date.today().year, date.today().month
        self.cell_w = 80
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        page_header(self, "Plan", "Calendar",
                    "Click a weekday to mark / unmark a holiday. Click a Saturday or Sunday to mark / "
                    "unmark it as a working day."
                    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        left = card(self)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 9))
        right = card(self, width=270)
        right.grid(row=1, column=1, sticky="nsew", padx=(9, 0))
        right.grid_propagate(False)
        self.grid_columnconfigure(1, weight=0)

        left.bind("<Configure>", self._fit_cells)
        self._build_month_nav(left)
        self.grid_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.grid_frame.pack(padx=18, pady=(6, 8))
        self._build_legend(left)

        self.hol_head = ctk.CTkLabel(right, text="", text_color=t.INK, font=t.font(15, "bold", serif=True),
                                     justify="left", wraplength=230)
        self.hol_head.pack(anchor="w", padx=20, pady=(18, 4))
        self.hol_list = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.hol_list.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    def on_show(self) -> None:
        self.render()

    def _fit_cells(self, event):
        """Make the day buttons as wide as the card allows (so Sunday is never cut off)."""
        w = max(54, min(92, (event.width - 56) // 7 - 6))
        if w != self.cell_w:
            self.cell_w = w
            self.render()

    # ------------------------------------------------------------ chrome
    def _build_month_nav(self, left):
        nav = ctk.CTkFrame(left, fg_color="transparent")
        nav.pack(fill="x", padx=20, pady=(18, 6))
        quiet_button(nav, "‹", lambda: self.shift(-1), width=38, height=36).pack(side="left")
        self.title_lbl = ctk.CTkLabel(nav, text="", font=t.font(22, "bold", serif=True), text_color=t.INK, width=230)
        self.title_lbl.pack(side="left", padx=10)
        quiet_button(nav, "›", lambda: self.shift(1), width=38, height=36).pack(side="left")
        accent_button(nav, "Today", self.go_today, width=76, height=36).pack(side="right")

    @staticmethod
    def _build_legend(left):
        legend = ctk.CTkFrame(left, fg_color="transparent")
        legend.pack(anchor="w", padx=22, pady=(4, 18))
        for color, label in ((t.WEEKEND, "Weekend (rest)"), (t.HOLIDAY, "Holiday"),
                             (t.WORKING_WEEKEND, "Working weekend"), (t.SURFACE_2, "Working day")):
            ctk.CTkLabel(legend, text="", fg_color=color, corner_radius=6, width=16, height=16
                         ).pack(side="left")
            ctk.CTkLabel(legend, text=label, text_color=t.MUTED, font=t.font(12)).pack(side="left", padx=(6, 16))
        ctk.CTkLabel(legend, text="★", text_color=t.BUTTER_DEEP, font=t.font(14, "bold")).pack(side="left")
        ctk.CTkLabel(legend, text="New-list day", text_color=t.MUTED, font=t.font(12)).pack(side="left", padx=(5, 0))

    # ------------------------------------------------------------ navigation
    def shift(self, delta):
        m = self.month + delta
        self.year += (m - 1) // 12
        self.month = (m - 1) % 12 + 1
        self.render()

    def go_today(self):
        self.year, self.month = date.today().year, date.today().month
        self.render()

    # ------------------------------------------------------------ month grid
    def render(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        y, m = self.year, self.month
        self.title_lbl.configure(text=f"{calendar.month_name[m]} {y}")
        cal = WorkCalendar.from_config(self.ctx.cfg)
        h, w = cal.holidays, cal.working_weekends
        today = date.today()
        fw = cal.first_working_day(y, m)

        for c, name in enumerate(WEEKDAYS):
            ctk.CTkLabel(self.grid_frame, text=name.upper(), width=self.cell_w + 4, text_color=t.MUTED,
                         font=t.font(11, "bold")).grid(row=0, column=c, pady=(0, 4))

        for r, week in enumerate(calendar.Calendar(0).monthdatescalendar(y, m), start=1):
            for c, d in enumerate(week):
                self._day_button(d, r, c, cal, h, w, today, fw)
        self.render_holiday_list()

    def _day_button(self, d, r, c, cal, h, w, today, fw):
        other = d.month != self.month
        weekend, hol = cal.is_weekend(d), cal.is_holiday(d)
        work_we = weekend and cal.is_marked_working(d)
        label = str(d.day)
        fg, tc, hov = t.SURFACE_2, t.INK, t.LINE
        if weekend:
            fg, tc, hov = t.WEEKEND, t.MUTED, "#DDD5BF"
        if work_we:
            fg, tc, hov = t.WORKING_WEEKEND, t.INK, "#C2DEE1"
            label += "\n" + (w[d.isoformat()] or "Working")[:9]
        if hol:
            fg, tc, hov = t.HOLIDAY, "#4A3000", t.HOLIDAY_HOVER
            label += "\n" + (h[d.isoformat()] or "Holiday")[:9]
        elif d == fw:
            label += "\n★"
        if other:
            fg, tc = "transparent", t.LINE_STRONG
        ctk.CTkButton(
            self.grid_frame, text=label, width=self.cell_w, height=62, corner_radius=14,
            fg_color=fg, hover_color=hov, text_color=tc, text_color_disabled=tc,
            font=t.font(13, "bold" if d == today else "normal"),
            border_width=2 if d == today else 0, border_color=t.INK,
            state="disabled" if other else "normal",
            command=lambda dd=d: self.toggle_day(dd)).grid(row=r, column=c, padx=3, pady=3)

    # ------------------------------------------------------------ editing
    def _changed(self):
        self.ctx.store.save(self.ctx.cfg)
        self.render()
        self.ctx.bus.publish(events.CALENDAR_CHANGED)

    def toggle_day(self, d: date):
        """Weekdays toggle a holiday, Saturdays/Sundays toggle a working weekend."""
        cfg = self.ctx.cfg
        weekend = WorkCalendar.is_weekend(d)
        store = cfg.setdefault("working_weekends", {}) if weekend else cfg["holidays"]
        iso = d.isoformat()
        if iso in store:
            del store[iso]
        else:
            when = d.strftime('%a %d %b %Y')
            text, title, default = ((f"Reason for working on {when} (optional):", "Mark working weekend", "Working")
                                    if weekend else
                                    (f"Holiday name for {when} (optional):", "Mark holiday", "Holiday"))
            name = ctk.CTkInputDialog(text=text, title=title).get_input()
            if name is None:  # cancelled
                return
            store[iso] = name.strip() or default
        self._changed()

    def render_holiday_list(self):
        cfg = self.ctx.cfg
        for w in self.hol_list.winfo_children():
            w.destroy()
        y = self.year
        items = sorted((k, v) for k, v in cfg["holidays"].items() if k.startswith(f"{y}-"))
        wk = sorted((k, v) for k, v in (cfg.get("working_weekends") or {}).items() if k.startswith(f"{y}-"))
        self.hol_head.configure(text=f"{y}  ·  {len(items)} holidays, {len(wk)} working weekends")
        items = [(k, v, False) for k, v in items] + [(k, v, True) for k, v in wk]
        if not items:
            ctk.CTkLabel(self.hol_list, text="Nothing marked yet.\nClick a day on the calendar.",
                         text_color=t.MUTED, justify="left").pack(anchor="w", padx=10, pady=10)
        for iso, name, is_wk in items:
            d = datetime.strptime(iso, "%Y-%m-%d").date()
            row = ctk.CTkFrame(self.hol_list, fg_color=t.SURFACE_2, corner_radius=12)
            row.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(row, text=d.strftime("%d %b").upper(), width=56,
                         text_color=t.POND if is_wk else t.WARN,
                         font=t.font(12, "bold")).pack(side="left", padx=(10, 4), pady=8)
            ctk.CTkLabel(row, text=("Working · " if is_wk else "") + name, text_color=t.INK,
                         anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="✕", width=28, height=26, fg_color="transparent",
                          hover_color=t.LINE, text_color=t.MUTED,
                          command=lambda k=iso, wk=is_wk: self.delete_entry(k, wk)).pack(side="right", padx=6)

    def delete_entry(self, iso, is_wk=False):
        cfg = self.ctx.cfg
        (cfg.setdefault("working_weekends", {}) if is_wk else cfg["holidays"]).pop(iso, None)
        self._changed()
