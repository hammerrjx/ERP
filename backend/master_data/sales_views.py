from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F, Q, Sum
from django.utils import timezone
from rest_framework import decorators, response, serializers

from backend.domain.sales import (
    CustomerMaterial,
    SalesOrder,
    SalesOrderLine,
    SalesQuote,
    SalesQuoteLine,
)
from backend.domain.system import ApprovalStatus, AuditEvent
from .api_common import ApprovalViewSet, ensure_editable, ensure_status_unchanged, make_viewset
from .serializers.sales_quotes import (
    CustomerMaterialSerializer,
    SalesQuoteLineSerializer,
    SalesQuoteSerializer,
)
from .serializers.sales_orders import (
    SalesOrderLineSerializer,
    SalesOrderListSerializer,
    SalesOrderSerializer,
    clean_sales_order,
)
from backend.models import (
    Department,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    StockBalance,
)
from .serializers.purchase import (
    PurchaseRequisitionSerializer,
)


class CustomerMaterialViewSet(make_viewset(CustomerMaterial, CustomerMaterialSerializer)):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.get_username())

    def perform_update(self, serializer):
        ensure_editable(serializer.instance)
        ensure_status_unchanged(serializer)
        serializer.save(updated_by=self.request.user.get_username())


SalesQuoteLineViewSet = make_viewset(SalesQuoteLine, SalesQuoteLineSerializer)


class SalesOrderViewSet(ApprovalViewSet):
    queryset = SalesOrder.objects.select_related(
        "customer",
        "sales_person",
        "business_group",
        "payment_method",
        "currency",
        "address_code",
        "source_quote",
    )
    serializer_class = SalesOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lines") if self.action != "list" else queryset

    def get_serializer_class(self):
        return SalesOrderListSerializer if self.action == "list" else SalesOrderSerializer

    @decorators.action(detail=True, methods=["post"], url_path="delivery-approve")
    @transaction.atomic
    def delivery_approve(self, request, pk=None):
        order = self.get_object()
        if order.status != ApprovalStatus.APPROVED:
            raise serializers.ValidationError("只有已审核订单可以进行交期审核")
        order.delivery_approved = True
        order.delivery_approved_by = request.user.get_username() or "system"
        order.delivery_approved_at = timezone.now()
        order.save(update_fields=["delivery_approved", "delivery_approved_by", "delivery_approved_at", "updated_at"])
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="delivery-unapprove")
    @transaction.atomic
    def delivery_unapprove(self, request, pk=None):
        order = self.get_object()
        order.delivery_approved = False
        order.delivery_approved_by = ""
        order.delivery_approved_at = None
        order.save(update_fields=["delivery_approved", "delivery_approved_by", "delivery_approved_at", "updated_at"])
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="po-change-confirm")
    @transaction.atomic
    def po_change_confirm(self, request, pk=None):
        order = self.get_object()
        order.po_change_requested = True
        order.po_change_confirmed = True
        order.po_change_by = request.user.get_username() or "system"
        order.po_change_at = timezone.now()
        order.po_change_confirmed_by = order.po_change_by
        order.po_change_confirmed_at = order.po_change_at
        order.po_change_notes = request.data.get("notes", order.po_change_notes)
        order.save(
            update_fields=[
                "po_change_requested",
                "po_change_confirmed",
                "po_change_by",
                "po_change_at",
                "po_change_confirmed_by",
                "po_change_confirmed_at",
                "po_change_notes",
                "updated_at",
            ]
        )
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="po-change-unconfirm")
    @transaction.atomic
    def po_change_unconfirm(self, request, pk=None):
        order = self.get_object()
        order.po_change_confirmed = False
        order.po_change_confirmed_by = ""
        order.po_change_confirmed_at = None
        order.save(
            update_fields=["po_change_confirmed", "po_change_confirmed_by", "po_change_confirmed_at", "updated_at"]
        )
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="print")
    @transaction.atomic
    def print(self, request, pk=None):
        order = self.get_object()
        order.print_count += 1
        order.save(update_fields=["print_count", "updated_at"])
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="generate-requisition")
    @transaction.atomic
    def generate_requisition(self, request, pk=None):
        order = self.get_object()
        if order.status != ApprovalStatus.APPROVED:
            raise serializers.ValidationError("只有已审核销售订单可以进行 MRP 请购分析")
        department_id = request.data.get("department")
        if not department_id:
            raise serializers.ValidationError({"department": "请购部门必填"})
        needed_date = request.data.get("needed_date") or timezone.localdate()
        department = Department.objects.filter(pk=department_id).first()
        if not department:
            raise serializers.ValidationError({"department": "请购部门不存在"})
        requisition = PurchaseRequisition.objects.create(
            department=department,
            request_date=timezone.localdate(),
            needed_date=needed_date,
            aggregation_mode=PurchaseRequisition.AggregationMode.NONE,
            quantity_rule="mrp",
            only_positive=True,
            source_sales_order=order,
            notes=request.data.get("notes", f"销售订单 {order.number} MRP 请购分析"),
            created_by=request.user.get_username(),
        )
        created = 0
        supply_by_material = {}
        for line in order.lines.select_related("material", "uom"):
            demand = max(line.quantity - line.delivered_quantity, Decimal("0"))
            key = (line.material_id, line.uom_id)
            if key not in supply_by_material:
                on_order = sum(
                    (
                        max(item.quantity - item.received_quantity, Decimal("0"))
                        for item in PurchaseOrderLine.objects.filter(
                            material=line.material,
                            uom=line.uom,
                            order__status=ApprovalStatus.APPROVED,
                        ).exclude(order__purchase_type=PurchaseOrder.PurchaseType.NON_PRODUCTION)
                    ),
                    Decimal("0"),
                )
                available = StockBalance.objects.filter(material=line.material, uom=line.uom).aggregate(
                    total=Sum(F("quantity") - F("reserved_quantity")),
                )["total"] or Decimal("0")
                supply_by_material[key] = [on_order, max(available, Decimal("0")), False]
            on_order, available, safety_applied = supply_by_material[key]
            safety_stock = Decimal("0") if safety_applied else line.material.safety_stock_qty
            requested = max(demand + safety_stock - on_order - available, Decimal("0"))
            remaining_supply = max(on_order + available - demand - safety_stock, Decimal("0"))
            remaining_on_order = min(on_order, remaining_supply)
            supply_by_material[key] = [remaining_on_order, remaining_supply - remaining_on_order, True]
            if requested <= 0:
                continue
            requisition_line = PurchaseRequisitionLine(
                requisition=requisition,
                line_number=line.line_number,
                material=line.material,
                uom=line.uom,
                mrp_demand_qty=demand.normalize(),
                on_order_qty=on_order,
                available_qty=available,
                safety_stock_qty=safety_stock,
                source_sales_order_line=line,
            )
            requisition_line.full_clean()
            requisition_line.save()
            created += 1
        if not created:
            requisition.delete()
            raise serializers.ValidationError("按 MRP 原则计算后没有大于 0 的请购明细")
        AuditEvent.objects.create(
            model=requisition._meta.label_lower,
            object_id=str(requisition.pk),
            action="mrp_generate",
            actor=request.user.get_username() or "system",
            payload={"source_sales_order_id": order.pk},
        )
        return response.Response(PurchaseRequisitionSerializer(requisition).data, status=201)


