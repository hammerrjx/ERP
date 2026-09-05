from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models, transaction
from django.utils import timezone


class ApprovalStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PENDING = "pending", "待审核"
    APPROVED = "approved", "已审核"
    REJECTED = "rejected", "已驳回"
    VOID = "void", "已作废"


class AuditedModel(models.Model):
    status = models.CharField(max_length=16, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.CharField(max_length=64, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=240, blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def submit(self):
        if self.status not in {ApprovalStatus.DRAFT, ApprovalStatus.REJECTED}:
            raise ValidationError("只有草稿或已驳回记录可以提交审核")
        self.status = ApprovalStatus.PENDING

    def approve(self, actor):
        if self.status != ApprovalStatus.PENDING:
            raise ValidationError("只有待审核记录可以审核")
        self.status = ApprovalStatus.APPROVED
        self.approved_by = actor
        self.approved_at = timezone.now()
        self.rejection_reason = ""

    def reject(self, actor, reason):
        if self.status != ApprovalStatus.PENDING:
            raise ValidationError("只有待审核记录可以驳回")
        if not reason:
            raise ValidationError("驳回必须填写原因")
        self.status = ApprovalStatus.REJECTED
        self.approved_by = actor
        self.approved_at = timezone.now()
        self.rejection_reason = reason

    def unapprove(self):
        if self.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核记录可以反审核")
        self.status = ApprovalStatus.DRAFT
        self.approved_by = ""
        self.approved_at = None

    def confirm(self, actor):
        if self.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核记录可以确认")
        if self.is_confirmed:
            raise ValidationError("记录已经确认")
        self.is_confirmed = True
        self.confirmed_by = actor
        self.confirmed_at = timezone.now()

    def unconfirm(self):
        if not self.is_confirmed:
            raise ValidationError("记录尚未确认")
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None

    def void(self):
        if self.status == ApprovalStatus.VOID:
            raise ValidationError("记录已经作废")
        self.status = ApprovalStatus.VOID

    def restore(self):
        if self.status != ApprovalStatus.VOID:
            raise ValidationError("只有已作废记录可以反作废")
        self.status = ApprovalStatus.DRAFT
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None


class DocumentEvidence(models.Model):
    """Signed slips and other evidence linked to an ERP document."""

    class EvidenceType(models.TextChoices):
        SUPPLIER_DELIVERY = "supplier_delivery", "供应商送货签收单"
        CUSTOMER_DELIVERY = "customer_delivery", "客户送货签收单"
        CUSTOMER_RETURN = "customer_return", "客户退货单"
        WAREHOUSE_RETURN = "warehouse_return", "仓库退货单"

    document_type = models.CharField(max_length=40)
    document_id = models.PositiveIntegerField()
    document_number = models.CharField(max_length=80, blank=True)
    evidence_type = models.CharField(max_length=32, choices=EvidenceType.choices)
    file = models.FileField(upload_to="document_evidence/")
    notes = models.CharField(max_length=240, blank=True)
    uploaded_by = models.CharField(max_length=64, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at", "-id")
        indexes = [models.Index(fields=("document_type", "document_id"), name="evidence_document_idx")]


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
    factor = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.000001"))])
    min_pack_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))])
    min_ship_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))])

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


