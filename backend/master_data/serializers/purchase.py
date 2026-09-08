from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from backend.models import (
    GoodsReceipt,
    GoodsReceiptLine,
    Partner,
    PayableVoucher,
    PayableVoucherLine,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchaseReturn,
    PurchaseReturnLine,
    RequestForQuotation,
    RfqLine,
    SupplierInquiry,
    SupplierQuote,
    SupplierQuoteLine,
)

from .common import BaseSerializer, serializer_for


class SupplierQuoteLineSerializer(serializers.ModelSerializer):
    untaxed_unit_price = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SupplierQuoteLine
        fields = "__all__"
        validators = []
        read_only_fields = (
            "quote",
            "unit_price",
            "untaxed_unit_price",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "modification_count",
            "source_object",
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
            "number",
            "currency",
            "purchase_uom",
            "uom_rate_m",
            "uom_rate_d",
            "tax_included",
            "tax_rate",
            "unit_price",
            "parent_material",
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
            "is_sales_confirmed",
            "sales_confirmed_by",
            "sales_confirmed_at",
            "modification_count",
            "source_object",
            "supplier_code",
            "supplier_name",
            "business_group_code",
            "business_group_name",
            "material_code",
            "material_name",
            "material_specification",
            "tax_code",
            "tax_name",
            "invoice_name",
            "currency_code",
            "purchase_uom_code",
            "operation_sequence",
            "parent_material_code",
            "untaxed_unit_price",
            "effective_min_purchase_qty",
            "effective_min_pack_qty",
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
        attrs.update(
            {
                "currency": supplier.currency,
                "tax_included": supplier.quote_tax_included,
                "tax_rate": supplier.tax_rate,
                "purchase_uom": getattr(conversion, "business_uom", None) or material.uom,
                "uom_rate_m": getattr(conversion, "business_qty", 1),
                "uom_rate_d": getattr(conversion, "stock_qty", 1),
                "parent_material": operation.routing.material
                if operation and quote_type == SupplierQuote.QuoteType.OUTSOURCE
                else None,
            }
        )
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
                "material_unit_price": data.get("material_unit_price")
                if quote.quote_type == SupplierQuote.QuoteType.PURCHASE
                else None,
                "processing_unit_price": data.get("processing_unit_price")
                if quote.quote_type == SupplierQuote.QuoteType.OUTSOURCE
                else None,
                "notes": data.get("notes", ""),
                "created_by": actor,
            }
            line = SupplierQuoteLine(**values)
            try:
                line.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict or exc.messages) from exc
            line.save()


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
        expected_type = (
            SupplierQuote.QuoteType.OUTSOURCE
            if order.purchase_type == PurchaseOrder.PurchaseType.OUTSOURCE
            else SupplierQuote.QuoteType.PURCHASE
        )
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
        attrs.update(
            {
                "unit_price": unit_price,
                "uom": quote.purchase_uom or material.uom,
                "source_supplier_quote_line": tier,
            }
        )
        return super().validate(attrs)


GoodsReceiptSerializer = serializer_for(GoodsReceipt)


GoodsReceiptLineSerializer = serializer_for(GoodsReceiptLine)


PayableVoucherSerializer = serializer_for(PayableVoucher)


PayableVoucherLineSerializer = serializer_for(PayableVoucherLine)


PurchaseReturnSerializer = serializer_for(PurchaseReturn)


PurchaseReturnLineSerializer = serializer_for(PurchaseReturnLine)
