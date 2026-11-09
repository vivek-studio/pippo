"""Pippo's look - "Pond & Butter".

Art direction: a calm, editorial desk for a very small duck.
  * warm paper background, hairline borders, generous space;
  * deep pond-ink sidebar with one butter-yellow accent (the only loud colour);
  * serif headlines (Georgia) over a clean sans (Segoe UI), small uppercase eyebrows for structure;
  * one soft pond-teal for "secondary", status colours kept quiet.
Every colour and font in the app comes from here - change a token, the whole app follows.
"""
from __future__ import annotations

import customtkinter as ctk

# ---- surfaces
PAPER = "#FAF6EC"        # window background (warm cream)
SURFACE = "#FFFFFF"      # cards
SURFACE_2 = "#F6F1E3"    # inputs, quiet fills
LINE = "#E8E1CF"         # hairlines
LINE_STRONG = "#D8CFB6"

# ---- ink
INK = "#1E2A32"          # sidebar + primary text
INK_2 = "#2C3B46"        # hover on ink
INK_SOFT = "#4C5B66"     # secondary text
MUTED = "#8A9298"        # captions
ON_INK = "#FBF6E8"       # text on the sidebar
ON_INK_MUTED = "#9FB0BA"

# ---- accents
BUTTER = "#FFC93C"
BUTTER_DEEP = "#F2B50F"
BUTTER_SOFT = "#FFF0BF"
POND = "#2F7F8F"
POND_DEEP = "#256876"
POND_SOFT = "#D9ECEE"

# ---- status
OK = "#2E9E6B"
WARN = "#D98200"
ERR = "#D6455A"
LAVENDER = "#8D83C9"     # "napping"

# ---- calendar
WEEKEND = "#ECE6D6"
HOLIDAY = "#FFD766"
HOLIDAY_HOVER = "#F5C84A"
WORKING_WEEKEND = POND_SOFT

# ---- shape
RADIUS_CARD = 18
RADIUS_CONTROL = 12
RADIUS_PILL = 14

FONT_SANS = "Segoe UI"
FONT_SERIF = "Georgia"
FONT_MONO = "Consolas"


def font(size: int = 13, weight: str = "normal", serif: bool = False, mono: bool = False) -> ctk.CTkFont:
    family = FONT_MONO if mono else FONT_SERIF if serif else FONT_SANS
    return ctk.CTkFont(family=family, size=size, weight=weight)


def apply_global_theme() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