class Employee(AuditedModel):
    """Employee/business-person master synchronized from the legacy user table."""

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    group_code = models.CharField(max_length=32, blank=True)
    department_code = models.CharField(max_length=32, blank=True)
    default_site = models.CharField(max_length=16, blank=True)
    is_employee = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_left = models.BooleanField(default=False)
    phone = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    qq = models.CharField(max_length=30, blank=True)
    wechat = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=16, blank=True)
    company = models.CharField(max_length=160, blank=True)
    source_object = models.CharField(max_length=40, default="usr_mstr")

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}".strip()


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="rates")
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    rate_to_company = models.DecimalField(max_digits=18, decimal_places=8, validators=[MinValueValidator(Decimal("0.00000001"))])
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
    discount_date_method = models.CharField(max_length=1, choices=CalculationMethod.choices, default=CalculationMethod.MONTH_END)
    discount_percent = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    discount_days = models.IntegerField(default=0)
    discount_start_day = models.IntegerField(default=0)
    due_date_method = models.CharField(max_length=1, choices=CalculationMethod.choices, default=CalculationMethod.MONTH_END)
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
    default_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, null=True, blank=True, related_name="default_categories")
    default_location = models.ForeignKey("Location", on_delete=models.PROTECT, null=True, blank=True, related_name="default_categories")
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
    warehouse = models.ForeignKey("Warehouse", on_delete=models.PROTECT, null=True, blank=True, related_name="locations")
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
    payment_method_master = models.ForeignKey("PaymentMethod", on_delete=models.PROTECT, null=True, blank=True, related_name="partners")
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
    tax_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    discount_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))])
    tax_number = models.CharField(max_length=32, blank=True)
    legal_person = models.CharField(max_length=80, blank=True)
    registered_capital = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    annual_revenue = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    employee_count = models.PositiveIntegerField(default=0)
    opening_date = models.DateField(null=True, blank=True)
    service_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    credit_limit_1 = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    credit_limit_2 = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    default_receipt_location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True, related_name="default_partner_receipts")
    supplier_type = models.CharField(max_length=32, blank=True)
    tax_category = models.CharField(max_length=40, blank=True)
    material_price_method = models.CharField(max_length=40, blank=True)
    material_price_factor = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))])
    backup_ratio = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    over_receipt_ratio = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    over_order_delivery_ratio = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    gross_weight_g = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    net_weight_g = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    length = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    width = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    height = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    volume = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    version = models.CharField(max_length=40, blank=True)
    drawing_number = models.CharField(max_length=80, blank=True)
    scrap_rate = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    products_per_carton = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    image = models.ImageField(upload_to="materials/", blank=True)
    default_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="default_materials")
    default_storage_position = models.CharField(max_length=80, blank=True)
    batch_control = models.BooleanField(default=False)
    batch_rule = models.CharField(max_length=80, blank=True)
    abc_class = models.CharField(max_length=8, blank=True)
    count_cycle_days = models.PositiveIntegerField(default=0)
    shelf_life_days = models.PositiveIntegerField(default=0)
    warehouse_manager = models.CharField(max_length=64, blank=True)
    safety_stock_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    max_stock_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    stock_warning_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    production_lead_days = models.PositiveIntegerField(default=0)
    purchase_lead_days = models.PositiveIntegerField(default=0)
    quality_control = models.CharField(max_length=20, default="required")
    quality_lead_days = models.PositiveIntegerField(default=0)
    supply_method = models.CharField(max_length=20, default="purchase")
    phantom = models.BooleanField(default=False)
    roll = models.BooleanField(default=False)
    min_purchase_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    min_pack_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    min_issue_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("1"), validators=[MinValueValidator(Decimal("0"))])
    receipt_consume_mode = models.CharField(max_length=40, blank=True)
    outsource_receipt_consume_mode = models.CharField(max_length=40, blank=True)
    buyer = models.CharField(max_length=64, blank=True)
    planner = models.CharField(max_length=64, blank=True)
    default_supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True, blank=True, related_name="default_materials")
    production_line = models.CharField(max_length=80, blank=True)
    order_strategy = models.CharField(max_length=40, blank=True)
    order_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    order_period_days = models.PositiveIntegerField(default=0)
    over_receipt_ratio = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    business_qty = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    stock_qty = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])

    class Meta:
        constraints = [models.UniqueConstraint(fields=("material", "usage"), name="uniq_material_uom_usage")]

    def clean(self):
        if self.business_uom_id and self.material_id and self.business_uom.category_id != self.material.uom.category_id:
            raise ValidationError("业务单位与库存单位必须属于同一单位类别")


class CustomerMaterial(models.Model):
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="customer_materials")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="customer_materials")
    customer_code = models.CharField(max_length=80)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_specification = models.CharField(max_length=240, blank=True)
    customer_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, null=True, blank=True, related_name="customer_materials")
    customer_uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    customer_uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
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
        constraints = [models.UniqueConstraint(fields=("customer", "material", "customer_code"), name="uniq_customer_material_external_code")]

    def clean(self):
        if self.customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise ValidationError("客户物料只能关联客户合作伙伴")


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


class SupplierQuoteSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls):
        period = timezone.localdate().strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SupplierQuote.objects.filter(number__startswith=f"MYPQ{period[2:]}").values_list("number", flat=True)
            sequence.last_value = max([sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())])
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYPQ{period[2:]}{sequence.last_value:04d}"


