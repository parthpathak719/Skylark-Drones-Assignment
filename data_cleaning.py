"""
data_cleaning.py

Small, focused helpers for handling the messy real world data described
in the assignment: missing values, inconsistent number formats, stray
text in numeric-ish fields (like the "#VALUE!" and "5360 HA" cases found
in Work Orders), rows where a header row got accidentally pasted into
the data itself, client codes that are formatted differently across
boards but refer to the same client, and reliable totals for numeric
fields (computed here in Python rather than asked of the LLM, since
summing many rows in-context is error-prone).

These are used to clean data before handing it to the LLM, and to build
a short "data quality note" that the agent can mention to the user.
"""

import re


def safe_float(value):
    """
    Tries to pull a number out of a messy text value.
    Returns None if nothing numeric could be found, instead of raising.

    Examples this needs to handle:
        "5360 HA"    -> 5360.0
        "#VALUE!"    -> None
        "1,310.850"  -> 1310.85
        None         -> None
        ""           -> None
    """
    if value is None:
        return None

    text = str(value).strip()
    if text == "" or text.upper() == "NA" or text.startswith("#"):
        return None

    # Strip commas used as thousands separators, then pull the first
    # number-looking chunk out of the string (handles trailing units like "HA").
    cleaned = text.replace(",", "")
    match = re.search(r"-?\d+(\.\d+)?", cleaned)
    if not match:
        return None

    return float(match.group())


def extract_unit(value):
    """
    Pulls a trailing unit label out of a quantity field, if there is one.
    "5360 HA" -> "HA"
    "3000"    -> None
    """
    if value is None:
        return None

    text = str(value).strip()
    match = re.search(r"[A-Za-z]+", text)
    if match:
        return match.group()
    return None


def data_quality_report(rows, fields_to_check):
    """
    Builds a short summary of how much data is missing or malformed
    across a list of row dicts, for the given field names.

    This is meant to be handed to the LLM as context, or surfaced
    directly to the user, so gaps in the data are communicated rather
    than silently ignored.
    """
    total = len(rows)
    report = {}

    for field in fields_to_check:
        missing = 0
        unparseable = 0
        for row in rows:
            value = row.get(field)
            if value is None or str(value).strip() == "":
                missing += 1
            elif str(value).strip().startswith("#"):
                unparseable += 1

        if missing or unparseable:
            report[field] = {
                "total_rows": total,
                "missing": missing,
                "unparseable": unparseable,
            }

    return report


def find_leaked_header_rows(rows):
    """
    Detects rows where the header row itself got pasted into the data by
    accident, e.g. a "Close Date (A)" cell literally containing the text
    "Close Date (A)" instead of a real date. This happens when someone
    copy-pastes a header row into the middle of a spreadsheet.

    A row is flagged if at least half of its fields hold a value that is
    identical to that field's own column name. Returns a list of
    {"id": ..., "name": ...} for each corrupted row found, so the agent
    can tell the user which rows were excluded and why, instead of
    silently trying to parse header text as real data.
    """
    corrupted = []
    for row in rows:
        fields = [key for key in row.keys() if key not in ("id", "name")]
        if not fields:
            continue
        leaked = sum(1 for key in fields if row.get(key) == key)
        if leaked >= len(fields) / 2:
            corrupted.append({"id": row.get("id"), "name": row.get("name")})
    return corrupted


def normalize_client_code(code):
    """
    Normalizes client/customer identifier codes so the same client can be
    matched reliably across boards, rather than relying on the LLM to
    notice the connection on its own.

    One board formats a client as "COMPANY002", the other as
    "WOCOMPANY_002" for the exact same client, a board-specific prefix
    and underscore, not a different client. This strips both so both
    boards resolve to the same normalized code, e.g. "COMPANY002".
    """
    if code is None:
        return None
    normalized = str(code).strip()
    if normalized.upper().startswith("WO"):
        normalized = normalized[2:]
    normalized = normalized.replace("_", "")
    return normalized or None


def summarize_amounts(rows, amount_field, group_by_field=None):
    """
    Computes a reliable total for a numeric-ish field (using safe_float,
    so messy values like "#VALUE!" or "5360 HA" don't break the sum or
    get silently skipped without a count).

    This exists so the LLM can report pre-computed totals instead of
    adding many rows together itself in-context, which drifts on lists
    of more than a handful of rows. Optionally breaks the total down by
    another field, e.g. status or sector, so the LLM has trustworthy
    subtotals too, not just a grand total.
    """
    total = 0.0
    counted = 0

    for row in rows:
        value = safe_float(row.get(amount_field))
        if value is not None:
            total += value
            counted += 1

    summary = {
        "field": amount_field,
        "total": round(total, 2),
        "rows_included_in_total": counted,
        "rows_total": len(rows),
    }

    if group_by_field:
        groups = {}
        for row in rows:
            key = row.get(group_by_field) or "(blank)"
            groups.setdefault(key, {"total": 0.0, "row_count": 0})
            groups[key]["row_count"] += 1
            value = safe_float(row.get(amount_field))
            if value is not None:
                groups[key]["total"] += value

        for key in groups:
            groups[key]["total"] = round(groups[key]["total"], 2)

        summary[f"breakdown_by_{group_by_field}"] = groups

    return summary