from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Max
from rest_framework import serializers

from backend.models import DeliveryOrder, DeliveryOrderLine, SalesReturn, SalesReturnLine

from .common import BaseSerializer


class DeliveryOrderSerializer(BaseSerializer):
    def validate_delivery_date(self, value):
        if self.instance and value.strftime("%Y%m") != self.instance.delivery_date.strftime("%Y%m"):
            raise serializers.ValidationError("已保存送货单不能跨月修改日期，请按新日期另建送货单")
        return value

    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = DeliveryOrder
        fields = "__all__"
        read_only_fields = (
            "number",
            "status",
            "posted",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "approved_by",
            "approved_at",
            "confirmed_by",
            "confirmed_at",
            "customer_code",
            "customer_name",
        )


class DeliveryOrderLineSerializer(BaseSerializer):
    def validate(self, attrs):
        from backend.delivery import validate_quantities

        if self.instance is None and attrs.get("delivery"):
            attrs["line_number"] = (attrs["delivery"].lines.aggregate(number=Max("line_number"))["number"] or 0) + 10
        if "actual_quantity" in attrs and "srm_quantity" not in attrs:
            attrs["srm_quantity"] = attrs["actual_quantity"]
        attrs = super().validate(attrs)
        instance = self.instance or DeliveryOrderLine(**attrs)
        try:
            if instance.delivery.posted:
                raise DjangoValidationError("已回写订单的送货单不可修改明细")
            validate_quantities(instance.delivery, [instance], exclude_line=instance.pk, whole=False)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return attrs

    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    material_specification = serializers.CharField(source="material.specification", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)
    order_number = serializers.CharField(source="sales_order_line.order.number", read_only=True)
    order_line_number = serializers.IntegerField(source="sales_order_line.line_number", read_only=True)
    customer_po = serializers.CharField(source="sales_order_line.order.customer_po", read_only=True)
    ordered_quantity = serializers.DecimalField(
        source="sales_order_line.quantity", max_digits=19, decimal_places=8, read_only=True
    )
    delivered_quantity = serializers.DecimalField(
        source="sales_order_line.delivered_quantity", max_digits=19, decimal_places=8, read_only=True
    )
    returned_quantity = serializers.DecimalField(
        source="sales_order_line.returned_quantity", max_digits=19, decimal_places=8, read_only=True
    )
    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryOrderLine
        fields = "__all__"
        read_only_fields = (
            "line_number",
            "source_snapshot",
            "modification_count",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "material_code",
            "material_name",
            "material_specification",
            "uom_code",
            "order_number",
            "customer_po",
            "ordered_quantity",
            "delivered_quantity",
            "returned_quantity",
            "remaining_quantity",
        )

    def get_remaining_quantity(self, obj):
        return max(obj.sales_order_line.quantity - obj.sales_order_line.delivered_quantity, 0)


class DeliveryOrderDetailSerializer(DeliveryOrderSerializer):
    source_location_code = serializers.CharField(source="source_location.code", read_only=True, allow_null=True)
    source_location_name = serializers.CharField(source="source_location.name", read_only=True, allow_null=True)
    lines = serializers.SerializerMethodField()

    class Meta(DeliveryOrderSerializer.Meta):
        fields = "__all__"

    def get_lines(self, obj):
        from backend.delivery import order_line_data

        result = []
        for line in obj.lines.all():
            source = order_line_data(line.sales_order_line)
            source.update(line.source_snapshot or {})
            source.update(DeliveryOrderLineSerializer(line).data)
            source.update(
                {
                    "source_location_code": line.source_location.code,
                    "source_location_name": line.source_location.name,
                    "line_created_by": line.created_by,
                    "line_created_at": line.created_at,
                    "line_updated_by": line.updated_by,
                    "line_updated_at": line.updated_at,
                    "line_modification_count": line.modification_count,
                }
            )
            from decimal import ROUND_HALF_UP, Decimal

            source["delivery_amount"] = str(
                (Decimal(source["unit_price"]) * line.actual_quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            result.append(source)
        return result


class SalesReturnSerializer(BaseSerializer):
    class Meta:
        model = SalesReturn
        fields = "__all__"
        read_only_fields = ("number", "posted", "stock_posted", "posting_version", "revision", "status", "created_by", "created_at", "updated_by", "updated_at", "approved_by", "approved_at", "confirmed_by", "confirmed_at", "is_signed", "signed_by", "signed_at", "source_key", "downstream_references")


class SalesReturnLineSerializer(BaseSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(read_only=True)
    material_specification = serializers.CharField(read_only=True)
    customer_material_code = serializers.CharField(read_only=True)
    terminal_customer_code = serializers.CharField(read_only=True)
    terminal_customer_name = serializers.CharField(read_only=True)
    inventory_uom = serializers.PrimaryKeyRelatedField(read_only=True)
    uom_rate_m = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)
    uom_rate_d = serializers.DecimalField(max_digits=19, decimal_places=8, read_only=True)

    class Meta:
        model = SalesReturnLine
        fields = "__all__"
        read_only_fields = ("line_number", "material_name", "material_specification", "customer_material_code", "terminal_customer_code", "terminal_customer_name", "inventory_uom", "uom_rate_m", "uom_rate_d", "created_by", "created_at", "updated_by", "updated_at", "modification_count")

    def validate(self, attrs):
        if self.instance is None and attrs.get("sales_return"):
            attrs["line_number"] = (attrs["sales_return"].lines.aggregate(number=Max("line_number"))["number"] or 0) + 10
        attrs = super().validate(attrs)
        if attrs.get("sales_return") and attrs.get("material") and attrs["sales_return"].no_order:
            from backend.no_order_returns import derive_line
            derived = SalesReturnLine(**attrs)
            derive_line(derived)
            attrs.update({key: getattr(derived, key) for key in (
                "customer_material", "customer_material_code", "terminal_customer_code", "terminal_customer_name",
                "material_name", "material_specification", "inventory_uom", "uom", "uom_rate_m", "uom_rate_d")})
        if self.instance and self.instance.sales_return.posted:
            raise serializers.ValidationError("已审核退货明细不可修改")
        return attrs


class SalesReturnDetailSerializer(SalesReturnSerializer):
    lines = serializers.SerializerMethodField()

    class Meta(SalesReturnSerializer.Meta):
        fields = "__all__"

    def get_lines(self, obj):
        return SalesReturnLineSerializer(obj.lines.select_related("material", "customer_material", "inventory_uom", "uom"), many=True).data