SalesOrderLineViewSet = make_viewset(SalesOrderLine, SalesOrderLineSerializer)


class SalesQuoteViewSet(ApprovalViewSet):
    queryset = SalesQuote.objects.select_related("customer", "currency").prefetch_related(
        "lines__material",
        "lines__uom",
        "lines__customer_material",
        "lines__tiers",
    )
    serializer_class = SalesQuoteSerializer

    @decorators.action(detail=False, methods=["get"], url_path="previous")
    def previous(self, request):
        customer_id = request.query_params.get("customer")
        material_id = request.query_params.get("material")
        customer_material_id = request.query_params.get("customer_material")
        currency_id = request.query_params.get("currency")
        target_date = request.query_params.get("date")
        if target_date:
            try:
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                raise serializers.ValidationError({"date": "日期格式必须为 YYYY-MM-DD"})
        else:
            target_date = timezone.localdate()
        customer_material = None
        if customer_material_id:
            customer_material = CustomerMaterial.objects.filter(
                pk=customer_material_id,
                customer_id=customer_id,
                material_id=material_id,
            ).first()
            if not customer_material:
                raise serializers.ValidationError("客户、客户物料和本方物料必须三端一致")
        material_filter = {
            "quote__customer_id": customer_id,
            "material_id": material_id,
            "customer_material_code": customer_material.customer_code if customer_material else "",
            "quote__is_ratified": True,
            "quote__effective_date__lte": target_date,
        }
        if currency_id:
            material_filter["quote__currency_id"] = currency_id
        line = (
            SalesQuoteLine.objects.select_related("quote__currency")
            .filter(
                **material_filter,
            )
            .filter(Q(quote__expiry_date__isnull=True) | Q(quote__expiry_date__gte=target_date))
            .order_by("-quote__effective_date", "-quote__created_at", "-quote__number")
            .first()
        )
        if not line:
            return response.Response({})
        return response.Response(
            {
                "quote_id": line.quote_id,
                "quote_line_id": line.id,
                "quote_number": line.quote.number,
                "effective_date": line.quote.effective_date,
                "unit_price": line.unit_price,
                "price_type": line.price_type,
                "discount_rate": line.quote.discount_rate,
                "tax_included": line.quote.tax_included,
                "discounted_unit_price": line.discounted_unit_price,
                "untaxed_unit_price": line.untaxed_unit_price,
                "currency": line.quote.currency.code,
                "tax_rate": line.quote.tax_rate,
                "expiry_date": line.quote.expiry_date,
                "promised_date": line.promised_date,
            }
        )

    def destroy(self, request, *args, **kwargs):
        quote = self.get_object()
        if quote.is_ratified:
            raise serializers.ValidationError("已核准报价不能删除，请通过失效日期管理历史版本")
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=True, methods=["post"])
    @transaction.atomic
    def ratify(self, request, pk=None):
        quote = self.get_object()
        actor = request.user.get_username() or "system"
        line = quote.lines.first()
        if line:
            # Lock the version chain so concurrent ratifications cannot leave overlapping open prices.
            matching_quotes = (
                SalesQuote.objects.select_for_update()
                .filter(
                    customer=quote.customer,
                    currency=quote.currency,
                    lines__material=line.material,
                    lines__customer_material_code=line.customer_material_code,
                    is_ratified=True,
                )
                .exclude(pk=quote.pk)
                .order_by("-effective_date", "-created_at")
            )
            latest = matching_quotes.first()
            if latest and quote.effective_date <= latest.effective_date:
                raise serializers.ValidationError(
                    {"effective_date": "同一客户、物料、客户物料和币种下，新报价生效日期必须晚于现有最新报价"}
                )
        quote.ratify(actor)
        quote.save()
        if line:
            previous_quotes = (
                SalesQuote.objects.select_for_update()
                .filter(
                    customer=quote.customer,
                    lines__material=line.material,
                    lines__customer_material_code=line.customer_material_code,
                    currency=quote.currency,
                    is_ratified=True,
                    effective_date__lt=quote.effective_date,
                )
                .exclude(pk=quote.pk)
                .filter(
                    Q(expiry_date__isnull=True) | Q(expiry_date__gte=quote.effective_date),
                )
            )
            previous_quotes.update(expiry_date=quote.effective_date - timedelta(days=1))
        AuditEvent.objects.create(
            model=quote._meta.label_lower,
            object_id=str(quote.pk),
            action="ratify",
            actor=actor,
        )
        return response.Response(self.get_serializer(quote).data)

    @decorators.action(detail=True, methods=["post"])
    @transaction.atomic
    def convert(self, request, pk=None):
        quote = self.get_object()
        if quote.status != ApprovalStatus.APPROVED or not quote.is_ratified:
            raise serializers.ValidationError("只有已审核并核准的销售报价可以转销售订单")
        required = ("customer_po", "delivery_address", "promised_date")
        missing = [name for name in required if not request.data.get(name)]
        if missing:
            raise serializers.ValidationError({name: "此字段必填" for name in missing})
        order = SalesOrder(
            customer=quote.customer,
            currency=quote.currency,
            tax_included=quote.tax_included,
            tax_rate=quote.tax_rate,
            customer_po=request.data["customer_po"],
            address_code=quote.address_code,
            address_snapshot=quote.address_snapshot,
            delivery_address=request.data["delivery_address"],
            promised_date=request.data["promised_date"],
            delivery_mode=request.data.get("delivery_mode", SalesOrder.DeliveryMode.DIRECT),
            srm_number=request.data.get("srm_number", ""),
            notes=request.data.get("notes", ""),
            source_quote=quote,
            created_by=request.user.get_username(),
        )
        clean_sales_order(order)
        order.save()
        for line in quote.lines.all():
            requested_lines = request.data.get("lines", {})
            if not isinstance(requested_lines, dict):
                raise serializers.ValidationError({"lines": "按报价行ID提供本次正式数量和备品计划"})
            quantities = requested_lines.get(str(line.pk), {})
            if not isinstance(quantities, dict):
                raise serializers.ValidationError({"lines": "报价行数量格式无效"})
            quantity_field = serializers.DecimalField(max_digits=19, decimal_places=8, min_value=Decimal("0"))
            order_line = SalesOrderLine(
                order=order,
                line_number=line.line_number,
                material=line.material,
                customer_material=line.customer_material,
                uom=line.uom,
                quantity=quantity_field.run_validation(quantities.get("quantity", line.quantity)),
                spare_quantity=quantity_field.run_validation(quantities.get("spare_quantity", 0)),
                unit_price=line.unit_price.quantize(Decimal("0.000001")),
                promised_date=line.promised_date or order.promised_date,
                source_quote_line=line,
            )
            order_line.sync_derived_values()
            try:
                order_line.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.messages) from exc
            order_line.save()
        AuditEvent.objects.create(
            model=order._meta.label_lower,
            object_id=str(order.pk),
            action="convert_from_quote",
            actor=request.user.get_username() or "system",
            payload={"source_quote_id": quote.pk},
        )
        return response.Response(SalesOrderSerializer(order).data, status=201)
