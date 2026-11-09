"""PippoEngine - the object the GUI talks to. It wires the parts together and runs the Slack connection.

    cfg  : the live config dict (shared with the GUI, so edits apply instantly)
    log  : callable(message, level)  level in {"info", "ok", "warn", "err"}
    save : callable() persisting cfg after the engine changes it
"""
from __future__ import annotations

import os
import threading

from slack_sdk import WebClient

from .core.rows import RowCellPlanner
from .infra.slack_gateway import SlackGateway
from .messaging.picker import MessagePicker
from .router import EventRouter
from .workflows.announce import Announcer
from .workflows.daily_update import DailyUpdateStrategy
from .workflows.good_morning import GoodMorningWorkflow
from .workflows.new_list import NewListStrategy
from .workflows.previous_list import PreviousListReader
from .workflows.restructure import NoopRestructurer
from .workflows.row_writer import RowWriter
from .workflows.tagging import TagResponder


class PippoEngine:
    def __init__(self, cfg: dict, log, save):
        self.cfg = cfg
        self.log = log
        self.save = save
        self.client: WebClient | None = None
        self.app = None
        self.handler = None
        self.bot_user_id = None
        self.running = False
        self._run_lock = threading.Lock()
        self._picker = MessagePicker(cfg)
        self._good_morning: GoodMorningWorkflow | None = None
        self._tagger: TagResponder | None = None
        self.router = EventRouter(cfg, log, self.run_good_morning, self.tag_everybody)

    # ---------- wiring
    def attach(self, client, bot_user_id) -> None:
        """Connect the engine to a Slack client (start() does this; tests can hand in a fake)."""
        self.client, self.bot_user_id = client, bot_user_id
        self.router.bot_user_id = bot_user_id
        gateway = SlackGateway(client, self.log)
        planner = RowCellPlanner(self.log)
        rows = RowWriter(gateway, planner, self.log)
        self._tagger = TagResponder(self.cfg, gateway, self._picker, self.log)
        self._good_morning = GoodMorningWorkflow(
            self.cfg, gateway, self._picker, self.log, self.save,
            new_list=NewListStrategy(self.cfg, gateway, rows, self.log),
            daily=DailyUpdateStrategy(gateway, planner, rows, self.log),
            previous=PreviousListReader(gateway, self.log),
            restructurer=NoopRestructurer(self.log),
            announcer=Announcer(self.cfg, gateway, self._picker))

    # ---------- lifecycle
    def start(self):
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler

        bot = self.cfg["bot_token"].strip() or os.environ.get("SLACK_BOT_TOKEN", "")
        app_tok = self.cfg["app_token"].strip() or os.environ.get("SLACK_APP_TOKEN", "")
        if not bot or not app_tok:
            raise RuntimeError("Bot token and App token are required (Settings → Slack).")

        client = WebClient(token=bot)
        auth = client.auth_test()
        self.attach(client, auth["user_id"])
        self.log(f"Authenticated as {auth.get('user')} ({self.bot_user_id})", "ok")

        self.app = App(client=self.client)
        self.app.event("app_mention")(self.router.on_mention)
        self.app.event("message")(self.router.on_message)

        self.handler = SocketModeHandler(self.app, app_tok)
        self.handler.connect()
        self.running = True
        self.log("Pippo is awake and listening 🐾", "ok")

    def stop(self):
        try:
            if self.handler:
                self.handler.close()
        except Exception as e:  # noqa
            self.log(f"Error while stopping: {e}", "warn")
        self.running = False
        self.handler = None
        self.log("Pippo is napping now 😴", "warn")

    # ---------- work
    def run_good_morning(self, event):
        """One Good Morning at a time; a second one while one is running is ignored."""
        if not self._run_lock.acquire(blocking=False):
            self.log("Another Good Morning run is in progress, ignoring.", "warn")
            return
        try:
            self._good_morning.run(event)
        except Exception as e:  # noqa
            self.log(f"Unexpected error in Good Morning: {e}", "err")
        finally:
            self._run_lock.release()

    def tag_everybody(self, event):
        self._tagger.respond(event)
