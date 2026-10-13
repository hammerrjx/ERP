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
from backend.inventory_codes import PURCHASE_RECEIPT, PURCHASE_RETURN


class SupplierQuoteSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls, day=None):
        period = models.DateField().to_python(day or timezone.localdate()).strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SupplierQuote.objects.filter(number__startswith=f"MYPQ{period[2:]}").values_list(
                "number", flat=True
            )
            sequence.last_value = max(
                [sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())]
            )
            sequence.last_value += 1
            if sequence.last_value > 9999:
                raise ValidationError('本月四位报价流水已用尽')
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
            self.number = SupplierQuoteSequence.next_number(self.effective_date)
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


class PurchaseRequisitionSequence(models.Model):
    period = models.CharField(max_length=4, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)

    @classmethod
    @transaction.atomic
    def next_number(cls, day):
        period = day.strftime('%y%m')
        seq, _ = cls.objects.select_for_update().get_or_create(period=period)
        prefix = 'MYPR' + period
        values = PurchaseRequisition.objects.filter(number__startswith=prefix).values_list('number', flat=True)
        seq.last_value = max([seq.last_value, *(int(n[8:]) for n in values if len(n) == 12 and n[8:].isdigit())]) + 1
        if seq.last_value > 9999:
            raise ValidationError('当月请购编号已用尽')
        seq.save()
        return prefix + f'{seq.last_value:04d}'


