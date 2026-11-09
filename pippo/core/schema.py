"""Building a new list's columns from the template, and reading Slack's rich-text / select values."""
from __future__ import annotations

from .columns import COL_SORT, COLUMN_ORDER, NUMBER_OPTIONS, SKIP_COLUMN_TYPES


def build_schema_from_template(template: dict) -> list[dict]:
    schema = []
    for col in template["columns"]:
        ctype = col.get("type")
        if ctype in SKIP_COLUMN_TYPES:
            continue
        opts = col.get("options") or {}
        entry = {"key": col["key"], "name": col["name"], "type": ctype,
                 "is_primary_column": col.get("is_primary_column", False)}
        if ctype == "user":
            entry["options"] = {"format": "multi_entity", "show_member_name": True}
        elif ctype == "select":
            entry["options"] = {"format": "single_select", "choices": [
                {"value": c["value"], "label": c["label"], "color": c.get("color", "gray")}
                for c in opts.get("choices", [])]}
        elif ctype == "number":
            entry["options"] = dict(NUMBER_OPTIONS)
        elif ctype == "rating":
            entry["options"] = {"emoji": opts.get("emoji", ":star:"), "max": opts.get("max", 2)}
        elif ctype == "date":
            entry["options"] = {"date_format": opts.get("date_format", "DD/MM/YYYY")}
        schema.append(entry)
    if not any(c["name"] == COL_SORT for c in schema):
        schema.append({"key": "sort_order", "name": COL_SORT, "type": "number",
                       "is_primary_column": False,
                       "options": dict(NUMBER_OPTIONS)})
    order = [n.lower() for n in COLUMN_ORDER]
    return sorted(schema, key=lambda c: order.index(c["name"].lower()) if c["name"].lower() in order else len(order))


def rich_text_value(text: str) -> list[dict]:
    return [{"type": "rich_text", "elements": [
        {"type": "rich_text_section", "elements": [{"type": "text", "text": text}]}]}]


def flatten_rich_text(node) -> str:
    out = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("type") == "text" and "text" in n:
                out.append(n["text"])
            for v in n.values():
                if isinstance(v, (list, dict)):
                    walk(v)
        elif isinstance(n, list):
            for x in n:
                walk(x)

    walk(node)
    return "".join(out).strip()


def choice_value(col: dict, label) -> str | None:
    """Value of the select-column choice whose label matches (case-insensitive), else None."""
    for c in (col.get("options") or {}).get("choices", []):
        if c["label"].lower() == (label or "").lower():
            return c["value"]
    return None
