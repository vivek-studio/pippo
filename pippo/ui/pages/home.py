"""Home: wake Pippo up, see today's plan, read Pippo's diary."""
from __future__ import annotations

from datetime import date, datetime

import customtkinter as ctk

from ...core.day_plan import MODE_DAILY, MODE_FIRST, MODE_OFF, describe_today
from ...core.work_calendar import WorkCalendar
from .. import events
from .. import theme as t
from ..duck import DuckCanvas
from ..widgets import accent_button, card, eyebrow, page_header, pill, quiet_button, textbox
from .base import AppContext, Page

# status -> (duck mood, headline, button text, button colours)
STATUS_VIEW = {
    "online": ("awake", "Pippo is awake & listening", "■  Let Pippo nap"),
    "starting": ("waking", "Pippo is waking up…", "Waking up…"),
    "offline": ("asleep", "Pippo is napping", "▶  Wake Pippo up"),
}

BADGES = {MODE_OFF: ("Non-working day", t.LAVENDER),
          MODE_FIRST: ("First working day", t.BUTTER_DEEP),
          MODE_DAILY: ("Working day", t.POND)}


class HomePage(Page):
    key, nav_label = "home", "Home"

    def __init__(self, parent, ctx: AppContext):
        super().__init__(parent, ctx)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        page_header(self, "Dashboard", "Good morning.",
                    "Wake Pippo up, peek at today's plan, watch what it's doing."
                    ).grid(row=0, column=0, sticky="w", pady=(0, 18))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew")
        top.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self._build_status_card(top).grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        self._build_today_card(top).grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        self._build_diary(self).grid(row=2, column=0, sticky="nsew", pady=(18, 0))

        bus = ctx.bus
        bus.subscribe(events.LOG, self.append_log)
        bus.subscribe(events.STATUS, self.set_status)
        for topic in (events.STATE, events.CALENDAR_CHANGED, events.SETTINGS_SAVED, events.TICK):
            bus.subscribe(topic, self.refresh_today)

        self.append_log("Hi! Fill in Settings, then wake me up 🐾", "info")
        self.refresh_today()

    def on_show(self) -> None:
        self.refresh_today()

    # ------------------------------------------------------------ cards
    def _build_status_card(self, parent):
        c = card(parent)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(22, 0))
        self.duck = DuckCanvas(row, size=104, bg=t.SURFACE)
        self.duck.pack(side="left")
        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left", padx=(16, 0), fill="x", expand=True)
        eyebrow(col, "Pippo").pack(anchor="w")
        self.status_lbl = ctk.CTkLabel(col, text="", text_color=t.INK, font=t.font(21, "bold", serif=True),
                                       justify="left", wraplength=250)
        self.status_lbl.pack(anchor="w", pady=(2, 0))
        self.start_btn = accent_button(c, "", command=self.ctx.controller.toggle, height=46)
        self.start_btn.pack(fill="x", padx=24, pady=(18, 24))
        self.set_status("offline")
        return c

    def _build_today_card(self, parent):
        c = card(parent)
        eyebrow(c, "Today").pack(anchor="w", padx=24, pady=(22, 0))
        self.today_title = ctk.CTkLabel(c, text="", text_color=t.INK, font=t.font(24, "bold", serif=True))
        self.today_title.pack(anchor="w", padx=24, pady=(2, 0))
        self.today_badge = pill(c, "", t.POND)
        self.today_badge.pack(anchor="w", padx=24, pady=(10, 0))
        self.today_text = ctk.CTkLabel(c, text="", text_color=t.INK_SOFT, justify="left", wraplength=400,
                                       font=t.font(13))
        self.today_text.pack(anchor="w", padx=24, pady=(10, 4))
        self.next_first = ctk.CTkLabel(c, text="", text_color=t.MUTED, font=t.font(12))
        self.next_first.pack(anchor="w", padx=24, pady=(0, 22))
        return c

    def _build_diary(self, parent):
        c = card(parent)
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(1, weight=1)
        head = ctk.CTkFrame(c, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=22, pady=(16, 8))
        eyebrow(head, "Pippo's diary").pack(side="left")
        quiet_button(head, "Clear", self.clear_log, width=70, height=28).pack(side="right")
        self.log_box = textbox(c, font=t.font(12, mono=True))
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        for tag, col in (("ok", t.OK), ("warn", t.WARN), ("err", t.ERR)):
            self.log_box.tag_config(tag, foreground=col)
        self.log_box.configure(state="disabled")
        return c

    # ------------------------------------------------------------ diary
    def append_log(self, msg, level="info"):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{stamp}  {msg}\n", level if level in ("ok", "warn", "err") else ())
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ------------------------------------------------------------ status
    def set_status(self, state):
        mood, headline, button_text = STATUS_VIEW.get(state, STATUS_VIEW["offline"])
        online, busy = state == "online", state == "starting"
        self.duck.set_mood(mood)
        self.status_lbl.configure(text=headline)
        self.start_btn.configure(
            text=button_text,
            fg_color=t.INK if online else t.BUTTER,
            hover_color=t.INK_2 if online else t.BUTTER_DEEP,
            text_color=t.ON_INK if online else t.INK,
            state="disabled" if busy else "normal")

    def refresh_today(self):
        cfg = self.ctx.cfg
        today = date.today()
        d = describe_today(cfg, today)
        self.today_title.configure(text=today.strftime("%A, %d %B %Y"))
        label, color = BADGES[d["mode"]]
        self.today_badge.configure(text=f"  {label}  ", fg_color=color)
        self.today_text.configure(text=d["text"])

        cal = WorkCalendar.from_config(cfg)
        y, m = today.year, today.month
        fw = cal.first_working_day(y, m)
        if fw is None or fw < today:
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
            fw = cal.first_working_day(y, m)
        self.next_first.configure(
            text=f"Next new-list day:  {fw.strftime('%a, %d %b %Y')}" if fw else "")
