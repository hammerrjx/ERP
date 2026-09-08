"""Delivery domain models; Django app label remains backend."""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from .base import ApprovalStatus, AuditedModel, AuditEvent
from .inventory import StockBalance
from .master_data import CustomerAddress, Partner
from .sales import SalesOrder, SalesOrderLine


class DeliveryOrderSequence(models.Model):
    period = models.CharField(max_length=8, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls, delivery_date=None):
        delivery_date = delivery_date or timezone.localdate()
        period = delivery_date.strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = DeliveryOrder.objects.filter(number__startswith=f"MYSD{period[2:]}").values_list(
                "number", flat=True
            )
            sequence.last_value = max(
                [sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())]
            )
            sequence.last_value += 1
            if sequence.last_value > 9999:
                raise ValidationError("送货单四位流水已用完，请核实源系统编号配置")
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYSD{period[2:]}{sequence.last_value:04d}"


class DeliveryNumberReservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=40, unique=True)
    delivery_date = models.DateField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery = models.OneToOneField("DeliveryOrder", null=True, blank=True, on_delete=models.PROTECT)


class DeliveryOrder(AuditedModel):
    class DocumentType(models.TextChoices):
        NORMAL = "normal", "正常送货"
        RETURN = "return", "正常退货"
        RED_FLUSH = "red_flush", "红冲单据"

    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="delivery_orders")
    sales_order = models.ForeignKey(
        "SalesOrder", on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_orders"
    )
    delivery_date = models.DateField(default=timezone.localdate)
    delivery_address = models.CharField(max_length=240)
    address_code = models.CharField(max_length=40, blank=True)
    address_snapshot = models.CharField(max_length=240, blank=True)
    document_type = models.CharField(max_length=16, choices=DocumentType.choices, default=DocumentType.NORMAL)
    delivery_mode = models.CharField(
        max_length=16, choices=SalesOrder.DeliveryMode.choices, default=SalesOrder.DeliveryMode.DIRECT
    )
    source_location = models.ForeignKey(
        "Location", on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_orders"
    )
    default_print_person = models.CharField(max_length=64, blank=True)
    srm_number = models.CharField(max_length=80, blank=True)
    customer_po = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    actual_ship_time = models.DateTimeField(null=True, blank=True)
    source_delivery = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="red_flushes"
    )
    posted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ("-delivery_date", "-number")

    def clean(self):
        if self.sales_order_id and self.customer_id != self.sales_order.customer_id:
            raise ValidationError({"customer": "送货客户必须与销售订单一致"})
        if self.sales_order_id and self.customer_po != self.sales_order.customer_po:
            raise ValidationError({"customer_po": "送货单客户 PO 必须与销售订单一致"})
        if self.source_delivery_id and self.source_delivery.status != ApprovalStatus.APPROVED:
            raise ValidationError({"source_delivery": "退货或红冲必须关联已审核送货单"})
        if self.source_delivery_id and self.source_delivery.customer_id != self.customer_id:
            raise ValidationError({"source_delivery": "来源送货单客户必须一致"})
        if self.address_code:
            address = CustomerAddress.objects.filter(
                customer=self.customer, code=self.address_code, enabled=True
            ).first()
            if address:
                self.address_snapshot = address.address
        if "先出货后补单" in self.notes and not self.actual_ship_time:
            raise ValidationError({"actual_ship_time": "先出货后补单必须记录实际出货时间"})

    def approve(self, actor):
        from backend.delivery import validate_quantities

        lines = list(
            self.lines.select_related(
                "sales_order_line__order",
                "material",
                "uom",
                "source_location",
                "customer_material",
                "source_delivery_line",
            )
        )
        if not lines:
            raise ValidationError("送货单至少需要一条明细")
        customer_ids = {line.sales_order_line.order.customer_id for line in lines if line.sales_order_line_id}
        if customer_ids != {self.customer_id}:
            raise ValidationError("送货明细必须属于送货单客户")
        locked = {
            line.pk: line
            for line in SalesOrderLine.objects.select_for_update()
            .filter(
                pk__in=[line.sales_order_line_id for line in lines],
            )
            .order_by("pk")
        }
        for line in lines:
            line.sales_order_line = locked[line.sales_order_line_id]
        validate_quantities(self, lines)
        for line in lines:
            line.full_clean()
            if line.sales_order_line.order.status != ApprovalStatus.APPROVED:
                raise ValidationError("销售订单审核通过后才能送货")
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            order_line = line.sales_order_line
            quantity_delta = line.actual_quantity
            spare_delta = line.actual_spare_quantity
            stock_delta = -(quantity_delta + spare_delta)
            movement_type = "sales_delivery" if stock_delta < 0 else "sales_return"
            order_line.delivered_quantity = max(order_line.delivered_quantity + quantity_delta, Decimal("0"))
            order_line.delivered_spare_quantity = max(order_line.delivered_spare_quantity + spare_delta, Decimal("0"))
            if (quantity_delta < 0 or spare_delta < 0) and order_line.line_status in ("C", "closed"):
                order_line.line_status = "normal"
                order_line.closed_by = ""
                order_line.closed_at = None
                order_line.save(update_fields=["line_status", "closed_by", "closed_at"])
                AuditEvent.objects.create(
                    model=order_line._meta.label_lower,
                    object_id=str(order_line.pk),
                    action="reopen_for_replacement",
                    actor=actor,
                    payload={"delivery": self.pk},
                )
            order_line.save(update_fields=["delivered_quantity", "delivered_spare_quantity", "updated_at"])
            if (
                getattr(settings, "ERP_DELIVERY_POST_STOCK", False)
                and self.delivery_mode == SalesOrder.DeliveryMode.DIRECT
                and not line.material.no_stock_movement
            ):
                StockBalance.adjust(
                    material=line.material,
                    location=line.source_location,
                    uom=line.uom,
                    quantity=stock_delta,
                    movement_type=movement_type,
                    source_model=self._meta.label_lower,
                    source_id=self.pk,
                    source_line_id=line.pk,
                    actor=actor,
                    batch_number=line.batch_number,
                )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = DeliveryOrderSequence.next_number(self.delivery_date)
        super().save(*args, **kwargs)

    def unapprove(self):
        if self.posted:
            raise ValidationError("已回写订单的送货单不能反审核修改，请通过负数送货冲回")
        super().unapprove()


