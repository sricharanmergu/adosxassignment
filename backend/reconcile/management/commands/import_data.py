import csv
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from reconcile.models import Location, SystemARecord, SystemBEntry


def normalize_ref(raw):
    match = re.search(r"\d+", raw or "")
    return f"REC-{match.group()}" if match else None


def parse_amount(raw):
    value = (raw or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def parse_date(raw):
    try:
        return date.fromisoformat((raw or "").strip())
    except ValueError:
        return None


def rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        yield from csv.DictReader(source)


class Command(BaseCommand):
    help = "Import the three assignment CSVs without discarding dirty rows."

    def add_arguments(self, parser):
        parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[3] / "data")

    @transaction.atomic
    def handle(self, *args, **options):
        root = options["data_dir"]
        locations = {obj.location_id: obj for obj in Location.objects.all()}
        counts = {"locations_read": 0, "a_read": 0, "a_saved": 0, "b_read": 0, "b_saved": 0, "blank_values": 0, "refs_cleaned": 0, "invalid_dates": 0, "invalid_amounts": 0}
        for row in rows(root / "locations.csv"):
            counts["locations_read"] += 1
            key = (row.get("location_id") or "").strip()
            obj, _ = Location.objects.update_or_create(location_id=key, defaults={"org_id": (row.get("org_id") or "").strip(), "name": (row.get("location_name") or "").strip()})
            locations[key] = obj
        for row in rows(root / "system_a.csv"):
            counts["a_read"] += 1
            values = {key: (value or "").strip() for key, value in row.items()}
            event_date = parse_date(values.get("event_date"))
            if values.get("event_date") and event_date is None: counts["invalid_dates"] += 1
            money = {key: parse_amount(values.get(key)) for key in ("base_value", "adjustment", "total_value")}
            counts["invalid_amounts"] += sum(bool(values.get(key)) and money[key] is None for key in money)
            loc = locations.get(values.get("location_id"))
            SystemARecord.objects.update_or_create(record_id=values["record_id"], defaults={"location": loc, "location_id_raw": values.get("location_id", ""), "event_date": event_date, "category_code": values.get("category_code", ""), "actor_id": values.get("actor_id") or None, **money, "state": values.get("state", "")})
            counts["a_saved"] += 1
        for row in rows(root / "system_b.csv"):
            counts["b_read"] += 1
            values = {key: (value or "").strip() for key, value in row.items()}
            ref = normalize_ref(values.get("record_ref"))
            if ref and values.get("record_ref") != ref: counts["refs_cleaned"] += 1
            amount = parse_amount(values.get("value"))
            if not values.get("value"): counts["blank_values"] += 1
            elif amount is None: counts["invalid_amounts"] += 1
            recorded_on = parse_date(values.get("recorded_on"))
            if values.get("recorded_on") and recorded_on is None: counts["invalid_dates"] += 1
            SystemBEntry.objects.update_or_create(entry_id=values["entry_id"], defaults={"record_ref_raw": values.get("record_ref", ""), "record_ref": ref, "location": locations.get(values.get("location_id")), "location_id_raw": values.get("location_id", ""), "recorded_on": recorded_on, "value_raw": values.get("value", ""), "value": amount, "label": values.get("label", "")})
            counts["b_saved"] += 1
        self.stdout.write(self.style.SUCCESS(f"Locations: {counts['locations_read']} read; A: {counts['a_read']} read, {counts['a_saved']} saved; B: {counts['b_read']} read, {counts['b_saved']} saved; blank B values: {counts['blank_values']}; refs cleaned: {counts['refs_cleaned']}; invalid dates: {counts['invalid_dates']}; invalid amounts: {counts['invalid_amounts']}"))
