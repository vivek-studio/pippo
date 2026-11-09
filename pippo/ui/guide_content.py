"""The in-app guide, as data. Add a topic here and it shows up in the Guide page - no UI code to touch."""
from __future__ import annotations

from dataclasses import dataclass, field


# ---- block types ------------------------------------------------------------------------------
@dataclass
class P:
    text: str


@dataclass
class H:
    text: str


@dataclass
class Steps:
    items: list[str]


@dataclass
class Bullets:
    items: list[str]


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]
    widths: list[int] = field(default_factory=list)


@dataclass
class Tip:
    text: str


@dataclass
class Warn:
    text: str


@dataclass
class Code:
    text: str


@dataclass
class Topic:
    key: str
    title: str
    summary: str
    blocks: list


TOPICS: list[Topic] = [
    Topic("meet", "Meet Pippo", "What Pippo is and what it does for you.", [
        P("Pippo is a tiny Slack helper that keeps your monthly project list tidy. It lives in this app, "
          "connects to Slack, and waits for someone to say hello."),
        H("The two things Pippo does"),
        Bullets([
            "Someone writes “@Pippo good morning” → Pippo reads the latest Daily Radio (“Project Status”) post, "
            "builds or updates this month's Slack List, and announces it in the target channel.",
            "Someone tags @Pippo in anything else → Pippo tags the team you chose in Settings.",
        ]),
        Tip("Pippo only answers while this app is open and Pippo is awake (Home → Wake Pippo up). "
            "If the app is closed or Pippo is napping, Slack messages are simply not seen."),
    ]),
    Topic("start", "Quick start", "From zero to the first Good Morning.", [
        Steps([
            "Settings → Slack connection: paste the Bot token (xoxb-…) and the App token (xapp-…).",
            "Settings → Channels: set the Source channel ID (where the Daily Radio is posted) and the "
            "Target channel ID (where the list is shared and announced).",
            "Settings → List: check the client name and list title. The list template is found automatically.",
            "Settings → Who can Pippo tag: pick the people Pippo may tag.",
            "Calendar: mark your holidays (and any working weekends).",
            "Press Save, go Home and press “Wake Pippo up”. The diary should say Pippo is awake.",
            "In Slack, write “@Pippo good morning” in an allowed channel.",
        ]),
        Tip("On the first working day of a month Pippo needs no old list ID - it builds a brand-new list. "
            "On every other day it continues the month's list, so Last list ID must be known "
            "(Pippo saves it by itself after it creates a list)."),
    ]),
    Topic("day", "A day with Pippo", "Exactly what happens after “good morning”.", [
        Steps([
            "Pippo takes today's date from the time of your Slack message (not from the computer clock).",
            "Not a working day (weekend or holiday)? Pippo replies that it's a non-working day and stops.",
            "Pippo reads the latest “Project Status” post from the last 50 messages of the source channel. "
            "No post, or nothing parseable? It tells you and stops.",
            "First working day of the month → a NEW list is created from scratch. "
            "Any other working day → the month's list is updated.",
            "Restructuring runs (a placeholder for future rules).",
            "A new list is shared with the target channel. The announcement is posted there.",
            "Heads-ups are posted if something needs a human (see Troubleshooting).",
            "Pippo remembers the list IDs.",
        ]),
        H("Good to know"),
        Bullets([
            "Saying good morning twice on the first working day does not create a second list - Pippo re-uses today's.",
            "Only one Good Morning runs at a time; a second one while one is running is ignored.",
            "The same Slack message is never handled twice.",
            "Replies go to the channel where you greeted Pippo (inside the thread, if you wrote in a thread).",
            "Good Morning only works in the channels listed in Settings → Good Morning channels "
            "(empty = every channel Pippo is in).",
        ]),
    ]),
    Topic("list", "The monthly list", "Columns, statuses, stars and sorting.", [
        P("One list per month, titled like “November - 2026”. A new list gets these columns, in this order "
          "(any extra template column follows):"),
        Table(["Column", "Filled by Pippo"], [
            ["Project Name", "From the radio"],
            ["Round", "From the radio (empty on Handed Off rows)"],
            ["Due Today", "Stars: 2 = due today + AM HO, 1 = due today"],
            ["Due Date", "From the radio (Handed Off: from the previous list)"],
            ["Assignee", "Left for people; cleared every normal day"],
            ["Status", "Not Started or Handed Off"],
            ["Currently Working", "Left for people; cleared every normal day"],
            ["No. of Assets", "From the radio “(N assets)”"],
            ["Design Lead / Functional Lead / Copy Leads", "Left for people; cleared every normal day"],
            ["Sort Order", "Helper number the saved view sorts by"],
        ], widths=[230, 330]),
        H("Status"),
        Bullets([
            "Not Started: the project is in today's radio under DUE TODAY, PROJECTS KICKING OFF or IN PIPELINE.",
            "Handed Off: everything else - FEEDBACK AWAITED, and any row that is no longer in the radio.",
            "Handed Off rows have no round, and their due date is the one the project had in the PREVIOUS list "
            "(empty if it wasn't there; untouched if that list can't be read).",
        ]),
        H("Sorting"),
        P("Order: due today with AM HO, then due today, then everything else by date (no date last). "
          "Handed Off rows always sit at the bottom (Sort Order 999). Ties keep the radio's order."),
        Tip("Slack lists can't be re-ordered by Pippo directly. Save a view sorted by “Sort Order”, ascending, "
            "and the order follows. If the column is missing Pippo tells you."),
        H("Normal working days, in short"),
        Bullets([
            "Rows are matched to radio entries by project name only.",
            "Name, round, due date and asset count are taken from today's radio. An empty radio value never "
            "wipes an old cell (no round / no “due on” date / no asset count → the old cell stays).",
            "Radio projects not yet in the list are added as new rows.",
            "A project on two or more rows is flagged in Slack - it should never happen. "
            "The row with the same round (then the earlier date) is the one updated.",
            "A project twice in the radio: the entry due earlier wins.",
        ]),
    ]),
    Topic("radio", "The Daily Radio", "What Pippo can read from the Project Status post.", [
        P("Pippo looks for the newest message containing “Project Status” (any capitals) among the last 50 "
          "messages of the source channel."),
        Code("Project Status - 5 November, 2026\n"
             "DUE TODAY\n"
             "1. Alpha - RD2 (AM HO) (10 assets)\n"
             "PROJECTS KICKING OFF\n"
             "1. Charlie - KO due on 11/09 (3 assets)\n"
             "IN PIPELINE\n"
             "1. Delta - RD3 due on 11/20\n"
             "FEEDBACK AWAITED\n"
             "1. Foxtrot - awaited by 11/06 due on 11/08"),
        Bullets([
            "The header date looks like “5 November, 2026”. Its year is used for every date in the post.",
            "Sections: DUE TODAY, PROJECTS KICKING OFF, IN PIPELINE, FEEDBACK AWAITED (asterisks are ignored).",
            "Lines are numbered “1.” or “1)”, then “Project - Round due on MM/DD”.",
            "Rounds understood: RD1, RD2a …, KO, SKU Swaps, Additional Revisions.",
            "“(AM HO)” marks an AM handoff; “(N assets)” gives the asset count.",
            "DUE TODAY projects always take the post's header date.",
            "FEEDBACK AWAITED lines use only the “due on/by” date - never the “awaited by” date.",
            "Projects named NA, N/A, none or - are skipped.",
        ]),
    ]),
    Topic("calendar", "Calendar", "Holidays, weekends and the new-list day.", [
        Bullets([
            "Saturdays and Sundays rest by default.",
            "Click a weekday to mark it as a holiday (you can name it). Click again to remove it.",
            "Click a Saturday or Sunday to mark it as a working day. Click again to remove it.",
            "The ★ marks the first working day of the month - the day Pippo creates a new list.",
            "Home shows today's plan and the next new-list day.",
        ]),
        P("On a non-working day Pippo answers “good morning” with a sleepy reply and does nothing else."),
    ]),
    Topic("tag", "Tagging the team", "What happens when someone tags @Pippo.", [
        Bullets([
            "Any message that tags @Pippo and isn't a good morning gets a reply in its thread, "
            "mentioning everyone in Settings → Who can Pippo tag.",
            "It works in any channel Pippo is in, on any day.",
            "Replies come from your list, in shuffled order - none repeats until all were used.",
            "Nobody on the list? Pippo says so instead of tagging anyone.",
            "Pippo only ever tags the people on that list.",
        ]),
    ]),
    Topic("messages", "Messages", "Make Pippo sound like you.", [
        P("Boxes that take several messages use ONE message per line. Empty box = Pippo's built-in messages. "
          "Unknown placeholders stay exactly as typed."),
        Table(["Message", "Placeholders"], [
            ["Good Morning greeting", "{user} {date} {client} {url} {month} {year}"],
            ["List post (under the greeting)", "{user} {date} {client} {url} {month} {year}   <!channel> = @channel"],
            ["Non-working day replies", "{user} {date} {reason}"],
            ["When @Pippo is tagged", "{mentions} {user}"],
            ["List title", "{month} {year} {date} {client}"],
        ], widths=[230, 330]),
        Tip("Write <@{user}> to mention the person who greeted Pippo."),
    ]),
    Topic("settings", "Settings reference", "Every field, in one place.", [
        Table(["Field", "What it does"], [
            ["Bot token / App token", "Slack credentials. Blank = SLACK_BOT_TOKEN / SLACK_APP_TOKEN environment variables."],
            ["Workspace ID / domain", "Used to build the list link."],
            ["Source channel ID", "Where the Daily Radio is posted."],
            ["Target channel ID", "Where the list is shared and announced."],
            ["Good Morning channels", "Comma-separated IDs where good morning works. Empty = all."],
            ["Client name", "Shown in the announcement."],
            ["List title", "Name pattern of each month's list."],
            ["Template JSON", "Columns of new lists. Blank = found automatically."],
            ["Last list ID", "The list in use. Pippo updates it itself."],
            ["Previous list ID", "The list before it (Handed Off dates). Pippo fills it in."],
            ["Who can Pippo tag", "The people Pippo may tag."],
            ["Messages", "Greetings, list post, non-working replies, tag replies."],
        ], widths=[200, 360]),
        Warn("Tokens are stored as plain text in your user folder. Don't share config.json."),
    ]),
    Topic("slack", "Slack setup", "What the Slack app needs.", [
        Steps([
            "Create a Slack app and install it to your workspace.",
            "Turn on Socket Mode and create an App-level token (xapp-…).",
            "Subscribe to the bot events app_mention and message.channels "
            "(message.groups too if channels are private).",
            "Give the bot scopes for reading history, posting and Lists - typically app_mentions:read, "
            "chat:write, channels:history, lists:read and lists:write.",
            "Copy the Bot token (xoxb-…) and invite Pippo to the source and target channels.",
        ]),
        Tip("Scope names can change - if something fails, Pippo's diary shows Slack's own error name."),
    ]),
    Topic("trouble", "Troubleshooting", "What Pippo's messages mean.", [
        Table(["Pippo says…", "What to do"], [
            ["I don't know which list to use yet", "Put the current list's ID in Settings → Last list ID."],
            ["I couldn't read the source channel", "Check the Source channel ID and that Pippo is in the channel."],
            ["I couldn't find a recent Project Status message", "Post the Daily Radio first, or check the channel."],
            ["…couldn't parse any projects", "Check the post matches the Daily Radio format."],
            ["I can't find a number column called Sort Order", "Add it (type Number) and save a view sorted by it."],
            ["Tiny hiccup… last month's list", "Set Previous list ID, and check Pippo can open that list."],
            ["…more than one row", "Delete the extra rows of the named projects."],
            ["Slack returned an error", "Open the diary on Home for Slack's error name."],
        ], widths=[250, 310]),
        H("Warnings in the diary"),
        Bullets([
            "“Round / Status isn't an option in the list” - add that choice to the column.",
            "“The latest Daily Radio is dated …, not today” - the radio post is old; Pippo still used it.",
        ]),
    ]),
    Topic("files", "Files & the .exe", "Where things live and how to package Pippo.", [
        Bullets([
            "Settings are saved in config.json: %APPDATA%\\Pippo on Windows, ~/.pippo elsewhere. "
            "Set PIPPO_HOME to choose another folder.",
            "The list template and the team list ship with Pippo (data/ folder). A newer copy dropped in "
            "Pippo's settings folder is used instead.",
            "To build Pippo.exe, run build_exe.bat. The result is dist\\Pippo.exe.",
        ]),
        H("Testing safely"),
        Warn("Writing “good morning force new” makes Pippo act as if today were the first working day: it creates a "
             "REAL new list and announces it. Use it in a test workspace."),
    ]),
]
