"""Engineering domain models; Django app label remains backend."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .base import AuditedModel


class BillOfMaterial(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    parent_material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="boms")
    version = models.CharField(max_length=20, default="A")
    effective_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(null=True, blank=True)
    kind = models.CharField(max_length=20, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="bom_mstr")

    class Meta:
        ordering = ("parent_material__code", "-effective_date", "version")
        constraints = [models.UniqueConstraint(fields=("parent_material", "version"), name="uniq_material_bom_version")]

    def clean(self):
        if self.expiry_date and self.expiry_date < self.effective_date:
            raise ValidationError({"expiry_date": "失效日期不能早于生效日期"})


class BomLine(models.Model):
    bom = models.ForeignKey(BillOfMaterial, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    component = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="bom_component_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="bom_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    scrap_rate = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    operation = models.PositiveIntegerField(default=0)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="ps_mstr")

    class Meta:
        ordering = ("bom", "line_number")
        constraints = [models.UniqueConstraint(fields=("bom", "line_number"), name="uniq_bom_line_number")]

    def clean(self):
        if self.bom_id and self.component_id == self.bom.parent_material_id:
            raise ValidationError({"component": "BOM 组件不能与父物料相同"})
        if self.expiry_date and self.effective_date and self.expiry_date < self.effective_date:
            raise ValidationError({"expiry_date": "失效日期不能早于生效日期"})


class Routing(AuditedModel):
    code = models.CharField(max_length=40)
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="routings")
    version = models.CharField(max_length=20, default="A")
    effective_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="route_mstr")

    class Meta:
        ordering = ("material__code", "version")
        constraints = [models.UniqueConstraint(fields=("material", "version"), name="uniq_material_routing_version")]

    def clean(self):
        if self.expiry_date and self.expiry_date < self.effective_date:
            raise ValidationError({"expiry_date": "失效日期不能早于生效日期"})


class RoutingOperation(models.Model):
    routing = models.ForeignKey(Routing, on_delete=models.CASCADE, related_name="operations")
    sequence = models.PositiveIntegerField()
    name = models.CharField(max_length=120)
    work_center = models.CharField(max_length=40)
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="routing_operations")
    run_time = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    production_rate = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    yield_rate = models.DecimalField(
        max_digits=7, decimal_places=4, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))]
    )
    supplier = models.ForeignKey(
        "Partner", on_delete=models.PROTECT, null=True, blank=True, related_name="routing_operations"
    )
    tool = models.CharField(max_length=80, blank=True)
    parameters = models.CharField(max_length=240, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    is_default = models.BooleanField(default=False)
    is_alternate = models.BooleanField(default=False)
    alternate_sequence = models.PositiveIntegerField(default=0)
    operation_type = models.CharField(max_length=20, default="internal")
    purchase_material = models.ForeignKey(
        "Material", on_delete=models.PROTECT, null=True, blank=True, related_name="outsource_operations"
    )
    source_object = models.CharField(max_length=40, default="ro_det")

    class Meta:
        ordering = ("routing", "sequence")
        constraints = [models.UniqueConstraint(fields=("routing", "sequence"), name="uniq_routing_operation_sequence")]

    def clean(self):
        if self.yield_rate > Decimal("100"):
            raise ValidationError({"yield_rate": "良率不能超过 100%"})