class PurchaseRequisition(AuditedModel):
    class AggregationMode(models.TextChoices):
        NONE = "none", "不汇总"
        MATERIAL = "material", "按物料汇总"

    number = models.CharField(max_length=40, unique=True, blank=True)
    department = models.ForeignKey("Department", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisitions")
    site = models.CharField(max_length=20, default='1000')
    requisition_type = models.CharField(max_length=1, default='P')
    document_type = models.CharField(max_length=1, blank=True)
    requester = models.CharField(max_length=64, blank=True)
    version = models.PositiveIntegerField(default=0)
    print_count = models.PositiveIntegerField(default=0)
    source_profile = models.CharField(max_length=40, blank=True)
    source_snapshot = models.JSONField(default=dict, blank=True)
    request_date = models.DateField(default=timezone.localdate)
    needed_date = models.DateField(null=True, blank=True)
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
        if self.requisition_type != 'P':
            raise ValidationError('本期仅开放P采购请购，其他类型保留只读')
        if not self.source_profile and self.document_type != '':
            raise ValidationError('本期手工请购只开放普通单别')

    def approve(self, actor):
        self.clean()
        if not self.lines.exists():
            raise ValidationError('请购单至少需要一行')
        for line in self.lines.all():
            line.clean()
        super().approve(actor)

    def unapprove(self):
        self.clean()
        if self.lines.filter(converted_qty__gt=0).exists() or self.lines.filter(purchase_order_lines__isnull=False).exists():
            raise ValidationError('已关联采购，不能反审核')
        super().unapprove()

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = PurchaseRequisitionSequence.next_number(self.request_date)
        super().save(*args, **kwargs)


class PurchaseRequisitionLine(models.Model):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisition_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisition_lines")
    needed_date = models.DateField(null=True, blank=True)
    line_status = models.CharField(max_length=8, blank=True)
    source_kind = models.CharField(max_length=16, default='manual')
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)
    modification_count = models.PositiveIntegerField(default=0)
    source_snapshot = models.JSONField(default=dict, blank=True)
    material_snapshot = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    closed_by = models.CharField(max_length=64, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    close_reason = models.TextField(blank=True)
    mrp_demand_qty = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    on_order_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    available_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    safety_stock_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    requested_qty = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"))
    calculation_snapshot = models.JSONField(default=dict, editable=False)
    source_sales_order_line = models.ForeignKey(
        "SalesOrderLine", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisition_lines"
    )
    converted_qty = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
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
        quantity = self.requested_qty if self.pk or self.source_kind != 'legacy_mrp' else self.calculated_quantity()
        if not self.material_id and not self.material_snapshot.get('pt_part'):
            raise ValidationError('请选择物料')
        if self.material_id and self.uom_id != self.material.uom_id:
            raise ValidationError('请购数量必须使用物料库存单位')
        if self.converted_qty > quantity:
            raise ValidationError('请购数量不能小于已采购数量')
        if self.requisition_id and self.requisition.only_positive and quantity <= 0:
            raise ValidationError({"requested_qty": "只显示请购量大于 0 时不能保存零请购量明细"})

    def save(self, *args, **kwargs):
        if not self.pk and self.source_kind == 'legacy_mrp':
            self.requested_qty = self.calculated_quantity()
        if not self.calculation_snapshot:
            self.calculation_snapshot = {
            "rule": self.requisition.quantity_rule,
            "mrp_demand_qty": str(self.mrp_demand_qty),
            "on_order_qty": str(self.on_order_qty),
            "available_qty": str(self.available_qty),
            "safety_stock_qty": str(self.safety_stock_qty),
            "requested_qty": str(self.requested_qty),
        }
        with transaction.atomic():
            super().save(*args, **kwargs)
            # New trade rows retain one source each. Historical imported snapshots
            # are never rewritten; only the live allocation follows a quantity edit.
            if self.source_kind == 'trade_mrp' and self.calculation_snapshot.get('rule_version') == 'trade-net-v3':
                if not kwargs.get('update_fields') or 'requested_qty' in kwargs['update_fields']:
                    self.sources.update(quantity=self.requested_qty)


class PurchaseRequisitionSource(models.Model):
    line = models.ForeignKey(PurchaseRequisitionLine, on_delete=models.CASCADE, related_name='sources')
    sequence = models.PositiveIntegerField()
    source_number = models.CharField(max_length=80, blank=True)
    source_marker = models.CharField(max_length=80, blank=True)
    source_sequence = models.IntegerField(default=0)
    quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ('line', 'sequence')
        constraints = [models.UniqueConstraint(fields=('line', 'sequence'), name='uniq_requisition_source_line')]


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
    department = models.ForeignKey("Department", on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_orders")
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
    site = models.CharField(max_length=16, default="1000")
    document_type = models.CharField(max_length=16, default="standard")
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    shipping_address = models.CharField(max_length=240, blank=True)
    billing_address = models.CharField(max_length=240, blank=True)
    revision_label = models.CharField(max_length=40, blank=True)
    terms = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    delivery_approved_by = models.CharField(max_length=64, blank=True)
    delivery_approved_at = models.DateTimeField(null=True, blank=True)
    high_price_permission = models.CharField(max_length=80, blank=True)
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
            from .document_numbers import next_document_number
            prefix = {'production': 'MYPO', 'non_production': 'MYPUO', 'outsource': 'MYPS'}[self.purchase_type]
            self.number = next_document_number(prefix, self.order_date, 'PurchaseOrder')
        super().save(*args, **kwargs)


class PurchaseOrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="purchase_order_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="purchase_order_lines")
    quantity = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    received_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    returned_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
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
    allocation_managed = models.BooleanField(default=False)
    snapshot = models.JSONField(default=dict, blank=True)
    needed_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    notes = models.CharField(max_length=240, blank=True)
    line_status = models.CharField(max_length=1, blank=True)
    closed_by = models.CharField(max_length=64, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)
    modification_count = models.PositiveIntegerField(default=0)
    spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    over_receipt_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    extra_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    copper_price = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    accepted_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    accepted_inventory_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    received_spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    accepted_spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    accepted_spare_inventory_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    returned_spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    minimum_price = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    source_object = models.CharField(max_length=40, default="pod_det")

    class Meta:
        ordering = ("order", "line_number")
        constraints = [models.UniqueConstraint(fields=("order", "line_number"), name="uniq_purchase_order_line")]

    def clean(self):
        if self.uom_rate_m <= 0 or self.uom_rate_d <= 0:
            raise ValidationError('采购单位换算分子和分母必须大于0')

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.allocation_managed:
            return super().save(*args, **kwargs)
        from backend.requisitions import purchase_quantity, update_applied
        old = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
        ids = sorted({item.source_requisition_line_id for item in (old, self) if item and item.source_requisition_line_id})
        list(PurchaseRequisitionLine.objects.select_for_update().filter(pk__in=ids).order_by('pk'))
        deltas = {}
        for item, sign in ((old, -1), (self, 1)):
            if item and item.source_requisition_line_id:
                key = item.source_requisition_line_id
                deltas[key] = deltas.get(key, Decimal(0)) + sign * purchase_quantity(item)
        for key, delta in deltas.items():
            if delta:
                update_applied(key, delta)
        super().save(*args, **kwargs)


class GoodsReceipt(AuditedModel):
    site = models.CharField(max_length=16, default="1000")
    version = models.PositiveIntegerField(default=1)
    posting_version = models.PositiveIntegerField(default=0)
    imported = models.BooleanField(default=False)
    default_print_person = models.CharField(max_length=80, blank=True)
    print_count = models.PositiveIntegerField(default=0)
    iqc_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="iqc_receipts")
    raw_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="raw_receipts")
    class ReceiptType(models.TextChoices):
        NORMAL = "normal", "采购收货"
        NON_PRODUCTION = "non_production", "非生产收货"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="goods_receipts")
    # A receipt can contain lines from several purchase orders; the line is the source of truth.
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="goods_receipts")
    receipt_date = models.DateField(default=timezone.localdate)
    supplier_delivery_number = models.CharField(max_length=80, blank=True)
    receipt_type = models.CharField(max_length=20, choices=ReceiptType.choices, default=ReceiptType.NORMAL)
    notes = models.CharField(max_length=240, blank=True)
    posted = models.BooleanField(default=False, editable=False)
    # Source document header: dgyzx1.grn_mstr.
    source_object = models.CharField(max_length=40, default="grn_mstr")

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
        from backend.receiving import approve_document
        approve_document(self, actor)

    def unapprove(self, actor=''):
        from backend.receiving import unapprove_document
        unapprove_document(self, actor)

    def save(self, *args, **kwargs):
        if not self.number:
            from .document_numbers import next_document_number
            prefix = 'MYPUG' if self.receipt_type == self.ReceiptType.NON_PRODUCTION else 'MYPG'
            self.number = next_document_number(prefix, self.receipt_date, 'GoodsReceipt')
        super().save(*args, **kwargs)


