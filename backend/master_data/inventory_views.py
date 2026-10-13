from decimal import Decimal
from datetime import date

from rest_framework import response, viewsets, serializers
from django.db.models import Q

from backend.domain.inventory import (
    StockBalance,
    StockCount,
    StockCountLine,
    StockTransaction,
    StockTransfer,
    StockTransferLine,
)
from backend.domain.warehouse_documents import InventoryDocumentLine
from .serializers.common import serializer_for
from .api_common import ErpRolePermission, make_viewset
from .inventory_snapshot_views import SnapshotReportMixin
from backend.inventory_codes import COUNT_ADJUSTMENT, source_code
from .sales_pagination import PagedSalesMixin


class StockReadMixin(PagedSalesMixin):
    search_fields = ('material__code', 'material__name', 'location__code', 'batch_number')

    def get_queryset(self):
        qs = super().get_queryset().select_related('material', 'location', 'uom')
        params = self.request.query_params
        if params.get('location'):
            qs = qs.filter(location_id=params['location'])
        if qs.model == StockTransaction:
            try:
                start = date.fromisoformat(params['start']) if params.get('start') else None
                end = date.fromisoformat(params['end']) if params.get('end') else None
            except ValueError:
                raise serializers.ValidationError('日期格式错误')
            if start and end and start > end:
                raise serializers.ValidationError('结束日期不能早于开始日期')
            if start:
                qs = qs.filter(effective_date__gte=start)
            if end:
                qs = qs.filter(effective_date__lte=end)
        return qs

    def get_serializer_class(self):
        # Keep foreign-key IDs for existing clients, add labels for paged readers.
        base = super().get_serializer_class()
        return type('StockReadSerializer', (base,), {
            'material_code': serializers.CharField(source='material.code', read_only=True),
            'material_name': serializers.CharField(source='material.name', read_only=True),
            'location_code': serializers.CharField(source='location.code', read_only=True),
            'uom_name': serializers.CharField(source='uom.name', read_only=True),
        })


class StockBalanceViewSet(StockReadMixin, viewsets.ReadOnlyModelViewSet):
    queryset = StockBalance.objects.all()
    serializer_class = serializer_for(StockBalance)
    permission_classes = (ErpRolePermission,)


