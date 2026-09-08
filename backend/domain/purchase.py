"""Purchase domain models; Django app label remains backend."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from .base import ApprovalStatus, AuditedModel
from .inventory import StockBalance
from .master_data import Partner


class SupplierQuoteSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls):
        period = timezone.localdate().strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SupplierQuote.objects.filter(number__startswith=f"MYPQ{period[2:]}").values_list(
                "number", flat=True
            )
            sequence.last_value = max(
                [sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())]
            )
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYPQ{period[2:]}{sequence.last_value:04d}"


class SupplierQuote(AuditedModel):
    class QuoteType(models.TextChoices):
        PURCHASE = "purchase", "采购报价"
        OUTSOURCE = "outsource", "外协报价"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="supplier_quotes")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="supplier_quotes")
    business_group = models.ForeignKey(
        "BusinessGroup",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="supplier_quotes",
    )
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="supplier_quotes")
    purchase_uom = models.ForeignKey(
        "Uom", on_delete=models.PROTECT, null=True, blank=True, related_name="supplier_quotes"
    )
    uom_rate_m = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    uom_rate_d = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    quote_type = models.CharField(max_length=16, choices=QuoteType.choices)
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    material_unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    processing_unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    min_purchase_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    min_pack_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    delivery_days = models.PositiveIntegerField(default=0)
    operation = models.ForeignKey(
        "RoutingOperation", on_delete=models.PROTECT, null=True, blank=True, related_name="supplier_quotes"
    )
    parent_material = models.ForeignKey(
        "Material", on_delete=models.PROTECT, null=True, blank=True, related_name="outsource_supplier_quotes"
    )
    notes = models.CharField(max_length=240, blank=True)
    workflow_status = models.CharField(max_length=1, blank=True)
    is_ratified = models.BooleanField(default=False)
    ratified_by = models.CharField(max_length=64, blank=True)
    ratified_at = models.DateTimeField(null=True, blank=True)
    is_sales_confirmed = models.BooleanField(default=False)
    sales_confirmed_by = models.CharField(max_length=64, blank=True)
    sales_confirmed_at = models.DateTimeField(null=True, blank=True)
    modification_count = models.PositiveIntegerField(default=0)
    source_object = models.CharField(max_length=40, default="pc_mstr")

    class Meta:
        ordering = ("-effective_date", "-number")

    def clean(self):
        if self.supplier.kind not in {Partner.PartnerKind.SUPPLIER, Partner.PartnerKind.BOTH}:
            raise ValidationError("报价必须关联供应商")
        if self.supplier.status != ApprovalStatus.APPROVED:
            raise ValidationError("供应商审核通过后才能建立报价")
        if self.material.status != ApprovalStatus.APPROVED:
            raise ValidationError("物料审核通过后才能建立报价")
        if self.expiry_date and self.expiry_date < self.effective_date:
            raise ValidationError({"expiry_date": "失效日期不能早于生效日期"})
        if self.supplier.currency_id and self.currency_id != self.supplier.currency_id:
            raise ValidationError({"currency": "报价币种必须与供应商常用币种一致"})
        if self.quote_type == self.QuoteType.PURCHASE and self.processing_unit_price:
            raise ValidationError("采购报价应填写材料单价，不能填写加工单价")
        if self.quote_type == self.QuoteType.OUTSOURCE and self.material_unit_price:
            raise ValidationError("外协报价应填写加工单价，不能填写材料单价")
        if self.quote_type == self.QuoteType.OUTSOURCE and not self.operation_id:
            raise ValidationError({"operation": "外协报价必须关联工序"})
        new_end = self.expiry_date or date.max
        overlap = (
            SupplierQuote.objects.filter(
                supplier=self.supplier,
                material=self.material,
                currency=self.currency,
                quote_type=self.quote_type,
            )
            .exclude(pk=self.pk)
            .filter(
                effective_date__lte=new_end,
            )
            .filter(
                models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gte=self.effective_date),
            )
        )
        if self.quote_type == self.QuoteType.OUTSOURCE:
            overlap = overlap.filter(operation=self.operation)
        if overlap.exists():
            raise ValidationError("同一供应商、物料、币种、报价类型和工序的有效日期不能重叠")

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = SupplierQuoteSequence.next_number()
        self.unit_price = self.material_unit_price + self.processing_unit_price
        super().save(*args, **kwargs)

    @property
    def untaxed_unit_price(self):
        if not self.tax_included:
            return self.unit_price
        divisor = Decimal("1") + self.tax_rate / Decimal("100")
        return (self.unit_price / divisor).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)

    @property
    def effective_min_purchase_qty(self):
        return self.min_purchase_qty or self.material.min_purchase_qty

    @property
    def effective_min_pack_qty(self):
        return self.min_pack_qty or self.material.min_pack_qty

    def price_for(self, quantity):
        quantity = Decimal(str(quantity))
        tiers = self.lines.order_by("-min_qty")
        if tiers.exists():
            tier = tiers.filter(min_qty__lte=quantity).first()
            if tier:
                return tier.unit_price, tier
        return self.unit_price, None

    def confirm(self, actor):
        if self.status in {ApprovalStatus.DRAFT, ApprovalStatus.REJECTED}:
            self.status = ApprovalStatus.PENDING
        elif self.status != ApprovalStatus.PENDING:
            raise ValidationError("只有草稿、已驳回或待审核报价可以采购确认")
        self.is_confirmed = True
        self.confirmed_by = actor
        self.confirmed_at = timezone.now()
        self.rejection_reason = ""

    def unconfirm(self):
        if self.status != ApprovalStatus.PENDING or not self.is_confirmed:
            raise ValidationError("只有待审核的采购确认报价可以反确认")
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None

    def approve(self, actor):
        if not self.is_confirmed:
            raise ValidationError("报价采购确认后才能审核")
        super().approve(actor)

    def ratify(self, actor):
        if self.status != ApprovalStatus.APPROVED or self.is_ratified:
            raise ValidationError("只有已审核且未核准的报价可以核准")
        self.is_ratified = True
        self.ratified_by = actor
        self.ratified_at = timezone.now()

    def unratify(self):
        if not self.is_ratified:
            raise ValidationError("报价尚未核准")
        self.is_ratified = False
        self.ratified_by = ""
        self.ratified_at = None

    def sales_confirm(self, actor):
        if self.status == ApprovalStatus.VOID:
            raise ValidationError("已作废报价不能销售确认")
        self.is_sales_confirmed = True
        self.sales_confirmed_by = actor
        self.sales_confirmed_at = timezone.now()

    def sales_unconfirm(self):
        if not self.is_sales_confirmed:
            raise ValidationError("报价尚未销售确认")
        self.is_sales_confirmed = False
        self.sales_confirmed_by = ""
        self.sales_confirmed_at = None


class SupplierQuoteLine(models.Model):
    quote = models.ForeignKey(SupplierQuote, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField(default=1)
    min_qty = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    material_unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))]
    )
    processing_unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))]
    )
    unit_price = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    notes = models.CharField(max_length=240, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    modification_count = models.PositiveIntegerField(default=0)
    source_object = models.CharField(max_length=40, default="pcd_det")

    class Meta:
        ordering = ("quote", "min_qty", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("quote", "min_qty"), name="uniq_quote_min_qty"),
            models.UniqueConstraint(fields=("quote", "line_number"), name="uniq_supplier_quote_line"),
        ]

    def clean(self):
        if self.quote.quote_type == SupplierQuote.QuoteType.PURCHASE and self.processing_unit_price is not None:
            raise ValidationError("采购报价明细不能填写加工单价")
        if self.quote.quote_type == SupplierQuote.QuoteType.OUTSOURCE and self.material_unit_price is not None:
            raise ValidationError("外协报价明细不能填写材料单价")

    def save(self, *args, **kwargs):
        self.unit_price = (self.material_unit_price or Decimal("0")) + (self.processing_unit_price or Decimal("0"))
        super().save(*args, **kwargs)

    @property
    def untaxed_unit_price(self):
        if not self.quote.tax_included:
            return self.unit_price
        divisor = Decimal("1") + self.quote.tax_rate / Decimal("100")
        return (self.unit_price / divisor).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


class PurchaseRequisition(AuditedModel):
    class AggregationMode(models.TextChoices):
        NONE = "none", "不汇总"
        MATERIAL = "material", "按物料汇总"

    number = models.CharField(max_length=40, unique=True, blank=True)
    department = models.ForeignKey("Department", on_delete=models.PROTECT, related_name="purchase_requisitions")
    request_date = models.DateField(default=timezone.localdate)
    needed_date = models.DateField()
    aggregation_mode = models.CharField(max_length=16, choices=AggregationMode.choices, default=AggregationMode.NONE)
    quantity_rule = models.CharField(max_length=16, default="mrp")
    only_positive = models.BooleanField(default=True)
    source_sales_order = models.ForeignKey(
        "SalesOrder", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisitions"
    )
    conversion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"), editable=False)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="pr_mstr")

    class Meta:
        ordering = ("-request_date", "-number")

    def clean(self):
        if self.needed_date and self.request_date and self.needed_date < self.request_date:
            raise ValidationError({"needed_date": "需求日期不能早于请购日期"})

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"PR-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class PurchaseRequisitionLine(models.Model):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="purchase_requisition_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="purchase_requisition_lines")
    mrp_demand_qty = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    on_order_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    available_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    safety_stock_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    requested_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), editable=False)
    calculation_snapshot = models.JSONField(default=dict, editable=False)
    source_sales_order_line = models.ForeignKey(
        "SalesOrderLine", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisition_lines"
    )
    converted_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    source_object = models.CharField(max_length=40, default="req_mstr")
    source_detail_object = models.CharField(max_length=40, default="reqd_det")

    class Meta:
        ordering = ("requisition", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("requisition", "line_number"), name="uniq_purchase_requisition_line")
        ]

    def calculated_quantity(self):
        return max(self.mrp_demand_qty + self.safety_stock_qty - self.on_order_qty - self.available_qty, Decimal("0"))

    def clean(self):
        quantity = self.calculated_quantity()
        if (
            self.requisition_id
            and self.requisition.aggregation_mode == PurchaseRequisition.AggregationMode.NONE
            and not self.source_sales_order_line_id
        ):
            raise ValidationError({"source_sales_order_line": "不汇总请购必须保留销售订单明细来源"})
        if self.requisition_id and self.requisition.only_positive and quantity <= 0:
            raise ValidationError({"requested_qty": "只显示请购量大于 0 时不能保存零请购量明细"})

    def save(self, *args, **kwargs):
        self.requested_qty = self.calculated_quantity()
        self.calculation_snapshot = {
            "rule": self.requisition.quantity_rule,
            "mrp_demand_qty": str(self.mrp_demand_qty),
            "on_order_qty": str(self.on_order_qty),
            "available_qty": str(self.available_qty),
            "safety_stock_qty": str(self.safety_stock_qty),
            "requested_qty": str(self.requested_qty),
        }
        super().save(*args, **kwargs)


class RequestForQuotation(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT, related_name="rfqs")
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="rfqs")
    inquiry_date = models.DateField(default=timezone.localdate)
    response_due_date = models.DateField()
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ("-inquiry_date", "-number")

    def clean(self):
        if self.response_due_date and self.response_due_date < self.inquiry_date:
            raise ValidationError({"response_due_date": "报价截止日期不能早于询价日期"})

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"RFQ-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class RfqLine(models.Model):
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    requisition_line = models.ForeignKey(PurchaseRequisitionLine, on_delete=models.PROTECT, related_name="rfq_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="rfq_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="rfq_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])

    class Meta:
        ordering = ("rfq", "line_number")
        constraints = [models.UniqueConstraint(fields=("rfq", "line_number"), name="uniq_rfq_line")]

    def clean(self):
        if self.rfq_id and self.requisition_line_id and self.requisition_line.requisition_id != self.rfq.requisition_id:
            raise ValidationError({"requisition_line": "询价行必须来自询价单关联的请购单"})
        if self.material_id and self.requisition_line_id and self.material_id != self.requisition_line.material_id:
            raise ValidationError({"material": "询价物料必须与请购行一致"})


class SupplierInquiry(models.Model):
    rfq_line = models.ForeignKey(RfqLine, on_delete=models.CASCADE, related_name="supplier_responses")
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="inquiry_responses")
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    tax_rate = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    promised_date = models.DateField()
    selected = models.BooleanField(default=False)
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ("rfq_line", "unit_price", "promised_date")
        constraints = [models.UniqueConstraint(fields=("rfq_line", "supplier"), name="uniq_rfq_supplier_response")]

    def clean(self):
        if self.supplier_id and self.supplier.kind not in {Partner.PartnerKind.SUPPLIER, Partner.PartnerKind.BOTH}:
            raise ValidationError({"supplier": "询价响应必须关联供应商"})
        if self.supplier_id and self.supplier.status != ApprovalStatus.APPROVED:
            raise ValidationError({"supplier": "供应商审核通过后才能参与询价"})


class PurchaseOrder(AuditedModel):
    class PurchaseType(models.TextChoices):
        PRODUCTION = "production", "生产采购"
        NON_PRODUCTION = "non_production", "非生产采购"
        OUTSOURCE = "outsource", "外协采购"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="purchase_orders")
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="purchase_orders")
    department = models.ForeignKey("Department", on_delete=models.PROTECT, related_name="purchase_orders")
    order_date = models.DateField(default=timezone.localdate)
    buyer = models.CharField(max_length=64, blank=True)
    payment_method = models.CharField(max_length=80)
    tax_rate = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    purchase_type = models.CharField(max_length=20, choices=PurchaseType.choices, default=PurchaseType.PRODUCTION)
    cost_center = models.ForeignKey(
        "Department", on_delete=models.PROTECT, null=True, blank=True, related_name="cost_center_purchase_orders"
    )
    notes = models.CharField(max_length=240, blank=True)
    source_requisition = models.ForeignKey(
        PurchaseRequisition, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_orders"
    )
    source_purchase_return = models.ForeignKey(
        "PurchaseReturn", on_delete=models.PROTECT, null=True, blank=True, related_name="replacement_orders"
    )
    source_object = models.CharField(max_length=40, default="po_mstr")

    class Meta:
        ordering = ("-order_date", "-number")

    def clean(self):
        if self.supplier_id and self.supplier.kind not in {Partner.PartnerKind.SUPPLIER, Partner.PartnerKind.BOTH}:
            raise ValidationError({"supplier": "采购单必须关联供应商"})
        if self.supplier_id and self.supplier.status != ApprovalStatus.APPROVED:
            raise ValidationError({"supplier": "供应商审核通过后才能建立采购单"})
        if self.purchase_type == self.PurchaseType.NON_PRODUCTION and not self.cost_center:
            raise ValidationError({"cost_center": "非生产采购必须填写成本中心 CC"})

    def approve(self, actor):
        if not self.lines.exists():
            raise ValidationError("采购单至少需要一条明细")
        for line in self.lines.all():
            line.full_clean()
        super().approve(actor)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"PO-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class PurchaseOrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="purchase_order_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="purchase_order_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    received_quantity = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    returned_quantity = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    source_requisition_line = models.ForeignKey(
        PurchaseRequisitionLine, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines"
    )
    source_supplier_quote = models.ForeignKey(
        SupplierQuote, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines"
    )
    source_supplier_quote_line = models.ForeignKey(
        SupplierQuoteLine, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines"
    )
    source_object = models.CharField(max_length=40, default="pod_det")

    class Meta:
        ordering = ("order", "line_number")
        constraints = [models.UniqueConstraint(fields=("order", "line_number"), name="uniq_purchase_order_line")]


class GoodsReceipt(AuditedModel):
    class ReceiptType(models.TextChoices):
        NORMAL = "normal", "采购收货"
        NON_PRODUCTION = "non_production", "非生产收货"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="goods_receipts")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="goods_receipts")
    receipt_date = models.DateField(default=timezone.localdate)
    supplier_delivery_number = models.CharField(max_length=80, blank=True)
    receipt_type = models.CharField(max_length=20, choices=ReceiptType.choices, default=ReceiptType.NORMAL)
    notes = models.CharField(max_length=240, blank=True)
    posted = models.BooleanField(default=False, editable=False)
    # Legacy receiving header is exposed by coerp_dgyzx1.dbo.v_prh_receiver.
    source_object = models.CharField(max_length=40, default="prh_receiver")

    class Meta:
        ordering = ("-receipt_date", "-number")

    def clean(self):
        if self.purchase_order_id and self.supplier_id != self.purchase_order.supplier_id:
            raise ValidationError({"supplier": "收货供应商必须与采购单一致"})
        if (
            self.purchase_order_id
            and self.purchase_order.purchase_type == PurchaseOrder.PurchaseType.NON_PRODUCTION
            and self.receipt_type != self.ReceiptType.NON_PRODUCTION
        ):
            raise ValidationError({"receipt_type": "非生产采购必须使用非生产收货"})
        if (
            self.purchase_order_id
            and self.purchase_order.purchase_type != PurchaseOrder.PurchaseType.NON_PRODUCTION
            and self.receipt_type == self.ReceiptType.NON_PRODUCTION
        ):
            raise ValidationError({"receipt_type": "生产采购不能使用非生产收货"})

    def approve(self, actor):
        if self.purchase_order.status != ApprovalStatus.APPROVED:
            raise ValidationError("采购单审核通过后才能收货")
        lines = list(self.lines.select_related("purchase_order_line", "material", "uom", "location"))
        if not lines:
            raise ValidationError("收货单至少需要一条明细")
        for line in lines:
            line.full_clean()
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            order_line = line.purchase_order_line
            order_line.received_quantity += line.quantity
            order_line.save(update_fields=["received_quantity"])
            if self.receipt_type == self.ReceiptType.NORMAL and not line.material.no_stock_movement:
                StockBalance.adjust(
                    material=line.material,
                    location=line.location,
                    uom=line.uom,
                    quantity=line.quantity,
                    movement_type="purchase_receipt",
                    source_model=self._meta.label_lower,
                    source_id=self.pk,
                    source_line_id=line.pk,
                    actor=actor,
                    batch_number=line.batch_number,
                )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"GR-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class GoodsReceiptLine(models.Model):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    purchase_order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name="receipt_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    accepted_quantity = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    rejected_quantity = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    # Legacy receiving detail is exposed by coerp_dgyzx1.dbo.v_prh_hist.
    source_object = models.CharField(max_length=40, default="prh_hist")

    class Meta:
        ordering = ("receipt", "line_number")
        constraints = [models.UniqueConstraint(fields=("receipt", "line_number"), name="uniq_goods_receipt_line")]

    def clean(self):
        order_line = self.purchase_order_line
        if self.receipt_id and order_line.order_id != self.receipt.purchase_order_id:
            raise ValidationError({"purchase_order_line": "收货行必须来自收货单关联采购单"})
        if self.material_id != order_line.material_id or self.uom_id != order_line.uom_id:
            raise ValidationError("收货物料和单位必须与采购行一致")
        tolerance = order_line.quantity * (Decimal("1") + self.receipt.supplier.over_receipt_ratio / Decimal("100"))
        if order_line.received_quantity + self.quantity > tolerance:
            raise ValidationError({"quantity": "收货数量超过采购数量及允许超收比例"})


class PayableVoucher(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    voucher_date = models.DateField(default=timezone.localdate)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="payable_vouchers")
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="payable_vouchers")
    payment_method = models.CharField(max_length=80)
    due_date = models.DateField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(Decimal("0"))])
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    invoice_number = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="ap_mstr")

    class Meta:
        ordering = ("-voucher_date", "-number")

    def recalculate(self):
        totals = self.lines.aggregate(
            net=models.Sum("net_amount"),
            tax=models.Sum("tax_amount"),
            gross=models.Sum("gross_amount"),
        )
        self.net_amount = totals["net"] or Decimal("0")
        self.tax_amount = totals["tax"] or Decimal("0")
        self.gross_amount = totals["gross"] or Decimal("0")
        self.save(update_fields=["net_amount", "tax_amount", "gross_amount", "updated_at"])

    def approve(self, actor):
        if not self.lines.exists():
            raise ValidationError("应付凭单至少需要一条来源明细")
        super().approve(actor)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"AP-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class PayableVoucherLine(models.Model):
    voucher = models.ForeignKey(PayableVoucher, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    source_receipt_line = models.OneToOneField(
        GoodsReceiptLine,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payable_voucher_line",
    )
    source_purchase_return_line = models.OneToOneField(
        "PurchaseReturnLine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payable_voucher_line",
    )
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="payable_voucher_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="payable_voucher_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    source_object = models.CharField(max_length=40, default="apd_det")

    class Meta:
        ordering = ("voucher", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("voucher", "line_number"), name="uniq_payable_voucher_line"),
            models.CheckConstraint(
                condition=(
                    models.Q(source_receipt_line__isnull=False, source_purchase_return_line__isnull=True)
                    | models.Q(source_receipt_line__isnull=True, source_purchase_return_line__isnull=False)
                ),
                name="payable_line_exactly_one_source",
            ),
        ]

    def clean(self):
        if bool(self.source_receipt_line_id) == bool(self.source_purchase_return_line_id):
            raise ValidationError("应付来源必须且只能选择收货明细或采购退货明细")
        source = self.source_receipt_line if self.source_receipt_line_id else self.source_purchase_return_line
        order_line = source.purchase_order_line
        document = source.receipt if self.source_receipt_line_id else source.purchase_return
        if document.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核收货或采购退货明细可以生成应付凭单")
        if self.voucher_id and (
            self.voucher.supplier_id != document.supplier_id
            or self.voucher.currency_id != order_line.order.currency_id
            or self.voucher.payment_method != order_line.order.payment_method
            or self.voucher.tax_rate != order_line.order.tax_rate
        ):
            raise ValidationError("应付凭单供应商、币种、支付方式和税率必须与来源采购单一致")
        if self.material_id != source.material_id or self.uom_id != source.uom_id:
            raise ValidationError("应付凭单物料和单位必须与收货明细一致")
        if self.quantity != source.quantity:
            raise ValidationError({"quantity": "应付数量必须与来源明细一致"})
        if self.unit_price != order_line.unit_price:
            raise ValidationError({"unit_price": "应付单价必须与来源采购行一致"})

    def save(self, *args, **kwargs):
        sign = Decimal("1") if self.source_receipt_line_id else Decimal("-1")
        self.net_amount = (sign * self.quantity * self.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.tax_amount = (self.net_amount * self.voucher.tax_rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self.gross_amount = self.net_amount + self.tax_amount
        super().save(*args, **kwargs)
        self.voucher.recalculate()


class PurchaseReturn(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="purchase_returns")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="purchase_returns")
    return_date = models.DateField(default=timezone.localdate)
    replenishment = models.BooleanField(default=True)
    reason = models.CharField(max_length=240)
    posted = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ("-return_date", "-number")

    def clean(self):
        if self.purchase_order_id and self.supplier_id != self.purchase_order.supplier_id:
            raise ValidationError({"supplier": "退货供应商必须与采购单一致"})

    def approve(self, actor):
        if self.purchase_order.status != ApprovalStatus.APPROVED:
            raise ValidationError("采购单审核通过后才能退货")
        lines = list(self.lines.select_related("purchase_order_line", "material", "uom", "source_location"))
        if not lines:
            raise ValidationError("采购退货单至少需要一条明细")
        for line in lines:
            line.full_clean()
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            StockBalance.adjust(
                material=line.material,
                location=line.source_location,
                uom=line.uom,
                quantity=-line.quantity,
                movement_type="purchase_return",
                source_model=self._meta.label_lower,
                source_id=self.pk,
                source_line_id=line.pk,
                actor=actor,
                batch_number=line.batch_number,
            )
            order_line = line.purchase_order_line
            order_line.returned_quantity += line.quantity
            order_line.save(update_fields=["returned_quantity"])
        if self.replenishment and not self.replacement_orders.exists():
            source = self.purchase_order
            replacement = PurchaseOrder.objects.create(
                supplier=source.supplier,
                currency=source.currency,
                department=source.department,
                order_date=timezone.localdate(),
                buyer=source.buyer,
                payment_method=source.payment_method,
                tax_rate=source.tax_rate,
                promised_date=max(line.purchase_order_line.promised_date for line in lines),
                purchase_type=source.purchase_type,
                cost_center=source.cost_center,
                notes=f"采购退货 {self.number} 自动补货",
                source_purchase_return=self,
                created_by=actor,
            )
            for index, line in enumerate(lines, 1):
                PurchaseOrderLine.objects.create(
                    order=replacement,
                    line_number=index * 10,
                    material=line.material,
                    uom=line.uom,
                    quantity=line.quantity,
                    unit_price=line.purchase_order_line.unit_price,
                    promised_date=line.purchase_order_line.promised_date,
                    source_requisition_line=line.purchase_order_line.source_requisition_line,
                )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"RTV-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class PurchaseReturnLine(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    purchase_order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name="return_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="purchase_return_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="purchase_return_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    source_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="purchase_return_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    reason = models.CharField(max_length=240)

    class Meta:
        ordering = ("purchase_return", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("purchase_return", "line_number"), name="uniq_purchase_return_line")
        ]

    def clean(self):
        order_line = self.purchase_order_line
        if self.purchase_return_id and order_line.order_id != self.purchase_return.purchase_order_id:
            raise ValidationError({"purchase_order_line": "退货行必须来自退货单关联采购单"})
        if self.material_id != order_line.material_id or self.uom_id != order_line.uom_id:
            raise ValidationError("退货物料和单位必须与采购行一致")
        if order_line.returned_quantity + self.quantity > order_line.quantity:
            raise ValidationError({"quantity": "退货数量不能超过采购数量"})
