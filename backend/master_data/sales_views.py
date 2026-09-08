from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F, Q, Sum
from django.utils import timezone
from rest_framework import decorators, response, serializers

from backend.domain.sales import (
    CustomerMaterial, SalesOrder, SalesOrderLine, SalesQuote, SalesQuoteLine,
)
from backend.domain.delivery import DeliveryOrder, DeliveryOrderLine, SalesReturn, SalesReturnLine
from backend.domain.system import ApprovalStatus, AuditEvent
from .api_common import ApprovalViewSet, ensure_editable, ensure_status_unchanged, make_viewset
from .serializers import (
    CustomerMaterialSerializer, DeliveryOrderDetailSerializer, DeliveryOrderLineSerializer, DeliveryOrderSerializer,
    SalesOrderLineSerializer, SalesOrderListSerializer, SalesOrderSerializer, SalesQuoteLineSerializer,
    SalesQuoteSerializer, SalesReturnLineSerializer, SalesReturnSerializer,
)
from backend.models import (
    Department, PurchaseOrder, PurchaseOrderLine, PurchaseRequisition,
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
            raise serializers.ValidationError('按 MRP 原则计算后没有大于 0 的请购明细')
        AuditEvent.objects.create(model=requisition._meta.label_lower, object_id=str(requisition.pk), action="mrp_generate", actor=request.user.get_username() or "system", payload={"source_sales_order_id": order.pk})
        return response.Response(PurchaseRequisitionSerializer(requisition).data, status=201)


SalesOrderLineViewSet = make_viewset(SalesOrderLine, SalesOrderLineSerializer)


class DeliveryOrderViewSet(ApprovalViewSet):
    queryset = DeliveryOrder.objects.select_related("customer", "sales_order", "source_location").prefetch_related(
        "lines__sales_order_line__order__currency", "lines__sales_order_line__inventory_uom",
        "lines__sales_order_line__customer_material", "lines__material", "lines__uom", "lines__source_location",
        "lines__sales_order_line__material__default_location", "lines__sales_order_line__material__uom", "lines__sales_order_line__uom",
    )
    serializer_class = DeliveryOrderSerializer

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        from backend.models import DeliveryNumberReservation
        instance = DeliveryOrder.objects.select_for_update().get(pk=self.get_object().pk)
        ensure_editable(instance)
        if DeliveryNumberReservation.objects.filter(delivery=instance).exists():
            raise serializers.ValidationError("已取号的送货单请作废，保留单号记录")
        return super().destroy(request, *args, **kwargs)

    @transaction.atomic
    def perform_update(self, serializer):
        from backend.delivery import validate_quantities
        obj = DeliveryOrder.objects.select_for_update().get(pk=serializer.instance.pk)
        if obj.posted:
            raise serializers.ValidationError("已回写订单的单据不能修改")
        super().perform_update(serializer)
        try:
            validate_quantities(serializer.instance, list(serializer.instance.lines.select_related("sales_order_line__order")))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

    def get_serializer_class(self):
        return DeliveryOrderDetailSerializer if self.action == "retrieve" else DeliveryOrderSerializer

    @decorators.action(detail=False, methods=["post"], url_path="reserve-number")
    @transaction.atomic
    def reserve_number(self, request):
        from backend.models import DeliveryNumberReservation, DeliveryOrderSequence
        key = serializers.UUIDField().run_validation(request.data.get("request_id"))
        day = serializers.DateField().run_validation(request.data.get("delivery_date"))
        existing = DeliveryNumberReservation.objects.select_for_update().filter(pk=key).first()
        if existing:
            if existing.owner_id != request.user.pk:
                raise serializers.ValidationError("取号请求不属于当前用户")
            return response.Response({"reservation": str(existing.pk), "number": existing.number})
        try:
            number = DeliveryOrderSequence.next_number(day)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        reserved = DeliveryNumberReservation.objects.create(id=key, number=number, delivery_date=day, owner=request.user)
        return response.Response({"reservation": str(reserved.pk), "number": number}, status=201)

    @decorators.action(detail=False, methods=["get"], url_path="order-candidates")
    def order_candidates(self, request):
        from backend.delivery import SOURCE_RELATED, commitments, order_line_data
        customer = serializers.IntegerField(min_value=1).run_validation(request.query_params.get("customer"))
        page = serializers.IntegerField(min_value=1).run_validation(request.query_params.get("page", 1))
        queryset = SalesOrderLine.objects.filter(order__customer_id=customer, order__status=ApprovalStatus.APPROVED).filter(
            Q(line_status__in=("normal", ""))
            | (Q(line_status__in=("C", "closed")) & (Q(delivered_quantity__gt=0) | Q(delivered_spare_quantity__gt=0)))
        )
        fields = {"customer_po": "order__customer_po", "material_code": "material__code",
                  "customer_material_code": "customer_material__customer_code",
                  "terminal_material_code": "customer_material__terminal_customer_code",
                  "order_number": "order__number"}
        mode = request.query_params.get("match", "contains")
        if mode not in ("contains", "exact", "range"):
            raise serializers.ValidationError("查询方式无效")
        for key, field in fields.items():
            value, upper = request.query_params.get(key, "").strip(), request.query_params.get(key + "_to", "").strip()
            if value:
                queryset = queryset.filter(**{field + ("__icontains" if mode == "contains" else "__iexact" if mode == "exact" else "__gte"): value})
            if upper and mode == "range":
                queryset = queryset.filter(**{field + "__lte": upper})
        for key, field in (("order_date", "order__order_date"), ("promised_date", "promised_date")):
            for suffix, lookup in (("_from", "__gte"), ("_to", "__lte")):
                raw = request.query_params.get(key + suffix)
                if raw:
                    queryset = queryset.filter(**{field + lookup: serializers.DateField().run_validation(raw)})
        exclude = request.query_params.get("delivery")
        if exclude:
            exclude = serializers.IntegerField(min_value=1).run_validation(exclude)
            if not DeliveryOrder.objects.filter(pk=exclude, customer_id=customer).exists():
                raise serializers.ValidationError("送货单与查询客户不一致")
        count = queryset.count()
        rows = list(queryset.select_related(*SOURCE_RELATED).order_by("-order__order_date", "-order_id", "line_number")[(page - 1) * 30:page * 30])
        occupied = commitments([row.pk for row in rows], exclude)
        return response.Response({"count": count, "page": page, "page_size": 30,
                                  "results": [order_line_data(row, occupied[row.pk]) for row in rows]})

    @decorators.action(detail=False, methods=["post"], url_path="save-sheet")
    @transaction.atomic
    def save_sheet(self, request):
        from backend.delivery import save_sheet
        from backend.models import DeliveryNumberReservation
        key = serializers.UUIDField().run_validation(request.data.get("reservation"))
        reservation = DeliveryNumberReservation.objects.select_for_update().filter(pk=key, owner=request.user).first()
        if not reservation:
            raise serializers.ValidationError("请先取得正式单号")
        if reservation.delivery_id:
            return response.Response(DeliveryOrderDetailSerializer(reservation.delivery).data)
        saved = save_sheet(request.data, request.user, reservation=reservation)
        return response.Response(DeliveryOrderDetailSerializer(saved).data, status=201)

    @decorators.action(detail=True, methods=["post"], url_path="save-sheet")
    @transaction.atomic
    def update_sheet(self, request, pk=None):
        from backend.delivery import save_sheet
        instance = DeliveryOrder.objects.select_for_update().get(pk=self.get_object().pk)
        saved = save_sheet(request.data, request.user, instance=instance)
        return response.Response(DeliveryOrderDetailSerializer(saved).data)

    @transaction.atomic
    def transition(self, obj, action, actor="", reason=""):
        obj = DeliveryOrder.objects.select_for_update().get(pk=obj.pk)
        if action == "approve" and obj.status == ApprovalStatus.APPROVED:
            return response.Response(self.get_serializer(obj).data)
        return super().transition(obj, action, actor, reason)

    @decorators.action(detail=False, methods=["post"], url_path="generate-from-order")
    @transaction.atomic
    def generate_from_order(self, request):
        from backend.delivery import commitments, save_sheet
        data = dict(request.data)
        if "lines" not in data:
            order_id = serializers.IntegerField(min_value=1).run_validation(data.get("sales_order"))
            order = SalesOrder.objects.filter(pk=order_id).first()
            if not order:
                raise serializers.ValidationError("客户订单不存在")
            rows = list(order.lines.all())
            occupied = commitments([row.pk for row in rows])
            data["lines"] = [{"sales_order_line": row.pk,
                              "actual_quantity": str(max(row.quantity - row.delivered_quantity - occupied[row.pk][0], 0)),
                              "actual_spare_quantity": str(max(row.spare_quantity - row.delivered_spare_quantity - occupied[row.pk][2], 0))}
                             for row in rows if row.quantity - row.delivered_quantity - occupied[row.pk][0] > 0
                             or row.spare_quantity - row.delivered_spare_quantity - occupied[row.pk][2] > 0]
            data.setdefault("delivery_address", order.delivery_address)
        saved = save_sheet(data, request.user)
        return response.Response(DeliveryOrderDetailSerializer(saved).data, status=201)

_DeliveryOrderLineBase = make_viewset(DeliveryOrderLine, DeliveryOrderLineSerializer)
_DeliveryOrderLineBase.queryset = DeliveryOrderLine.objects.select_related(
    "delivery", "sales_order_line__order", "sales_order_line__order__currency",
    "sales_order_line__customer_material", "sales_order_line__material",
    "sales_order_line__uom", "sales_order_line__inventory_uom", "material",
    "customer_material", "uom", "source_location",
)


class DeliveryOrderLineViewSet(_DeliveryOrderLineBase):
    def lock_source(self, request, instance=None):
        parents = [request.data.get("delivery"), getattr(instance, "delivery_id", None)]
        parent_ids = [serializers.IntegerField(min_value=1).run_validation(value) for value in parents if value]
        list(DeliveryOrder.objects.select_for_update().filter(pk__in=parent_ids).order_by("pk"))
        ids = [request.data.get("sales_order_line")]
        if instance:
            ids.append(instance.sales_order_line_id)
        try:
            ids = [int(value) for value in ids if value]
        except (ValueError, TypeError):
            raise serializers.ValidationError("订单行编号无效")
        list(SalesOrderLine.objects.select_for_update().filter(pk__in=ids).order_by("pk"))

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.lock_source(request)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.lock_source(request, instance)
        result = super().update(request, *args, **kwargs)
        DeliveryOrder.objects.filter(pk=instance.delivery_id).update(updated_at=timezone.now())
        return result

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.lock_source(request, instance)
        result = super().destroy(request, *args, **kwargs)
        DeliveryOrder.objects.filter(pk=instance.delivery_id).update(updated_at=timezone.now())
        return result

    def perform_create(self, serializer):
        from backend.delivery import order_line_data
        source = serializer.validated_data["sales_order_line"]
        line = serializer.save(created_by=self.request.user.get_username(), source_snapshot=order_line_data(source))
        DeliveryOrder.objects.filter(pk=line.delivery_id).update(updated_at=timezone.now())

    def perform_update(self, serializer):
        ensure_editable(serializer.instance)
        from backend.delivery import order_line_data
        source = serializer.validated_data.get("sales_order_line", serializer.instance.sales_order_line)
        snapshot = serializer.instance.source_snapshot
        if not snapshot or snapshot.get("sales_order_line") != source.pk:
            snapshot = order_line_data(source)
        line = serializer.save(updated_by=self.request.user.get_username(), modification_count=serializer.instance.modification_count + 1, source_snapshot=snapshot)
        DeliveryOrder.objects.filter(pk=line.delivery_id).update(updated_at=timezone.now())

class SalesReturnViewSet(make_viewset(SalesReturn, SalesReturnSerializer)):
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer

    @transaction.atomic
    def transition(self, obj, action, actor="", reason=""):
        obj = SalesReturn.objects.select_for_update().get(pk=obj.pk)
        if action == "approve" and obj.status == ApprovalStatus.APPROVED:
            return response.Response(self.get_serializer(obj).data)
        return super().transition(obj, action, actor, reason)


class SalesReturnLineViewSet(make_viewset(SalesReturnLine, SalesReturnLineSerializer)):
    def lock_source(self, request, instance=None):
        parents = [request.data.get("sales_return"), getattr(instance, "sales_return_id", None)]
        parent_ids = [serializers.IntegerField(min_value=1).run_validation(value) for value in parents if value]
        list(SalesReturn.objects.select_for_update().filter(pk__in=parent_ids).order_by("pk"))
        raw_orders = [request.data.get("sales_order_line"), getattr(instance, "sales_order_line_id", None)]
        raw_deliveries = [request.data.get("source_delivery_line"), getattr(instance, "source_delivery_line_id", None)]
        ids = []
        for raw_order in filter(None, raw_orders):
            ids.append(serializers.IntegerField(min_value=1).run_validation(raw_order))
        for raw_delivery in filter(None, raw_deliveries):
            key = serializers.IntegerField(min_value=1).run_validation(raw_delivery)
            ids.extend(DeliveryOrderLine.objects.filter(pk=key).values_list("sales_order_line_id", flat=True))
        list(SalesOrderLine.objects.select_for_update().filter(pk__in=ids).order_by("pk"))

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.lock_source(request)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.lock_source(request, self.get_object())
        return super().update(request, *args, **kwargs)


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