class SupplierQuote(AuditedModel):
    class QuoteType(models.TextChoices):
        PURCHASE = "purchase", "采购报价"
        OUTSOURCE = "outsource", "外协报价"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="supplier_quotes")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="supplier_quotes")
    business_group = models.ForeignKey(
        BusinessGroup, on_delete=models.PROTECT, null=True, blank=True, related_name="supplier_quotes",
    )
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="supplier_quotes")
    purchase_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, null=True, blank=True, related_name="supplier_quotes")
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    quote_type = models.CharField(max_length=16, choices=QuoteType.choices)
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    material_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    processing_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    min_purchase_qty = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    min_pack_qty = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    delivery_days = models.PositiveIntegerField(default=0)
    operation = models.ForeignKey("RoutingOperation", on_delete=models.PROTECT, null=True, blank=True, related_name="supplier_quotes")
    parent_material = models.ForeignKey(Material, on_delete=models.PROTECT, null=True, blank=True, related_name="outsource_supplier_quotes")
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
        overlap = SupplierQuote.objects.filter(
            supplier=self.supplier,
            material=self.material,
            currency=self.currency,
            quote_type=self.quote_type,
        ).exclude(pk=self.pk).filter(
            effective_date__lte=new_end,
        ).filter(
            models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gte=self.effective_date),
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
    material_unit_price = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    processing_unit_price = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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


class AuditEvent(models.Model):
    model = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64)
    action = models.CharField(max_length=40)
    actor = models.CharField(max_length=64)
    reason = models.CharField(max_length=240, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class Department(AuditedModel):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=80)
    manager = models.CharField(max_length=64, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    source_created_by = models.CharField(max_length=64, blank=True)
    source_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}"


class Role(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="roles")
    permissions = models.JSONField(default=list)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("department__code", "code")

    def __str__(self):
        return f"{self.code} {self.name}"


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="erp_role_assignments")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="assignments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="user_roles")
    is_primary = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "role", "department"), name="uniq_user_role_department")]


class ApprovalRule(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    document_type = models.CharField(max_length=40)
    sequence = models.PositiveSmallIntegerField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="approval_rules")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="approval_rules")
    min_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    max_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("document_type", "sequence", "code")
        constraints = [models.UniqueConstraint(fields=("document_type", "sequence", "department"), name="uniq_document_approval_step")]

    def clean(self):
        if self.role_id and self.department_id and self.role.department_id != self.department_id:
            raise ValidationError("审批角色必须属于审批部门")
        if self.max_amount is not None and self.max_amount < self.min_amount:
            raise ValidationError({"max_amount": "金额上限不能小于金额下限"})


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


class BillOfMaterial(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    parent_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="boms")
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
    component = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="bom_component_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="bom_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    scrap_rate = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="routings")
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
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="routing_operations")
    run_time = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    production_rate = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    yield_rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))])
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True, blank=True, related_name="routing_operations")
    tool = models.CharField(max_length=80, blank=True)
    parameters = models.CharField(max_length=240, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    is_default = models.BooleanField(default=False)
    is_alternate = models.BooleanField(default=False)
    alternate_sequence = models.PositiveIntegerField(default=0)
    operation_type = models.CharField(max_length=20, default="internal")
    purchase_material = models.ForeignKey(Material, on_delete=models.PROTECT, null=True, blank=True, related_name="outsource_operations")
    source_object = models.CharField(max_length=40, default="ro_det")

    class Meta:
        ordering = ("routing", "sequence")
        constraints = [models.UniqueConstraint(fields=("routing", "sequence"), name="uniq_routing_operation_sequence")]

    def clean(self):
        if self.yield_rate > Decimal("100"):
            raise ValidationError({"yield_rate": "良率不能超过 100%"})


class SalesQuoteSequence(models.Model):
    period = models.CharField(max_length=6, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(cls):
        period = timezone.localdate().strftime("%Y%m")
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(period=period)
            existing = SalesQuote.objects.filter(number__startswith=f"MYSQ{period[2:]}").values_list("number", flat=True)
            sequence.last_value = max([sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())])
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
            existing = SalesOrder.objects.filter(number__startswith=f"MYSO{period[2:]}").values_list("number", flat=True)
            sequence.last_value = max([sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())])
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYSO{period[2:]}{sequence.last_value:04d}"


