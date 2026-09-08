"""Sales domain models; Django app label remains backend."""

from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from .base import ApprovalStatus, AuditedModel
from .master_data import MaterialUomConversion, Partner


class CustomerMaterial(models.Model):
    customer = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="customer_materials")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="customer_materials")
    customer_code = models.CharField(max_length=80)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_specification = models.CharField(max_length=240, blank=True)
    customer_uom = models.ForeignKey(
        "Uom", on_delete=models.PROTECT, null=True, blank=True, related_name="customer_materials"
    )
    customer_uom_rate_m = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    customer_uom_rate_d = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    customer_barcode = models.CharField(max_length=80, blank=True)
    terminal_customer_code = models.CharField(max_length=80, blank=True)
    terminal_customer_name = models.CharField(max_length=160, blank=True)
    enabled = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("customer", "material", "customer_code"), name="uniq_customer_material_external_code"
            )
        ]

    def clean(self):
        if self.customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise ValidationError("客户物料只能关联客户合作伙伴")


class SalesQuoteSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls):
        period = timezone.localdate().strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SalesQuote.objects.filter(number__startswith=f"MYSQ{period[2:]}").values_list(
                "number", flat=True
            )
            sequence.last_value = max(
                [sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())]
            )
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYSQ{period[2:]}{sequence.last_value:04d}"


class SalesOrderSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls, order_date=None):
        period = (order_date or timezone.localdate()).strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SalesOrder.objects.filter(number__startswith=f"MYSO{period[2:]}").values_list(
                "number", flat=True
            )
            sequence.last_value = max(
                [sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())]
            )
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYSO{period[2:]}{sequence.last_value:04d}"


class SalesQuote(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="sales_quotes")
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="sales_quotes")
    effective_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(null=True, blank=True)
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    discount_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))]
    )
    backup_ratio = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    address_code = models.ForeignKey(
        "CustomerAddress", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_quotes"
    )
    address_snapshot = models.CharField(max_length=240, blank=True)
    address = models.CharField(max_length=240, blank=True)
    payment_terms = models.CharField(max_length=80, blank=True)
    usage = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    modification_count = models.PositiveIntegerField(default=0)
    is_ratified = models.BooleanField(default=False)
    ratified_by = models.CharField(max_length=64, blank=True)
    ratified_at = models.DateTimeField(null=True, blank=True)
    source_object = models.CharField(max_length=40, default="sc_mstr")

    class Meta:
        ordering = ("-effective_date", "-number")

    def clean(self):
        if self.customer_id and self.customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise ValidationError({"customer": "销售报价必须关联客户"})
        if self.address_code_id and self.address_code.customer_id != self.customer_id:
            raise ValidationError({"address_code": "报价地址必须属于当前客户"})
        if self.expiry_date and self.expiry_date < self.effective_date:
            raise ValidationError({"expiry_date": "失效日期不能早于生效日期"})

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = SalesQuoteSequence.next_number()
        if self.address_code_id:
            self.address_snapshot = self.address_code.address
            self.address = self.address_snapshot
        elif self.address_snapshot:
            self.address = self.address_snapshot
        super().save(*args, **kwargs)

    def confirm(self, actor):
        if self.status not in {ApprovalStatus.DRAFT, ApprovalStatus.REJECTED}:
            raise ValidationError("只有草稿或已驳回报价可以确认")
        self.status = ApprovalStatus.PENDING
        self.is_confirmed = True
        self.confirmed_by = actor
        self.confirmed_at = timezone.now()
        self.rejection_reason = ""

    def unconfirm(self):
        if self.status != ApprovalStatus.PENDING or not self.is_confirmed:
            raise ValidationError("只有待审核报价可以反确认")
        self.status = ApprovalStatus.DRAFT
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None

    def approve(self, actor):
        if self.status != ApprovalStatus.PENDING or not self.is_confirmed:
            raise ValidationError("只有已确认的待审核报价可以审核")
        super().approve(actor)

    def unapprove(self):
        if self.is_ratified:
            raise ValidationError("已核准报价必须先反核准")
        super().unapprove()

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