class GoodsReceiptLine(models.Model):
    spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    pending_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    notes = models.CharField(max_length=240, blank=True)
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    purchase_order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name="receipt_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    quantity = models.DecimalField(max_digits=19, decimal_places=8)
    accepted_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    rejected_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="goods_receipt_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    # Source document detail: dgyzx1.grnd_det.
    source_object = models.CharField(max_length=40, default="grnd_det")

    class Meta:
        ordering = ("receipt", "line_number")
        constraints = [models.UniqueConstraint(fields=("receipt", "line_number"), name="uniq_goods_receipt_line")]

    def clean(self):
        from backend.receiving import validate_line
        validate_line(self)


class PurchaseReturn(AuditedModel):
    site = models.CharField(max_length=16, default="1000")
    version = models.PositiveIntegerField(default=1)
    posting_version = models.PositiveIntegerField(default=0)
    imported = models.BooleanField(default=False)
    default_print_person = models.CharField(max_length=80, blank=True)
    print_count = models.PositiveIntegerField(default=0)
    return_location = models.ForeignKey("Location", null=True, blank=True, on_delete=models.PROTECT, related_name="purchase_return_headers")
    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="purchase_returns")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_returns")
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
        from backend.receiving import approve_document
        approve_document(self, actor)

    def unapprove(self, actor=''):
        from backend.receiving import unapprove_document
        unapprove_document(self, actor)

    def save(self, *args, **kwargs):
        if not self.number:
            from .document_numbers import next_document_number
            self.number = next_document_number('MYPT', self.return_date, 'PurchaseReturn')
        super().save(*args, **kwargs)


