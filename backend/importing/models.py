from django.db import models
from django.db.models import Q


class ErpImportProfile(models.Model):
    """Web-side binding for one read-only legacy ERP source and company."""
    name = models.CharField(max_length=80)
    company = models.ForeignKey("backend.Company", on_delete=models.PROTECT, related_name="erp_import_profiles")
    source_database = models.CharField(max_length=128, default="coerp_dgyzx1")
    source_catalog = models.CharField(max_length=128, default="coerp_base")
    source_view = models.CharField(max_length=128, default="V_AI_PT_MSTR")
    source_company_column = models.CharField(max_length=128, default="coerp_dgyzx1")
    enabled = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-is_default", "id")
        constraints = [models.UniqueConstraint(condition=Q(enabled=True, is_default=True), fields=("is_default",), name="uniq_enabled_default_import_profile")]


class MaterialImportBatch(models.Model):
    class Status(models.TextChoices):
        PREVIEW = "preview", "待确认"
        IMPORTED = "imported", "已导入"
        FAILED = "failed", "导入失败"

    source_file = models.FileField(upload_to="imports/materials/%Y/%m/%d")
    original_filename = models.CharField(max_length=255)
    default_tax_code = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PREVIEW)
    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    imported_rows = models.PositiveIntegerField(default=0)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "-id")


class MaterialImportRow(models.Model):
    class Status(models.TextChoices):
        VALID = "valid", "可导入"
        ERROR = "error", "有错误"
        IMPORTED = "imported", "已导入"

    batch = models.ForeignKey(MaterialImportBatch, on_delete=models.CASCADE, related_name="rows")
    row_number = models.PositiveIntegerField()
    source_data = models.JSONField(default=dict)
    normalized_data = models.JSONField(default=dict)
    allocated_code = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ERROR)
    errors = models.JSONField(default=list)
    material = models.ForeignKey("backend.Material", on_delete=models.PROTECT, null=True, blank=True, related_name="import_rows")

    class Meta:
        ordering = ("row_number",)
        constraints = [models.UniqueConstraint(fields=("batch", "row_number"), name="uniq_material_import_row")]
