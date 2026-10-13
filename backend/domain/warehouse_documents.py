"""Warehouse documents and read-only legacy inventory records."""

from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.utils import timezone


class InventoryDocument(models.Model):
    KINDS = [("transfer", "转仓单"), ("receipt", "计划外入库单"), ("issue", "计划外出库单"),
             ("count", "盘点单"), ("scrap", "报废单"), ("opening", "期初库存单")]
    STATES = [("draft", "草稿"), ("confirmed", "已确认"), ("posted", "已审核"), ("reversed", "已冲销")]
    number = models.CharField(max_length=40, unique=True, blank=True)
    kind = models.CharField(max_length=12, choices=KINDS)
    document_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=12, choices=STATES, default="draft")
    from_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_outgoing")
    to_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_incoming")
    from_department = models.ForeignKey("Department", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_outgoing")
    to_department = models.ForeignKey("Department", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_incoming")
    category_code = models.CharField(max_length=30, blank=True)
    transfer_class = models.CharField(max_length=30, blank=True)
    supplier = models.ForeignKey("Partner", null=True, blank=True, on_delete=models.PROTECT)
    count_basis = models.CharField(max_length=1, default="2", choices=[("1", "盘点日期实时库存"), ("2", "即时库存"), ("3", "盘点日期单据库存")])
    # Legacy adj_mstr.adj_checker stores usr_mstr.usr_user, not a free-text name.
    checker = models.ForeignKey("Employee", null=True, blank=True, on_delete=models.PROTECT, related_name="inventory_counts")
    printer = models.CharField(max_length=64, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    created_by = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_by = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.CharField(max_length=64, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    reversed_by = models.CharField(max_length=64, blank=True)
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_reason = models.CharField(max_length=240, blank=True)
    source_key = models.CharField(max_length=160, blank=True)
    source_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-document_date", "-id")

    def save(self, *args, **kwargs):
        if not self.number:
            from .document_numbers import next_document_number
            if self.kind == 'opening':
                # Local-only baseline, not a source business document.
                self.number = f"OP{timezone.now():%Y%m%d%H%M%S}-{uuid4().hex[:8].upper()}"
            else:
                prefix = {'transfer': 'MYMT', 'receipt': 'MYMG', 'issue': 'MYMU', 'count': 'MYMJ', 'scrap': 'MYMC'}[self.kind]
                self.number = next_document_number(prefix, self.document_date, 'InventoryDocument', 'StockTransfer', 'StockCount')
        super().save(*args, **kwargs)


class InventoryDocumentLine(models.Model):
    document = models.ForeignKey(InventoryDocument, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT)
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0"))
    from_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_outgoing_lines")
    to_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="warehouse_incoming_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    grade = models.CharField(max_length=8, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    modification_count = models.PositiveIntegerField(default=0)
    modified_by = models.CharField(max_length=64, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    reference_number = models.CharField(max_length=40, blank=True)
    reference_line = models.PositiveIntegerField(null=True, blank=True)
    reference_cost = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    system_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, editable=False)
    counted_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    variance_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, editable=False)

    class Meta:
        ordering = ("line_number",)
        constraints = [models.UniqueConstraint(fields=("document", "line_number"), name="uniq_warehouse_document_line")]


class LegacyInventoryRecord(models.Model):
    source_database = models.CharField(max_length=40)
    source_table = models.CharField(max_length=40)
    source_key = models.CharField(max_length=160)
    material = models.ForeignKey("Material", on_delete=models.PROTECT, null=True)
    location = models.ForeignKey("Location", on_delete=models.PROTECT, null=True)
    effective_date = models.DateField(null=True)
    payload = models.JSONField()
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("source_database", "source_table", "source_key"), name="uniq_legacy_inventory_record")]


class InventoryDictionary(models.Model):
    dictionary = models.CharField(max_length=30)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ("dictionary", "code")
        constraints = [models.UniqueConstraint(fields=("dictionary", "code"), name="uniq_inventory_dictionary")]
