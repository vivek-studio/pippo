"""Names of the list columns Pippo knows about, and the constants of its list rules."""
from __future__ import annotations

# Column names Pippo fills from the Daily Radio
COL_NAME, COL_ROUND, COL_DATE, COL_ASSETS = "Project Name", "Round", "Due Date", "No. of Assets"
COL_STATUS = "Status"
COL_STARS, COL_SORT = "Due Today", "Sort Order"   # Sort Order = helper number column the saved view sorts by

# Columns emptied on every row, every normal working day
CLEAR_COLUMNS = ["Assignee", "Currently Working", "Design Lead", "Copy Leads", "Functional Lead"]

STATUS_NOT_STARTED, STATUS_HANDED_OFF = "Not Started", "Handed Off"
HANDED_OFF_SORT = 999
FAR_DATE = "9999-12-31"

# Slack adds these two to every list by itself, so Pippo never creates them.
SKIP_COLUMN_TYPES = {"last_edited_by", "last_edited_time"}

# Column order of every new list (names as in the template; matched case-insensitively).
# A template column that isn't listed here goes after these, in template order.
COLUMN_ORDER = [COL_NAME, COL_ROUND, COL_STARS, COL_DATE, "Assignee", COL_STATUS, "Currently Working",
                COL_ASSETS, "Design Lead", "Functional Lead", "Copy Leads", COL_SORT]

# slackLists.create only accepts "format" on select / user / channel columns
# (single_select, multi_select, single_entity, multi_entity) - never on text, number or date columns.
NUMBER_OPTIONS = {"precision": 0}
