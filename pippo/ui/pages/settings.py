"""Settings: everything Pippo needs lives here."""
from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk

from .. import events
from .. import theme as t
from ..widgets import accent_button, page_header
from .base import AppContext, Page
from .settings_form import LINE_LIST_KEYS, FormSection, SettingsForm
from .tag_users import TagUsersEditor

PLAIN_KEYS = ("bot_token", "app_token", "workspace_id", "workspace_domain", "source_channel_id",
              "target_channel_id", "client_name", "list_title_format", "template_json_path",
              "last_list_id", "previous_list_id")


class SettingsPage(Page):
    key, nav_label = "settings", "Settings"

    def __init__(self, parent, ctx: AppContext):
        super().__init__(parent, ctx)
        self.form = SettingsForm(ctx.cfg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        page_header(head, "Configure", "Settings", "Everything Pippo needs lives here. Press Save when done."
                    ).pack(side="left")
        accent_button(head, "Save", self.save, width=110).pack(side="right")
        self.save_note = ctk.CTkLabel(head, text="", text_color=t.OK, font=t.font(13, "bold"))
        self.save_note.pack(side="right", padx=16)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self._build_sections()

        # the engine saves list IDs by itself - keep the two boxes in step
        ctx.bus.subscribe(events.STATE, self.sync_list_ids)

    # ------------------------------------------------------------ layout
    def _build_sections(self):
        sc, cfg = self.scroll, self.ctx.cfg

        s = FormSection(sc, self.form, 1, "Slack connection",
                        "Leave blank to use the SLACK_BOT_TOKEN / SLACK_APP_TOKEN environment variables. "
                        "Tokens are stored as plain text in your user folder.")
        s.field("Bot token", "bot_token", "xoxb-…", secret=True)
        s.field("App token", "app_token", "xapp-… (Socket Mode)", secret=True)
        s.field("Workspace ID", "workspace_id", "Used to build list links (T…)")
        s.field("Workspace domain", "workspace_domain", "e.g. esga-india  →  esga-india.slack.com")

        s = FormSection(sc, self.form, 2, "Channels")
        s.field("Source channel ID", "source_channel_id", "Where the Daily Radio “Project Status” post lives")
        s.field("Target channel ID", "target_channel_id", "Where the list is shared and announced")
        s.field("Good Morning channels", "good_morning_channel_ids",
                "Comma-separated channel IDs. Leave empty to allow every channel Pippo is in.")

        s = FormSection(sc, self.form, 3, "List")
        s.field("Client name", "client_name", "Shown under the date in the announcement")
        s.field("List title", "list_title_format",
                "Placeholders: {month}  {year}  {date}  {client}.  Default gives “November - 2026”")
        s.field("Template JSON", "template_json_path",
                "Structure used to build the new list from scratch on the first working day. "
                "Blank = look next to the app.", browse=self._browse)
        s.field("Last list ID", "last_list_id",
                "Only needed on normal days if Pippo hasn't made a list yet. The first working day "
                "never needs it — Pippo builds a new list from scratch and saves its ID here.")
        s.field("Previous list ID", "previous_list_id",
                "The list before the current one. Handed Off projects take their due date from it. "
                "Pippo fills this in by itself whenever it creates a new list.")

        s = FormSection(sc, self.form, 4, "Who can Pippo tag?",
                        "Pippo only ever tags the people below, whenever someone tags @Pippo outside a Good "
                        "Morning. Anyone not on this list is never tagged.")
        self.tag_editor = TagUsersEditor(s, cfg, owner=self.winfo_toplevel())
        s.field("When @Pippo is tagged", "msg_tag_replies",
                "Sent in ANY channel, any day, whenever someone tags @Pippo in something that isn't a "
                "Good Morning. ONE reply per line; Pippo uses them in shuffled order, so nobody gets "
                "the same one twice in a row. Placeholders: {mentions}  <@{user}>. "
                "Empty = Pippo's built-in replies.", multiline=True)

        s = FormSection(sc, self.form, 5, "Messages",
                        "Placeholders: {user}  {date}  {client}  {url}  {reason}   (<!channel> = @channel)")
        s.field("Good Morning greeting", "msg_greetings", multiline=True,
                hint="First line of the post in the target channel. ONE greeting per line; Pippo uses them "
                     "in shuffled order, never the same one twice in a row. Placeholder: <@{user}>. "
                     "Empty = built-in greetings.")
        s.field("List post (under the greeting)", "msg_announcement_body", multiline=True,
                hint="Always the same: @channel, date, client, list link.")
        s.field("Non-working day replies", "msg_non_working_replies", multiline=True,
                hint="ONE reply per line, used in shuffled order. Placeholders: <@{user}>  {date}  {reason}. "
                     "Empty = built-in replies.")

    @staticmethod
    def _browse(var):
        p = filedialog.askopenfilename(title="Choose template JSON",
                                       filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if p:
            var.set(p)

    def sync_list_ids(self):
        for k in ("last_list_id", "previous_list_id"):
            self.form.set_value(k, self.ctx.cfg.get(k, ""))

    # ------------------------------------------------------------ save
    def save(self):
        cfg, form = self.ctx.cfg, self.form
        for key in PLAIN_KEYS:
            cfg[key] = form.value(key).strip()
        cfg["msg_announcement_body"] = form.value("msg_announcement_body")
        cfg["workspace_domain"] = cfg["workspace_domain"].replace(".slack.com", "").strip()
        for key in LINE_LIST_KEYS:
            cfg[key] = [l.strip() for l in form.value(key).splitlines() if l.strip()]
        cfg["good_morning_channel_ids"] = [
            c.strip() for c in form.value("good_morning_channel_ids").replace("\n", ",").split(",") if c.strip()]
        cfg["tag_users"] = [dict(u) for u in self.tag_editor.users]

        warn = []
        if cfg["bot_token"] and not cfg["bot_token"].startswith("xoxb-"):
            warn.append("Bot token should start with xoxb-")
        if cfg["app_token"] and not cfg["app_token"].startswith("xapp-"):
            warn.append("App token should start with xapp-")
        self.ctx.store.save(cfg)
        self.ctx.bus.publish(events.SETTINGS_SAVED)
        msg = "✓ Saved"
        if self.ctx.controller.running:
            msg += "  (restart Pippo to apply token changes)"
        self.save_note.configure(text=msg, text_color=t.OK)
        self.after(4000, lambda: self.save_note.configure(text=""))
        if warn:
            messagebox.showwarning("Pippo", "Saved, but:\n• " + "\n• ".join(warn))
