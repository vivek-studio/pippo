"""Guide: Pippo's manual, built from ui/guide_content.py."""
from __future__ import annotations

import customtkinter as ctk

from .. import theme as t
from ..guide_content import TOPICS, Bullets, Code, H, P, Steps, Table, Tip, Topic, Warn
from ..widgets import card, eyebrow, page_header
from .base import AppContext, Page


class GuidePage(Page):
    key, nav_label = "guide", "Guide"

    def __init__(self, parent, ctx: AppContext):
        super().__init__(parent, ctx)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        page_header(self, "Read me", "Guide", "Everything Pippo does, and how to set it up."
                    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        nav = card(self, width=230)
        nav.grid(row=1, column=0, sticky="ns", padx=(0, 14))
        nav.grid_propagate(False)
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        side = ctk.CTkScrollableFrame(nav, fg_color="transparent")
        side.pack(fill="both", expand=True, padx=6, pady=8)
        for i, topic in enumerate(TOPICS, start=1):
            b = ctk.CTkButton(side, text=f"{i:02d}   {topic.title}", anchor="w", height=36, corner_radius=10,
                              fg_color="transparent", hover_color=t.SURFACE_2, text_color=t.INK_SOFT,
                              font=t.font(13), command=lambda k=topic.key: self.show_topic(k))
            b.pack(fill="x", pady=1)
            self.nav_buttons[topic.key] = b

        self.body = card(self)
        self.body.grid(row=1, column=1, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)
        self.scroll = None
        self.wrapped: list = []
        self.show_topic(TOPICS[0].key)

    # ------------------------------------------------------------ topics
    def show_topic(self, key: str) -> None:
        topic = next(tp for tp in TOPICS if tp.key == key)
        for k, b in self.nav_buttons.items():
            on = k == key
            b.configure(fg_color=t.BUTTER_SOFT if on else "transparent",
                        text_color=t.INK if on else t.INK_SOFT,
                        font=t.font(13, "bold" if on else "normal"))
        if self.scroll is not None:
            self.scroll.destroy()
        self.scroll = ctk.CTkScrollableFrame(self.body, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.wrapped = []
        self._render(topic)
        self.scroll.bind("<Configure>", self._rewrap)

    def _rewrap(self, event=None):
        width = max(260, self.scroll.winfo_width() - 90)
        for lbl, inset in self.wrapped:
            lbl.configure(wraplength=width - inset)

    def _label(self, parent, text, inset=0, **kw):
        lbl = ctk.CTkLabel(parent, text=text, justify="left", anchor="w", wraplength=520 - inset, **kw)
        self.wrapped.append((lbl, inset))
        return lbl

    # ------------------------------------------------------------ renderers (one per block type)
    def _render(self, topic: Topic) -> None:
        s = self.scroll
        eyebrow(s, "Guide", color=t.POND).pack(anchor="w", padx=18, pady=(12, 0))
        ctk.CTkLabel(s, text=topic.title, font=t.font(28, "bold", serif=True), text_color=t.INK
                     ).pack(anchor="w", padx=18)
        self._label(s, topic.summary, text_color=t.MUTED, font=t.font(13)).pack(anchor="w", padx=18, pady=(2, 10))
        draw = {P: self._p, H: self._h, Steps: self._steps, Bullets: self._bullets, Table: self._table,
                Tip: lambda b: self._note(b, t.BUTTER_SOFT, t.BUTTER, "TIP"),
                Warn: lambda b: self._note(b, "#FDE6E9", t.ERR, "CAREFUL"), Code: self._code}
        for block in topic.blocks:
            draw[type(block)](block)

    def _p(self, b):
        self._label(self.scroll, b.text, text_color=t.INK, font=t.font(13)).pack(anchor="w", padx=18, pady=5)

    def _h(self, b):
        self._label(self.scroll, b.text, text_color=t.INK, font=t.font(17, "bold", serif=True)
                    ).pack(anchor="w", padx=18, pady=(14, 2))

    def _steps(self, b):
        for i, text in enumerate(b.items, start=1):
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(row, text=str(i), width=28, height=28, corner_radius=14, fg_color=t.INK,
                         text_color=t.ON_INK, font=t.font(12, "bold")).pack(side="left", anchor="n")
            self._label(row, text, inset=70, text_color=t.INK, font=t.font(13)).pack(side="left", padx=(12, 0))

    def _bullets(self, b):
        for text in b.items:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(row, text="•", text_color=t.BUTTER_DEEP, font=t.font(16, "bold"), width=20
                         ).pack(side="left", anchor="n")
            self._label(row, text, inset=60, text_color=t.INK, font=t.font(13)).pack(side="left")

    def _table(self, b):
        box = ctk.CTkFrame(self.scroll, fg_color=t.SURFACE_2, corner_radius=12, border_width=1, border_color=t.LINE)
        box.pack(fill="x", padx=18, pady=8)
        for c, h in enumerate(b.headers):
            eyebrow(box, h).grid(row=0, column=c, sticky="w", padx=14, pady=(10, 4))
        box.grid_columnconfigure(len(b.headers) - 1, weight=1)
        for r, row in enumerate(b.rows, start=1):
            for c, text in enumerate(row):
                lbl = ctk.CTkLabel(box, text=text, justify="left", anchor="w", text_color=t.INK,
                                   font=t.font(12, "bold" if c == 0 else "normal"),
                                   wraplength=(b.widths[c] if b.widths else 260) - 24)
                lbl.grid(row=r, column=c, sticky="nw", padx=14, pady=5)
        self._pad(box)

    @staticmethod
    def _pad(box):
        ctk.CTkFrame(box, height=6, fg_color="transparent").grid(column=0, columnspan=2, sticky="ew")

    def _note(self, b, bg, border, label):
        box = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=12, border_width=1, border_color=border)
        box.pack(fill="x", padx=18, pady=8)
        eyebrow(box, label, color=t.INK).pack(anchor="w", padx=14, pady=(10, 0))
        self._label(box, b.text, inset=60, text_color=t.INK, font=t.font(13)).pack(anchor="w", padx=14, pady=(2, 12))

    def _code(self, b):
        box = ctk.CTkFrame(self.scroll, fg_color=t.INK, corner_radius=12)
        box.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(box, text=b.text, justify="left", anchor="w", text_color=t.ON_INK,
                     font=t.font(12, mono=True)).pack(anchor="w", padx=16, pady=14)