class SalesQuote(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="sales_quotes")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="sales_quotes")
    effective_date = models.DateField(default=timezone.localdate)
    expiry_date = models.DateField(null=True, blank=True)
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    discount_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))])
    backup_ratio = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    address_code = models.ForeignKey("CustomerAddress", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_quotes")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="sales_quote_lines")
    customer_material = models.ForeignKey(CustomerMaterial, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_quote_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="sales_quote_lines")
    quantity = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    unit_price = models.DecimalField(max_digits=19, decimal_places=8, validators=[MinValueValidator(Decimal("0"))])
    price_type = models.CharField(max_length=1, choices=PriceType.choices, default=PriceType.FUTURES)
    tax_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
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
        return (self.unit_price * self.quote.discount_rate / Decimal("100")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)

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
    backup_ratio = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
        return (self.unit_price * self.quote_line.quote.discount_rate / Decimal("100")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)

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
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="sales_orders")
    order_type = models.CharField(max_length=1, choices=OrderType.choices, default=OrderType.FORMAL)
    sales_person = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders")
    customer_buyer = models.CharField(max_length=80, blank=True)
    business_group = models.ForeignKey(BusinessGroup, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="sales_orders")
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    tax_included = models.BooleanField(default=True)
    tax_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    order_date = models.DateField(default=timezone.localdate)
    customer_po = models.CharField(max_length=80)
    srm_number = models.CharField(max_length=80, blank=True)
    version = models.CharField(max_length=20, default="A")
    consumption_forecast = models.BooleanField(default=False)
    forecast_number = models.CharField(max_length=80, blank=True)
    address_code = models.ForeignKey("CustomerAddress", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_orders")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="sales_order_lines")
    customer_material = models.ForeignKey(CustomerMaterial, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_order_lines")
    customer_material_name = models.CharField(max_length=160, blank=True)
    customer_material_specification = models.CharField(max_length=240, blank=True)
    terminal_customer_code = models.CharField(max_length=80, blank=True)
    terminal_customer_name = models.CharField(max_length=160, blank=True)
    material_name = models.CharField(max_length=200, blank=True)
    material_specification = models.CharField(max_length=240, blank=True)
    tax_code = models.CharField(max_length=32, blank=True)
    tax_name = models.CharField(max_length=160, blank=True)
    invoice_name = models.CharField(max_length=160, blank=True)
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="sales_order_lines")
    inventory_uom = models.ForeignKey(Uom, on_delete=models.PROTECT, null=True, blank=True, related_name="inventory_sales_order_lines")
    uom_rate_m = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    uom_rate_d = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("1"), validators=[MinValueValidator(Decimal("0.00000001"))])
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    spare_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    spare_ratio = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    delivered_spare_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    returned_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    returned_spare_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    price_type = models.CharField(max_length=1, choices=PriceType.choices, default=PriceType.FUTURES)
    discount_rate = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("100"), validators=[MinValueValidator(Decimal("0"))])
    discounted_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    untaxed_unit_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    tax_included_amount = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    untaxed_amount = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    special_cost = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    total_cost = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), editable=False)
    fixed_price = models.BooleanField(default=False)
    after_sales_method = models.CharField(max_length=80, blank=True)
    after_sales_method_name = models.CharField(max_length=120, blank=True)
    copper_origin = models.CharField(max_length=80, blank=True)
    copper_currency = models.CharField(max_length=40, blank=True)
    copper_price = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    requested_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    delivered_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    line_status = models.CharField(max_length=16, default="normal")
    closed_by = models.CharField(max_length=64, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    income_account = models.CharField(max_length=32, blank=True)
    income_account_name = models.CharField(max_length=160, blank=True)
    replenishment_return = models.BooleanField(default=False)
    products_per_carton = models.DecimalField(max_digits=19, decimal_places=8, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    source_quote_line = models.ForeignKey(SalesQuoteLine, on_delete=models.PROTECT, null=True, blank=True, related_name="order_lines")

    class Meta:
        ordering = ("order", "line_number")
        constraints = [models.UniqueConstraint(fields=("order", "line_number"), name="uniq_sales_order_line")]

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
        if self.source_quote_line_id:
            quote_line = self.source_quote_line
            self.unit_price = quote_line.unit_price.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            self.price_type = quote_line.price_type
            self.discount_rate = quote_line.quote.discount_rate
            self.promised_date = self.promised_date or quote_line.promised_date
        self.discounted_unit_price = (self.unit_price * self.discount_rate / Decimal("100")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        tax_rate = self.order.tax_rate if self.order_id else Decimal("0")
        divisor = Decimal("1") + tax_rate / Decimal("100")
        self.untaxed_unit_price = (self.discounted_unit_price / divisor if self.order.tax_included else self.discounted_unit_price).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.tax_included_amount = (self.quantity * self.discounted_unit_price).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.untaxed_amount = (self.quantity * self.untaxed_unit_price).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.total_cost = (self.quantity * self.special_cost).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        self.spare_ratio = (self.spare_quantity / self.quantity * Decimal("100")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP) if self.quantity else Decimal("0")
        self.cartons = (self.quantity / self.products_per_carton).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP) if self.products_per_carton else Decimal("0")


class PurchaseRequisition(AuditedModel):
    class AggregationMode(models.TextChoices):
        NONE = "none", "不汇总"
        MATERIAL = "material", "按物料汇总"

    number = models.CharField(max_length=40, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="purchase_requisitions")
    request_date = models.DateField(default=timezone.localdate)
    needed_date = models.DateField()
    aggregation_mode = models.CharField(max_length=16, choices=AggregationMode.choices, default=AggregationMode.NONE)
    quantity_rule = models.CharField(max_length=16, default="mrp")
    only_positive = models.BooleanField(default=True)
    source_sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisitions")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="purchase_requisition_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="purchase_requisition_lines")
    mrp_demand_qty = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    on_order_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    available_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    safety_stock_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    requested_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), editable=False)
    calculation_snapshot = models.JSONField(default=dict, editable=False)
    source_sales_order_line = models.ForeignKey(SalesOrderLine, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_requisition_lines")
    converted_qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    source_object = models.CharField(max_length=40, default="req_mstr")
    source_detail_object = models.CharField(max_length=40, default="reqd_det")

    class Meta:
        ordering = ("requisition", "line_number")
        constraints = [models.UniqueConstraint(fields=("requisition", "line_number"), name="uniq_purchase_requisition_line")]

    def calculated_quantity(self):
        return max(self.mrp_demand_qty + self.safety_stock_qty - self.on_order_qty - self.available_qty, Decimal("0"))

    def clean(self):
        quantity = self.calculated_quantity()
        if self.requisition_id and self.requisition.aggregation_mode == PurchaseRequisition.AggregationMode.NONE and not self.source_sales_order_line_id:
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
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="rfqs")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="rfq_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="rfq_lines")
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
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="inquiry_responses")
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    tax_rate = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
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
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="purchase_orders")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="purchase_orders")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="purchase_orders")
    order_date = models.DateField(default=timezone.localdate)
    buyer = models.CharField(max_length=64, blank=True)
    payment_method = models.CharField(max_length=80)
    tax_rate = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    purchase_type = models.CharField(max_length=20, choices=PurchaseType.choices, default=PurchaseType.PRODUCTION)
    cost_center = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name="cost_center_purchase_orders")
    notes = models.CharField(max_length=240, blank=True)
    source_requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_orders")
    source_purchase_return = models.ForeignKey("PurchaseReturn", on_delete=models.PROTECT, null=True, blank=True, related_name="replacement_orders")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="purchase_order_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="purchase_order_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    promised_date = models.DateField()
    received_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    returned_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    source_requisition_line = models.ForeignKey(PurchaseRequisitionLine, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines")
    source_supplier_quote = models.ForeignKey(SupplierQuote, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines")
    source_supplier_quote_line = models.ForeignKey(SupplierQuoteLine, on_delete=models.PROTECT, null=True, blank=True, related_name="purchase_order_lines")
    source_object = models.CharField(max_length=40, default="pod_det")

    class Meta:
        ordering = ("order", "line_number")
        constraints = [models.UniqueConstraint(fields=("order", "line_number"), name="uniq_purchase_order_line")]


class StockBalance(models.Model):
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="stock_balances")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="stock_balances")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="stock_balances")
    batch_number = models.CharField(max_length=80, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"))
    reserved_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("material__code", "location__code", "batch_number")
        constraints = [models.UniqueConstraint(fields=("material", "location", "batch_number"), name="uniq_stock_balance_key")]

    @classmethod
    def adjust(cls, *, material, location, uom, quantity, movement_type, source_model, source_id, source_line_id, actor, batch_number=""):
        balance, _ = cls.objects.select_for_update().get_or_create(
            material=material,
            location=location,
            batch_number=batch_number,
            defaults={"uom": uom},
        )
        if balance.uom_id != uom.id:
            raise ValidationError("库存流水单位必须与余额单位一致")
        next_quantity = balance.quantity + quantity
        if next_quantity < 0 and not location.allow_negative:
            raise ValidationError(f"库位 {location.code} 库存不足，不允许负库存")
        balance.quantity = next_quantity
        balance.save(update_fields=["quantity", "updated_at"])
        StockTransaction.objects.create(
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
        )
        return balance


class StockTransaction(models.Model):
    movement_type = models.CharField(max_length=24)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="stock_transactions")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="stock_transactions")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="stock_transactions")
    batch_number = models.CharField(max_length=80, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=6)
    balance_after = models.DecimalField(max_digits=18, decimal_places=6)
    source_model = models.CharField(max_length=80)
    source_id = models.CharField(max_length=64)
    source_line_id = models.CharField(max_length=64)
    actor = models.CharField(max_length=64)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-posted_at", "-id")
        constraints = [models.UniqueConstraint(fields=("source_model", "source_line_id", "movement_type", "location"), name="uniq_stock_source_movement")]


