"""Pippo's settings: the defaults and where they are stored."""
from .defaults import DEFAULT_CONFIG
from .store import ConfigStore, app_dir

__all__ = ["DEFAULT_CONFIG", "ConfigStore", "app_dir"]
