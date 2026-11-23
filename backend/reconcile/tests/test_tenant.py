from django.test import Client
from reconcile.models import Location, SystemARecord, SystemBEntry
from decimal import Decimal


def test_org_api_does_not_return_foreign_records_or_locations(db):
    a = Location.objects.create(location_id="A1", org_id="ORG-A", name="A")
    b = Location.objects.create(location_id="B1", org_id="ORG-B", name="B")
    SystemARecord.objects.create(record_id="REC-A", location=a, location_id_raw="A1", total_value=Decimal("20.00"))
    SystemARecord.objects.create(record_id="REC-B", location=b, location_id_raw="B1", total_value=Decimal("30.00"))
    SystemBEntry.objects.create(entry_id="E-A", record_ref="REC-A", record_ref_raw="REC-A", location=b, location_id_raw="B1", value=Decimal("19.00"))
    SystemBEntry.objects.create(entry_id="E-B", record_ref="REC-B", record_ref_raw="REC-B", location=a, location_id_raw="A1", value=Decimal("30.00"))
    response = Client().get("/api/disagreements/?org=ORG-A")
    body = response.json()
    assert response.status_code == 200
    assert all(row["record_id"] != "REC-B" for row in body)
    assert all(row["b_location"] is None or row["b_location"] != "B1" for row in body)
    assert any(row["record_id"] == "REC-A" and row["b_location"] is None for row in body)
    reverse = Client().get("/api/disagreements/?org=ORG-B").json()
    assert all(row["record_id"] != "REC-A" for row in reverse)
    assert all(row["a_location"] is None or row["a_location"] != "A1" for row in reverse)
    assert all(row["b_location"] is None or row["b_location"] != "A1" for row in reverse)
