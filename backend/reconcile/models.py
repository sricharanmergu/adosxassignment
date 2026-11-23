from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=32, unique=True)
    org_id = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.location_id} ({self.org_id})"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=40, unique=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    location_id_raw = models.CharField(max_length=64, blank=True)
    event_date = models.DateField(null=True, blank=True)
    category_code = models.CharField(max_length=40, blank=True)
    actor_id = models.CharField(max_length=40, null=True, blank=True)
    base_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    adjustment = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=24, blank=True)


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=64, unique=True)
    record_ref_raw = models.CharField(max_length=80, blank=True)
    record_ref = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    location_id_raw = models.CharField(max_length=64, blank=True)
    recorded_on = models.DateField(null=True, blank=True)
    value_raw = models.CharField(max_length=80, blank=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    label = models.CharField(max_length=160, blank=True)
