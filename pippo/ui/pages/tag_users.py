"""Who may Pippo tag? - the chips, the manual "add" row and the team picker."""
from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ...infra.resources import load_user_map
from .. import theme as t
from ..widgets import accent_button, entry, quiet_button
from .settings_form import FormSection


class TagUsersEditor:
    """Edits a copy of cfg['tag_users']; the Settings page reads `.users` when saving."""

    def __init__(self, section: FormSection, cfg: dict, owner):
        self.owner = owner                     # the window the picker should sit on top of
        self.users = [dict(u) for u in cfg.get("tag_users", [])]

        self.frame = ctk.CTkFrame(section.inner, fg_color="transparent")
        section.place(self.frame)

        add = ctk.CTkFrame(section.inner, fg_color="transparent")
        section.place(add, sticky="w", pady=6)
        self.new_uid = entry(add, placeholder_text="Slack user ID (U…)", width=170)
        self.new_uid.pack(side="left")
        self.new_uname = entry(add, placeholder_text="Name (optional)", width=150)
        self.new_uname.pack(side="left", padx=6)
        quiet_button(add, "Add", self.add, width=60, height=38).pack(side="left")
        accent_button(add, "Pick from team…", self.open_picker, width=150, height=38).pack(side="left", padx=(14, 0))
        self.render()

    # ---- chips
    def render(self):
        for w in self.frame.winfo_children():
            w.destroy()
        if not self.users:
            ctk.CTkLabel(self.frame, text="Nobody yet — Pippo won't tag anyone.", text_color=t.MUTED
                         ).pack(anchor="w", pady=4)
        wrap = ctk.CTkFrame(self.frame, fg_color="transparent")
        wrap.pack(fill="x")
        for i, u in enumerate(self.users):
            chip = ctk.CTkFrame(wrap, fg_color=t.BUTTER_SOFT, corner_radius=16, border_width=1,
                                border_color=t.BUTTER)
            chip.grid(row=i // 3, column=i % 3, padx=(0, 8), pady=3, sticky="w")
            ctk.CTkLabel(chip, text=f"@{u.get('name') or u['id']}", text_color=t.INK, font=t.font(12, "bold")
                         ).pack(side="left", padx=(12, 2), pady=4)
            ctk.CTkButton(chip, text="✕", width=22, height=22, fg_color="transparent",
                          hover_color=t.BUTTER, text_color=t.INK_SOFT,
                          command=lambda idx=i: self.remove(idx)).pack(side="left", padx=(0, 6))

    def add(self):
        uid = self.new_uid.get().strip().upper()
        if not uid.startswith(("U", "W")) or len(uid) < 6:
            messagebox.showwarning("Pippo", "That doesn't look like a Slack user ID (e.g. U01ABC23DE).")
            return
        if not any(u["id"] == uid for u in self.users):
            self.users.append({"id": uid, "name": self.new_uname.get().strip()})
        self.new_uid.delete(0, "end")
        self.new_uname.delete(0, "end")
        self.render()

    def remove(self, idx):
        self.users.pop(idx)
        self.render()

    def open_picker(self):
        TagPicker(self.owner, load_user_map(), self.users, on_done=self.render)


class TagPicker(ctk.CTkToplevel):
    """Tick the people Pippo may tag. Changes `users` in place, then calls on_done."""

    def __init__(self, owner, people: list[dict], users: list[dict], on_done):
        super().__init__(owner)
        self.people, self.users, self.on_done = people, users, on_done
        self.title("Pick people Pippo may tag")
        self.geometry("440x620")
        self.configure(fg_color=t.PAPER)
        self.transient(owner)
        if not people:
            ctk.CTkLabel(self, text="Couldn't find slack_user_map.json.\nYou can still add IDs by hand.",
                         text_color=t.ERR).pack(pady=40)
            return

        ctk.CTkLabel(self, text="Who may Pippo tag?", font=t.font(22, "bold", serif=True), text_color=t.INK
                     ).pack(pady=(20, 2))
        self.search = entry(self, placeholder_text="Search name…")
        self.search.pack(fill="x", padx=18, pady=(8, 6))
        self.show_apps = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self, text="show apps & bots too", variable=self.show_apps, progress_color=t.POND,
                      text_color=t.MUTED, command=self.render).pack(anchor="w", padx=20, pady=(0, 6))
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=t.SURFACE)
        self.list_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.checks: dict = {}
        self.chosen0 = {u["id"] for u in users}
        accent_button(self, "Use selected", self.done, height=42).pack(pady=(0, 16))
        self.search.bind("<KeyRelease>", self.render)
        self.render()

    def render(self, *_):
        for w in self.list_frame.winfo_children():
            w.destroy()
        term = self.search.get().strip().lower()
        for u in self.people:
            if u["app"] and not self.show_apps.get() and u["id"] not in self.chosen0:
                continue
            if term and term not in u["name"].lower():
                continue
            var = self.checks.setdefault(u["id"], ctk.BooleanVar(value=u["id"] in self.chosen0))
            ctk.CTkCheckBox(self.list_frame, text=u["name"] + ("  (app)" if u["app"] else ""), variable=var,
                            fg_color=t.POND, hover_color=t.POND_DEEP, text_color=t.INK
                            ).pack(anchor="w", padx=10, pady=4)

    def done(self):
        by_id = {u["id"]: u for u in self.people}
        for uid, var in self.checks.items():
            have = next((i for i, u in enumerate(self.users) if u["id"] == uid), None)
            if var.get() and have is None:
                self.users.append({"id": uid, "name": by_id[uid]["name"]})
            elif not var.get() and have is not None:
                self.users.pop(have)
        self.on_done()
        self.destroy()
