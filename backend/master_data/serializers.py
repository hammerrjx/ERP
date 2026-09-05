from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from backend.models import (
    ApprovalRule, AuditEvent, BillOfMaterial, BomLine, BusinessGroup, Company, Currency, CurrencyRate,
    CustomerMaterial, CustomerAddress, Department, DocumentEvidence, Employee, Location,
    Material, MaterialCompany, MaterialUomConversion, Partner, PartnerBankAccount, PaymentMethod,
    PartnerCompany, PartnerContact, ProductCategory, SupplierQuote, SupplierQuoteLine, TaxCode,
    DeliveryOrder, DeliveryOrderLine, GoodsReceipt, GoodsReceiptLine, PayableVoucher,
    PayableVoucherLine, PurchaseOrder, PurchaseOrderLine,
    PurchaseRequisition, PurchaseRequisitionLine, PurchaseReturn, PurchaseReturnLine,
    RequestForQuotation, RfqLine, Role, Routing, RoutingOperation, SalesOrder,
    SalesOrderLine, SalesQuote, SalesQuoteLine, SalesQuoteTier, SalesReturn, SalesReturnLine,
    StockBalance, StockCount,
    StockCountLine, StockTransaction, StockTransfer, StockTransferLine,
    SupplierInquiry, Uom, UomCategory, UserRole, Warehouse,
)


class BaseSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = self.instance or self.Meta.model()
        for name, value in attrs.items():
            if not self.Meta.model._meta.get_field(name).many_to_many:
                setattr(instance, name, value)
        try:
            instance.full_clean(exclude=[f.name for f in self.Meta.model._meta.many_to_many])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
        return attrs

    class Meta:
        fields = "__all__"


def serializer_for(model):
    audit_fields = ("created_by", "created_at", "updated_by", "updated_at")
    model_fields = {field.name for field in model._meta.get_fields()}
    return type(
        f"{model.__name__}Serializer",
        (BaseSerializer,),
        {"Meta": type("Meta", (), {
            "model": model,
            "fields": "__all__",
            "read_only_fields": tuple(field for field in audit_fields if field in model_fields),
        })},
    )


