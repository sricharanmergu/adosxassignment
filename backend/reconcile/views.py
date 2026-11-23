import json
from decimal import Decimal

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .compare import compare
from .models import SystemARecord, SystemBEntry

REASONS = {"MISSING_IN_B", "ORPHAN_IN_B", "DUPLICATE_IN_B", "VALUE_MISMATCH", "LOCATION_MISMATCH", "DATE_MISMATCH"}


def money(value):
    return format(value, ".2f") if value is not None else None


def rows_for_org(org):
    a_objects = list(SystemARecord.objects.filter(location__org_id=org).select_related("location"))
    a_ids = {row.record_id for row in a_objects}
    # Include own-org B rows to find orphans, plus matching rows for tenant-owned A records.
    b_objects = list(SystemBEntry.objects.filter(Q(location__org_id=org) | Q(record_ref__in=a_ids)).select_related("location"))
    a_rows = {row.record_id: {"total": row.total_value, "location": row.location_id_raw, "date": row.event_date.isoformat() if row.event_date else None, "org": org} for row in a_objects}
    all_a_refs = set(SystemARecord.objects.values_list("record_id", flat=True))
    b_rows = [{"entry_id": row.entry_id, "ref": row.record_ref, "value": row.value, "location": row.location_id_raw, "location_org": row.location.org_id if row.location_id else None, "date": row.recorded_on.isoformat() if row.recorded_on else None} for row in b_objects if row.record_ref in a_ids or row.record_ref not in all_a_refs]
    disagreements = compare(a_rows, b_rows)
    payload = []
    for item in disagreements:
        a = item["a"]
        entries = item["entries"]
        first = entries[0] if entries else None
        foreign_b = bool(first and first.get("location_org") and first["location_org"] != org)
        payload.append({
            "reason": item["reason"], "record_id": item["record_id"],
            "location": (a.get("location") if a else (None if foreign_b else first.get("location"))),
            "a_location": a.get("location") if a else None,
            "b_location": None if foreign_b else (first.get("location") if first else None),
            "a_value": money(a.get("total")) if a else None,
            "b_value": ", ".join(money(entry.get("value")) or "" for entry in entries) if entries else None,
            "difference": money(a["total"] - sum((entry["value"] or Decimal("0") for entry in entries), start=Decimal("0"))) if a and a.get("total") is not None and all(entry.get("value") is not None for entry in entries) else None,
            "date": a.get("date") if a else (None if foreign_b else first.get("date")),
        })
    return payload


@require_GET
def disagreements(request):
    org = (request.GET.get("org") or "").strip()
    if org not in set(SystemARecord.objects.values_list("location__org_id", flat=True).distinct()):
        return JsonResponse({"error": "A valid org query parameter is required."}, status=400)
    results = rows_for_org(org)
    reason = request.GET.get("reason")
    if reason:
        if reason not in REASONS:
            return JsonResponse({"error": "Unknown reason."}, status=400)
        results = [item for item in results if item["reason"] == reason]
    sort = request.GET.get("sort", "")
    if sort in {"value", "-value"}:
        results.sort(key=lambda row: (row["a_value"] is None, Decimal(row["a_value"]) if row["a_value"] is not None else Decimal("0")), reverse=sort.startswith("-"))
    return JsonResponse(results, safe=False)
