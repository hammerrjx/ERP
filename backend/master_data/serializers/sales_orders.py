from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from backend.models import Partner, SalesOrder, SalesOrderLine

from .common import BaseSerializer


def clean_sales_order(instance):
    try:
        instance.full_clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages) from exc


class SalesOrderLineInputSerializer(serializers.ModelSerializer):
    execution_summary = serializers.SerializerMethodField()

    def get_execution_summary(self, obj):
        from backend.delivery import execution_summary

        return execution_summary(obj)

    class Meta:
        model = SalesOrderLine
        fields = "__all__"
        read_only_fields = (
            "order",
            "delivered_quantity",
            "customer_material_name",
            "customer_material_specification",
            "terminal_customer_code",
            "terminal_customer_name",
            "material_name",
            "material_specification",
            "tax_code",
            "tax_name",
            "invoice_name",
            "inventory_uom",
            "uom_rate_m",
            "uom_rate_d",
            "spare_ratio",
            "delivered_spare_quantity",
            "returned_quantity",
            "returned_spare_quantity",
            "discount_rate",
            "discounted_unit_price",
            "untaxed_unit_price",
            "tax_included_amount",
            "untaxed_amount",
            "total_cost",
            "after_sales_method",
            "after_sales_method_name",
            "line_status",
            "closed_by",
            "closed_at",
            "income_account",
            "income_account_name",
            "replenishment_return",
            "products_per_carton",
            "cartons",
            "configuration_approved",
            "configuration_approved_by",
            "configuration_approved_at",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "modification_count",
        )
        extra_kwargs = {
            "line_number": {"required": False},
            "customer_material": {"required": False},
            "uom": {"required": False},
            "unit_price": {"required": False},
            "source_quote_line": {"required": False},
        }