CompanySerializer = serializer_for(Company)
BusinessGroupSerializer = serializer_for(BusinessGroup)
CurrencySerializer = serializer_for(Currency)
CurrencyRateSerializer = serializer_for(CurrencyRate)
PaymentMethodSerializer = serializer_for(PaymentMethod)
class CustomerMaterialSerializer(BaseSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    material_specification = serializers.CharField(source="material.specification", read_only=True)

    class Meta:
        model = CustomerMaterial
        fields = (
            "id", "customer", "material", "material_code", "material_name", "material_specification",
            "customer_code", "customer_name", "customer_specification", "customer_uom",
            "customer_uom_rate_m", "customer_uom_rate_d", "customer_barcode",
            "terminal_customer_code", "terminal_customer_name", "enabled", "notes",
            "created_by", "created_at", "updated_by", "updated_at",
        )
        read_only_fields = ("material_code", "material_name", "material_specification", "created_by", "created_at", "updated_by", "updated_at")


class CustomerAddressSerializer(BaseSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
        read_only_fields = (
            "created_by", "created_at", "updated_by", "updated_at", "source_object", "source_key",
        )
DocumentEvidenceSerializer = serializer_for(DocumentEvidence)
LocationSerializer = serializer_for(Location)
MaterialSerializer = serializer_for(Material)
MaterialCompanySerializer = serializer_for(MaterialCompany)
MaterialUomConversionSerializer = serializer_for(MaterialUomConversion)

class PartnerContactInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerContact
        fields = ("name", "position", "phone", "fax", "email", "is_primary")


class PartnerSerializer(BaseSerializer):
    contacts = PartnerContactInputSerializer(many=True, required=False)
    payment_method_name = serializers.CharField(source="payment_method_master.description", read_only=True)

    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def validate(self, attrs):
        contacts = attrs.pop("contacts", None)
        master = attrs.get("payment_method_master")
        if master:
            attrs["payment_method"] = master.code
        elif attrs.get("payment_method"):
            attrs["payment_method_master"] = PaymentMethod.objects.filter(code=attrs["payment_method"]).first()
        attrs = super().validate(attrs)
        if contacts is not None and len(contacts) > 4:
            raise serializers.ValidationError({"contacts": "最多可保存 4 个联系方式"})
        attrs["contacts"] = contacts
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop("contacts", None)
        partner = Partner.objects.create(**validated_data)
        self._replace_contacts(partner, contacts)
        return partner

    @transaction.atomic
    def update(self, instance, validated_data):
        contacts = validated_data.pop("contacts", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.save()
        self._replace_contacts(instance, contacts)
        return instance

    @staticmethod
    def _replace_contacts(partner, contacts):
        if contacts is None:
            return
        partner.contacts.all().delete()
        PartnerContact.objects.bulk_create([
            PartnerContact(partner=partner, **contact) for contact in contacts if contact.get("name")
        ])


PartnerBankAccountSerializer = serializer_for(PartnerBankAccount)
PartnerCompanySerializer = serializer_for(PartnerCompany)
PartnerContactSerializer = serializer_for(PartnerContact)
EmployeeSerializer = serializer_for(Employee)
ProductCategorySerializer = serializer_for(ProductCategory)
TaxCodeSerializer = serializer_for(TaxCode)
UomSerializer = serializer_for(Uom)
UomCategorySerializer = serializer_for(UomCategory)
AuditEventSerializer = serializer_for(AuditEvent)
DepartmentSerializer = serializer_for(Department)
RoleSerializer = serializer_for(Role)
UserRoleSerializer = serializer_for(UserRole)
ApprovalRuleSerializer = serializer_for(ApprovalRule)
BillOfMaterialSerializer = serializer_for(BillOfMaterial)
BomLineSerializer = serializer_for(BomLine)
RoutingSerializer = serializer_for(Routing)
RoutingOperationSerializer = serializer_for(RoutingOperation)
WarehouseSerializer = serializer_for(Warehouse)


class SupplierQuoteLineSerializer(serializers.ModelSerializer):
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SupplierQuoteLine
        fields = "__all__"
        validators = []
        read_only_fields = (
            "quote", "unit_price", "untaxed_unit_price", "created_by", "created_at",
            "updated_by", "updated_at", "modification_count", "source_object",
        )
        extra_kwargs = {"line_number": {"required": False}}


class SupplierQuoteSerializer(serializers.ModelSerializer):
    lines = SupplierQuoteLineSerializer(many=True, required=False)
    supplier_code = serializers.CharField(source="supplier.code", read_only=True)
    supplier_name = serializers.CharField(source="supplier.short_name", read_only=True)
    business_group_code = serializers.CharField(source="business_group.code", read_only=True)
    business_group_name = serializers.CharField(source="business_group.name", read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    material_specification = serializers.CharField(source="material.specification", read_only=True)
    tax_code = serializers.CharField(source="material.tax_code", read_only=True)
    tax_name = serializers.CharField(source="material.tax_name", read_only=True)
    invoice_name = serializers.CharField(source="material.invoice_name", read_only=True)
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    purchase_uom_code = serializers.CharField(source="purchase_uom.code", read_only=True)
    operation_sequence = serializers.IntegerField(source="operation.sequence", read_only=True)
    parent_material_code = serializers.CharField(source="parent_material.code", read_only=True)
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    effective_min_purchase_qty = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    effective_min_pack_qty = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SupplierQuote
        fields = "__all__"
        read_only_fields = (
            "number", "currency", "purchase_uom", "uom_rate_m", "uom_rate_d",
            "tax_included", "tax_rate", "unit_price", "parent_material", "status",
            "created_by", "created_at", "updated_by", "updated_at", "approved_by",
            "approved_at", "rejection_reason", "is_confirmed", "confirmed_by", "confirmed_at",
            "is_ratified", "ratified_by", "ratified_at", "is_sales_confirmed",
            "sales_confirmed_by", "sales_confirmed_at", "modification_count", "source_object",
            "supplier_code", "supplier_name", "business_group_code", "business_group_name", "material_code", "material_name",
            "material_specification", "tax_code", "tax_name", "invoice_name", "currency_code",
            "purchase_uom_code", "operation_sequence", "parent_material_code",
            "untaxed_unit_price", "effective_min_purchase_qty", "effective_min_pack_qty",
        )

    def validate(self, attrs):
        supplier = attrs.get("supplier") or getattr(self.instance, "supplier", None)
        material = attrs.get("material") or getattr(self.instance, "material", None)
        quote_type = attrs.get("quote_type") or getattr(self.instance, "quote_type", None)
        operation = attrs.get("operation", getattr(self.instance, "operation", None))
        if not supplier or supplier.kind not in {Partner.PartnerKind.SUPPLIER, Partner.PartnerKind.BOTH}:
            raise serializers.ValidationError({"supplier": "报价必须关联供应商"})
        if supplier.status != "approved":
            raise serializers.ValidationError({"supplier": "供应商审核通过后才能建立报价"})
        if not supplier.currency_id:
            raise serializers.ValidationError({"supplier": "供应商资料未设置常用币种"})
        if not material or material.status != "approved":
            raise serializers.ValidationError({"material": "物料审核通过后才能建立报价"})
        business_group = attrs.get("business_group", getattr(self.instance, "business_group", None))
        if self.instance is None and not business_group:
            raise serializers.ValidationError({"business_group": "新建报价必须选择业务组"})
        if business_group and not business_group.active:
            raise serializers.ValidationError({"business_group": "业务组已停用"})
        if self.instance and self.instance.status not in {"draft", "rejected"}:
            raise serializers.ValidationError("只有草稿或已驳回报价可以修改")
        if quote_type == SupplierQuote.QuoteType.PURCHASE and operation:
            raise serializers.ValidationError({"operation": "采购报价不能关联外协工序"})
        conversion = material.uom_conversions.select_related("business_uom").filter(usage="purchase").first()
        attrs.update({
            "currency": supplier.currency,
            "tax_included": supplier.quote_tax_included,
            "tax_rate": supplier.tax_rate,
            "purchase_uom": getattr(conversion, "business_uom", None) or material.uom,
            "uom_rate_m": getattr(conversion, "business_qty", 1),
            "uom_rate_d": getattr(conversion, "stock_qty", 1),
            "parent_material": operation.routing.material if operation and quote_type == SupplierQuote.QuoteType.OUTSOURCE else None,
        })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        quote = SupplierQuote(**validated_data)
        try:
            quote.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict or exc.messages) from exc
        quote.save()
        self._replace_lines(quote, lines)
        return quote

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop("lines", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.modification_count += 1
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict or exc.messages) from exc
        instance.save()
        if lines is not None:
            self._replace_lines(instance, lines)
        return instance

    def _replace_lines(self, quote, lines):
        quote.lines.all().delete()
        actor = self.context["request"].user.get_username() if self.context.get("request") else quote.created_by
        for index, data in enumerate(lines, 1):
            values = {
                "quote": quote,
                "line_number": data.get("line_number") or index,
                "min_qty": data["min_qty"],
                "material_unit_price": data.get("material_unit_price") if quote.quote_type == SupplierQuote.QuoteType.PURCHASE else None,
                "processing_unit_price": data.get("processing_unit_price") if quote.quote_type == SupplierQuote.QuoteType.OUTSOURCE else None,
                "notes": data.get("notes", ""),
                "created_by": actor,
            }
            line = SupplierQuoteLine(**values)
            try:
                line.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict or exc.messages) from exc
            line.save()


class SalesQuoteTierSerializer(serializers.ModelSerializer):
    discounted_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SalesQuoteTier
        fields = "__all__"
        extra_kwargs = {"line_number": {"required": False}}
        read_only_fields = (
            "quote_line", "discounted_unit_price", "untaxed_unit_price", "created_by", "created_at",
            "updated_by", "updated_at", "modification_count", "source_object",
        )


class SalesQuoteLineSerializer(serializers.ModelSerializer):
    tiers = SalesQuoteTierSerializer(many=True, required=False)
    discounted_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)

    class Meta:
        model = SalesQuoteLine
        fields = "__all__"
        validators = []
        read_only_fields = (
            "discounted_unit_price", "untaxed_unit_price", "material_code", "uom_code",
            "customer_material_code", "customer_material_name", "terminal_customer_code",
            "terminal_customer_name", "material_name", "material_specification", "tax_rate",
            "uom", "uom_rate_m", "uom_rate_d",
        )
        extra_kwargs = {"quote": {"required": False}, "line_number": {"required": False}}

    def validate(self, attrs):
        quote = attrs.get("quote") or getattr(self.instance, "quote", None)
        material = attrs.get("material") or getattr(self.instance, "material", None)
        customer_material = attrs.get("customer_material") or getattr(self.instance, "customer_material", None)
        if quote and customer_material:
            if customer_material.customer_id != quote.customer_id:
                raise serializers.ValidationError({"customer_material": "客户物料不属于当前报价客户"})
            if material and customer_material.material_id != material.id:
                raise serializers.ValidationError({"customer_material": "客户物料与本方物料编码不匹配"})
            if not customer_material.enabled:
                raise serializers.ValidationError({"customer_material": "客户物料已停用"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tiers = validated_data.pop("tiers", [])
        quote = validated_data["quote"]
        material = validated_data["material"]
        customer_material = validated_data.get("customer_material")
        conversion = material.uom_conversions.select_related("business_uom").filter(usage="sales").first()
        validated_data.update({
            "line_number": validated_data.get("line_number") or 10,
            "uom": (customer_material.customer_uom if customer_material else None) or getattr(conversion, "business_uom", None) or material.uom,
            "tax_rate": quote.tax_rate,
            "uom_rate_m": customer_material.customer_uom_rate_m if customer_material and customer_material.customer_uom_id else getattr(conversion, "business_qty", 1),
            "uom_rate_d": customer_material.customer_uom_rate_d if customer_material and customer_material.customer_uom_id else getattr(conversion, "stock_qty", 1),
            "customer_material_code": customer_material.customer_code if customer_material else "",
            "customer_material_name": customer_material.customer_name if customer_material else "",
            "terminal_customer_code": customer_material.terminal_customer_code if customer_material else "",
            "terminal_customer_name": customer_material.terminal_customer_name if customer_material else "",
            "material_name": material.name,
            "material_specification": material.specification,
        })
        line = SalesQuoteLine(**validated_data)
        line.full_clean()
        line.save()
        actor = self.context["request"].user.get_username() if self.context.get("request") else quote.created_by
        for index, data in enumerate(tiers, 1):
            SalesQuoteTier.objects.create(
                quote_line=line, line_number=data.get("line_number") or index * 10,
                min_quantity=data["min_quantity"], unit_price=data["unit_price"],
                backup_ratio=data.get("backup_ratio", quote.backup_ratio), notes=data.get("notes", ""), created_by=actor,
            )
        return line


class SalesQuoteSerializer(serializers.ModelSerializer):
    lines = SalesQuoteLineSerializer(many=True)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), required=False)
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    material_code = serializers.SerializerMethodField()
    customer_material_code = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()

    class Meta:
        model = SalesQuote
        fields = "__all__"
        read_only_fields = (
            "number", "backup_ratio",
            "address_snapshot", "payment_terms", "status", "created_by", "created_at", "updated_by",
            "updated_at", "approved_by", "approved_at", "rejection_reason", "is_confirmed",
            "confirmed_by", "confirmed_at", "is_ratified", "ratified_by", "ratified_at",
            "modification_count", "source_object", "customer_code", "customer_name", "currency_code",
            "material_code", "customer_material_code", "unit_price",
        )

    def _first_line(self, obj):
        if not hasattr(obj, "_serialized_first_line"):
            lines = list(obj.lines.all())
            obj._serialized_first_line = lines[0] if lines else None
        return obj._serialized_first_line

    def get_material_code(self, obj):
        line = self._first_line(obj)
        return line.material.code if line else ""

    def get_customer_material_code(self, obj):
        line = self._first_line(obj)
        return line.customer_material_code if line else ""

    def get_unit_price(self, obj):
        line = self._first_line(obj)
        return format(line.unit_price, ".8f") if line else None

    def validate(self, attrs):
        customer = attrs.get("customer") or getattr(self.instance, "customer", None)
        lines = attrs.get("lines")
        if not customer or customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise serializers.ValidationError({"customer": "销售报价必须关联客户"})
        if not customer.currency_id:
            raise serializers.ValidationError({"customer": "客户资料未设置常用币种"})
        if self.instance and self.instance.status not in {"draft", "rejected"}:
            raise serializers.ValidationError("只有草稿或已驳回报价可以修改")
        if lines is not None and len(lines) != 1:
            raise serializers.ValidationError({"lines": "每张销售报价必须且只能包含一个本方物料"})
        if "currency" not in attrs:
            attrs["currency"] = customer.currency
        if "tax_included" not in attrs:
            attrs["tax_included"] = customer.quote_tax_included
        if "tax_rate" not in attrs:
            attrs["tax_rate"] = customer.tax_rate
        if "discount_rate" not in attrs:
            attrs["discount_rate"] = (
                getattr(self.instance, "discount_rate", None)
                if self.instance is not None else customer.discount_rate
            )
        attrs.update({
            "backup_ratio": customer.backup_ratio,
            "payment_terms": customer.payment_terms,
        })
        address_code = attrs["address_code"] if "address_code" in attrs else getattr(self.instance, "address_code", None)
        if address_code:
            if address_code.customer_id != customer.id or not address_code.enabled:
                raise serializers.ValidationError({"address_code": "客户地址不存在、已停用或不属于当前客户"})
            attrs["address_snapshot"] = address_code.address
            attrs["address"] = address_code.address
        elif "address" not in attrs:
            attrs["address"] = getattr(self.instance, "address", None) or customer.delivery_address or customer.address
        expiry = attrs.get("expiry_date", getattr(self.instance, "expiry_date", None))
        effective = attrs.get("effective_date", getattr(self.instance, "effective_date", None))
        if expiry and effective and expiry < effective:
            raise serializers.ValidationError({"expiry_date": "失效日期不能早于生效日期"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop("lines")
        quote = SalesQuote(**validated_data)
        quote.full_clean()
        quote.save()
        self._replace_line(quote, lines[0], creating=True)
        return quote

    @transaction.atomic
    def update(self, instance, validated_data):
        line_data = validated_data.pop("lines", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.modification_count += 1
        instance.full_clean()
        instance.save()
        if line_data is not None:
            self._replace_line(instance, line_data[0], creating=False)
        return instance

    def _replace_line(self, quote, data, creating):
        tiers = data.pop("tiers", [])
        material = data["material"]
        customer_material = data.get("customer_material")
        if customer_material and (customer_material.customer_id != quote.customer_id or customer_material.material_id != material.id):
            raise serializers.ValidationError({"lines": [{"customer_material": "客户、客户物料和本方物料必须三端一致"}]})
        if customer_material and not customer_material.enabled:
            raise serializers.ValidationError({"lines": [{"customer_material": "客户物料已停用"}]})
        conversion = material.uom_conversions.select_related("business_uom").filter(usage="sales").first()
        uom = (customer_material.customer_uom if customer_material else None) or getattr(conversion, "business_uom", None) or material.uom
        rate_m = customer_material.customer_uom_rate_m if customer_material and customer_material.customer_uom_id else getattr(conversion, "business_qty", 1)
        rate_d = customer_material.customer_uom_rate_d if customer_material and customer_material.customer_uom_id else getattr(conversion, "stock_qty", 1)
        values = {
            **data,
            "line_number": data.get("line_number") or 10,
            "uom": uom,
            "tax_rate": quote.tax_rate,
            "uom_rate_m": rate_m,
            "uom_rate_d": rate_d,
            "customer_material_code": customer_material.customer_code if customer_material else "",
            "customer_material_name": customer_material.customer_name if customer_material else "",
            "terminal_customer_code": customer_material.terminal_customer_code if customer_material else "",
            "terminal_customer_name": customer_material.terminal_customer_name if customer_material else "",
            "material_name": material.name,
            "material_specification": material.specification,
        }
        if creating:
            line = SalesQuoteLine(quote=quote, **values)
        else:
            line = quote.lines.select_for_update().first()
            if not line:
                line = SalesQuoteLine(quote=quote)
            for name, value in values.items():
                setattr(line, name, value)
        line.full_clean()
        line.save()
        line.tiers.all().delete()
        actor = self.context["request"].user.get_username() if self.context.get("request") else quote.created_by
        for index, tier_data in enumerate(tiers, 1):
            tier = SalesQuoteTier(
                quote_line=line,
                line_number=tier_data.get("line_number") or index * 10,
                min_quantity=tier_data["min_quantity"],
                unit_price=tier_data["unit_price"],
                backup_ratio=tier_data.get("backup_ratio", quote.backup_ratio),
                notes=tier_data.get("notes", ""),
                created_by=actor,
            )
            tier.full_clean()
            tier.save()
class SalesOrderLineInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderLine
        fields = "__all__"
        read_only_fields = (
            "order",
            "customer_material_name", "customer_material_specification", "terminal_customer_code", "terminal_customer_name",
            "material_name", "material_specification", "tax_code", "tax_name", "invoice_name",
            "inventory_uom", "uom_rate_m", "uom_rate_d", "spare_ratio", "delivered_spare_quantity",
            "returned_quantity", "returned_spare_quantity", "discount_rate", "discounted_unit_price",
            "untaxed_unit_price", "tax_included_amount", "untaxed_amount", "total_cost", "after_sales_method",
            "after_sales_method_name", "line_status", "closed_by", "closed_at", "income_account",
            "income_account_name", "replenishment_return", "products_per_carton", "cartons",
            "configuration_approved", "configuration_approved_by", "configuration_approved_at",
            "created_by", "created_at", "updated_by", "updated_at", "modification_count",
        )
        extra_kwargs = {
            "line_number": {"required": False}, "customer_material": {"required": False}, "uom": {"required": False},
            "unit_price": {"required": False}, "source_quote_line": {"required": False},
        }


class SalesOrderSerializer(BaseSerializer):
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    lines = SalesOrderLineInputSerializer(many=True, required=False)

    class Meta:
        model = SalesOrder
        fields = "__all__"
        read_only_fields = (
            "number", "address_snapshot", "status", "created_by", "created_at", "updated_by", "updated_at",
            "approved_by", "approved_at", "rejection_reason", "is_confirmed", "confirmed_by", "confirmed_at",
            "customer_code", "customer_name",
            "source_quote",
            "po_change_by", "po_change_at", "po_change_confirmed", "po_change_confirmed_by", "po_change_confirmed_at",
            "delivery_approved", "delivery_approved_by", "delivery_approved_at", "print_count",
        )

    def validate(self, attrs):
        customer = attrs.get("customer") or getattr(self.instance, "customer", None)
        address = attrs["address_code"] if "address_code" in attrs else getattr(self.instance, "address_code", None)
        if not customer or customer.kind not in {Partner.PartnerKind.CUSTOMER, Partner.PartnerKind.BOTH}:
            raise serializers.ValidationError({"customer": "销售订单必须关联客户"})
        if address and address.customer_id != customer.id:
            raise serializers.ValidationError({"address_code": "订单地址必须属于当前客户"})
        if address and not address.enabled:
            raise serializers.ValidationError({"address_code": "客户地址已停用"})
        employee = attrs.get("sales_person") or getattr(self.instance, "sales_person", None)
        if employee and (not employee.is_employee or employee.is_locked or employee.is_left):
            raise serializers.ValidationError({"sales_person": "业务员必须是启用中的员工"})
        payment_method = attrs.get("payment_method") or getattr(self.instance, "payment_method", None)
        if payment_method and payment_method.is_void:
            raise serializers.ValidationError({"payment_method": "支付方式已作废"})
        business_group = attrs.get("business_group") or getattr(self.instance, "business_group", None)
        if business_group and not business_group.active:
            raise serializers.ValidationError({"business_group": "业务组已停用"})
        order_type = attrs.get("order_type", getattr(self.instance, "order_type", SalesOrder.OrderType.FORMAL))
        if order_type not in {SalesOrder.OrderType.FORMAL, SalesOrder.OrderType.SAMPLE}:
            raise serializers.ValidationError({"order_type": "单别只能选择正式订单或样品订单"})
        lines = attrs.get("lines")
        if lines is not None:
            if not lines:
                raise serializers.ValidationError({"lines": "客户订单至少需要一条明细"})
            for index, line in enumerate(lines, 1):
                if not line.get("line_number"):
                    line["line_number"] = index * 10
                customer_material = line.get("customer_material")
                if customer_material and (customer_material.customer_id != customer.id or customer_material.material_id != line["material"].id or not customer_material.enabled):
                    raise serializers.ValidationError({"lines": [{"customer_material": "客户物料与客户/物料不匹配或已停用"}]})
                source_quote_line = line.get("source_quote_line")
                if source_quote_line:
                    if (source_quote_line.quote.customer_id != customer.id or source_quote_line.material_id != line["material"].id
                            or not source_quote_line.quote.is_ratified):
                        raise serializers.ValidationError({"lines": [{"source_quote_line": "来源销售报价与订单客户、物料不匹配或未核准"}]})
                    quote = source_quote_line.quote
                    order_currency = attrs.get("currency") or getattr(self.instance, "currency", None)
                    order_date = attrs.get("order_date") or getattr(self.instance, "order_date", None) or timezone.localdate()
                    if quote.currency_id != order_currency.id:
                        raise serializers.ValidationError({"lines": [{"source_quote_line": "来源销售报价币种与订单币种不一致"}]})
                    if quote.effective_date > order_date or (quote.expiry_date and quote.expiry_date < order_date):
                        raise serializers.ValidationError({"lines": [{"source_quote_line": "来源销售报价在订单日期无效"}]})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        order = SalesOrder(**validated_data)
        order.full_clean()
        order.save()
        self._replace_lines(order, lines)
        self._sync_source_quote(order)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop("lines", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.full_clean()
        instance.save()
        if lines is not None:
            self._replace_lines(instance, lines)
            self._sync_source_quote(instance)
        return instance

    @staticmethod
    def _sync_source_quote(order):
        quote_line = order.lines.select_related("source_quote_line__quote").filter(source_quote_line__isnull=False).first()
        quote = quote_line.source_quote_line.quote if quote_line else None
        quote_id = quote.id if quote else None
        if order.source_quote_id != quote_id:
            order.source_quote = quote
            order.save(update_fields=["source_quote", "updated_at"])

    @staticmethod
    def _replace_lines(order, lines):
        order.lines.all().delete()
        for index, data in enumerate(lines, 1):
            data = dict(data)
            data["order"] = order
            data["line_number"] = data.get("line_number") or index * 10
            customer_material = data.get("customer_material")
            if not data.get("uom"):
                data["uom"] = (customer_material.customer_uom if customer_material and customer_material.customer_uom_id else data["material"].uom)
            if not data.get("source_quote_line"):
                quote_filter = {
                    "quote__customer": order.customer,
                    "quote__currency": order.currency,
                    "material": data["material"],
                    "quote__is_ratified": True,
                    "quote__effective_date__lte": order.order_date,
                }
                customer_code = customer_material.customer_code if customer_material else ""
                data["source_quote_line"] = SalesQuoteLine.objects.filter(
                    **quote_filter, customer_material_code=customer_code,
                ).filter(
                    Q(quote__expiry_date__isnull=True) | Q(quote__expiry_date__gte=order.order_date),
                ).select_related("quote").order_by(
                    "-quote__effective_date", "-quote__created_at", "-quote__number",
                ).first()
            line = SalesOrderLine(**data)
            line.created_by = order.created_by
            line.sync_derived_values()
            line.full_clean()
            line.save()


class SalesOrderListSerializer(serializers.ModelSerializer):
    """Keep the order list lightweight; detail/edit requests use SalesOrderSerializer."""
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = SalesOrder
        fields = tuple(field.name for field in SalesOrder._meta.fields) + ("customer_code", "customer_name")
        read_only_fields = fields


class SalesOrderLineSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name_display = serializers.CharField(source="material.name", read_only=True)
    customer_material_code = serializers.SerializerMethodField()
    uom_code = serializers.CharField(source="uom.code", read_only=True)
    inventory_uom_code = serializers.CharField(source="inventory_uom.code", read_only=True)
    currency_code = serializers.CharField(source="order.currency.code", read_only=True)
    order_notes = serializers.CharField(source="order.notes", read_only=True)
    customer_material_notes = serializers.CharField(source="customer_material.notes", read_only=True, allow_null=True)
    executed_positive_quantity = serializers.SerializerMethodField()
    executed_negative_quantity = serializers.SerializerMethodField()
    net_executed_quantity = serializers.SerializerMethodField()
    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderLine
        fields = "__all__"
        read_only_fields = (
            "material_code", "material_name_display", "customer_material_code", "uom_code", "inventory_uom_code", "currency_code", "order_notes", "customer_material_notes",
            "executed_positive_quantity", "executed_negative_quantity", "net_executed_quantity", "remaining_quantity",
            "customer_material_name", "customer_material_specification", "terminal_customer_code", "terminal_customer_name",
            "material_name", "material_specification", "tax_code", "tax_name", "invoice_name",
            "inventory_uom", "uom_rate_m", "uom_rate_d", "spare_ratio", "delivered_spare_quantity",
            "returned_quantity", "returned_spare_quantity", "discount_rate", "discounted_unit_price",
            "untaxed_unit_price", "tax_included_amount", "untaxed_amount", "total_cost", "after_sales_method",
            "after_sales_method_name", "line_status", "closed_by", "closed_at", "income_account",
            "income_account_name", "replenishment_return", "products_per_carton", "cartons",
            "configuration_approved", "configuration_approved_by", "configuration_approved_at",
            "created_by", "created_at", "updated_by", "updated_at", "modification_count",
        )
        extra_kwargs = {"line_number": {"required": False}, "customer_material": {"required": False}, "uom": {"required": False}, "source_quote_line": {"required": False}}

    def get_customer_material_code(self, obj):
        return obj.customer_material.customer_code if obj.customer_material_id else ""

    def _execution_totals(self, obj):
        totals = getattr(obj, "_execution_totals", None)
        if totals is None:
            from django.db.models import Case, DecimalField, Sum, Value, When
            totals = obj.delivery_lines.filter(delivery__status="approved").aggregate(
                positive=Sum(Case(When(actual_quantity__gt=0, then="actual_quantity"), default=Value(0), output_field=DecimalField(max_digits=18, decimal_places=6))),
                negative=Sum(Case(When(actual_quantity__lt=0, then="actual_quantity"), default=Value(0), output_field=DecimalField(max_digits=18, decimal_places=6))),
            )
            obj._execution_totals = totals
        return totals

    def get_executed_positive_quantity(self, obj):
        return self._execution_totals(obj).get("positive") or 0

    def get_executed_negative_quantity(self, obj):
        return abs(self._execution_totals(obj).get("negative") or 0)

    def get_net_executed_quantity(self, obj):
        totals = self._execution_totals(obj)
        return max((totals.get("positive") or 0) + (totals.get("negative") or 0), 0)

    def get_remaining_quantity(self, obj):
        totals = self._execution_totals(obj)
        return max(obj.quantity - max((totals.get("positive") or 0) + (totals.get("negative") or 0), 0), 0)

    def validate(self, attrs):
        order = attrs.get("order") or getattr(self.instance, "order", None)
        material = attrs.get("material") or getattr(self.instance, "material", None)
        customer_material = attrs.get("customer_material") or getattr(self.instance, "customer_material", None)
        source_quote_line = attrs.get("source_quote_line") or getattr(self.instance, "source_quote_line", None)
        if order and customer_material and (customer_material.customer_id != order.customer_id or customer_material.material_id != material.id or not customer_material.enabled):
            raise serializers.ValidationError({"customer_material": "客户物料与客户/物料不匹配或已停用"})
        if source_quote_line:
            if source_quote_line.quote.customer_id != order.customer_id or source_quote_line.material_id != material.id or not source_quote_line.quote.is_ratified:
                raise serializers.ValidationError({"source_quote_line": "来源销售报价与订单客户、物料不匹配或未核准"})
            if source_quote_line.quote.currency_id != order.currency_id:
                raise serializers.ValidationError({"source_quote_line": "来源销售报价币种与订单币种不一致"})
            if source_quote_line.quote.effective_date > order.order_date or (source_quote_line.quote.expiry_date and source_quote_line.quote.expiry_date < order.order_date):
                raise serializers.ValidationError({"source_quote_line": "来源销售报价在订单日期无效"})
        return attrs

    def create(self, validated_data):
        line = SalesOrderLine(**validated_data)
        line.created_by = self.context.get("request").user.get_username() if self.context.get("request") else ""
        line.sync_derived_values()
        line.full_clean()
        line.save()
        return line

    def update(self, instance, validated_data):
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.modification_count += 1
        instance.sync_derived_values()
        instance.full_clean()
        instance.save()
        return instance
PurchaseRequisitionSerializer = serializer_for(PurchaseRequisition)
PurchaseRequisitionLineSerializer = serializer_for(PurchaseRequisitionLine)
RequestForQuotationSerializer = serializer_for(RequestForQuotation)
RfqLineSerializer = serializer_for(RfqLine)
SupplierInquirySerializer = serializer_for(SupplierInquiry)
PurchaseOrderSerializer = serializer_for(PurchaseOrder)


class PurchaseOrderLineSerializer(BaseSerializer):
    class Meta:
        model = PurchaseOrderLine
        fields = "__all__"

    def validate(self, attrs):
        quote = attrs.get("source_supplier_quote") or getattr(self.instance, "source_supplier_quote", None)
        if not quote:
            return super().validate(attrs)
        order = attrs.get("order") or getattr(self.instance, "order", None)
        material = attrs.get("material") or getattr(self.instance, "material", None)
        quantity = attrs.get("quantity") or getattr(self.instance, "quantity", None)
        if quote.status != "approved" or not quote.is_confirmed or not quote.is_ratified:
            raise serializers.ValidationError({"source_supplier_quote": "只能使用已采购确认、已审核并核准的报价"})
        if quote.supplier_id != order.supplier_id or quote.currency_id != order.currency_id:
            raise serializers.ValidationError({"source_supplier_quote": "报价供应商和币种必须与采购单一致"})
        if quote.material_id != material.id:
            raise serializers.ValidationError({"source_supplier_quote": "报价物料必须与采购明细一致"})
        expected_type = SupplierQuote.QuoteType.OUTSOURCE if order.purchase_type == PurchaseOrder.PurchaseType.OUTSOURCE else SupplierQuote.QuoteType.PURCHASE
        if quote.quote_type != expected_type:
            raise serializers.ValidationError({"source_supplier_quote": "报价类型与采购类型不一致"})
        if quote.effective_date > order.order_date or (quote.expiry_date and quote.expiry_date < order.order_date):
            raise serializers.ValidationError({"source_supplier_quote": "报价在采购单日期无效"})
        try:
            unit_price, tier = quote.price_for(quantity)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"source_supplier_quote": exc.messages}) from exc
        supplied_tier = attrs.get("source_supplier_quote_line")
        if supplied_tier and supplied_tier != tier:
            raise serializers.ValidationError({"source_supplier_quote_line": "阶梯行与采购数量不匹配"})
        attrs.update({
            "unit_price": unit_price,
            "uom": quote.purchase_uom or material.uom,
            "source_supplier_quote_line": tier,
        })
        return super().validate(attrs)
GoodsReceiptSerializer = serializer_for(GoodsReceipt)
GoodsReceiptLineSerializer = serializer_for(GoodsReceiptLine)
PayableVoucherSerializer = serializer_for(PayableVoucher)
PayableVoucherLineSerializer = serializer_for(PayableVoucherLine)
StockBalanceSerializer = serializer_for(StockBalance)
StockTransactionSerializer = serializer_for(StockTransaction)
class DeliveryOrderSerializer(BaseSerializer):
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    class Meta:
        model = DeliveryOrder
        fields = "__all__"
        read_only_fields = ("number", "status", "posted", "created_by", "created_at", "updated_by", "updated_at", "approved_by", "approved_at", "confirmed_by", "confirmed_at", "customer_code", "customer_name")


class DeliveryOrderLineSerializer(BaseSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    material_specification = serializers.CharField(source="material.specification", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)
    order_number = serializers.CharField(source="sales_order_line.order.number", read_only=True)
    customer_po = serializers.CharField(source="sales_order_line.order.customer_po", read_only=True)
    ordered_quantity = serializers.DecimalField(source="sales_order_line.quantity", max_digits=18, decimal_places=6, read_only=True)
    delivered_quantity = serializers.DecimalField(source="sales_order_line.delivered_quantity", max_digits=18, decimal_places=6, read_only=True)
    returned_quantity = serializers.DecimalField(source="sales_order_line.returned_quantity", max_digits=18, decimal_places=6, read_only=True)
    remaining_quantity = serializers.SerializerMethodField()
    class Meta:
        model = DeliveryOrderLine
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at", "material_code", "material_name", "material_specification", "uom_code", "order_number", "customer_po", "ordered_quantity", "delivered_quantity", "returned_quantity", "remaining_quantity")

    def get_remaining_quantity(self, obj):
        return max(obj.sales_order_line.quantity - obj.sales_order_line.delivered_quantity, 0)


class DeliveryOrderDetailSerializer(DeliveryOrderSerializer):
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, allow_null=True)
    source_location_name = serializers.CharField(source="source_location.name", read_only=True, allow_null=True)
    lines = serializers.SerializerMethodField()

    class Meta(DeliveryOrderSerializer.Meta):
        fields = "__all__"

    def get_lines(self, obj):
        data = DeliveryOrderLineSerializer(obj.lines.all(), many=True).data
        order_lines = {line.pk: line.sales_order_line for line in obj.lines.all()}
        for item in data:
            source = order_lines[item["id"]]
            item.update({
                "order_line_number": source.line_number,
                "unit_price": str(source.unit_price),
                "currency_code": source.order.currency.code,
                "tax_rate": str(source.order.tax_rate),
                "spare_quantity": str(source.spare_quantity),
                "delivered_spare_quantity": str(source.delivered_spare_quantity),
                "uom_rate_m": str(source.uom_rate_m),
                "uom_rate_d": str(source.uom_rate_d),
                "inventory_uom_code": source.inventory_uom.code if source.inventory_uom_id else "",
                "customer_material_code": source.customer_material.customer_code if source.customer_material_id else "",
                "customer_material_name": source.customer_material_name,
                "customer_material_specification": source.customer_material_specification,
                "customer_material_notes": source.customer_material.notes if source.customer_material_id else "",
                "terminal_customer_code": source.terminal_customer_code,
                "terminal_customer_name": source.terminal_customer_name,
                "order_notes": source.order.notes,
                "line_created_by": source.created_by,
                "line_created_at": source.created_at,
                "line_updated_by": source.updated_by,
                "line_updated_at": source.updated_at,
                "line_modification_count": source.modification_count,
                "source_location_code": next(line.source_location.code for line in obj.lines.all() if line.pk == item["id"]),
                "source_location_name": next(line.source_location.name for line in obj.lines.all() if line.pk == item["id"]),
            })
        return data
StockTransferSerializer = serializer_for(StockTransfer)
StockTransferLineSerializer = serializer_for(StockTransferLine)
StockCountSerializer = serializer_for(StockCount)
StockCountLineSerializer = serializer_for(StockCountLine)
PurchaseReturnSerializer = serializer_for(PurchaseReturn)
PurchaseReturnLineSerializer = serializer_for(PurchaseReturnLine)
SalesReturnSerializer = serializer_for(SalesReturn)
SalesReturnLineSerializer = serializer_for(SalesReturnLine)


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "is_active", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return self.Meta.model.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