class PurchaseReturnLine(models.Model):
    spare_quantity = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=1)
    iqc_number = models.CharField(max_length=40, blank=True)
    iqc_line = models.PositiveIntegerField(default=0)
    replacement_line = models.OneToOneField(PurchaseOrderLine, null=True, blank=True, on_delete=models.PROTECT, related_name="replacement_source")
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    purchase_order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name="return_lines")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="purchase_return_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="purchase_return_lines")
    quantity = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    source_location = models.ForeignKey("Location", on_delete=models.PROTECT, related_name="purchase_return_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    reason = models.CharField(max_length=240)

    class Meta:
        ordering = ("purchase_return", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("purchase_return", "line_number"), name="uniq_purchase_return_line")
        ]

    def clean(self):
        from backend.receiving import validate_line
        validate_line(self)


from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(pre_delete, sender=PurchaseOrderLine)
def release_requisition_on_purchase_delete(sender, instance, **kwargs):
    if instance.source_requisition_line_id and not instance.allocation_managed:
        from backend.requisitions import purchase_quantity, update_applied
        update_applied(instance.source_requisition_line_id, -purchase_quantity(instance))


class PurchaseOrderAllocation(models.Model):
    """podr_det: purchase-unit and stock-unit quantities allocated to a requisition."""
    line = models.ForeignKey(PurchaseOrderLine, on_delete=models.CASCADE, related_name="allocations")
    sequence = models.PositiveIntegerField()
    kind = models.CharField(max_length=1, choices=(("1", "请购单"), ("2", "额外采购")))
    requisition_line = models.ForeignKey(PurchaseRequisitionLine, null=True, blank=True,
        on_delete=models.PROTECT, related_name="purchase_allocations")
    quantity = models.DecimalField(max_digits=19, decimal_places=8)
    inventory_quantity = models.DecimalField(max_digits=19, decimal_places=8)
    snapshot = models.JSONField(default=dict, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)
    modification_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("line", "sequence")
        constraints = [models.UniqueConstraint(fields=("line", "sequence"), name="uniq_po_allocation_sequence")]

    @transaction.atomic
    def save(self, *args, **kwargs):
        from backend.requisitions import update_applied
        if self.quantity < 0 or self.inventory_quantity < 0:
            raise ValidationError('来源分配数量不能为负数')
        if (self.kind == '1') != bool(self.requisition_line_id):
            raise ValidationError('请购分配必须关联请购行，额外采购不能关联请购行')
        if self.requisition_line_id and self.line.material_id != self.requisition_line.material_id:
            raise ValidationError('来源请购物料与采购物料不一致')
        old = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
        ids = sorted({a.requisition_line_id for a in (old, self) if a and a.kind == "1" and a.requisition_line_id})
        list(PurchaseRequisitionLine.objects.select_for_update().filter(pk__in=ids).order_by('pk'))
        deltas = {}
        for a, sign in ((old, -1), (self, 1)):
            if a and a.kind == '1' and a.requisition_line_id:
                deltas[a.requisition_line_id] = deltas.get(a.requisition_line_id, Decimal(0)) + sign * a.inventory_quantity
        for key, delta in deltas.items():
            if delta: update_applied(key, delta)
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=PurchaseOrderAllocation)
def release_purchase_allocation(sender, instance, **kwargs):
    if instance.kind == '1' and instance.requisition_line_id:
        from backend.requisitions import update_applied
        update_applied(instance.requisition_line_id, -instance.inventory_quantity)


class PurchaseGeneration(models.Model):
    key = models.CharField(max_length=80, unique=True)
    actor = models.CharField(max_length=150)
    request_hash = models.CharField(max_length=64)
    order_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