class GoodsReceipt(AuditedModel):
    class ReceiptType(models.TextChoices):
        NORMAL = "normal", "采购收货"
        NON_PRODUCTION = "non_production", "非生产收货"

    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="goods_receipts")
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
        if self.purchase_order_id and self.purchase_order.purchase_type == PurchaseOrder.PurchaseType.NON_PRODUCTION and self.receipt_type != self.ReceiptType.NON_PRODUCTION:
            raise ValidationError({"receipt_type": "非生产采购必须使用非生产收货"})
        if self.purchase_order_id and self.purchase_order.purchase_type != PurchaseOrder.PurchaseType.NON_PRODUCTION and self.receipt_type == self.ReceiptType.NON_PRODUCTION:
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="goods_receipt_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="goods_receipt_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    accepted_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    rejected_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="goods_receipt_lines")
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
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="payable_vouchers")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="payable_vouchers")
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
            net=models.Sum("net_amount"), tax=models.Sum("tax_amount"), gross=models.Sum("gross_amount"),
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
        GoodsReceiptLine, on_delete=models.PROTECT, null=True, blank=True, related_name="payable_voucher_line",
    )
    source_purchase_return_line = models.OneToOneField(
        "PurchaseReturnLine", on_delete=models.PROTECT, null=True, blank=True, related_name="payable_voucher_line",
    )
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="payable_voucher_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="payable_voucher_lines")
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
        self.tax_amount = (self.net_amount * self.voucher.tax_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.gross_amount = self.net_amount + self.tax_amount
        super().save(*args, **kwargs)
        self.voucher.recalculate()


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
            existing = DeliveryOrder.objects.filter(number__startswith=f"MYSD{period[2:]}").values_list("number", flat=True)
            sequence.last_value = max([sequence.last_value, *(int(number[-4:]) for number in existing if str(number)[-4:].isdigit())])
            sequence.last_value += 1
            sequence.save(update_fields=("last_value", "updated_at"))
        return f"MYSD{period[2:]}{sequence.last_value:04d}"


class DeliveryOrder(AuditedModel):
    class DocumentType(models.TextChoices):
        NORMAL = "normal", "正常送货"
        RETURN = "return", "正常退货"
        RED_FLUSH = "red_flush", "红冲单据"

    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="delivery_orders")
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_orders")
    delivery_date = models.DateField(default=timezone.localdate)
    delivery_address = models.CharField(max_length=240)
    address_code = models.CharField(max_length=40, blank=True)
    address_snapshot = models.CharField(max_length=240, blank=True)
    document_type = models.CharField(max_length=16, choices=DocumentType.choices, default=DocumentType.NORMAL)
    delivery_mode = models.CharField(max_length=16, choices=SalesOrder.DeliveryMode.choices, default=SalesOrder.DeliveryMode.DIRECT)
    source_location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_orders")
    default_print_person = models.CharField(max_length=64, blank=True)
    srm_number = models.CharField(max_length=80, blank=True)
    customer_po = models.CharField(max_length=80)
    notes = models.CharField(max_length=240, blank=True)
    actual_ship_time = models.DateTimeField(null=True, blank=True)
    source_delivery = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="red_flushes")
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
            address = CustomerAddress.objects.filter(customer=self.customer, code=self.address_code, enabled=True).first()
            if address:
                self.address_snapshot = address.address
                self.delivery_address = address.address
        if "先出货后补单" in self.notes and not self.actual_ship_time:
            raise ValidationError({"actual_ship_time": "先出货后补单必须记录实际出货时间"})

    def approve(self, actor):
        lines = list(self.lines.select_related("sales_order_line__order", "material", "uom", "source_location", "customer_material", "source_delivery_line"))
        if not lines:
            raise ValidationError("送货单至少需要一条明细")
        customer_ids = {line.sales_order_line.order.customer_id for line in lines if line.sales_order_line_id}
        if self.customer_id not in customer_ids:
            raise ValidationError("送货明细必须属于送货单客户")
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
            movement_type = "sales_delivery" if quantity_delta > 0 else "sales_return"
            order_line.delivered_quantity = max(order_line.delivered_quantity + quantity_delta, Decimal("0"))
            order_line.delivered_spare_quantity = max(order_line.delivered_spare_quantity + spare_delta, Decimal("0"))
            if quantity_delta < 0:
                order_line.returned_quantity += abs(quantity_delta)
            if spare_delta < 0:
                order_line.returned_spare_quantity += abs(spare_delta)
            order_line.save(update_fields=["delivered_quantity", "delivered_spare_quantity", "returned_quantity", "returned_spare_quantity", "updated_at"])
            if getattr(settings, "ERP_DELIVERY_POST_STOCK", False) and self.delivery_mode == SalesOrder.DeliveryMode.DIRECT and not line.material.no_stock_movement:
                StockBalance.adjust(
                    material=line.material,
                    location=line.source_location,
                    uom=line.uom,
                    quantity=(-(line.actual_quantity + line.actual_spare_quantity) if quantity_delta > 0 else abs(line.actual_quantity + line.actual_spare_quantity)),
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


class DeliveryOrderLine(models.Model):
    delivery = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    sales_order_line = models.ForeignKey(SalesOrderLine, on_delete=models.PROTECT, related_name="delivery_lines")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="delivery_order_lines")
    customer_material = models.ForeignKey(CustomerMaterial, on_delete=models.PROTECT, null=True, blank=True, related_name="delivery_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="delivery_order_lines")
    actual_quantity = models.DecimalField(max_digits=18, decimal_places=6)
    ordered_spare_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    actual_spare_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"))
    source_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="delivery_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    source_delivery_line = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="red_flush_lines")
    srm_customer_po = models.CharField(max_length=80)
    srm_material_code = models.CharField(max_length=80)
    srm_material_name = models.CharField(max_length=160)
    srm_quantity = models.DecimalField(max_digits=18, decimal_places=6)
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ("delivery", "line_number")
        constraints = [models.UniqueConstraint(fields=("delivery", "line_number"), name="uniq_delivery_order_line")]

    def clean(self):
        order_line = self.sales_order_line
        if self.delivery.document_type in {DeliveryOrder.DocumentType.RETURN, DeliveryOrder.DocumentType.RED_FLUSH}:
            self.actual_quantity = -abs(self.actual_quantity)
            self.actual_spare_quantity = -abs(self.actual_spare_quantity)
        if self.actual_quantity < 0:
            self.srm_quantity = self.actual_quantity
        if not self.actual_quantity:
            raise ValidationError({"actual_quantity": "实际送货数量不能为 0"})
        if self.actual_quantity < 0 and abs(self.actual_quantity) > self.sales_order_line.delivered_quantity:
            raise ValidationError({"actual_quantity": "退货数量超过订单当前已送数量"})
        if self.actual_spare_quantity < 0 and self.delivery.document_type == DeliveryOrder.DocumentType.NORMAL:
            raise ValidationError({"actual_spare_quantity": "正常送货的送备品数不能为负数"})
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
        if self.delivery.document_type == DeliveryOrder.DocumentType.NORMAL and self.actual_quantity > 0 and order_line.delivered_quantity + self.actual_quantity > order_line.quantity:
            raise ValidationError({"actual_quantity": "实际送货数量超过销售订单未交数量"})
        if self.delivery.document_type == DeliveryOrder.DocumentType.NORMAL and self.actual_spare_quantity > 0 and order_line.delivered_spare_quantity + self.actual_spare_quantity > order_line.spare_quantity:
            raise ValidationError({"actual_spare_quantity": "实际送备品数超过销售订单未交备品数"})
        if self.material.batch_control and self.delivery.delivery_mode == SalesOrder.DeliveryMode.DIRECT and not self.batch_number:
            raise ValidationError({"batch_number": "启用批号控制的物料送货时必须选择批号"})
        if self.source_delivery_line_id:
            source = self.source_delivery_line
            if self.delivery.source_delivery_id and source.delivery_id != self.delivery.source_delivery_id:
                raise ValidationError({"source_delivery_line": "来源送货明细必须属于来源送货单"})
            if source.sales_order_line_id != self.sales_order_line_id or source.material_id != self.material_id:
                raise ValidationError({"source_delivery_line": "来源送货明细必须与当前订单行和物料一致"})
            already_reversed = DeliveryOrderLine.objects.filter(
                source_delivery_line=source, delivery__status=ApprovalStatus.APPROVED,
            ).exclude(pk=self.pk).aggregate(
                quantity=models.Sum("actual_quantity"), spare_quantity=models.Sum("actual_spare_quantity"),
            )
            reversed_quantity = abs(already_reversed["quantity"] or Decimal("0"))
            if abs(self.actual_quantity) + reversed_quantity > abs(source.actual_quantity):
                raise ValidationError({"actual_quantity": "退货或红冲数量超过原送货数量"})
            reversed_spare_quantity = abs(already_reversed["spare_quantity"] or Decimal("0"))
            if abs(self.actual_spare_quantity) + reversed_spare_quantity > abs(source.actual_spare_quantity):
                raise ValidationError({"actual_spare_quantity": "退货或红冲备品数超过原送备品数"})


class StockTransfer(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    transfer_date = models.DateField(default=timezone.localdate)
    from_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="outgoing_transfers")
    to_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="incoming_transfers")
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
            StockBalance.adjust(location=self.from_location, quantity=-line.quantity, movement_type="transfer_out", **common)
            StockBalance.adjust(location=self.to_location, quantity=line.quantity, movement_type="transfer_in", **common)
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"TR-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class StockTransferLine(models.Model):
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="stock_transfer_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="stock_transfer_lines")
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
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="stock_counts")
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
                    movement_type="count_adjustment",
                    source_model=self._meta.label_lower,
                    source_id=self.pk,
                    source_line_id=line.pk,
                    actor=actor,
                    batch_number=line.batch_number,
                )
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"SC-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class StockCountLine(models.Model):
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="stock_count_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="stock_count_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    system_quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"), editable=False)
    counted_quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
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