class SalesQuoteLine(models.Model):
    class PriceType(models.TextChoices):
        FUTURES = "1", "期货价"
        PERIOD = "2", "期目价"
        SPOT = "3", "即日价"
        NEGOTIATED = "4", "议价"

    quote = models.ForeignKey(SalesQuote, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="sales_quote_lines")
    customer_material = models.ForeignKey(
        CustomerMaterial, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_quote_lines"
    )
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="sales_quote_lines")
    quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    price_type = models.CharField(max_length=1, choices=PriceType.choices, default=PriceType.FUTURES)
    tax_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    uom_rate_m = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    uom_rate_d = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    customer_material_code = models.CharField(max_length=80, blank=True)
    customer_material_name = models.CharField(max_length=160, blank=True)
    terminal_customer_code = models.CharField(max_length=80, blank=True)
    terminal_customer_name = models.CharField(max_length=160, blank=True)
    material_name = models.CharField(max_length=200, blank=True)
    material_specification = models.CharField(max_length=240, blank=True)
    promised_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ("quote", "line_number")
        constraints = [models.UniqueConstraint(fields=("quote", "line_number"), name="uniq_sales_quote_line")]

    def clean(self):
        if self.customer_material_id:
            if self.customer_material.customer_id != self.quote.customer_id:
                raise ValidationError({"customer_material": "客户物料不属于当前报价客户"})
            if self.customer_material.material_id != self.material_id:
                raise ValidationError({"customer_material": "客户物料与本方物料编码不匹配"})

    @property
    def discounted_unit_price(self):
        return (self.unit_price * self.quote.discount_rate / Decimal("100")).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )

    @property
    def untaxed_unit_price(self):
        if not self.quote.tax_included:
            return self.unit_price
        divisor = Decimal("1") + self.quote.tax_rate / Decimal("100")
        return (self.unit_price / divisor).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


class SalesQuoteTier(models.Model):
    quote_line = models.ForeignKey(SalesQuoteLine, on_delete=models.CASCADE, related_name="tiers")
    line_number = models.PositiveIntegerField()
    min_quantity = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    backup_ratio = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    notes = models.CharField(max_length=240, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    modification_count = models.PositiveIntegerField(default=0)
    source_object = models.CharField(max_length=40, default="scd_det")

    class Meta:
        ordering = ("quote_line", "min_quantity", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("quote_line", "line_number"), name="uniq_sales_quote_tier_line"),
            models.UniqueConstraint(fields=("quote_line", "min_quantity"), name="uniq_sales_quote_tier_threshold"),
        ]

    @property
    def discounted_unit_price(self):
        return (self.unit_price * self.quote_line.quote.discount_rate / Decimal("100")).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )

    @property
    def untaxed_unit_price(self):
        quote = self.quote_line.quote
        if not quote.tax_included:
            return self.unit_price
        divisor = Decimal("1") + quote.tax_rate / Decimal("100")
        return (self.unit_price / divisor).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


class SalesOrder(AuditedModel):
    class OrderType(models.TextChoices):
        FORMAL = "1", "正式订单"
        SAMPLE = "2", "样品订单"

    class DeliveryMode(models.TextChoices):
        DIRECT = "direct", "直送"
        SUPPLIER = "supplier", "供应商代送"

    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="sales_orders")
    order_type = models.CharField(max_length=1, choices=OrderType.choices, default=OrderType.FORMAL)
    sales_person = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders"
    )
    customer_buyer = models.CharField(max_length=80, blank=True)
    business_group = models.ForeignKey(
        "BusinessGroup", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders"
    )
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders"
    )
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="sales_orders")
    exchange_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    order_date = models.DateField(default=timezone.localdate)
    customer_po = models.CharField(max_length=80)
    srm_number = models.CharField(max_length=80, blank=True)
    version = models.CharField(max_length=20, default="A")
    consumption_forecast = models.BooleanField(default=False)
    forecast_number = models.CharField(max_length=80, blank=True)
    address_code = models.ForeignKey(
        "CustomerAddress", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders"
    )
    address_snapshot = models.CharField(max_length=240, blank=True)
    delivery_address = models.CharField(max_length=240)
    delivery_mode = models.CharField(max_length=16, choices=DeliveryMode.choices, default=DeliveryMode.DIRECT)
    promised_date = models.DateField()
    consignment = models.BooleanField(default=False)
    po_change_requested = models.BooleanField(default=False)
    po_change_by = models.CharField(max_length=64, blank=True)
    po_change_at = models.DateTimeField(null=True, blank=True)
    po_change_confirmed = models.BooleanField(default=False)
    po_change_confirmed_by = models.CharField(max_length=64, blank=True)
    po_change_confirmed_at = models.DateTimeField(null=True, blank=True)
    po_change_notes = models.TextField(blank=True)
    delivery_approved = models.BooleanField(default=False)
    delivery_approved_by = models.CharField(max_length=64, blank=True)
    delivery_approved_at = models.DateTimeField(null=True, blank=True)
    print_count = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=240, blank=True)
    source_quote = models.ForeignKey(SalesQuote, on_delete=models.PROTECT, null=True, blank=True, related_name="orders")

    class Meta:
        ordering = ("-order_date", "-number")

    def clean(self):
        from .delivery import DeliveryOrderLine

        if self.pk and DeliveryOrderLine.objects.filter(sales_order_line__order_id=self.pk).exists():
            previous = type(self).objects.get(pk=self.pk)
            if any(
                getattr(previous, field) != getattr(self, field)
                for field in ("customer_id", "currency_id", "customer_po")
            ):
                raise ValidationError("已有送货引用的订单不能更换客户、币种或客户PO")
        if self.address_code_id and self.address_code.customer_id != self.customer_id:
            raise ValidationError({"address_code": "订单地址必须属于当前客户"})
        if self.address_code_id:
            self.address_snapshot = self.address_code.address
            self.delivery_address = self.address_snapshot
        elif self.address_snapshot:
            self.delivery_address = self.address_snapshot

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = SalesOrderSequence.next_number(self.order_date)
        super().save(*args, **kwargs)


