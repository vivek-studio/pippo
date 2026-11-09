"""Small reusable building blocks, all styled from theme.py."""
from __future__ import annotations

import customtkinter as ctk

from . import theme as t


def card(parent, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=t.SURFACE, corner_radius=t.RADIUS_CARD, border_width=1,
                        border_color=t.LINE, **kw)


def eyebrow(parent, text: str, color: str = t.MUTED, **kw) -> ctk.CTkLabel:
    """Small uppercase label used to give every block a quiet name."""
    return ctk.CTkLabel(parent, text=text.upper(), text_color=color, font=t.font(11, "bold"), **kw)


def page_header(parent, eyebrow_text: str, title: str, subtitle: str | None = None) -> ctk.CTkFrame:
    box = ctk.CTkFrame(parent, fg_color="transparent")
    eyebrow(box, eyebrow_text, color=t.POND).pack(anchor="w")
    ctk.CTkLabel(box, text=title, font=t.font(32, "bold", serif=True), text_color=t.INK
                 ).pack(anchor="w", pady=(2, 0))
    if subtitle:
        ctk.CTkLabel(box, text=subtitle, text_color=t.INK_SOFT, font=t.font(13), justify="left",
                     wraplength=720).pack(anchor="w", pady=(4, 0))
    return box


def primary_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    opts = dict(height=42, corner_radius=t.RADIUS_CONTROL, fg_color=t.INK, hover_color=t.INK_2,
                text_color=t.ON_INK, font=t.font(13, "bold"))
    opts.update(kw)
    return ctk.CTkButton(parent, text=text, command=command, **opts)


def accent_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    opts = dict(height=42, corner_radius=t.RADIUS_CONTROL, fg_color=t.BUTTER, hover_color=t.BUTTER_DEEP,
                text_color=t.INK, font=t.font(13, "bold"))
    opts.update(kw)
    return ctk.CTkButton(parent, text=text, command=command, **opts)


def quiet_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    opts = dict(height=34, corner_radius=t.RADIUS_CONTROL, fg_color=t.SURFACE_2, hover_color=t.LINE,
                text_color=t.INK, font=t.font(12, "bold"), border_width=1, border_color=t.LINE)
    opts.update(kw)
    return ctk.CTkButton(parent, text=text, command=command, **opts)


def pill(parent, text: str, fg: str, text_color: str = "#FFFFFF", **kw) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=f"  {text}  ", fg_color=fg, text_color=text_color,
                        corner_radius=t.RADIUS_PILL, font=t.font(12, "bold"), height=26, **kw)


def entry(parent, **kw) -> ctk.CTkEntry:
    opts = dict(height=38, fg_color=t.SURFACE_2, border_width=1, border_color=t.LINE,
                corner_radius=t.RADIUS_CONTROL, text_color=t.INK)
    opts.update(kw)
    return ctk.CTkEntry(parent, **opts)


def textbox(parent, **kw) -> ctk.CTkTextbox:
    opts = dict(fg_color=t.SURFACE_2, border_width=1, border_color=t.LINE, corner_radius=t.RADIUS_CONTROL,
                text_color=t.INK, wrap="word")
    opts.update(kw)
    return ctk.CTkTextbox(parent, **opts)


def hairline(parent, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, height=1, fg_color=t.LINE, corner_radius=0, **kw)
