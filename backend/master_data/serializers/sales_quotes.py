from django.db import transaction
from rest_framework import serializers

from backend.models import Currency, CustomerMaterial, Partner, SalesQuote, SalesQuoteLine, SalesQuoteTier

from .common import BaseSerializer


class CustomerMaterialSerializer(BaseSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    material_specification = serializers.CharField(source="material.specification", read_only=True)

    class Meta:
        model = CustomerMaterial
        fields = (
            "id",
            "customer",
            "material",
            "material_code",
            "material_name",
            "material_specification",
            "customer_code",
            "customer_name",
            "customer_specification",
            "customer_uom",
            "customer_uom_rate_m",
            "customer_uom_rate_d",
            "customer_barcode",
            "terminal_customer_code",
            "terminal_customer_name",
            "enabled",
            "notes",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )
        read_only_fields = (
            "material_code",
            "material_name",
            "material_specification",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )


class SalesQuoteTierSerializer(serializers.ModelSerializer):
    discounted_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SalesQuoteTier
        fields = "__all__"
        extra_kwargs = {"line_number": {"required": False}}
        read_only_fields = (
            "quote_line",
            "discounted_unit_price",
            "untaxed_unit_price",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "modification_count",
            "source_object",
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
            "discounted_unit_price",
            "untaxed_unit_price",
            "material_code",
            "uom_code",
            "customer_material_code",
            "customer_material_name",
            "terminal_customer_code",
            "terminal_customer_name",
            "material_name",
            "material_specification",
            "tax_rate",
            "uom",
            "uom_rate_m",
            "uom_rate_d",
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
        validated_data.update(
            {
                "line_number": validated_data.get("line_number") or 10,
                "uom": (customer_material.customer_uom if customer_material else None)
                or getattr(conversion, "business_uom", None)
                or material.uom,
                "tax_rate": quote.tax_rate,
                "uom_rate_m": customer_material.customer_uom_rate_m
                if customer_material and customer_material.customer_uom_id
                else getattr(conversion, "business_qty", 1),
                "uom_rate_d": customer_material.customer_uom_rate_d
                if customer_material and customer_material.customer_uom_id
                else getattr(conversion, "stock_qty", 1),
                "customer_material_code": customer_material.customer_code if customer_material else "",
                "customer_material_name": customer_material.customer_name if customer_material else "",
                "terminal_customer_code": customer_material.terminal_customer_code if customer_material else "",
                "terminal_customer_name": customer_material.terminal_customer_name if customer_material else "",
                "material_name": material.name,
                "material_specification": material.specification,
            }
        )
        line = SalesQuoteLine(**validated_data)
        line.full_clean()
        line.save()
        actor = self.context["request"].user.get_username() if self.context.get("request") else quote.created_by
        for index, data in enumerate(tiers, 1):
            SalesQuoteTier.objects.create(
                quote_line=line,
                line_number=data.get("line_number") or index * 10,
                min_quantity=data["min_quantity"],
                unit_price=data["unit_price"],
                backup_ratio=data.get("backup_ratio", quote.backup_ratio),
                notes=data.get("notes", ""),
                created_by=actor,
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
            "number",
            "backup_ratio",
            "address_snapshot",
            "payment_terms",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "is_confirmed",
            "confirmed_by",
            "confirmed_at",
            "is_ratified",
            "ratified_by",
            "ratified_at",
            "modification_count",
            "source_object",
            "customer_code",
            "customer_name",
            "currency_code",
            "material_code",
            "customer_material_code",
            "unit_price",
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
                getattr(self.instance, "discount_rate", None) if self.instance is not None else customer.discount_rate
            )
        attrs.update(
            {
                "backup_ratio": customer.backup_ratio,
                "payment_terms": customer.payment_terms,
            }
        )
        address_code = (
            attrs["address_code"] if "address_code" in attrs else getattr(self.instance, "address_code", None)
        )
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
        if customer_material and (
            customer_material.customer_id != quote.customer_id or customer_material.material_id != material.id
        ):
            raise serializers.ValidationError(
                {"lines": [{"customer_material": "客户、客户物料和本方物料必须三端一致"}]}
            )
        if customer_material and not customer_material.enabled:
            raise serializers.ValidationError({"lines": [{"customer_material": "客户物料已停用"}]})
        conversion = material.uom_conversions.select_related("business_uom").filter(usage="sales").first()
        uom = (
            (customer_material.customer_uom if customer_material else None)
            or getattr(conversion, "business_uom", None)
            or material.uom
        )
        rate_m = (
            customer_material.customer_uom_rate_m
            if customer_material and customer_material.customer_uom_id
            else getattr(conversion, "business_qty", 1)
        )
        rate_d = (
            customer_material.customer_uom_rate_d
            if customer_material and customer_material.customer_uom_id
            else getattr(conversion, "stock_qty", 1)
        )
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
