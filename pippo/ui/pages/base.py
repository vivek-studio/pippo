"""What every page of the app looks like from the outside."""
from __future__ import annotations

from dataclasses import dataclass

import customtkinter as ctk

from ...config.store import ConfigStore
from ..controller import EngineController
from ..events import EventBus


@dataclass
class AppContext:
    """Everything a page may need - handed in, never reached for (dependency injection)."""
    cfg: dict
    store: ConfigStore
    controller: EngineController
    bus: EventBus


class Page(ctk.CTkFrame):
    """Subclass, set `key` / `nav_label`, build your widgets in __init__, override on_show if needed.
    Then add the class to PAGES in ui/app.py - the sidebar picks it up by itself."""
    key: str = ""
    nav_label: str = ""

    def __init__(self, parent, ctx: AppContext):
        super().__init__(parent, fg_color="transparent")
        self.ctx = ctx

    def on_show(self) -> None:
        """Called every time the page becomes visible."""