class PurchaseReturn(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="purchase_returns")
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
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="purchase_return_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="purchase_return_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    source_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="purchase_return_lines")
    batch_number = models.CharField(max_length=80, blank=True)
    reason = models.CharField(max_length=240)

    class Meta:
        ordering = ("purchase_return", "line_number")
        constraints = [models.UniqueConstraint(fields=("purchase_return", "line_number"), name="uniq_purchase_return_line")]

    def clean(self):
        order_line = self.purchase_order_line
        if self.purchase_return_id and order_line.order_id != self.purchase_return.purchase_order_id:
            raise ValidationError({"purchase_order_line": "退货行必须来自退货单关联采购单"})
        if self.material_id != order_line.material_id or self.uom_id != order_line.uom_id:
            raise ValidationError("退货物料和单位必须与采购行一致")
        if order_line.returned_quantity + self.quantity > order_line.quantity:
            raise ValidationError({"quantity": "退货数量不能超过采购数量"})


class SalesReturn(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    customer = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="sales_returns")
    return_date = models.DateField(default=timezone.localdate)
    srm_number = models.CharField(max_length=80)
    reason = models.CharField(max_length=240)
    no_order = models.BooleanField(default=True)
    source_delivery = models.ForeignKey(DeliveryOrder, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_returns")
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
        for line in lines:
            line.full_clean()
        super().approve(actor)
        if self.posted:
            return
        for line in lines:
            if not line.material.no_stock_movement:
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
            order_line = line.sales_order_line or (line.source_delivery_line.sales_order_line if line.source_delivery_line_id else None)
            if order_line:
                if line.quantity > order_line.delivered_quantity:
                    raise ValidationError({"quantity": "退货数量不能超过销售订单已送数量"})
                order_line.delivered_quantity -= line.quantity
                order_line.returned_quantity += line.quantity
                order_line.save(update_fields=["delivered_quantity", "returned_quantity", "updated_at"])
        self.posted = True

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"SRT-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class SalesReturnLine(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="sales_return_lines")
    uom = models.ForeignKey(Uom, on_delete=models.PROTECT, related_name="sales_return_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    original_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="originating_sales_returns")
    return_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="received_sales_returns")
    batch_number = models.CharField(max_length=80, blank=True)
    sales_order_line = models.ForeignKey("SalesOrderLine", on_delete=models.PROTECT, null=True, blank=True, related_name="sales_return_lines")
    source_delivery_line = models.ForeignKey(DeliveryOrderLine, on_delete=models.PROTECT, null=True, blank=True, related_name="sales_return_lines")

    class Meta:
        ordering = ("sales_return", "line_number")
        constraints = [models.UniqueConstraint(fields=("sales_return", "line_number"), name="uniq_sales_return_line")]

    def clean(self):
        if self.sales_return_id and not self.sales_return.no_order and not self.sales_order_line_id and not self.source_delivery_line_id:
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
        if self.sales_return_id and self.sales_return.no_order and self.original_location_id and self.original_location.code.upper() == "FG01":
            if self.return_location.code.upper() != "RMA":
                raise ValidationError({"return_location": "FG01 无订单销售退货必须先进入实体不良仓 RMA"})
        if self.sales_return_id and self.source_delivery_line_id:
            source = self.source_delivery_line
            if self.sales_return.source_delivery_id and source.delivery_id != self.sales_return.source_delivery_id:
                raise ValidationError({"source_delivery_line": "退货行必须来自关联送货单"})
            if self.material_id != source.material_id or self.uom_id != source.uom_id:
                raise ValidationError("退货物料和单位必须与原送货明细一致")
            already_returned = source.sales_return_lines.filter(
                sales_return__status=ApprovalStatus.APPROVED,
            ).exclude(pk=self.pk).aggregate(quantity=models.Sum("quantity"))["quantity"] or Decimal("0")
            if already_returned + self.quantity > source.actual_quantity:
                raise ValidationError({"quantity": "退货数量不能超过原送货数量"})