class DeliveryOrderLine(models.Model):
    delivery = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    sales_order_line = models.ForeignKey("SalesOrderLine", on_delete=models.PROTECT, related_name="delivery_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="delivery_order_lines")
    customer_material = models.ForeignKey(
        "CustomerMaterial", on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_lines"
    )
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="delivery_order_lines")
    actual_quantity = models.DecimalField(max_digits=19, decimal_places=8)
    ordered_spare_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    actual_spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"))
    source_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="delivery_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    source_delivery_line = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="red_flush_lines"
    )
    srm_customer_po = models.CharField(max_length=80)
    srm_material_code = models.CharField(max_length=80)
    srm_material_name = models.CharField(max_length=160)
    srm_quantity = models.DecimalField(max_digits=19, decimal_places=8)
    notes = models.CharField(max_length=240, blank=True)
    source_snapshot = models.JSONField(default=dict, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    modification_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("delivery", "line_number")
        constraints = [models.UniqueConstraint(fields=("delivery", "line_number"), name="uniq_delivery_order_line")]

    def clean(self):
        order_line = self.sales_order_line
        if order_line.order.customer_id != self.delivery.customer_id:
            raise ValidationError({"sales_order_line": "订单明细必须属于送货客户"})
        if self.customer_material_id != order_line.customer_material_id:
            raise ValidationError({"customer_material": "客户物料必须与来源订单行一致"})
        if self.source_location_id and self.source_location.disabled_for_inventory:
            raise ValidationError({"source_location": "该库位已停用"})
        if not self.actual_quantity and not self.actual_spare_quantity:
            raise ValidationError({"actual_quantity": "送货数量与备品数不能同时为 0"})
        if self.actual_quantity * self.actual_spare_quantity < 0:
            raise ValidationError("送货数量与备品数方向必须一致")
        if self.actual_quantity < 0 and abs(self.actual_quantity) > self.sales_order_line.delivered_quantity:
            raise ValidationError({"actual_quantity": "退货数量超过订单当前已送数量"})
        if self.actual_spare_quantity < 0 and abs(self.actual_spare_quantity) > order_line.delivered_spare_quantity:
            raise ValidationError({"actual_spare_quantity": "退回备品超过当前已送备品数"})
        if self.delivery_id and self.delivery.sales_order_id and order_line.order_id != self.delivery.sales_order_id:
            raise ValidationError({"sales_order_line": "送货行必须来自送货单关联销售订单"})
        if self.material_id != order_line.material_id or self.uom_id != order_line.uom_id:
            raise ValidationError("送货物料和单位必须与销售订单行一致")
        if self.srm_customer_po != order_line.order.customer_po:
            raise ValidationError({"srm_customer_po": "SRM 客户 PO 与来源销售订单不一致"})
        valid_codes = {self.material.code}
        if self.customer_material_id:
            valid_codes.add(self.customer_material.customer_code)
        if self.srm_material_code not in valid_codes:
            raise ValidationError({"srm_material_code": "SRM 物料编码与 ERP 不一致"})
        if self.srm_material_name != self.material.name:
            raise ValidationError({"srm_material_name": "SRM 物料名称与 ERP 不一致"})
        if self.srm_quantity != self.actual_quantity:
            raise ValidationError({"srm_quantity": "SRM 数量与实际送货数量不一致"})
        if self.actual_quantity > 0 and order_line.delivered_quantity + self.actual_quantity > order_line.quantity:
            raise ValidationError({"actual_quantity": "实际送货数量超过销售订单未交数量"})
        if (
            self.actual_spare_quantity > 0
            and order_line.delivered_spare_quantity + self.actual_spare_quantity > order_line.spare_quantity
        ):
            raise ValidationError({"actual_spare_quantity": "实际送备品数超过销售订单未交备品数"})
        if (
            self.material.batch_control
            and self.delivery.delivery_mode == SalesOrder.DeliveryMode.DIRECT
            and not self.batch_number
        ):
            raise ValidationError({"batch_number": "启用批号控制的物料送货时必须选择批号"})
        if self.source_delivery_line_id:
            source = self.source_delivery_line
            if source.delivery.status != ApprovalStatus.APPROVED:
                raise ValidationError("来源送货行必须已经审核")
            if self.delivery.source_delivery_id and source.delivery_id != self.delivery.source_delivery_id:
                raise ValidationError({"source_delivery_line": "来源送货明细必须属于来源送货单"})
            if source.sales_order_line_id != self.sales_order_line_id or source.material_id != self.material_id:
                raise ValidationError({"source_delivery_line": "来源送货明细必须与当前订单行和物料一致"})
            already_reversed = (
                DeliveryOrderLine.objects.filter(
                    source_delivery_line=source,
                    delivery__status=ApprovalStatus.APPROVED,
                )
                .exclude(pk=self.pk)
                .aggregate(
                    quantity=models.Sum("actual_quantity"),
                    spare_quantity=models.Sum("actual_spare_quantity"),
                )
            )
            reversed_quantity = abs(already_reversed["quantity"] or Decimal("0"))
            if abs(self.actual_quantity) + reversed_quantity > abs(source.actual_quantity):
                raise ValidationError({"actual_quantity": "退货或红冲数量超过原送货数量"})
            reversed_spare_quantity = abs(already_reversed["spare_quantity"] or Decimal("0"))
            if abs(self.actual_spare_quantity) + reversed_spare_quantity > abs(source.actual_spare_quantity):
                raise ValidationError({"actual_spare_quantity": "退货或红冲备品数超过原送备品数"})


class SalesReturn(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="sales_returns")
    return_date = models.DateField(default=timezone.localdate)
    srm_number = models.CharField(max_length=80)
    reason = models.CharField(max_length=240)
    no_order = models.BooleanField(default=True)
    source_delivery = models.ForeignKey(
        DeliveryOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_returns"
    )
    posted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ("-return_date", "-number")

    def clean(self):
        if self.customer_id and self.customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise ValidationError({"customer": "销售退货必须关联客户"})
        if self.source_delivery_id and self.source_delivery.status != ApprovalStatus.APPROVED:
            raise ValidationError({"source_delivery": "有订单退货必须关联已审核送货单"})
        if self.source_delivery_id and self.source_delivery.customer_id != self.customer_id:
            raise ValidationError({"source_delivery": "来源送货单客户必须一致"})

    def approve(self, actor):
        lines = list(self.lines.select_related("material", "uom", "original_location", "return_location"))
        if not lines:
            raise ValidationError("销售退货单至少需要一条明细")
        sources = {
            line.sales_order_line_id
            or (line.source_delivery_line.sales_order_line_id if line.source_delivery_line_id else None)
            for line in lines
        }
        locked = {
            line.pk: line
            for line in SalesOrderLine.objects.select_for_update()
            .filter(pk__in=[key for key in sources if key])
            .order_by("pk")
        }
        for line in lines:
            source_id = line.sales_order_line_id or (
                line.source_delivery_line.sales_order_line_id if line.source_delivery_line_id else None
            )
            if source_id:
                line.sales_order_line = locked[source_id]
        for line in lines:
            line.full_clean()
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            if getattr(settings, "ERP_DELIVERY_POST_STOCK", False) and not line.material.no_stock_movement:
                StockBalance.adjust(
                    material=line.material,
                    location=line.return_location,
                    uom=line.uom,
                    quantity=line.quantity,
                    movement_type="sales_return",
                    source_model=self._meta.label_lower,
                    source_id=self.pk,
                    source_line_id=line.pk,
                    actor=actor,
                    batch_number=line.batch_number,
                )
            order_line = line.sales_order_line or (
                line.source_delivery_line.sales_order_line if line.source_delivery_line_id else None
            )
            if order_line:
                if line.quantity > order_line.delivered_quantity:
                    raise ValidationError({"quantity": "退货数量不能超过销售订单已送数量"})
                order_line.delivered_quantity -= line.quantity
                order_line.returned_quantity += line.quantity
                if order_line.line_status in ("C", "closed"):
                    order_line.line_status = "normal"
                    order_line.closed_by = ""
                    order_line.closed_at = None
                    order_line.save(update_fields=["line_status", "closed_by", "closed_at"])
                    AuditEvent.objects.create(
                        model=order_line._meta.label_lower,
                        object_id=str(order_line.pk),
                        action="reopen_for_replacement",
                        actor=actor,
                        payload={"sales_return": self.pk},
                    )
                order_line.save(update_fields=["delivered_quantity", "returned_quantity", "updated_at"])
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"SRT-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)

    def unapprove(self):
        if self.posted:
            raise ValidationError("已回写订单的退货单不能反审核修改")
        super().unapprove()


class SalesReturnLine(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="sales_return_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="sales_return_lines")
    quantity = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0.000001"))])
    original_location = models.ForeignKey(
        "Location", on_delete=models.PROTECT, related_name="originating_sales_returns"
    )
    return_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="received_sales_returns")
    batch_number = models.CharField(max_length=80, blank=True)
    sales_order_line = models.ForeignKey(
        "SalesOrderLine", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_return_lines"
    )
    source_delivery_line = models.ForeignKey(
        DeliveryOrderLine, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_return_lines"
    )

    class Meta:
        ordering = ("sales_return", "line_number")
        constraints = [models.UniqueConstraint(fields=("sales_return", "line_number"), name="uniq_sales_return_line")]

    def clean(self):
        if (
            self.sales_return_id
            and not self.sales_return.no_order
            and not self.sales_order_line_id
            and not self.source_delivery_line_id
        ):
            raise ValidationError({"sales_order_line": "有订单退货必须关联销售订单明细"})
        order_line = self.sales_order_line
        if self.source_delivery_line_id:
            source_order_line = self.source_delivery_line.sales_order_line
            if order_line and order_line.pk != source_order_line.pk:
                raise ValidationError({"sales_order_line": "销售订单明细必须与来源送货明细一致"})
            order_line = source_order_line
            if self.sales_return_id and self.sales_return.no_order:
                raise ValidationError({"source_delivery_line": "有订单退货才能关联来源送货明细"})
        if order_line and self.sales_return_id and order_line.order.customer_id != self.sales_return.customer_id:
            raise ValidationError({"sales_order_line": "销售订单客户必须与退货客户一致"})
        if order_line and (self.material_id != order_line.material_id or self.uom_id != order_line.uom_id):
            raise ValidationError("退货物料和单位必须与销售订单行一致")
        if order_line:
            from backend.delivery import commitments

            reserved = commitments([order_line.pk], exclude_return_line=self.pk)[order_line.pk][1]
            if self.quantity + reserved > order_line.delivered_quantity:
                raise ValidationError({"quantity": "本次退货与其他未审核退回合计超过净已送数量"})
        if (
            self.sales_return_id
            and self.sales_return.no_order
            and self.original_location_id
            and self.original_location.code.upper() == "FG01"
        ):
            if self.return_location.code.upper() != "RMA":
                raise ValidationError({"return_location": "FG01 无订单销售退货必须先进入实体不良仓 RMA"})
        if self.sales_return_id and self.source_delivery_line_id:
            source = self.source_delivery_line
            if source.delivery.status != ApprovalStatus.APPROVED:
                raise ValidationError("来源送货行必须已经审核")
            if self.sales_return.source_delivery_id and source.delivery_id != self.sales_return.source_delivery_id:
                raise ValidationError({"source_delivery_line": "退货行必须来自关联送货单"})
            if self.material_id != source.material_id or self.uom_id != source.uom_id:
                raise ValidationError("退货物料和单位必须与原送货明细一致")
            already_returned = source.sales_return_lines.filter(
                sales_return__status__in=(
                    ApprovalStatus.APPROVED,
                    ApprovalStatus.DRAFT,
                    ApprovalStatus.PENDING,
                    ApprovalStatus.REJECTED,
                ),
            ).exclude(pk=self.pk).aggregate(quantity=models.Sum("quantity"))["quantity"] or Decimal("0")
            reversed_quantity = source.red_flush_lines.filter(
                delivery__status__in=(
                    ApprovalStatus.APPROVED,
                    ApprovalStatus.DRAFT,
                    ApprovalStatus.PENDING,
                    ApprovalStatus.REJECTED,
                ),
                actual_quantity__lt=0,
            ).aggregate(total=models.Sum("actual_quantity"))["total"] or Decimal("0")
            if already_returned + abs(reversed_quantity) + self.quantity > source.actual_quantity:
                raise ValidationError({"quantity": "退货数量不能超过原送货数量"})