class SalesOrderLine(models.Model):
    class PriceType(models.TextChoices):
        FUTURES = "1", "期货价"
        PERIOD = "2", "期目价"
        SPOT = "3", "即日价"
        NEGOTIATED = "4", "议价"

    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="sales_order_lines")
    customer_material = models.ForeignKey(
        CustomerMaterial, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_order_lines"
    )
    customer_material_name = models.CharField(max_length=160, blank=True)
    customer_material_specification = models.CharField(max_length=240, blank=True)
    terminal_customer_code = models.CharField(max_length=80, blank=True)
    terminal_customer_name = models.CharField(max_length=160, blank=True)
    material_name = models.CharField(max_length=200, blank=True)
    material_specification = models.CharField(max_length=240, blank=True)
    tax_code = models.CharField(max_length=32, blank=True)
    tax_name = models.CharField(max_length=160, blank=True)
    invoice_name = models.CharField(max_length=160, blank=True)
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="sales_order_lines")
    inventory_uom = models.ForeignKey(
        "Uom", on_delete=models.PROTECT, null=True, blank=True, related_name="inventory_sales_order_lines"
    )
    uom_rate_m = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    uom_rate_d = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    quantity = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    spare_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    spare_ratio = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    delivered_spare_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    returned_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    returned_spare_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    unit_price = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    price_type = models.CharField(max_length=1, choices=PriceType.choices, default=PriceType.FUTURES)
    discount_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))]
    )
    discounted_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    untaxed_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    tax_included_amount = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    untaxed_amount = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    special_cost = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    total_cost = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    fixed_price = models.BooleanField(default=False)
    after_sales_method = models.CharField(max_length=80, blank=True)
    after_sales_method_name = models.CharField(max_length=120, blank=True)
    copper_origin = models.CharField(max_length=80, blank=True)
    copper_currency = models.CharField(max_length=40, blank=True)
    copper_price = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    promised_date = models.DateField()
    requested_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    delivered_quantity = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    line_status = models.CharField(max_length=16, default="normal")
    closed_by = models.CharField(max_length=64, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    income_account = models.CharField(max_length=32, blank=True)
    income_account_name = models.CharField(max_length=160, blank=True)
    replenishment_return = models.BooleanField(default=False)
    products_per_carton = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    cartons = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    special_configuration_requirement = models.CharField(max_length=240, blank=True)
    configuration_approved = models.BooleanField(default=False)
    configuration_approved_by = models.CharField(max_length=64, blank=True)
    configuration_approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modification_count = models.PositiveIntegerField(default=0)
    source_quote_line = models.ForeignKey(
        SalesQuoteLine, on_delete=models.PROTECT, null=True, blank=True, related_name="order_lines"
    )

    class Meta:
        ordering = ("order", "line_number")
        constraints = [models.UniqueConstraint(fields=("order", "line_number"), name="uniq_sales_order_line")]

    def clean(self):
        if self.quantity is not None and self.spare_quantity is not None:
            if self.quantity <= 0 and self.spare_quantity <= 0:
                raise ValidationError("正式数量与备品计划不能同时为零")
            if self.quantity < self.delivered_quantity or self.spare_quantity < self.delivered_spare_quantity:
                raise ValidationError("订单计划不能小于当前净已送数量")
        if self.customer_material_id and (
            self.customer_material.customer_id != self.order.customer_id
            or self.customer_material.material_id != self.material_id
            or not self.customer_material.enabled
        ):
            raise ValidationError("客户物料与订单客户、物料不一致或已停用")
        if self.source_quote_line_id:
            quote_line = self.source_quote_line
            quote = quote_line.quote
            customer_code = self.customer_material.customer_code if self.customer_material_id else ""
            if (
                quote.customer_id != self.order.customer_id
                or quote_line.material_id != self.material_id
                or quote_line.customer_material_code != customer_code
                or quote.currency_id != self.order.currency_id
            ):
                raise ValidationError("来源报价的客户、物料、客户料号或币种与订单不一致")
        if self.pk and self.delivery_lines.exists():
            previous = type(self).objects.get(pk=self.pk)
            if any(
                getattr(previous, field) != getattr(self, field)
                for field in (
                    "order_id",
                    "line_number",
                    "material_id",
                    "customer_material_id",
                    "uom_id",
                    "uom_rate_m",
                    "uom_rate_d",
                )
            ):
                raise ValidationError("已有送货引用的订单行不能更换来源身份、物料或单位")
            from backend.delivery import commitments

            occupied = commitments([self.pk])[self.pk]
            if (
                self.quantity < self.delivered_quantity + occupied[0]
                or self.spare_quantity < self.delivered_spare_quantity + occupied[2]
            ):
                raise ValidationError("订单计划不能小于已送数量与未审核占用合计")

    def sync_derived_values(self):
        customer_material = self.customer_material
        material = self.material
        self.material_name = material.name
        self.material_specification = material.specification
        self.tax_code = material.tax_code
        self.tax_name = material.tax_name
        self.invoice_name = material.invoice_name
        self.inventory_uom = material.uom
        self.products_per_carton = material.products_per_carton
        if customer_material:
            self.customer_material_name = customer_material.customer_name
            self.customer_material_specification = customer_material.customer_specification
            self.terminal_customer_code = customer_material.terminal_customer_code
            self.terminal_customer_name = customer_material.terminal_customer_name
            self.uom = customer_material.customer_uom or self.uom or material.uom
            self.uom_rate_m = customer_material.customer_uom_rate_m
            self.uom_rate_d = customer_material.customer_uom_rate_d
        else:
            self.customer_material_name = ""
            self.customer_material_specification = ""
            self.terminal_customer_code = ""
            self.terminal_customer_name = ""
            self.uom = self.uom or material.uom
            conversion = material.uom_conversions.filter(usage=MaterialUomConversion.Usage.SALES).first()
            if conversion:
                self.uom = conversion.business_uom
                self.uom_rate_m = conversion.business_qty
                self.uom_rate_d = conversion.stock_qty
        previous_quote_id = (
            type(self).objects.filter(pk=self.pk).values_list("source_quote_line_id", flat=True).first()
            if self.pk
            else None
        )
        if self.source_quote_line_id and self.source_quote_line_id != previous_quote_id:
            quote_line = self.source_quote_line
            self.unit_price = quote_line.unit_price.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            self.price_type = quote_line.price_type
            self.discount_rate = quote_line.quote.discount_rate
            self.promised_date = self.promised_date or quote_line.promised_date
        if not self.pk and not self.quantity and self.spare_quantity:
            self.unit_price = Decimal("0")
        self.discounted_unit_price = (self.unit_price * self.discount_rate / Decimal("100")).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        tax_rate = self.order.tax_rate if self.order_id else Decimal("0")
        divisor = Decimal("1") + tax_rate / Decimal("100")
        self.untaxed_unit_price = (
            self.discounted_unit_price / divisor if self.order.tax_included else self.discounted_unit_price
        ).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.tax_included_amount = (self.quantity * self.discounted_unit_price).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        self.untaxed_amount = (self.quantity * self.untaxed_unit_price).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        self.total_cost = (self.quantity * self.special_cost).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.spare_ratio = (
            (self.spare_quantity / self.quantity * Decimal("100")).quantize(
                Decimal("0.00000001"), rounding=ROUND_HALF_UP
            )
            if self.quantity
            else Decimal("0")
        )
        self.cartons = (
            (self.quantity / self.products_per_carton).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
            if self.products_per_carton
            else Decimal("0")
        )
