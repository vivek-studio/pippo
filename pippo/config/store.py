"""Where config.json lives (%APPDATA%\\Pippo on Windows) and how it is read and written."""
from __future__ import annotations

import json
import os
from pathlib import Path

from .defaults import DEFAULT_CONFIG


def app_dir() -> Path:
    override = os.environ.get("PIPPO_HOME")
    if override:
        p = Path(override)
    elif os.name == "nt":
        p = Path(os.environ.get("APPDATA", str(Path.home()))) / "Pippo"
    else:
        p = Path.home() / ".pippo"
    p.mkdir(parents=True, exist_ok=True)
    return p


class ConfigStore:
    """Loads the config on top of the defaults, and saves it atomically."""

    def __init__(self, path: Path | None = None):
        self.path = path or app_dir() / "config.json"

    def load(self) -> dict:
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        if self.path.exists():
            try:
                cfg.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                pass
        return cfg

    def save(self, cfg: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
