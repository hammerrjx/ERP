from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from backend.models import DeliveryOrder, DeliveryOrderLine, SalesReturn, SalesReturnLine

from .common import BaseSerializer, serializer_for


class DeliveryOrderSerializer(BaseSerializer):
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


SalesReturnSerializer = serializer_for(SalesReturn)


SalesReturnLineSerializer = serializer_for(SalesReturnLine)
