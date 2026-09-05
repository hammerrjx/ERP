from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F, Q, Sum
from django.utils import timezone
from rest_framework import decorators, response, serializers

from backend.domain.sales import (
    CustomerMaterial, DeliveryOrder, DeliveryOrderLine, SalesOrder, SalesOrderLine,
    SalesQuote, SalesQuoteLine, SalesReturn, SalesReturnLine,
)
from backend.domain.system import ApprovalStatus, AuditEvent
from .api_common import ApprovalViewSet, ensure_editable, ensure_status_unchanged, make_viewset
from .serializers import (
    CustomerMaterialSerializer, DeliveryOrderDetailSerializer, DeliveryOrderLineSerializer, DeliveryOrderSerializer,
    SalesOrderLineSerializer, SalesOrderListSerializer, SalesOrderSerializer, SalesQuoteLineSerializer,
    SalesQuoteSerializer, SalesReturnLineSerializer, SalesReturnSerializer,
)
from backend.models import (
    CustomerAddress, Department, PurchaseOrder, PurchaseOrderLine, PurchaseRequisition,
    PurchaseRequisitionLine, StockBalance,
)
from .serializers import PurchaseRequisitionSerializer

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
        "customer", "sales_person", "business_group", "payment_method", "currency", "address_code", "source_quote",
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
        order.save(update_fields=["po_change_requested", "po_change_confirmed", "po_change_by", "po_change_at", "po_change_confirmed_by", "po_change_confirmed_at", "po_change_notes", "updated_at"])
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=["post"], url_path="po-change-unconfirm")
    @transaction.atomic
    def po_change_unconfirm(self, request, pk=None):
        order = self.get_object()
        order.po_change_confirmed = False
        order.po_change_confirmed_by = ""
        order.po_change_confirmed_at = None
        order.save(update_fields=["po_change_confirmed", "po_change_confirmed_by", "po_change_confirmed_at", "updated_at"])
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
            raise serializers.ValidationError('只有已审核销售订单可以进行 MRP 请购分析')
        department_id = request.data.get('department')
        if not department_id:
            raise serializers.ValidationError({'department': '请购部门必填'})
        needed_date = request.data.get('needed_date') or timezone.localdate()
        department = Department.objects.filter(pk=department_id).first()
        if not department:
            raise serializers.ValidationError({'department': '请购部门不存在'})
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
        for line in order.lines.select_related('material', 'uom'):
            demand = max(line.quantity - line.delivered_quantity, Decimal('0'))
            key = (line.material_id, line.uom_id)
            if key not in supply_by_material:
                on_order = sum((
                    max(item.quantity - item.received_quantity, Decimal('0'))
                    for item in PurchaseOrderLine.objects.filter(
                        material=line.material, uom=line.uom, order__status=ApprovalStatus.APPROVED,
                    ).exclude(order__purchase_type=PurchaseOrder.PurchaseType.NON_PRODUCTION)
                ), Decimal('0'))
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
                mrp_demand_qty=demand,
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
            raise serializers.ValidationError('按 MRP 原则计算后没有大于 0 的请购明细')
        AuditEvent.objects.create(model=requisition._meta.label_lower, object_id=str(requisition.pk), action="mrp_generate", actor=request.user.get_username() or "system", payload={"source_sales_order_id": order.pk})
        return response.Response(PurchaseRequisitionSerializer(requisition).data, status=201)


SalesOrderLineViewSet = make_viewset(SalesOrderLine, SalesOrderLineSerializer)


