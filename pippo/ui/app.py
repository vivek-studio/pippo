"""The window: a dark sidebar, and one page at a time."""
from __future__ import annotations


import customtkinter as ctk

from .. import APP_NAME, __version__
from ..config.store import ConfigStore
from . import events
from . import theme as t
from .controller import DRAIN_MS, EngineController
from .duck import DuckCanvas
from .events import EventBus
from .pages.base import AppContext, Page
from .pages.calendar_page import CalendarPage
from .pages.guide import GuidePage
from .pages.home import HomePage
from .pages.settings import SettingsPage

# Add a page here and it appears in the sidebar.
PAGES: list[type[Page]] = [HomePage, CalendarPage, SettingsPage, GuidePage]

SIDEBAR_WIDTH = 236
TICK_MS = 60_000


class PippoApp(ctk.CTk):
    def __init__(self):
        t.apply_global_theme()
        super().__init__()
        self.title("Pippo 🐾")
        self.geometry("1200x780")
        self.minsize(1080, 700)
        self.configure(fg_color=t.PAPER)

        store = ConfigStore()
        cfg = store.load()
        bus = EventBus()
        controller = EngineController(cfg, store, bus)
        self.ctx = AppContext(cfg=cfg, store=store, controller=controller, bus=bus)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.nav: dict[str, ctk.CTkButton] = {}
        self.pages: dict[str, Page] = {}
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=32, pady=26)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        for page_cls in PAGES:
            page = page_cls(self.content, self.ctx)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[page.key] = page
            self._add_nav_button(page)

        bus.subscribe(events.STATUS, self._on_status)
        self.show_page(PAGES[0].key)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(DRAIN_MS, self._drain)
        self.after(TICK_MS, self._tick)

    # ------------------------------------------------------------ sidebar
    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0, fg_color=t.INK)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        self.side = side

        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.pack(anchor="w", padx=24, pady=(28, 28))
        mark = ctk.CTkFrame(brand, fg_color=t.BUTTER_SOFT, corner_radius=22, width=56, height=56)
        mark.pack(side="left")
        mark.pack_propagate(False)
        DuckCanvas(mark, size=46, bg=t.BUTTER_SOFT, mood="awake").pack(expand=True)
        text = ctk.CTkFrame(brand, fg_color="transparent")
        text.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(text, text=APP_NAME, font=t.font(26, "bold", serif=True), text_color=t.ON_INK).pack(anchor="w")
        ctk.CTkLabel(text, text="your tiny list helper", font=t.font(11), text_color=t.ON_INK_MUTED).pack(anchor="w")

        self.nav_holder = ctk.CTkFrame(side, fg_color="transparent")
        self.nav_holder.pack(fill="x", padx=14)

        foot = ctk.CTkFrame(side, fg_color="transparent")
        foot.pack(side="bottom", fill="x", padx=24, pady=22)
        self.dot = ctk.CTkLabel(foot, text="●", text_color=t.LAVENDER, font=t.font(12))
        self.dot.pack(side="left")
        self.state_lbl = ctk.CTkLabel(foot, text="Napping", text_color=t.ON_INK_MUTED, font=t.font(12, "bold"))
        self.state_lbl.pack(side="left", padx=(6, 0))
        ctk.CTkLabel(foot, text=f"v{__version__}", text_color=t.ON_INK_MUTED, font=t.font(11)).pack(side="right")

    def _add_nav_button(self, page: Page):
        n = len(self.nav) + 1
        b = ctk.CTkButton(self.nav_holder, text=f"{n:02d}    {page.nav_label}", anchor="w", height=44,
                          corner_radius=12, fg_color="transparent", hover_color=t.INK_2, text_color=t.ON_INK,
                          font=t.font(14, "bold"), command=lambda k=page.key: self.show_page(k))
        b.pack(fill="x", pady=2)
        self.nav[page.key] = b

    def _on_status(self, state):
        color, label = {"online": (t.OK, "Awake"), "starting": (t.WARN, "Waking up")}.get(
            state, (t.LAVENDER, "Napping"))
        self.dot.configure(text_color=color)
        self.state_lbl.configure(text=label)

    # ------------------------------------------------------------ pages
    def show_page(self, key: str):
        for k, page in self.pages.items():
            if k == key:
                page.grid()
            else:
                page.grid_remove()
        for k, b in self.nav.items():
            on = k == key
            b.configure(fg_color=t.BUTTER if on else "transparent",
                        text_color=t.INK if on else t.ON_INK,
                        hover_color=t.BUTTER_DEEP if on else t.INK_2)
        self.pages[key].on_show()

    # ------------------------------------------------------------ plumbing
    def _drain(self):
        self.ctx.controller.drain()
        self.after(DRAIN_MS, self._drain)

    def _tick(self):
        self.ctx.bus.publish(events.TICK)
        self.after(TICK_MS, self._tick)

    def _on_close(self):
        self.ctx.controller.shutdown()
        self.destroy()