class StockTransactionViewSet(StockReadMixin, viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = serializer_for(StockTransaction)
    permission_classes = (ErpRolePermission,)


class InventoryReportViewSet(viewsets.ViewSet):
    queryset = StockTransaction.objects.none()
    permission_classes = (ErpRolePermission,)

    def list(self, request):
        try:
            start = date.fromisoformat(request.query_params.get("start", date.today().replace(day=1).isoformat()))
            end = date.fromisoformat(request.query_params.get("end", date.today().isoformat()))
        except ValueError as exc:
            raise serializers.ValidationError("日期格式错误") from exc
        if end < start:
            raise serializers.ValidationError("结束日期不能早于开始日期")
        qs = StockTransaction.objects.filter(effective_date__lte=end).select_related("material", "location", "uom")
        if request.query_params.get("location"):
            qs = qs.filter(location_id=request.query_params["location"])
        if request.query_params.get("site"):
            qs = qs.filter(location__source_site=request.query_params["site"])
        if request.query_params.get("q"):
            qs = qs.filter(Q(material__code__icontains=request.query_params["q"]) | Q(material__name__icontains=request.query_params["q"]))
        report = {}
        for row in qs.order_by("effective_date", "id"):
            key = (row.material_id, row.location_id, row.batch_number)
            item = report.setdefault(key, dict(material_code=row.material.code, material_name=row.material.name,
                location_code=row.location.code, uom=row.uom.name, batch_number=row.batch_number,
                opening=Decimal(0), receipt=Decimal(0), issue=Decimal(0), adjustment=Decimal(0), closing=Decimal(0)))
            code = source_code(row.movement_type)
            if row.effective_date < start or row.movement_type == "opening":
                item["opening"] += row.quantity
            elif code == COUNT_ADJUSTMENT:
                item["adjustment"] += row.quantity
            elif row.quantity >= 0:
                item["receipt"] += row.quantity
            else:
                item["issue"] -= row.quantity
            item["closing"] += row.quantity
        return response.Response([{k: str(v) if isinstance(v, Decimal) else v for k, v in item.items()} for item in report.values()])


class InventoryQueryViewSet(viewsets.ViewSet):
    """Read-only inventory queries matching the dgyzx1 ledger grain.

    Every row keeps the local ids and source identifiers so a report can be
    reconciled with ld_det/tr_hist or the corresponding document history.
    """

    permission_classes = (ErpRolePermission,)

    def _params(self, request):
        params = request.query_params
        try:
            start = date.fromisoformat(params["start"]) if params.get("start") else None
            end = date.fromisoformat(params["end"]) if params.get("end") else None
        except ValueError as exc:
            raise serializers.ValidationError("日期格式错误") from exc
        if start and end and end < start:
            raise serializers.ValidationError("结束日期不能早于开始日期")
        return params, start, end

    @staticmethod
    def _page_bounds(request, total):
        """Opt-in pagination for the high-volume report endpoints."""
        if "page" not in request.query_params:
            return None
        try:
            page = max(1, int(request.query_params.get("page", "1")))
            page_size = min(500, max(1, int(request.query_params.get("page_size", "100"))))
        except ValueError as exc:
            raise serializers.ValidationError("分页参数错误") from exc
        start = (page - 1) * page_size
        return page, page_size, start, total

    @classmethod
    def _paged_rows(cls, request, qs, serializer):
        if "page" not in request.query_params:
            return response.Response([serializer(row) for row in qs])
        bounds = cls._page_bounds(request, qs.count())
        page, page_size, start, total = bounds
        return response.Response({"count": total, "page": page, "page_size": page_size,
                                  "results": [serializer(row) for row in qs[start:start + page_size]]})

    @staticmethod
    def _text_match(row, query):
        if not query:
            return True
        q = query.lower()
        return q in " ".join(str(row.get(key, "")) for key in (
            "number", "material_code", "material_name", "location_code",
            "from_location_code", "to_location_code", "batch_number", "source_key",
        )).lower()

    def _document_lines(self, request, kind):
        params, start, end = self._params(request)
        qs = InventoryDocumentLine.objects.filter(document__kind=kind).select_related(
            "document", "document__from_location", "document__to_location", "document__checker",
            "material", "uom", "from_location", "to_location",
        ).order_by("-document__document_date", "-document_id", "line_number")
        if start:
            qs = qs.filter(document__document_date__gte=start)
        if end:
            qs = qs.filter(document__document_date__lte=end)
        if params.get("status"):
            qs = qs.filter(document__status=params["status"])
        if params.get("location"):
            qs = qs.filter(Q(from_location_id=params["location"]) | Q(to_location_id=params["location"]) |
                           Q(document__from_location_id=params["location"]) | Q(document__to_location_id=params["location"]))
        if params.get("site"):
            qs = qs.filter(Q(from_location__source_site=params["site"]) | Q(to_location__source_site=params["site"]) |
                           Q(document__from_location__source_site=params["site"]) | Q(document__to_location__source_site=params["site"]))
        if params.get("q"):
            q = params["q"]
            qs = qs.filter(Q(document__number__icontains=q) | Q(material__code__icontains=q) |
                           Q(material__name__icontains=q) | Q(batch_number__icontains=q) |
                           Q(reference_number__icontains=q))
        return qs

    @staticmethod
    def _doc_row(line, *, include_count=False):
        doc = line.document
        from_location = line.from_location or doc.from_location
        to_location = line.to_location or doc.to_location
        row = {
            "id": line.id,
            "document_id": doc.id,
            "number": doc.number,
            "kind": doc.kind,
            "status": doc.status,
            "document_date": doc.document_date,
            "line_number": line.line_number,
            "material_id": line.material_id,
            "material_code": line.material.code,
            "material_name": line.material.name,
            "specification": line.material.specification,
            "uom_id": line.uom_id,
            "uom_code": line.uom.code,
            "uom_name": line.uom.name,
            "quantity": line.quantity,
            "batch_number": line.batch_number,
            "from_location_id": from_location.id if from_location else None,
            "from_location_code": from_location.code if from_location else "",
            "from_location_name": from_location.name if from_location else "",
            "to_location_id": to_location.id if to_location else None,
            "to_location_code": to_location.code if to_location else "",
            "to_location_name": to_location.name if to_location else "",
            "site": (from_location or to_location).source_site if (from_location or to_location) else "",
            "category_code": doc.category_code,
            "transfer_class": doc.transfer_class,
            "reference_number": line.reference_number,
            "reference_line": line.reference_line,
            "source_key": doc.source_key,
            "source_payload": doc.source_payload,
        }
        if include_count:
            row.update({
                "count_basis": doc.count_basis,
                "checker_id": doc.checker_id,
                "checker_code": doc.checker.code if doc.checker else "",
                "checker_name": doc.checker.name if doc.checker else "",
                "system_quantity": line.system_quantity,
                "counted_quantity": line.counted_quantity,
                "variance_quantity": line.variance_quantity,
            })
        return row

    def _list_documents(self, request, kind, *, include_count=False):
        rows = [self._doc_row(line, include_count=include_count) for line in self._document_lines(request, kind)]
        query = request.query_params.get("q", "")
        return response.Response([row for row in rows if self._text_match(row, query)])

    def list(self, request):
        return response.Response([])


class MaterialInventoryDetailViewSet(SnapshotReportMixin, InventoryQueryViewSet):
    def list(self, request):
        if request.query_params.get("source") in {"dgyzx1", "local"}:
            return self.snapshot_list(request)
        params, _start, _end = self._params(request)
        qs = StockBalance.objects.select_related("material", "location", "uom").order_by(
            "material__code", "location__code", "batch_number"
        )
        if params.get("location"):
            qs = qs.filter(location_id=params["location"])
        if params.get("site"):
            qs = qs.filter(location__source_site=params["site"])
        if params.get("q"):
            q = params["q"]
            qs = qs.filter(Q(material__code__icontains=q) | Q(material__name__icontains=q) |
                           Q(location__code__icontains=q) | Q(batch_number__icontains=q))
        def serialize(row):
            return {
            "id": row.id, "material_id": row.material_id, "material_code": row.material.code,
            "material_name": row.material.name, "specification": row.material.specification,
            "location_id": row.location_id, "location_code": row.location.code,
            "location_name": row.location.name, "site": row.location.source_site,
            "batch_number": row.batch_number, "uom_id": row.uom_id,
            "uom_code": row.uom.code, "uom_name": row.uom.name,
            "quantity": row.quantity, "reserved_quantity": row.reserved_quantity,
            "available_quantity": row.quantity - row.reserved_quantity,
            "updated_at": row.updated_at,
            }
        return self._paged_rows(request, qs, serialize)


class MaterialMovementDetailViewSet(SnapshotReportMixin, InventoryQueryViewSet):
    report_kind = "movement"

    def list(self, request):
        if request.query_params.get("source") in {"dgyzx1", "local"}:
            return self.snapshot_list(request)
        params, start, end = self._params(request)
        qs = StockTransaction.objects.select_related("material", "location", "uom", "business_uom").order_by(
            "-effective_date", "-id"
        )
        if start:
            qs = qs.filter(effective_date__gte=start)
        if end:
            qs = qs.filter(effective_date__lte=end)
        if params.get("location"):
            qs = qs.filter(location_id=params["location"])
        if params.get("site"):
            qs = qs.filter(location__source_site=params["site"])
        if params.get("q"):
            q = params["q"]
            qs = qs.filter(Q(material__code__icontains=q) | Q(material__name__icontains=q) |
                           Q(location__code__icontains=q) | Q(source_id__icontains=q) |
                           Q(source_line_id__icontains=q) | Q(batch_number__icontains=q))
        def serialize(row):
            return {
            "id": row.id, "movement_type": row.movement_type, "effective_date": row.effective_date,
            "material_id": row.material_id, "material_code": row.material.code,
            "material_name": row.material.name, "specification": row.material.specification,
            "location_id": row.location_id, "location_code": row.location.code,
            "location_name": row.location.name, "site": row.location.source_site,
            "batch_number": row.batch_number, "uom_id": row.uom_id,
            "uom_code": row.uom.code, "uom_name": row.uom.name,
            "quantity": row.quantity, "balance_after": row.balance_after,
            "source_model": row.source_model, "source_id": row.source_id,
            "source_line_id": row.source_line_id, "actor": row.actor,
            "business_quantity": row.business_quantity, "business_uom_code": row.business_uom.code if row.business_uom else "",
            "uom_rate_m": row.uom_rate_m, "uom_rate_d": row.uom_rate_d,
            "posted_at": row.posted_at,
            }
        return self._paged_rows(request, qs, serialize)


class TransferDetailViewSet(InventoryQueryViewSet):
    def list(self, request):
        return self._list_documents(request, "transfer")


class CountResultViewSet(InventoryQueryViewSet):
    def list(self, request):
        return self._list_documents(request, "count", include_count=True)


class UnplannedReceiptDetailViewSet(InventoryQueryViewSet):
    def list(self, request):
        return self._list_documents(request, "receipt")


class UnplannedIssueDetailViewSet(InventoryQueryViewSet):
    def list(self, request):
        return self._list_documents(request, "issue")


class ScrapDetailViewSet(InventoryQueryViewSet):
    def list(self, request):
        return self._list_documents(request, "scrap")
StockTransferViewSet = make_viewset(StockTransfer, serializer_for(StockTransfer))
StockTransferLineViewSet = make_viewset(StockTransferLine, serializer_for(StockTransferLine))
StockCountViewSet = make_viewset(StockCount, serializer_for(StockCount))
StockCountLineViewSet = make_viewset(StockCountLine, serializer_for(StockCountLine))


class InventoryAlertViewSet(viewsets.ViewSet):
    queryset = StockBalance.objects.none()
    permission_classes = (ErpRolePermission,)

    def list(self, request):
        alerts = []
        balances = StockBalance.objects.select_related("material", "location", "uom")
        for balance in balances:
            threshold = balance.material.stock_warning_qty
            if threshold > 0 and balance.quantity < threshold:
                alerts.append(
                    {
                        "material": balance.material_id,
                        "material_code": balance.material.code,
                        "material_name": balance.material.name,
                        "location": balance.location_id,
                        "location_code": balance.location.code,
                        "uom": balance.uom_id,
                        "quantity": f"{balance.quantity:.6f}",
                        "warning_quantity": f"{threshold:.6f}",
                        "shortage_quantity": f"{threshold - balance.quantity:.6f}",
                    }
                )
        return response.Response(alerts)
