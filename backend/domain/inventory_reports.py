"""Read-only source report batches, independent of the operational stock ledger."""
from django.db import models


class InventoryReportBatch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=40, default="coerp_dgyzx1")
    active = models.BooleanField(default=False, db_index=True)
    manifest = models.JSONField(default=dict)


class InventoryReportRow(models.Model):
    batch = models.ForeignKey(InventoryReportBatch, on_delete=models.CASCADE)
    kind = models.CharField(max_length=10)
    source_table = models.CharField(max_length=30)
    source_key = models.CharField(max_length=64)
    site = models.CharField(max_length=30)
    material_code = models.CharField(max_length=100)
    material_name = models.CharField(max_length=255, blank=True)
    specification = models.TextField(blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    group_code = models.CharField(max_length=100, blank=True)
    part_type = models.CharField(max_length=100, blank=True)
    location_code = models.CharField(max_length=100, blank=True)
    location_type = models.CharField(max_length=30, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    keeper_code = models.CharField(max_length=100, blank=True)
    movement_type = models.CharField(max_length=30, blank=True)
    document_date = models.DateField(null=True)
    posted_at = models.DateTimeField(null=True)
    document_number = models.CharField(max_length=100, blank=True)
    order_number = models.CharField(max_length=100, blank=True)
    partner_code = models.CharField(max_length=100, blank=True)
    partner_kind = models.CharField(max_length=20, blank=True)
    payload = models.JSONField(default=dict)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("batch", "kind", "source_table", "source_key"), name="unique_report_source_row")]
        indexes = [
            models.Index(fields=('batch', 'kind', 'site', 'location_code', 'material_code', 'batch_number', 'id', 'location_type'), name='report_site_inventory'),
            models.Index(fields=('batch', 'kind', 'site', 'document_date', 'movement_type'), name='report_site_dates'),
            models.Index(fields=("batch", "kind", "material_code", "document_date", "source_table", "source_key", "id"), name="report_document_order"),
            models.Index(fields=("batch", "kind", "material_code", "posted_at", "source_table", "source_key", "id"), name="report_posted_order"),
            models.Index(fields=("batch", "kind", "material_code", "order_number", "source_table", "source_key", "id"), name="report_order_number"),
            models.Index(fields=("batch", "kind", "document_date"), name="report_document_date"),
            models.Index(fields=("batch", "kind", "posted_at"), name="report_posted_date"),
            models.Index(fields=("batch", "kind", "location_code", "material_code", "batch_number", "id"), name="report_location_order"),
        ]


class InventoryReportLookup(models.Model):
    batch = models.ForeignKey(InventoryReportBatch, on_delete=models.CASCADE)
    kind = models.CharField(max_length=30)
    site = models.CharField(max_length=30, blank=True)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255, blank=True)
    specification = models.TextField(blank=True)
    source_order = models.PositiveIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=("batch", "kind", "site", "code"), name="unique_report_lookup")]
        indexes = [models.Index(fields=("batch", "kind", "source_order"), name="report_lookup_order")]
