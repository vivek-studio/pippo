"""Runs Pippo's engine and carries its messages (from other threads) safely to the screen."""
from __future__ import annotations

import logging
import queue
import threading

from ..config.store import ConfigStore
from ..engine import PippoEngine
from . import events
from .events import EventBus

DRAIN_MS = 150


class _QueueLogHandler(logging.Handler):
    """Slack libraries' warnings end up in Pippo's diary too."""

    def __init__(self, q):
        super().__init__(level=logging.WARNING)
        self.q = q

    def emit(self, record):
        self.q.put(("log", "warn", f"[{record.name}] {record.getMessage()}"))


class EngineController:
    """The engine's callbacks run on worker threads; they only put messages on a queue.
    `drain()` (called from the Tk thread) turns those messages into bus events."""

    def __init__(self, cfg: dict, store: ConfigStore, bus: EventBus):
        self.cfg, self.store, self.bus = cfg, store, bus
        self.q: queue.Queue = queue.Queue()
        for name in ("slack_bolt", "slack_sdk"):
            logging.getLogger(name).addHandler(_QueueLogHandler(self.q))
        self.engine = PippoEngine(cfg, self._log_from_thread, self._save_from_thread)

    # ---- engine callbacks (any thread)
    def _log_from_thread(self, msg, level="info"):
        self.q.put(("log", level, msg))

    def _save_from_thread(self):
        self.store.save(self.cfg)
        self.q.put(("state", None, None))

    # ---- Tk thread
    def drain(self) -> None:
        try:
            while True:
                kind, a, b = self.q.get_nowait()
                if kind == "log":
                    self.bus.publish(events.LOG, b, a)
                elif kind == "status":
                    self.bus.publish(events.STATUS, a)
                elif kind == "state":
                    self.bus.publish(events.STATE)
        except queue.Empty:
            pass

    # ---- actions
    @property
    def running(self) -> bool:
        return self.engine.running

    def toggle(self) -> None:
        if self.engine.running:
            threading.Thread(target=self._stop_worker, daemon=True).start()
            return
        self.bus.publish(events.STATUS, "starting")

        def work():
            try:
                self.engine.start()
                self.q.put(("status", "online", None))
            except Exception as e:  # noqa
                self.q.put(("log", "err", f"Could not start: {e}"))
                self.q.put(("status", "offline", None))

        threading.Thread(target=work, daemon=True).start()

    def _stop_worker(self):
        self.engine.stop()
        self.q.put(("status", "offline", None))

    def shutdown(self) -> None:
        if self.engine.running:
            try:
                self.engine.stop()
            except Exception:
                pass
