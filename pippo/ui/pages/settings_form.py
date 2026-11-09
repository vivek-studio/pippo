"""Form building blocks for the Settings page."""
from __future__ import annotations

import customtkinter as ctk

from .. import theme as t
from ..widgets import entry, eyebrow, quiet_button, textbox

# Settings boxes that hold one message per line (stored in the config as a list)
LINE_LIST_KEYS = ("msg_tag_replies", "msg_greetings", "msg_non_working_replies")


class SettingsForm:
    """Remembers every input widget by its config key, and reads their values back."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.inputs: dict = {}

    def value(self, key: str) -> str:
        v = self.inputs[key]
        return v.get("1.0", "end").strip() if isinstance(v, ctk.CTkTextbox) else v.get()

    def set_value(self, key: str, text: str) -> None:
        self.inputs[key].set(text)


class FormSection(ctk.CTkFrame):
    """A titled card holding label / input rows."""

    def __init__(self, parent, form: SettingsForm, index: int, title: str, sub: str | None = None):
        super().__init__(parent, fg_color=t.SURFACE, corner_radius=t.RADIUS_CARD, border_width=1,
                         border_color=t.LINE)
        self.form = form
        self.pack(fill="x", pady=8, padx=2)
        eyebrow(self, f"{index:02d}", color=t.BUTTER_DEEP).pack(anchor="w", padx=24, pady=(18, 0))
        ctk.CTkLabel(self, text=title, font=t.font(19, "bold", serif=True), text_color=t.INK
                     ).pack(anchor="w", padx=24, pady=(0, 0))
        if sub:
            ctk.CTkLabel(self, text=sub, text_color=t.INK_SOFT, font=t.font(12), justify="left",
                         wraplength=760).pack(anchor="w", padx=24, pady=(2, 4))
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(fill="x", padx=24, pady=(8, 18))
        self.inner.grid_columnconfigure(1, weight=1)
        self.row = 0

    def place(self, widget, columnspan: int = 3, sticky: str = "ew", pady=0) -> None:
        """Put a free-form widget on its own row."""
        widget.grid(row=self.row, column=0, columnspan=columnspan, sticky=sticky, pady=pady)
        self.row += 1

    def field(self, label, key, hint=None, secret=False, browse=None, multiline=False):
        r = self.row
        inner, form = self.inner, self.form
        ctk.CTkLabel(inner, text=label, text_color=t.INK, anchor="w", width=190, font=t.font(13, "bold")
                     ).grid(row=r, column=0, sticky="nw", pady=8, padx=(0, 12))
        init = form.cfg.get(key, "")
        if isinstance(init, list):
            init = ("\n" if key in LINE_LIST_KEYS else ", ").join(init)
        if multiline:
            box = textbox(inner, height=88)
            box.insert("1.0", init)
            box.grid(row=r, column=1, sticky="ew", pady=6)
            form.inputs[key] = box
        else:
            var = form.inputs[key] = ctk.StringVar(value=init)
            e = entry(inner, textvariable=var, show="•" if secret else None)
            e.grid(row=r, column=1, sticky="ew", pady=6)
            if secret:
                sw = ctk.CTkSwitch(inner, text="show", width=60, progress_color=t.POND, text_color=t.MUTED)
                sw.configure(command=lambda en=e, w=sw: en.configure(show="" if w.get() else "•"))
                sw.grid(row=r, column=2, padx=(12, 0))
            if browse:
                quiet_button(inner, "Browse…", lambda v=var: browse(v), width=84, height=38
                             ).grid(row=r, column=2, padx=(12, 0))
        if hint:
            ctk.CTkLabel(inner, text=hint, text_color=t.MUTED, font=t.font(11), anchor="w",
                         justify="left", wraplength=640).grid(row=r + 1, column=1, sticky="w")
            self.row += 1
        self.row += 1
