"""Inventory domain models; Django app label remains backend."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from .base import AuditedModel
from .warehouse_documents import InventoryDocument
from backend.inventory_codes import COUNT_ADJUSTMENT, TRANSFER_IN, TRANSFER_OUT


class StockBalance(models.Model):
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="stock_balances")
    location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="stock_balances")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="stock_balances")
    batch_number = models.CharField(max_length=80, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0"))
    reserved_quantity = models.DecimalField(
        max_digits=20, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("material__code", "location__code", "batch_number")
        constraints = [
            models.UniqueConstraint(fields=("material", "location", "batch_number"), name="uniq_stock_balance_key")
        ]

    @classmethod
    @transaction.atomic
    def adjust(
        cls,
        *,
        material,
        location,
        uom,
        quantity,
        movement_type,
        source_model,
        source_id,
        source_line_id,
        actor,
        batch_number="",
        effective_date=None,
        reversal_of=None,
        usage=None,
        uom_rate_m=None,
        uom_rate_d=None,
        forbid_negative=False,
        native_sales_rates=False,
    ):
        from .master_data import Location
        from backend.live_inventory import live_batch
        from datetime import date

        ledger = live_batch()
        if ledger and ledger.manifest.get('opening_date'):
            if (effective_date or timezone.localdate()) < date.fromisoformat(ledger.manifest['opening_date']):
                raise ValidationError('业务日期早于本地库存启用日期，不能重复计入期初前的业务')

        # A location lock also serializes first balance creation and count freezing.
        location = Location.objects.select_for_update().get(pk=location.pk)
        quantity = Decimal(quantity)
        if not quantity.is_finite() or quantity != quantity.quantize(Decimal("0.00000001")):
            raise ValidationError("库存数量必须是最多8位小数的有效数值")
        if location.disabled_for_inventory:
            raise ValidationError(f"库位 {location.code} 已停用")
        if material.no_stock_movement:
            raise ValidationError("不参与库存移动的物料不能记库存账")
        business_uom, business_quantity = uom, quantity
        rate_m = rate_d = Decimal(1)
        if material.uom_id != uom.pk or native_sales_rates:
            if uom_rate_m is None or uom_rate_d is None:
                conversion = material.uom_conversions.filter(usage=usage, business_uom=uom).first()
                if conversion is None:
                    raise ValidationError("缺少物料业务单位到库存基本单位的换算")
                rate_m, rate_d = conversion.business_qty, conversion.stock_qty
            else:
                rate_m, rate_d = Decimal(uom_rate_m), Decimal(uom_rate_d)
            if rate_m <= 0 or rate_d <= 0:
                raise ValidationError("单位换算比例必须大于零")
            converted = quantity * rate_m / rate_d if native_sales_rates else quantity * rate_d / rate_m
            quantity = converted.quantize(Decimal("0.00000001"))
            if quantity != converted:
                raise ValidationError("单位换算结果超过8位小数，请核实数量或比例")
            uom = material.uom
        if material.batch_control and not batch_number:
            raise ValidationError("批号控制物料必须填写批号")
        freezes = InventoryDocument.objects.filter(kind="count", status="confirmed", from_location=location)
        if source_model == "backend.inventorydocument":
            freezes = freezes.exclude(pk=source_id)
        if freezes.exists():
            raise ValidationError(f"库位 {location.code} 盘点中，暂停库存收发")
        if StockTransaction.objects.filter(source_model=source_model, source_line_id=str(source_line_id),
                                          movement_type=movement_type, location=location).exists():
            raise ValidationError("此来源行已经过账")
        from backend.live_inventory import opening_balance, project_movement
        balance = opening_balance(material, location, uom, batch_number)
        if balance.uom_id != uom.id:
            raise ValidationError("库存流水单位必须与余额单位一致")
        next_quantity = balance.quantity + quantity
        if next_quantity < 0 and (forbid_negative or not location.allow_negative):
            raise ValidationError(f"库位 {location.code} 库存不足，不允许负库存")
        if quantity < 0 and balance.reserved_quantity > 0 and next_quantity < balance.reserved_quantity:
            raise ValidationError("不能消耗已预留库存")
        balance.quantity = next_quantity
        balance.save(update_fields=["quantity", "updated_at"])
        movement = StockTransaction.objects.create(
            movement_type=movement_type,
            material=material,
            location=location,
            uom=uom,
            batch_number=batch_number,
            quantity=quantity,
            balance_after=next_quantity,
            source_model=source_model,
            source_id=str(source_id),
            source_line_id=str(source_line_id),
            actor=actor,
            effective_date=effective_date or timezone.localdate(),
            reversal_of=reversal_of,
            business_uom=business_uom, business_quantity=business_quantity,
            uom_rate_m=rate_m, uom_rate_d=rate_d,
        )
        project_movement(balance, movement)
        return balance


class StockTransaction(models.Model):
    movement_type = models.CharField(max_length=24)
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="stock_transactions")
    location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="stock_transactions")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="stock_transactions")
    batch_number = models.CharField(max_length=80, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    balance_after = models.DecimalField(max_digits=20, decimal_places=8)
    effective_date = models.DateField(default=timezone.localdate, db_index=True)
    reversal_of = models.OneToOneField("self", null=True, blank=True, on_delete=models.PROTECT, related_name="reversal")
    business_uom = models.ForeignKey("Uom", null=True, blank=True, on_delete=models.PROTECT, related_name="business_stock_transactions")
    business_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    uom_rate_m = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal(1))
    uom_rate_d = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal(1))
    source_model = models.CharField(max_length=80)
    source_id = models.CharField(max_length=64)
    source_line_id = models.CharField(max_length=64)
    actor = models.CharField(max_length=64)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-posted_at", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=("source_model", "source_line_id", "movement_type", "location"),
                name="uniq_stock_source_movement",
            )
        ]


class StockTransfer(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    transfer_date = models.DateField(default=timezone.localdate)
    from_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="outgoing_transfers")
    to_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="incoming_transfers")
    notes = models.CharField(max_length=240, blank=True)
    posted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ("-transfer_date", "-number")

    def clean(self):
        if self.from_location_id and self.from_location_id == self.to_location_id:
            raise ValidationError({"to_location": "调出和调入库位不能相同"})

    def approve(self, actor):
        lines = list(self.lines.select_related("material", "uom"))
        if not lines:
            raise ValidationError("调拨单至少需要一条明细")
        for line in lines:
            line.full_clean()
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            common = {
                "material": line.material,
                "uom": line.uom,
                "source_model": self._meta.label_lower,
                "source_id": self.pk,
                "source_line_id": line.pk,
                "actor": actor,
                "batch_number": line.batch_number,
            }
            StockBalance.adjust(
                location=self.from_location, quantity=-line.quantity, movement_type=TRANSFER_OUT, **common
            )
            StockBalance.adjust(
                location=self.to_location, quantity=line.quantity, movement_type=TRANSFER_IN, **common
            )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            from .document_numbers import next_document_number
            self.number = next_document_number('MYMT', self.transfer_date, 'StockTransfer', 'InventoryDocument')
        super().save(*args, **kwargs)


class StockTransferLine(models.Model):
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="stock_transfer_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="stock_transfer_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    batch_number = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ("transfer", "line_number")
        constraints = [models.UniqueConstraint(fields=("transfer", "line_number"), name="uniq_stock_transfer_line")]

    def clean(self):
        if self.material_id and self.material.batch_control and not self.batch_number:
            raise ValidationError({"batch_number": "启用批号控制的物料调拨时必须填写批号"})


class StockCount(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    count_date = models.DateField(default=timezone.localdate)
    location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="stock_counts")
    notes = models.CharField(max_length=240, blank=True)
    posted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ("-count_date", "-number")

    def approve(self, actor):
        lines = list(self.lines.select_related("material", "uom"))
        if not lines:
            raise ValidationError("盘点单至少需要一条明细")
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            if line.variance_quantity:
                StockBalance.adjust(
                    material=line.material,
                    location=self.location,
                    uom=line.uom,
                    quantity=line.variance_quantity,
                    movement_type=COUNT_ADJUSTMENT,
                    source_model=self._meta.label_lower,
                    source_id=self.pk,
                    source_line_id=line.pk,
                    actor=actor,
                    batch_number=line.batch_number,
                )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            from .document_numbers import next_document_number
            self.number = next_document_number('MYMJ', self.count_date, 'StockCount', 'InventoryDocument')
        super().save(*args, **kwargs)


class StockCountLine(models.Model):
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="stock_count_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="stock_count_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    system_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), editable=False)
    counted_quantity = models.DecimalField(
        max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))]
    )
    variance_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), editable=False)

    class Meta:
        ordering = ("stock_count", "line_number")
        constraints = [models.UniqueConstraint(fields=("stock_count", "line_number"), name="uniq_stock_count_line")]

    def save(self, *args, **kwargs):
        if self._state.adding:
            balance = StockBalance.objects.filter(
                material=self.material,
                location=self.stock_count.location,
                batch_number=self.batch_number,
            ).first()
            self.system_quantity = balance.quantity if balance else Decimal("0")
        self.variance_quantity = self.counted_quantity - self.system_quantity
        super().save(*args, **kwargs)
