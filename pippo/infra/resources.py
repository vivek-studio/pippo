"""Files shipped with Pippo (the list template and the team list) - from source AND from the .exe."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from ..config.store import app_dir

TEMPLATE_NAME = "November_-_2026.json"
USER_MAP_NAME = "slack_user_map.json"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Integrations / bots / workflows in the workspace - hidden in the picker unless "show apps" is on.
APP_IDS = {
    "USLACKBOT", "U01F9MA8D5W", "U02BBJHBP5K", "U03P4QL5X4J", "U04FTBLSNKV", "U05BDV4KBHN",
    "U05Q60B5ANP", "U0705B54679", "U0798SLUR4N", "U079FCJ6WRZ", "U07R1DQLF2B", "U086F7BFMPX",
    "U08L7JNMA2C", "U08P1UHMYLX", "U093Q35B012", "U09AV5YQEPR", "U09B6TY3V3L", "U09JUTVMSP7",
    "U09M85YMEN9", "U09MQGQQG65", "U0AA1833R5L", "U0ABSG2Q5PT", "U0ABU22ADFW", "U0AFTGGCJ7K",
    "U0AGY0YCUK0", "U0AQ4507AN4", "U0AQBJU1ER3", "U0AQF1WE52N", "U0B08G88YH4", "U0B0T7RTB9T",
    "U0B7B5BMZSS", "U0BRCFDNVST", "U0BRTFX9YD7", "U0BT3N33F9Q", "U0C1GHXKZFX", "U0C289Q0ZBQ",
    "U0C6XJCDB0D", "U0C7TT74ZEV",
}


def find_bundled(name: str, override: str = "") -> Path | None:
    """Find a file shipped with Pippo. Looked up, in order:
    your override path, Pippo's folder, inside the .exe, next to the program, the project folder,
    and finally the same places' data/ sub-folder."""
    flat_dirs = []
    if getattr(sys, "_MEIPASS", None):
        flat_dirs.append(Path(sys._MEIPASS))                         # baked into the .exe
    flat_dirs.append(Path(os.path.abspath(sys.argv[0])).parent)      # next to the program
    flat_dirs.append(PROJECT_ROOT)

    cands = []
    if override:
        cands.append(Path(override))
    cands.append(app_dir() / name)                                   # user can drop a newer copy here
    cands += [d / name for d in flat_dirs]
    cands += [d / "data" / name for d in flat_dirs]
    for p in cands:
        if p.is_file():
            return p
    return None


def resolve_template_path(cfg: dict) -> Path | None:
    return find_bundled(TEMPLATE_NAME, cfg.get("template_json_path") or "")


def load_user_map() -> list[dict]:
    """[{id, name, app}] for every active member, people first (A-Z), apps after."""
    p = find_bundled(USER_MAP_NAME)
    if not p:
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    out = [{"id": uid, "name": name, "app": uid in APP_IDS}
           for uid, name in raw.items() if name != "Deactivated User" and uid != "USLACKBOT"]
    return sorted(out, key=lambda u: (u["app"], u["name"].lower()))


def load_template(cfg: dict) -> dict:
    """The list template as a dict (raises FileNotFoundError when it can't be found)."""
    p = resolve_template_path(cfg)
    if not p:
        raise FileNotFoundError(
            f"Template '{TEMPLATE_NAME}' not found. Set its path in Settings → List.")
    return json.loads(p.read_text(encoding="utf-8"))
