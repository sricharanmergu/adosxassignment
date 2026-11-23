from collections import defaultdict


def compare(a_rows, b_rows):
    """Return disagreement records from plain Python mappings.

    A rows are keyed by record id. B entries use cleaned `ref` and Decimal-or-None values.
    """
    by_ref = defaultdict(list)
    for entry in b_rows:
        if entry.get("ref"):
            by_ref[entry["ref"]].append(entry)
    output = []
    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for entry in entries:
                output.append({"reason": "ORPHAN_IN_B", "record_id": ref, "entries": [entry], "a": None})
    for record_id, record in a_rows.items():
        entries = by_ref.get(record_id, [])
        if not entries:
            output.append({"reason": "MISSING_IN_B", "record_id": record_id, "entries": [], "a": record})
            continue
        if any(entry.get("value") is None for entry in entries):
            output.append({"reason": "VALUE_MISMATCH", "record_id": record_id, "entries": entries, "a": record})
        elif len(entries) > 1:
            # Multiple entries are accepted only when their exact sum is the A total.
            if record.get("total") is None or sum((entry["value"] for entry in entries), start=0) != record["total"]:
                output.append({"reason": "DUPLICATE_IN_B", "record_id": record_id, "entries": entries, "a": record})
        else:
            entry = entries[0]
            if entry["value"] != record.get("total"):
                output.append({"reason": "VALUE_MISMATCH", "record_id": record_id, "entries": entries, "a": record})
        # Date and location are checked for every entry, including entries in a valid split.
        for entry in entries:
            if entry.get("location") != record.get("location"):
                output.append({"reason": "LOCATION_MISMATCH", "record_id": record_id, "entries": [entry], "a": record})
            if entry.get("date") != record.get("date"):
                output.append({"reason": "DATE_MISMATCH", "record_id": record_id, "entries": [entry], "a": record})
    return output
