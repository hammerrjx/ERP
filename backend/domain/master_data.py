"""Master Data domain models; Django app label remains backend."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .base import AuditedModel


class Company(AuditedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160, unique=True)
    tax_number = models.CharField(max_length=32, blank=True)
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, null=True, blank=True, related_name="companies")

    def __str__(self):
        return f"{self.code} {self.name}"


class UomCategory(AuditedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Uom(AuditedModel):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(
        max_length=32,
        unique=True,
        validators=[RegexValidator(r"^[^A-Za-z]+$", "计量单位必须使用规范中文/本地化名称")],
    )
    description = models.CharField(max_length=160, blank=True)
    category = models.ForeignKey(UomCategory, on_delete=models.PROTECT, related_name="uoms")
    factor = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.000001"))]
    )
    min_pack_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))]
    )
    min_ship_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))]
    )

    def __str__(self):
        return self.name


class Currency(AuditedModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=40)
    symbol = models.CharField(max_length=8, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"{self.code} {self.name}"


class BusinessGroup(AuditedModel):
    """业务归属组，用于供应商报价的业务类型选择。"""

    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=80, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}"


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="rates")
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    rate_to_company = models.DecimalField(
        max_digits=18, decimal_places=8, validators=[MinValueValidator(Decimal("0.00000001"))]
    )
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-effective_date",)
        constraints = [models.UniqueConstraint(fields=("currency", "effective_date"), name="uniq_currency_rate_start")]


class PaymentMethod(AuditedModel):
    """Shared payment/credit terms master referenced by customers and suppliers."""

    class CalculationMethod(models.TextChoices):
        MONTH_END = "1", "月结日"
        INVOICE_DATE = "2", "发票日"
        FIXED_DATE = "3", "指定日期"

    code = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255, blank=True)
    discount_date_method = models.CharField(
        max_length=1, choices=CalculationMethod.choices, default=CalculationMethod.MONTH_END
    )
    discount_percent = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    discount_days = models.IntegerField(default=0)
    discount_start_day = models.IntegerField(default=0)
    due_date_method = models.CharField(
        max_length=1, choices=CalculationMethod.choices, default=CalculationMethod.MONTH_END
    )
    due_days = models.IntegerField(default=0)
    due_start_day = models.IntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True)
    is_void = models.BooleanField(default=False)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.description}".strip()


class ProductCategory(AuditedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    default_uom = models.ForeignKey(
        Uom, on_delete=models.PROTECT, null=True, blank=True, related_name="default_categories"
    )
    default_location = models.ForeignKey(
        "Location", on_delete=models.PROTECT, null=True, blank=True, related_name="default_categories"
    )
    code_prefix = models.CharField(max_length=16, blank=True)
    supply_method = models.CharField(max_length=20, default="purchase")
    part_type = models.CharField(max_length=80, blank=True)
    product_group = models.CharField(max_length=80, blank=True)
    buyer = models.CharField(max_length=64, blank=True)
    quality_control = models.CharField(max_length=20, default="exempt")
    phantom = models.BooleanField(default=False)
    main_production_plan = models.BooleanField(default=False)
    issue_material = models.BooleanField(default=False)
    roll = models.BooleanField(default=False)
    key_material = models.BooleanField(default=False)
    non_stock_material = models.BooleanField(default=False)
    batch_control = models.BooleanField(default=False)
    batch_rule = models.CharField(max_length=80, blank=True)
    material_view_permissions = models.CharField(max_length=240, default="*")
    material_edit_permissions = models.CharField(max_length=240, default="*")
    material_delete_permissions = models.CharField(max_length=240, default="*")
    material_approval_permissions = models.CharField(max_length=240, default="*")
    inventory_account = models.CharField(max_length=32, blank=True)
    outsource_material_account = models.CharField(max_length=32, blank=True)
    business_cost_account = models.CharField(max_length=32, blank=True)
    business_income_account = models.CharField(max_length=32, blank=True)
    production_cost_account = models.CharField(max_length=32, blank=True)
    print_permission = models.CharField(max_length=80, blank=True)
    material_code_rule = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.code} {self.name}"


class Location(AuditedModel):
    class LocationType(models.TextChoices):
        WAREHOUSE = "warehouse", "仓库"
        FG = "fg", "成品库"
        RM = "rm", "原料库"
        WIP = "wip", "在制品库"
        NG = "ng", "不良品库"
        VIRTUAL = "virtual", "虚拟库"

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    warehouse = models.ForeignKey(
        "Warehouse", on_delete=models.PROTECT, null=True, blank=True, related_name="locations"
    )
    location_type = models.CharField(max_length=16, choices=LocationType.choices, default=LocationType.WAREHOUSE)
    location_attribute = models.CharField(max_length=255, blank=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    manager = models.CharField(max_length=64, blank=True)
    warehouse_code = models.CharField(max_length=32, blank=True)
    participate_mrp = models.BooleanField(default=True)
    usable = models.BooleanField(default=True)
    allow_negative = models.BooleanField(default=False)
    quarantine_return = models.BooleanField(default=False)
    disabled_for_inventory = models.BooleanField(default=False)
    approval_permissions = models.CharField(max_length=240, blank=True)
    storage_account = models.CharField(max_length=32, blank=True)
    material_account = models.CharField(max_length=32, blank=True)
    outsource_material_account = models.CharField(max_length=32, blank=True)
    sales_income_account = models.CharField(max_length=32, blank=True)
    shipped_goods_account = models.CharField(max_length=32, blank=True)
    sales_cost_account = models.CharField(max_length=32, blank=True)
    department = models.CharField(max_length=64, blank=True)
    source_site = models.CharField(max_length=32, blank=True)
    source_object = models.CharField(max_length=40, default="loc_mstr")

    def __str__(self):
        return f"{self.code} {self.name}"


class Partner(AuditedModel):
    class PartnerKind(models.TextChoices):
        CUSTOMER = "customer", "客户"
        SUPPLIER = "supplier", "供应商"
        BOTH = "both", "客户及供应商"

    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=80)
    kind = models.CharField(max_length=12, choices=PartnerKind.choices)
    address = models.CharField(max_length=240, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    invoice_address = models.CharField(max_length=240, blank=True)
    delivery_address = models.CharField(max_length=240, blank=True)
    operating_address = models.CharField(max_length=240, blank=True)
    website = models.URLField(blank=True)
    business_owner = models.CharField(max_length=64, blank=True)
    buyer = models.CharField(max_length=64, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True, related_name="partners")
    payment_method = models.CharField(max_length=80, blank=True)
    payment_method_master = models.ForeignKey(
        "PaymentMethod", on_delete=models.PROTECT, null=True, blank=True, related_name="partners"
    )
    payment_method_2 = models.CharField(max_length=80, blank=True)
    payment_method_3 = models.CharField(max_length=80, blank=True)
    payment_terms = models.CharField(max_length=80, blank=True)
    quote_method = models.CharField(max_length=40, blank=True)
    tax_calculation_method = models.CharField(max_length=80, blank=True)
    price_type = models.CharField(max_length=40, blank=True)
    monthly_close_day = models.PositiveSmallIntegerField(default=0)
    after_sales_method = models.CharField(max_length=80, blank=True)
    round_order_quantity_for_tier_price = models.BooleanField(default=False)
    invoice_type = models.CharField(max_length=40, blank=True)
    quote_tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    discount_rate = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))]
    )
    tax_number = models.CharField(max_length=32, blank=True)
    legal_person = models.CharField(max_length=80, blank=True)
    registered_capital = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    annual_revenue = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    employee_count = models.PositiveIntegerField(default=0)
    opening_date = models.DateField(null=True, blank=True)
    service_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    category = models.CharField(max_length=40, blank=True)
    region = models.CharField(max_length=80, blank=True)
    copper_origin = models.CharField(max_length=80, blank=True)
    copper_currency = models.CharField(max_length=40, blank=True)
    parent_company = models.CharField(max_length=160, blank=True)
    sales_person = models.CharField(max_length=64, blank=True)
    payment_bank = models.CharField(max_length=120, blank=True)
    bank_account = models.CharField(max_length=80, blank=True)
    business_type = models.CharField(max_length=40, blank=True)
    credit_policy = models.CharField(max_length=80, blank=True)
    credit_limit_1 = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    credit_limit_2 = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    overdue_days_1 = models.PositiveIntegerField(default=0)
    overdue_days_2 = models.PositiveIntegerField(default=0)
    deposit_account = models.CharField(max_length=32, blank=True)
    receivable_account = models.CharField(max_length=32, blank=True)
    income_account = models.CharField(max_length=32, blank=True)
    cost_account = models.CharField(max_length=32, blank=True)
    after_sales_income_account = models.CharField(max_length=32, blank=True)
    view_permission = models.CharField(max_length=80, blank=True)
    purchase_account = models.CharField(max_length=32, blank=True)
    temporary_payable_account = models.CharField(max_length=32, blank=True)
    outsource_material_account = models.CharField(max_length=32, blank=True)
    default_receipt_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, null=True, blank=True, related_name="default_partner_receipts"
    )
    supplier_type = models.CharField(max_length=32, blank=True)
    tax_category = models.CharField(max_length=40, blank=True)
    material_price_method = models.CharField(max_length=40, blank=True)
    material_price_factor = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))]
    )
    backup_ratio = models.DecimalField(
        max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    over_receipt_ratio = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    over_order_delivery_ratio = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    quoted_settlement = models.BooleanField(default=False)
    three_certificates = models.BooleanField(default=False)
    business_license = models.BooleanField(default=False)
    internal_company = models.BooleanField(default=False)
    payment_hold = models.BooleanField(default=False)
    consignment = models.BooleanField(default=False)
    credit_enabled = models.BooleanField(default=True)
    business_type_code = models.CharField(max_length=40, blank=True)
    companies = models.ManyToManyField(Company, through="PartnerCompany", related_name="partners")

    def clean(self):
        if self.kind in {self.PartnerKind.SUPPLIER, self.PartnerKind.BOTH} and not self.payment_method:
            raise ValidationError({"payment_method": "供应商必须填写支付方式"})

    def __str__(self):
        return f"{self.code} {self.name}"


class PartnerCompany(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("partner", "company"), name="uniq_partner_company")]


class PartnerContact(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=80)
    position = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    fax = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)


class TaxCode(AuditedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    invoice_name = models.CharField(max_length=160, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}"


class PartnerBankAccount(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="bank_accounts")
    account_type = models.CharField(max_length=20, default="company")
    bank_name = models.CharField(max_length=120, blank=True)
    account_name = models.CharField(max_length=120, blank=True)
    account_number = models.CharField(max_length=80)
    bank_code = models.CharField(max_length=32, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    is_default = models.BooleanField(default=False)


class Material(AuditedModel):
    code = models.CharField(max_length=40, unique=True, blank=True)
    name = models.CharField(max_length=160)
    english_name = models.CharField(max_length=160, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name="materials")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="materials")
    old_code = models.CharField(max_length=40, blank=True)
    customs_code = models.CharField(max_length=40, blank=True)
    customs_name = models.CharField(max_length=160, blank=True)
    barcode = models.CharField(max_length=80, blank=True)
    tax_code = models.CharField(max_length=32)
    tax_name = models.CharField(max_length=160, blank=True)
    invoice_name = models.CharField(max_length=160, blank=True)
    tax_master = models.ForeignKey(TaxCode, on_delete=models.PROTECT, null=True, blank=True, related_name="materials")
    purpose = models.CharField(max_length=240, blank=True)
    active = models.BooleanField(default=True)
    used_in_companies = models.ManyToManyField(Company, through="MaterialCompany", related_name="materials")
    join_date = models.DateField(null=True, blank=True)
    part_type = models.CharField(max_length=80, blank=True)
    product_group = models.CharField(max_length=80, blank=True)
    engineering_reviewer = models.CharField(max_length=64, blank=True)
    specification = models.TextField(blank=True)
    carton_mark = models.TextField(blank=True)
    gross_weight_g = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    net_weight_g = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    length = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    width = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    height = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    volume = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    version = models.CharField(max_length=40, blank=True)
    drawing_number = models.CharField(max_length=80, blank=True)
    scrap_rate = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    products_per_carton = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    image = models.ImageField(upload_to="materials/", blank=True)
    default_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="default_materials")
    default_storage_position = models.CharField(max_length=80, blank=True)
    batch_control = models.BooleanField(default=False)
    batch_rule = models.CharField(max_length=80, blank=True)
    abc_class = models.CharField(max_length=8, blank=True)
    count_cycle_days = models.PositiveIntegerField(default=0)
    shelf_life_days = models.PositiveIntegerField(default=0)
    warehouse_manager = models.CharField(max_length=64, blank=True)
    safety_stock_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    max_stock_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    stock_warning_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    production_lead_days = models.PositiveIntegerField(default=0)
    purchase_lead_days = models.PositiveIntegerField(default=0)
    quality_control = models.CharField(max_length=20, default="required")
    quality_lead_days = models.PositiveIntegerField(default=0)
    supply_method = models.CharField(max_length=20, default="purchase")
    phantom = models.BooleanField(default=False)
    roll = models.BooleanField(default=False)
    min_purchase_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    min_pack_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    min_issue_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))]
    )
    receipt_consume_mode = models.CharField(max_length=40, blank=True)
    outsource_receipt_consume_mode = models.CharField(max_length=40, blank=True)
    buyer = models.CharField(max_length=64, blank=True)
    planner = models.CharField(max_length=64, blank=True)
    default_supplier = models.ForeignKey(
        Partner, on_delete=models.PROTECT, null=True, blank=True, related_name="default_materials"
    )
    production_line = models.CharField(max_length=80, blank=True)
    order_strategy = models.CharField(max_length=40, blank=True)
    order_qty = models.DecimalField(
        max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    order_period_days = models.PositiveIntegerField(default=0)
    over_receipt_ratio = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    default_operation = models.PositiveIntegerField(default=0)
    scheduling_class = models.CharField(max_length=80, blank=True)
    low_level_code = models.PositiveIntegerField(default=0)
    plan_order = models.BooleanField(default=True)
    non_production = models.BooleanField(default=False)
    purchase_quote_unrestricted = models.BooleanField(default=False)
    sales_quote_unrestricted = models.BooleanField(default=False)
    issue_qty_unrestricted = models.BooleanField(default=False)
    outsource_surplus_excluded_from_mrp = models.BooleanField(default=False)
    no_stock_movement = models.BooleanField(default=False)

    def clean(self):
        if self.tax_master_id:
            self.tax_code = self.tax_master.code
            self.tax_name = self.tax_master.name
            self.invoice_name = self.tax_master.invoice_name
        elif self.tax_code:
            tax_master = TaxCode.objects.filter(code=self.tax_code, active=True).first()
            if tax_master:
                self.tax_master = tax_master
                self.tax_name = tax_master.name
                self.invoice_name = tax_master.invoice_name
            elif TaxCode.objects.exists():
                raise ValidationError({"tax_code": "税务编码不存在或已停用"})
        if self.uom_id and self.uom.name.isascii():
            raise ValidationError({"uom": "物料单位必须使用规范中文/本地化单位"})
        if self.batch_control and not self.batch_rule:
            raise ValidationError({"batch_rule": "启用批号控制时必须填写批号规则"})

    def save(self, *args, **kwargs):
        if self.tax_master_id:
            self.tax_code = self.tax_master.code
            self.tax_name = self.tax_master.name
            self.invoice_name = self.tax_master.invoice_name
        elif self.tax_code:
            tax_master = TaxCode.objects.filter(code=self.tax_code, active=True).first()
            if tax_master:
                self.tax_master = tax_master
                self.tax_name = tax_master.name
                self.invoice_name = tax_master.invoice_name
        if not self.code and self.category_id:
            from django.db import transaction

            from backend.material_codes import allocate_material_code

            with transaction.atomic():
                category = ProductCategory.objects.select_for_update().get(pk=self.category_id)
                prefix = category.code_prefix or category.code
                prefix = prefix.strip()
                local_codes = Material.objects.filter(code__startswith=f"{prefix}-").values_list("code", flat=True)
                self.code = allocate_material_code(prefix, local_codes)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} {self.name}"


class MaterialCompany(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("material", "company"), name="uniq_material_company")]


class MaterialUomConversion(models.Model):
    class Usage(models.TextChoices):
        ENGINEERING = "engineering", "工程BOM"
        PRODUCTION = "production", "生产领用"
        PURCHASE = "purchase", "采购"
        SALES = "sales", "销售"

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="uom_conversions")
    usage = models.CharField(max_length=20, choices=Usage.choices)
    business_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="material_conversions")
    business_qty = models.DecimalField(
        max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))]
    )
    stock_qty = models.DecimalField(
        max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))]
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=("material", "usage"), name="uniq_material_uom_usage")]

    def clean(self):
        if self.business_uom_id and self.material_id and self.business_uom.category_id != self.material.uom.category_id:
            raise ValidationError("业务单位与库存单位必须属于同一单位类别")


class CustomerAddress(models.Model):
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="delivery_addresses")
    code = models.CharField(max_length=40)
    address = models.CharField(max_length=240)
    notes = models.CharField(max_length=240, blank=True)
    enabled = models.BooleanField(default=True)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_object = models.CharField(max_length=40, default="ca_mstr")
    source_key = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ("customer__code", "code")
        constraints = [models.UniqueConstraint(fields=("customer", "code"), name="uniq_customer_address_code")]

    def clean(self):
        if self.customer_id and self.customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise ValidationError({"customer": "客户地址必须关联客户合作伙伴"})


class Warehouse(AuditedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True, related_name="warehouses")
    address = models.CharField(max_length=240, blank=True)
    manager = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)
    source_object = models.CharField(max_length=40, default="si_mstr")

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}"
