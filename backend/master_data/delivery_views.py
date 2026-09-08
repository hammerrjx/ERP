from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import decorators, response, serializers

from backend.domain.sales import (
    SalesOrder,
    SalesOrderLine,
)
from backend.domain.delivery import DeliveryOrder, DeliveryOrderLine, SalesReturn, SalesReturnLine
from backend.domain.system import ApprovalStatus
from .api_common import ApprovalViewSet, ensure_editable, make_viewset
from .serializers.delivery import (
    DeliveryOrderDetailSerializer,
    DeliveryOrderLineSerializer,
    DeliveryOrderSerializer,
    SalesReturnLineSerializer,
    SalesReturnSerializer,
)


class DeliveryOrderViewSet(ApprovalViewSet):
    queryset = DeliveryOrder.objects.select_related("customer", "sales_order", "source_location").prefetch_related(
        "lines__sales_order_line__order__currency",
        "lines__sales_order_line__inventory_uom",
        "lines__sales_order_line__customer_material",
        "lines__material",
        "lines__uom",
        "lines__source_location",
        "lines__sales_order_line__material__default_location",
        "lines__sales_order_line__material__uom",
        "lines__sales_order_line__uom",
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
            validate_quantities(
                serializer.instance, list(serializer.instance.lines.select_related("sales_order_line__order"))
            )
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
        reserved = DeliveryNumberReservation.objects.create(
            id=key, number=number, delivery_date=day, owner=request.user
        )
        return response.Response({"reservation": str(reserved.pk), "number": number}, status=201)

    @decorators.action(detail=False, methods=["get"], url_path="order-candidates")
    def order_candidates(self, request):
        from backend.delivery import SOURCE_RELATED, commitments, order_line_data

        customer = serializers.IntegerField(min_value=1).run_validation(request.query_params.get("customer"))
        page = serializers.IntegerField(min_value=1).run_validation(request.query_params.get("page", 1))
        queryset = SalesOrderLine.objects.filter(
            order__customer_id=customer, order__status=ApprovalStatus.APPROVED
        ).filter(
            Q(line_status__in=("normal", ""))
            | (Q(line_status__in=("C", "closed")) & (Q(delivered_quantity__gt=0) | Q(delivered_spare_quantity__gt=0)))
        )
        fields = {
            "customer_po": "order__customer_po",
            "material_code": "material__code",
            "customer_material_code": "customer_material__customer_code",
            "terminal_material_code": "customer_material__terminal_customer_code",
            "order_number": "order__number",
        }
        mode = request.query_params.get("match", "contains")
        if mode not in ("contains", "exact", "range"):
            raise serializers.ValidationError("查询方式无效")
        for key, field in fields.items():
            value, upper = request.query_params.get(key, "").strip(), request.query_params.get(key + "_to", "").strip()
            if value:
                queryset = queryset.filter(
                    **{
                        field
                        + ("__icontains" if mode == "contains" else "__iexact" if mode == "exact" else "__gte"): value
                    }
                )
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
        rows = list(
            queryset.select_related(*SOURCE_RELATED).order_by("-order__order_date", "-order_id", "line_number")[
                (page - 1) * 30 : page * 30
            ]
        )
        occupied = commitments([row.pk for row in rows], exclude)
        return response.Response(
            {
                "count": count,
                "page": page,
                "page_size": 30,
                "results": [order_line_data(row, occupied[row.pk]) for row in rows],
            }
        )

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
            data["lines"] = [
                {
                    "sales_order_line": row.pk,
                    "actual_quantity": str(max(row.quantity - row.delivered_quantity - occupied[row.pk][0], 0)),
                    "actual_spare_quantity": str(
                        max(row.spare_quantity - row.delivered_spare_quantity - occupied[row.pk][2], 0)
                    ),
                }
                for row in rows
                if row.quantity - row.delivered_quantity - occupied[row.pk][0] > 0
                or row.spare_quantity - row.delivered_spare_quantity - occupied[row.pk][2] > 0
            ]
            data.setdefault("delivery_address", order.delivery_address)
        saved = save_sheet(data, request.user)
        return response.Response(DeliveryOrderDetailSerializer(saved).data, status=201)


_DeliveryOrderLineBase = make_viewset(DeliveryOrderLine, DeliveryOrderLineSerializer)
_DeliveryOrderLineBase.queryset = DeliveryOrderLine.objects.select_related(
    "delivery",
    "sales_order_line__order",
    "sales_order_line__order__currency",
    "sales_order_line__customer_material",
    "sales_order_line__material",
    "sales_order_line__uom",
    "sales_order_line__inventory_uom",
    "material",
    "customer_material",
    "uom",
    "source_location",
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
        line = serializer.save(
            updated_by=self.request.user.get_username(),
            modification_count=serializer.instance.modification_count + 1,
            source_snapshot=snapshot,
        )
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
