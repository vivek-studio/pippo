"""Pippo's face: a tiny vector duckling drawn on a canvas (no image files, no emoji fonts needed)."""
from __future__ import annotations

import tkinter as tk

from . import theme as t

MOODS = ("asleep", "waking", "awake")


class DuckCanvas(tk.Canvas):
    def __init__(self, parent, size: int = 120, bg: str = t.SURFACE, mood: str = "asleep"):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
        self.size = size
        self.set_mood(mood)

    def set_mood(self, mood: str) -> None:
        self.delete("all")
        s = self.size / 120.0

        def box(x1, y1, x2, y2):
            return x1 * s, y1 * s, x2 * s, y2 * s

        ink = t.INK
        # ground shadow
        self.create_oval(*box(26, 100, 98, 112), fill=t.LINE, outline="")
        # body + wing
        self.create_oval(*box(18, 52, 100, 108), fill=t.BUTTER, outline=ink, width=3)
        self.create_arc(*box(34, 66, 78, 100), start=200, extent=140, style="arc", outline=ink, width=3)
        # head
        self.create_oval(*box(46, 14, 100, 68), fill=t.BUTTER, outline=ink, width=3)
        # beak
        self.create_polygon(*[v * s for v in (98, 40, 116, 46, 98, 54)], fill="#FF9F1C", outline=ink,
                            width=3, joinstyle="round")
        # blush
        self.create_oval(*box(70, 48, 82, 57), fill="#FFB199", outline="")
        # eye
        if mood == "asleep":
            self.create_arc(*box(66, 34, 82, 46), start=200, extent=140, style="arc", outline=ink, width=3)
            self.create_text(30 * s, 24 * s, text="z", fill=t.LAVENDER, font=t.font(int(13 * s), "bold", serif=True))
            self.create_text(42 * s, 12 * s, text="Z", fill=t.LAVENDER, font=t.font(int(16 * s), "bold", serif=True))
        elif mood == "waking":
            self.create_oval(*box(70, 36, 78, 44), fill=ink, outline="")
            self.create_text(34 * s, 20 * s, text="…", fill=t.WARN, font=t.font(int(20 * s), "bold"))
        else:
            self.create_oval(*box(68, 33, 80, 45), fill=ink, outline="")
            self.create_oval(*box(73, 35, 77, 39), fill="#FFFFFF", outline="")
            self.create_text(26 * s, 22 * s, text="♪", fill=t.OK, font=t.font(int(18 * s), "bold"))
        # tuft
        self.create_arc(*box(64, 4, 78, 22), start=60, extent=120, style="arc", outline=ink, width=3)