class DeliveryOrderViewSet(ApprovalViewSet):
    queryset = DeliveryOrder.objects.select_related("customer", "sales_order", "source_location").prefetch_related(
        "lines__sales_order_line__order__currency", "lines__sales_order_line__inventory_uom",
        "lines__sales_order_line__customer_material", "lines__material", "lines__uom", "lines__source_location",
    )
    serializer_class = DeliveryOrderSerializer

    def get_serializer_class(self):
        return DeliveryOrderDetailSerializer if self.action == "retrieve" else DeliveryOrderSerializer

    @decorators.action(detail=False, methods=["post"], url_path="generate-from-order")
    @transaction.atomic
    def generate_from_order(self, request):
        order = SalesOrder.objects.filter(pk=request.data.get('sales_order')).first()
        selected = request.data.get("lines")
        if selected is not None and not isinstance(selected, list):
            raise serializers.ValidationError({"lines": "送货明细必须是列表"})
        selected_ids = set()
        for item in (selected or []):
            raw_line_id = item.get("sales_order_line")
            if not raw_line_id:
                continue
            try:
                selected_ids.add(int(raw_line_id))
            except (TypeError, ValueError):
                raise serializers.ValidationError({"lines": f"销售订单明细编号无效: {raw_line_id}"})
        source_lines = SalesOrderLine.objects.select_related("order__customer", "material", "uom", "customer_material").filter(pk__in=selected_ids) if selected is not None else (order.lines.select_related("order__customer", "material", "uom", "customer_material") if order else SalesOrderLine.objects.none())
        source_lines = list(source_lines)
        if not source_lines:
            raise serializers.ValidationError('请选择至少一条销售订单明细')
        orders = {line.order_id: line.order for line in source_lines}
        if order and any(line.order_id != order.id for line in source_lines):
            raise serializers.ValidationError('送货明细不能包含未选择销售订单的行')
        if any(item.status != ApprovalStatus.APPROVED for item in orders.values()):
            raise serializers.ValidationError('只有已审核销售订单可以生成送货草稿')
        customer_ids = {item.customer_id for item in orders.values()}
        if len(customer_ids) != 1:
            raise serializers.ValidationError('一张送货单只能包含同一客户的销售订单')
        order = order or next(iter(orders.values()))
        customer_id = request.data.get('customer')
        if customer_id and int(customer_id) != order.customer_id:
            raise serializers.ValidationError({'customer': '送货客户必须与销售订单一致'})
        customer_po = request.data.get('customer_po') or order.customer_po
        if customer_po != order.customer_po:
            raise serializers.ValidationError({'customer_po': '客户 PO 必须与销售订单一致'})
        address_code = request.data.get('address_code') or ''
        address = CustomerAddress.objects.filter(customer_id=order.customer_id, code=address_code, enabled=True).first() if address_code else None
        delivery_address = (address.address if address else request.data.get('delivery_address')) or order.delivery_address or ''
        source_location_id = request.data.get('source_location') or next((item.material.default_location_id for item in source_lines if item.material.default_location_id), None)
        if not source_location_id:
            raise serializers.ValidationError({'source_location': '出库库位必填，且物料必须配置默认库位'})
        delivery_mode = request.data.get('delivery_mode') or order.delivery_mode
        if delivery_mode not in {SalesOrder.DeliveryMode.DIRECT, SalesOrder.DeliveryMode.SUPPLIER}:
            raise serializers.ValidationError({'delivery_mode': '送货模式不合法'})
        delivery = DeliveryOrder(
            customer=order.customer, sales_order=order if len(orders) == 1 else None,
            delivery_address=delivery_address,
            address_code=address_code,
            address_snapshot=request.data.get('address_snapshot', delivery_address),
            document_type=request.data.get('document_type', DeliveryOrder.DocumentType.NORMAL),
            delivery_mode=delivery_mode,
            source_location_id=source_location_id,
            srm_number=request.data.get('srm_number') or order.srm_number or '', customer_po=customer_po,
            delivery_date=request.data.get('delivery_date') or timezone.localdate(),
            notes=request.data.get('notes', ''), created_by=request.user.get_username(),
        )
        try:
            delivery.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, 'message_dict', exc.messages)) from exc
        delivery.save()
        created = 0
        requested_lines = {}
        for item in (selected or []):
            raw_line_id = item.get("sales_order_line")
            if not raw_line_id:
                continue
            try:
                line_id = int(raw_line_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError({"lines": f"销售订单明细编号无效: {raw_line_id}"})
            requested_lines[line_id] = item
        if selected is not None and len(requested_lines) != len(selected):
            raise serializers.ValidationError({"lines": "每条送货明细必须且只能选择一个销售订单行"})
        found_line_ids = set()
        iterable_lines = source_lines if selected is not None else order.lines.select_related('material', 'uom', 'customer_material')
        for order_line in iterable_lines:
            source = requested_lines.get(order_line.pk)
            if selected is not None and source is None:
                continue
            found_line_ids.add(order_line.pk)
            quantity = Decimal(str(source.get("actual_quantity"))) if source and source.get("actual_quantity") is not None else order_line.quantity - order_line.delivered_quantity
            if delivery.document_type in {DeliveryOrder.DocumentType.RETURN, DeliveryOrder.DocumentType.RED_FLUSH}:
                quantity = abs(quantity)
            if quantity == 0 or (delivery.document_type == DeliveryOrder.DocumentType.NORMAL and quantity < 0):
                continue
            delivery_line = DeliveryOrderLine(
                delivery=delivery, line_number=order_line.line_number,
                sales_order_line=order_line, material=order_line.material,
                customer_material=order_line.customer_material, uom=order_line.uom,
                actual_quantity=quantity,
                ordered_spare_quantity=order_line.spare_quantity if hasattr(order_line, 'spare_quantity') else 0,
                actual_spare_quantity=Decimal(str(source.get('actual_spare_quantity', 0))) if source else Decimal('0'),
                source_location_id=(source or {}).get("source_location") or source_location_id or order_line.material.default_location_id,
                batch_number=(source or {}).get("batch_number", ""),
                srm_customer_po=order_line.order.customer_po,
                srm_material_code=(order_line.customer_material.customer_code if order_line.customer_material else order_line.material.code),
                srm_material_name=order_line.material.name,
                srm_quantity=quantity if delivery.document_type == DeliveryOrder.DocumentType.NORMAL else -quantity,
            )
            try:
                delivery_line.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(getattr(exc, 'message_dict', exc.messages)) from exc
            delivery_line.save()
            created += 1
        unknown_lines = set(requested_lines).difference(found_line_ids)
        if unknown_lines:
            raise serializers.ValidationError({"lines": f"销售订单不包含来源行: {sorted(unknown_lines)}"})
        if not created:
            delivery.delete()
            raise serializers.ValidationError('销售订单没有待送货明细')
        AuditEvent.objects.create(
            model=delivery._meta.label_lower,
            object_id=str(delivery.pk),
            action="generate_from_order",
            actor=request.user.get_username() or "system",
            payload={
                "document_type": delivery.document_type,
                "sales_order_ids": sorted(orders),
                "sales_order_numbers": sorted(item.number for item in orders.values()),
                "sales_order_line_ids": sorted(found_line_ids),
                "sales_order_lines": sorted(
                    f"{line.order.number}/{line.line_number}" for line in source_lines if line.pk in found_line_ids
                ),
            },
        )
        return response.Response(DeliveryOrderSerializer(delivery).data, status=201)


DeliveryOrderLineViewSet = make_viewset(DeliveryOrderLine, DeliveryOrderLineSerializer)
DeliveryOrderLineViewSet.queryset = DeliveryOrderLine.objects.select_related(
    "delivery", "sales_order_line__order", "sales_order_line__order__currency",
    "sales_order_line__customer_material", "sales_order_line__material",
    "sales_order_line__uom", "sales_order_line__inventory_uom", "material",
    "customer_material", "uom", "source_location",
)
SalesReturnViewSet = make_viewset(SalesReturn, SalesReturnSerializer)
SalesReturnLineViewSet = make_viewset(SalesReturnLine, SalesReturnLineSerializer)


class SalesQuoteViewSet(ApprovalViewSet):
    queryset = SalesQuote.objects.select_related("customer", "currency").prefetch_related(
        "lines__material", "lines__uom", "lines__customer_material", "lines__tiers",
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
                pk=customer_material_id, customer_id=customer_id, material_id=material_id,
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
        line = SalesQuoteLine.objects.select_related("quote__currency").filter(
            **material_filter,
        ).filter(Q(quote__expiry_date__isnull=True) | Q(quote__expiry_date__gte=target_date)).order_by(
            "-quote__effective_date", "-quote__created_at", "-quote__number"
        ).first()
        if not line:
            return response.Response({})
        return response.Response({
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
        })

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
            matching_quotes = SalesQuote.objects.select_for_update().filter(
                customer=quote.customer,
                currency=quote.currency,
                lines__material=line.material,
                lines__customer_material_code=line.customer_material_code,
                is_ratified=True,
            ).exclude(pk=quote.pk).order_by("-effective_date", "-created_at")
            latest = matching_quotes.first()
            if latest and quote.effective_date <= latest.effective_date:
                raise serializers.ValidationError(
                    {"effective_date": "同一客户、物料、客户物料和币种下，新报价生效日期必须晚于现有最新报价"}
                )
        quote.ratify(actor)
        quote.save()
        if line:
            previous_quotes = SalesQuote.objects.select_for_update().filter(
                customer=quote.customer,
                lines__material=line.material,
                lines__customer_material_code=line.customer_material_code,
                currency=quote.currency,
                is_ratified=True,
                effective_date__lt=quote.effective_date,
            ).exclude(pk=quote.pk).filter(
                Q(expiry_date__isnull=True) | Q(expiry_date__gte=quote.effective_date),
            )
            previous_quotes.update(expiry_date=quote.effective_date - timedelta(days=1))
        AuditEvent.objects.create(
            model=quote._meta.label_lower, object_id=str(quote.pk), action="ratify", actor=actor,
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
        order = SalesOrder.objects.create(
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
        for line in quote.lines.all():
            order_line = SalesOrderLine.objects.create(
                order=order,
                line_number=line.line_number,
                material=line.material,
                customer_material=line.customer_material,
                uom=line.uom,
                quantity=line.quantity.quantize(Decimal("0.000001")),
                spare_quantity=Decimal("0"),
                unit_price=line.unit_price.quantize(Decimal("0.000001")),
                promised_date=line.promised_date or order.promised_date,
                source_quote_line=line,
            )
            order_line.sync_derived_values()
            order_line.full_clean()
            order_line.save()
        AuditEvent.objects.create(
            model=order._meta.label_lower,
            object_id=str(order.pk),
            action="convert_from_quote",
            actor=request.user.get_username() or "system",
            payload={"source_quote_id": quote.pk},
        )
        return response.Response(SalesOrderSerializer(order).data, status=201)
