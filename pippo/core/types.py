"""Small shared type aliases."""
from __future__ import annotations

from typing import Callable

# log(message, level)  with level in {"info", "ok", "warn", "err"}
Log = Callable[..., None]
