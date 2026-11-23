from decimal import Decimal

from reconcile.compare import compare


def entry(entry_id, ref="REC-1", value="100.00", location="L1", date="2026-01-01"):
    return {"entry_id": entry_id, "ref": ref, "value": Decimal(value) if value is not None else None, "location": location, "date": date}


def record(total="100.00", location="L1", date="2026-01-01"):
    return {"total": Decimal(total) if total is not None else None, "location": location, "date": date}


def test_missing_in_b():
    assert [x["reason"] for x in compare({"REC-1": record()}, [])] == ["MISSING_IN_B"]


def test_orphan_in_b():
    assert [x["reason"] for x in compare({}, [entry("E1", ref="REC-9")])] == ["ORPHAN_IN_B"]


def test_duplicate_same_amount_is_flagged():
    result = compare({"REC-1": record()}, [entry("E1"), entry("E2")])
    assert "DUPLICATE_IN_B" in [x["reason"] for x in result]


def test_value_mismatch():
    assert "VALUE_MISMATCH" in [x["reason"] for x in compare({"REC-1": record()}, [entry("E1", value="99.00")])]


def test_blank_value_is_unknown_not_zero():
    result = compare({"REC-1": record()}, [entry("E1", value=None)])
    assert [x["reason"] for x in result] == ["VALUE_MISMATCH"]


def test_split_that_sums_is_not_an_error():
    result = compare({"REC-1": record()}, [entry("E1", value="40.00"), entry("E2", value="60.00")])
    assert result == []


def test_messy_references_normalize_to_matching_record():
    from reconcile.management.commands.import_data import normalize_ref, parse_amount
    assert [normalize_ref(value) for value in ("rec1034", "REC - 1070", "1112")] == ["REC-1034", "REC-1070", "REC-1112"]
    assert parse_amount("1,25,400.00") == Decimal("125400.00")
    assert parse_amount("") is None


def test_clean_row():
    assert compare({"REC-1": record()}, [entry("E1")]) == []


def test_location_mismatch():
    reasons = [x["reason"] for x in compare({"REC-1": record()}, [entry("E1", location="L2")])]
    assert reasons == ["LOCATION_MISMATCH"]


def test_date_mismatch():
    reasons = [x["reason"] for x in compare({"REC-1": record()}, [entry("E1", date="2026-01-02")])]
    assert reasons == ["DATE_MISMATCH"]