class SalesOrderSerializer(BaseSerializer):
    customer_code = serializers.CharField(source="customer.code", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    lines = SalesOrderLineInputSerializer(many=True, required=False)

    class Meta:
        model = SalesOrder
        fields = "__all__"
        read_only_fields = (
            "number",
            "address_snapshot",
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
            "customer_code",
            "customer_name",
            "source_quote",
            "po_change_by",
            "po_change_at",
            "po_change_confirmed",
            "po_change_confirmed_by",
            "po_change_confirmed_at",
            "delivery_approved",
            "delivery_approved_by",
            "delivery_approved_at",
            "print_count",
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
                if customer_material and (
                    customer_material.customer_id != customer.id
                    or customer_material.material_id != line["material"].id
                    or not customer_material.enabled
                ):
                    raise serializers.ValidationError(
                        {"lines": [{"customer_material": "客户物料与客户/物料不匹配或已停用"}]}
                    )
                source_quote_line = line.get("source_quote_line")
                if source_quote_line:
                    if (
                        source_quote_line.quote.customer_id != customer.id
                        or source_quote_line.material_id != line["material"].id
                        or not source_quote_line.quote.is_ratified
                    ):
                        raise serializers.ValidationError(
                            {"lines": [{"source_quote_line": "来源销售报价与订单客户、物料不匹配或未核准"}]}
                        )
                    quote = source_quote_line.quote
                    order_currency = attrs.get("currency") or getattr(self.instance, "currency", None)
                    order_date = (
                        attrs.get("order_date") or getattr(self.instance, "order_date", None) or timezone.localdate()
                    )
                    if quote.currency_id != order_currency.id:
                        raise serializers.ValidationError(
                            {"lines": [{"source_quote_line": "来源销售报价币种与订单币种不一致"}]}
                        )
                    if quote.effective_date > order_date or (quote.expiry_date and quote.expiry_date < order_date):
                        raise serializers.ValidationError(
                            {"lines": [{"source_quote_line": "来源销售报价在订单日期无效"}]}
                        )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        order = SalesOrder(**validated_data)
        clean_sales_order(order)
        order.save()
        self._replace_lines(order, lines)
        self._sync_source_quote(order)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop("lines", None)
        instance = SalesOrder.objects.select_for_update().get(pk=instance.pk)
        from ..api_common import ensure_editable

        ensure_editable(instance)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        clean_sales_order(instance)
        instance.save()
        if lines is not None:
            self._replace_lines(instance, lines)
            self._sync_source_quote(instance)
        return instance

    @staticmethod
    def _sync_source_quote(order):
        quote_line = (
            order.lines.select_related("source_quote_line__quote").filter(source_quote_line__isnull=False).first()
        )
        quote = quote_line.source_quote_line.quote if quote_line else None
        quote_id = quote.id if quote else None
        if order.source_quote_id != quote_id:
            order.source_quote = quote
            order.save(update_fields=["source_quote", "updated_at"])

    @staticmethod
    def _replace_lines(order, lines):
        previous = {line.line_number: line for line in order.lines.select_for_update()}
        numbers = [data.get("line_number") or index * 10 for index, data in enumerate(lines, 1)]
        if len(numbers) != len(set(numbers)):
            raise serializers.ValidationError({"lines": "订单行号不能重复"})
        removed = order.lines.exclude(line_number__in=numbers)
        if removed.filter(delivery_lines__isnull=False).exists():
            raise serializers.ValidationError({"lines": "已有送货引用的订单行不能删除或重编号"})
        removed.delete()
        for index, data in enumerate(lines, 1):
            data = dict(data)
            data["order"] = order
            data["line_number"] = data.get("line_number") or index * 10
            customer_material = data.get("customer_material")
            if not data.get("uom"):
                data["uom"] = (
                    customer_material.customer_uom
                    if customer_material and customer_material.customer_uom_id
                    else data["material"].uom
                )
            line = previous.get(data["line_number"]) or SalesOrderLine(created_by=order.created_by)
            for name, value in data.items():
                setattr(line, name, value)
            if line.pk:
                line.modification_count += 1
            line.sync_derived_values()
            clean_sales_order(line)
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
    execution_summary = serializers.SerializerMethodField()

    def get_execution_summary(self, obj):
        from backend.delivery import execution_summary

        return execution_summary(obj)

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
            "material_code",
            "material_name_display",
            "customer_material_code",
            "uom_code",
            "inventory_uom_code",
            "currency_code",
            "order_notes",
            "customer_material_notes",
            "executed_positive_quantity",
            "executed_negative_quantity",
            "net_executed_quantity",
            "remaining_quantity",
            "delivered_quantity",
            "customer_material_name",
            "customer_material_specification",
            "terminal_customer_code",
            "terminal_customer_name",
            "material_name",
            "material_specification",
            "tax_code",
            "tax_name",
            "invoice_name",
            "inventory_uom",
            "uom_rate_m",
            "uom_rate_d",
            "spare_ratio",
            "delivered_spare_quantity",
            "returned_quantity",
            "returned_spare_quantity",
            "discount_rate",
            "discounted_unit_price",
            "untaxed_unit_price",
            "tax_included_amount",
            "untaxed_amount",
            "total_cost",
            "after_sales_method",
            "after_sales_method_name",
            "line_status",
            "closed_by",
            "closed_at",
            "income_account",
            "income_account_name",
            "replenishment_return",
            "products_per_carton",
            "cartons",
            "configuration_approved",
            "configuration_approved_by",
            "configuration_approved_at",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "modification_count",
        )
        extra_kwargs = {
            "line_number": {"required": False},
            "customer_material": {"required": False},
            "uom": {"required": False},
            "source_quote_line": {"required": False},
        }

    def get_customer_material_code(self, obj):
        return obj.customer_material.customer_code if obj.customer_material_id else ""

    def _execution_totals(self, obj):
        totals = getattr(obj, "_execution_totals", None)
        if totals is None:
            from django.db.models import Case, DecimalField, Sum, Value, When

            totals = obj.delivery_lines.filter(delivery__posted=True).aggregate(
                positive=Sum(
                    Case(
                        When(actual_quantity__gt=0, then="actual_quantity"),
                        default=Value(0),
                        output_field=DecimalField(max_digits=19, decimal_places=8),
                    )
                ),
                negative=Sum(
                    Case(
                        When(actual_quantity__lt=0, then="actual_quantity"),
                        default=Value(0),
                        output_field=DecimalField(max_digits=19, decimal_places=8),
                    )
                ),
            )
            obj._execution_totals = totals
        return totals

    def get_executed_positive_quantity(self, obj):
        return self._execution_totals(obj).get("positive") or 0

    def get_executed_negative_quantity(self, obj):
        return abs(self._execution_totals(obj).get("negative") or 0)

    def get_net_executed_quantity(self, obj):
        return obj.delivered_quantity

    def get_remaining_quantity(self, obj):
        return max(obj.quantity - obj.delivered_quantity, 0)

    def validate(self, attrs):
        order = attrs.get("order") or getattr(self.instance, "order", None)
        material = attrs.get("material") or getattr(self.instance, "material", None)
        customer_material = attrs.get("customer_material") or getattr(self.instance, "customer_material", None)
        source_quote_line = attrs.get("source_quote_line", getattr(self.instance, "source_quote_line", None))
        if (
            order
            and customer_material
            and (
                customer_material.customer_id != order.customer_id
                or customer_material.material_id != material.id
                or not customer_material.enabled
            )
        ):
            raise serializers.ValidationError({"customer_material": "客户物料与客户/物料不匹配或已停用"})
        if source_quote_line:
            if (
                source_quote_line.quote.customer_id != order.customer_id
                or source_quote_line.material_id != material.id
                or not source_quote_line.quote.is_ratified
            ):
                raise serializers.ValidationError({"source_quote_line": "来源销售报价与订单客户、物料不匹配或未核准"})
            if source_quote_line.quote.currency_id != order.currency_id:
                raise serializers.ValidationError({"source_quote_line": "来源销售报价币种与订单币种不一致"})
            if source_quote_line.quote.effective_date > order.order_date or (
                source_quote_line.quote.expiry_date and source_quote_line.quote.expiry_date < order.order_date
            ):
                raise serializers.ValidationError({"source_quote_line": "来源销售报价在订单日期无效"})
        return attrs

    def create(self, validated_data):
        line = SalesOrderLine(**validated_data)
        line.created_by = self.context.get("request").user.get_username() if self.context.get("request") else ""
        line.sync_derived_values()
        clean_sales_order(line)
        line.save()
        return line

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = SalesOrderLine.objects.select_for_update().get(pk=instance.pk)
        from ..api_common import ensure_editable

        ensure_editable(instance)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.modification_count += 1
        instance.sync_derived_values()
        clean_sales_order(instance)
        instance.save()
        return instance
