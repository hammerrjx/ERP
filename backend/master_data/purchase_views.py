from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import decorators, response, serializers

from backend.domain.purchase import (
    GoodsReceipt, GoodsReceiptLine, PayableVoucher,
    PayableVoucherLine, PurchaseOrder, PurchaseOrderLine, PurchaseRequisition,
    PurchaseRequisitionLine, PurchaseReturn, PurchaseReturnLine, RequestForQuotation,
    RfqLine, SupplierInquiry, SupplierQuote, SupplierQuoteLine,
)
from backend.domain.system import ApprovalStatus, AuditEvent
from .api_common import ApprovalViewSet, make_viewset
from .exports import supplier_quote_workbook_response
from .serializers import (
    GoodsReceiptLineSerializer, GoodsReceiptSerializer, PayableVoucherLineSerializer,
    PayableVoucherSerializer, PurchaseOrderLineSerializer, PurchaseOrderSerializer,
    PurchaseRequisitionLineSerializer, PurchaseRequisitionSerializer,
    PurchaseReturnLineSerializer, PurchaseReturnSerializer, RequestForQuotationSerializer,
    RfqLineSerializer, SupplierInquirySerializer, SupplierQuoteLineSerializer,
    SupplierQuoteSerializer,
)

class SupplierQuoteViewSet(ApprovalViewSet):
    queryset = SupplierQuote.objects.select_related(
        "supplier", "business_group", "currency", "material__uom", "material__category", "purchase_uom",
        "operation__routing__material", "parent_material",
    ).prefetch_related("lines")
    serializer_class = SupplierQuoteSerializer

    @decorators.action(detail=False, methods=["get"])
    def resolve(self, request):
        required = ("supplier", "material", "quantity", "date")
        missing = [name for name in required if not request.query_params.get(name)]
        if missing:
            raise serializers.ValidationError({name: "此参数必填" for name in missing})
        quote_type = request.query_params.get("quote_type", SupplierQuote.QuoteType.PURCHASE)
        target_date = request.query_params["date"]
        quote = self.get_queryset().filter(
            supplier_id=request.query_params["supplier"],
            material_id=request.query_params["material"],
            quote_type=quote_type,
            status=ApprovalStatus.APPROVED,
            is_confirmed=True,
            is_ratified=True,
            effective_date__lte=target_date,
        ).filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=target_date)).order_by(
            "-effective_date", "-created_at",
        ).first()
        if not quote:
            raise serializers.ValidationError("未找到匹配日期、类型和状态的有效供应商报价")
        try:
            unit_price, tier = quote.price_for(request.query_params["quantity"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        data = self.get_serializer(quote).data
        data.update({
            "resolved_unit_price": format(unit_price, ".8f"),
            "resolved_line": tier.pk if tier else None,
            "resolved_min_qty": format(tier.min_qty, ".8f") if tier else "0.00000000",
        })
        return response.Response(data)

    @decorators.action(detail=True, methods=["post"], url_path="sales-confirm")
    def sales_confirm(self, request, pk=None):
        return self.transition(self.get_object(), "sales_confirm", request.user.get_username() or "system")

    @decorators.action(detail=True, methods=["post"], url_path="sales-unconfirm")
    def sales_unconfirm(self, request, pk=None):
        return self.transition(self.get_object(), "sales_unconfirm")

    @decorators.action(detail=False, methods=["post"])
    def export(self, request):
        ids = request.data.get("ids")
        queryset = self.get_queryset()
        if ids is not None:
            if not isinstance(ids, list) or any(not isinstance(value, int) or value <= 0 for value in ids):
                raise serializers.ValidationError({"ids": "当前筛选结果必须为正整数 ID 列表"})
            queryset = queryset.filter(pk__in=list(dict.fromkeys(ids)))
        return supplier_quote_workbook_response(queryset.order_by("number"))


SupplierQuoteLineViewSet = make_viewset(SupplierQuoteLine, SupplierQuoteLineSerializer)
PurchaseRequisitionLineViewSet = make_viewset(PurchaseRequisitionLine, PurchaseRequisitionLineSerializer)
RfqViewSet = make_viewset(RequestForQuotation, RequestForQuotationSerializer)
RfqLineViewSet = make_viewset(RfqLine, RfqLineSerializer)
SupplierInquiryViewSet = make_viewset(SupplierInquiry, SupplierInquirySerializer)
class PurchaseOrderViewSet(ApprovalViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    @decorators.action(detail=True, methods=["post"], url_path="generate-receipt")
    @transaction.atomic
    def generate_receipt(self, request, pk=None):
        order = self.get_object()
        if order.status != ApprovalStatus.APPROVED:
            raise serializers.ValidationError("只有已审核采购单可以生成收货草稿")
        receipt_type = request.data.get("receipt_type", GoodsReceipt.ReceiptType.NORMAL)
        if order.purchase_type == PurchaseOrder.PurchaseType.NON_PRODUCTION:
            receipt_type = GoodsReceipt.ReceiptType.NON_PRODUCTION
        receipt = GoodsReceipt(
            supplier=order.supplier,
            purchase_order=order,
            receipt_date=request.data.get("receipt_date") or timezone.localdate(),
            supplier_delivery_number=request.data.get("supplier_delivery_number", ""),
            receipt_type=receipt_type,
            notes=request.data.get("notes", ""),
            created_by=request.user.get_username(),
        )
        receipt.full_clean()
        receipt.save()
        created = 0
        selected = request.data.get("lines")
        if selected is not None and not isinstance(selected, list):
            raise serializers.ValidationError({"lines": "收货明细必须是列表"})
        requested_lines = {
            item.get("purchase_order_line"): item for item in (selected or [])
            if item.get("purchase_order_line")
        }
        if selected is not None and len(requested_lines) != len(selected):
            raise serializers.ValidationError({"lines": "每条收货明细必须且只能选择一个采购订单行"})
        found_line_ids = set()
        for order_line in order.lines.select_related("material", "uom"):
            source = requested_lines.get(order_line.pk)
            if selected is not None and source is None:
                continue
            found_line_ids.add(order_line.pk)
            quantity = Decimal(str(source.get("quantity"))) if source and source.get("quantity") is not None else order_line.quantity - order_line.received_quantity
            if quantity <= 0:
                continue
            line = GoodsReceiptLine(
                receipt=receipt,
                line_number=order_line.line_number,
                purchase_order_line=order_line,
                material=order_line.material,
                uom=order_line.uom,
                quantity=quantity,
                location_id=(source or {}).get("location") or order.supplier.default_receipt_location_id or order_line.material.default_location_id,
                batch_number=(source or {}).get("batch_number", ""),
            )
            line.full_clean()
            line.save()
            created += 1
        unknown_lines = set(requested_lines).difference(found_line_ids)
        if unknown_lines:
            raise serializers.ValidationError({"lines": f"采购订单不包含来源行: {sorted(unknown_lines)}"})
        if not created:
            receipt.delete()
            raise serializers.ValidationError("采购单没有待收货明细")
        AuditEvent.objects.create(
            model=receipt._meta.label_lower,
            object_id=str(receipt.pk),
            action="generate_from_purchase_order",
            actor=request.user.get_username() or "system",
            payload={"purchase_order_id": order.pk, "purchase_order_line_ids": list(requested_lines)},
        )
        return response.Response(GoodsReceiptSerializer(receipt).data, status=201)


PurchaseOrderLineViewSet = make_viewset(PurchaseOrderLine, PurchaseOrderLineSerializer)
GoodsReceiptViewSet = make_viewset(GoodsReceipt, GoodsReceiptSerializer)
GoodsReceiptLineViewSet = make_viewset(GoodsReceiptLine, GoodsReceiptLineSerializer)
PayableVoucherLineViewSet = make_viewset(PayableVoucherLine, PayableVoucherLineSerializer)
PurchaseReturnViewSet = make_viewset(PurchaseReturn, PurchaseReturnSerializer)
PurchaseReturnLineViewSet = make_viewset(PurchaseReturnLine, PurchaseReturnLineSerializer)


class PayableVoucherViewSet(ApprovalViewSet):
    queryset = PayableVoucher.objects.all()
    serializer_class = PayableVoucherSerializer

    @decorators.action(detail=False, methods=["post"], url_path="auto-generate")
    @transaction.atomic
    def auto_generate(self, request):
        receipt_line_ids = list(dict.fromkeys(request.data.get("receipt_line_ids") or []))
        return_line_ids = list(dict.fromkeys(request.data.get("purchase_return_line_ids") or []))
        if not receipt_line_ids and not return_line_ids:
            raise serializers.ValidationError("必须选择至少一条收货或采购退货明细")
        receipt_lines = list(GoodsReceiptLine.objects.filter(pk__in=receipt_line_ids).select_related(
            "receipt__supplier", "purchase_order_line__order__currency", "material", "uom",
        ))
        return_lines = list(PurchaseReturnLine.objects.filter(pk__in=return_line_ids).select_related(
            "purchase_return__supplier", "purchase_order_line__order__currency", "material", "uom",
        ))
        if len(receipt_lines) != len(receipt_line_ids):
            raise serializers.ValidationError({"receipt_line_ids": "包含不存在的收货明细"})
        if len(return_lines) != len(return_line_ids):
            raise serializers.ValidationError({"purchase_return_line_ids": "包含不存在的采购退货明细"})
        if any(line.receipt.status != ApprovalStatus.APPROVED for line in receipt_lines) or any(
            line.purchase_return.status != ApprovalStatus.APPROVED for line in return_lines
        ):
            raise serializers.ValidationError("只有已审核收货或采购退货明细可以生成应付凭单")
        used_receipts = set(PayableVoucherLine.objects.filter(
            source_receipt_line_id__in=receipt_line_ids,
        ).values_list("source_receipt_line_id", flat=True))
        used_returns = set(PayableVoucherLine.objects.filter(
            source_purchase_return_line_id__in=return_line_ids,
        ).values_list("source_purchase_return_line_id", flat=True))
        if used_receipts or used_returns:
            raise serializers.ValidationError({
                "sources": f"来源明细已生成凭单: 收货{sorted(used_receipts)} 退货{sorted(used_returns)}",
            })

        groups = {}
        for line in receipt_lines:
            order = line.purchase_order_line.order
            key = (line.receipt.supplier_id, order.currency_id, order.payment_method, order.tax_rate)
            groups.setdefault(key, []).append(("receipt", line))
        for line in return_lines:
            order = line.purchase_order_line.order
            key = (line.purchase_return.supplier_id, order.currency_id, order.payment_method, order.tax_rate)
            groups.setdefault(key, []).append(("return", line))

        vouchers = []
        for (supplier_id, currency_id, payment_method, tax_rate), sources in groups.items():
            voucher = PayableVoucher.objects.create(
                voucher_date=request.data.get("voucher_date") or timezone.localdate(),
                supplier_id=supplier_id,
                currency_id=currency_id,
                payment_method=payment_method,
                tax_rate=tax_rate,
                notes=request.data.get("notes", ""),
                created_by=request.user.get_username(),
            )
            for index, (source_type, line) in enumerate(sources, 1):
                voucher_line = PayableVoucherLine(
                    voucher=voucher,
                    line_number=index * 10,
                    source_receipt_line=line if source_type == "receipt" else None,
                    source_purchase_return_line=line if source_type == "return" else None,
                    material=line.material,
                    uom=line.uom,
                    quantity=line.quantity,
                    unit_price=line.purchase_order_line.unit_price,
                )
                voucher_line.full_clean()
                voucher_line.save()
            AuditEvent.objects.create(
                model=voucher._meta.label_lower,
                object_id=str(voucher.pk),
                action="auto_generate",
                actor=request.user.get_username() or "system",
                payload={
                    "receipt_line_ids": [line.pk for source_type, line in sources if source_type == "receipt"],
                    "purchase_return_line_ids": [line.pk for source_type, line in sources if source_type == "return"],
                },
            )
            vouchers.append(voucher)
        return response.Response(PayableVoucherSerializer(vouchers, many=True).data, status=201)


class PurchaseRequisitionViewSet(ApprovalViewSet):
    queryset = PurchaseRequisition.objects.all()
    serializer_class = PurchaseRequisitionSerializer

    @decorators.action(detail=True, methods=["post"])
    @transaction.atomic
    def convert(self, request, pk=None):
        requisition = self.get_object()
        if requisition.status != ApprovalStatus.APPROVED:
            raise serializers.ValidationError("只有已审核请购单可以转采购单")
        inquiry_ids = request.data.get("supplier_inquiry_ids") or []
        inquiries = list(SupplierInquiry.objects.filter(pk__in=inquiry_ids, selected=True).select_related(
            "supplier", "rfq_line__rfq", "rfq_line__requisition_line", "rfq_line__material", "rfq_line__uom",
        ))
        if len(inquiries) != len(set(inquiry_ids)) or not inquiries:
            raise serializers.ValidationError("必须选择有效且已选中的询价响应")
        if len({item.supplier_id for item in inquiries}) != 1:
            raise serializers.ValidationError("一张采购单只能选择同一供应商的询价响应")
        if any(item.rfq_line.rfq.requisition_id != requisition.id for item in inquiries):
            raise serializers.ValidationError("询价响应必须来自当前请购单")
        supplier = inquiries[0].supplier
        order = PurchaseOrder.objects.create(
            supplier=supplier,
            currency=inquiries[0].rfq_line.rfq.currency,
            department=requisition.department,
            payment_method=supplier.payment_method,
            tax_rate=inquiries[0].tax_rate,
            promised_date=max(item.promised_date for item in inquiries),
            source_requisition=requisition,
            created_by=request.user.get_username(),
        )
        for index, inquiry in enumerate(sorted(inquiries, key=lambda item: item.rfq_line.line_number), 1):
            rfq_line = inquiry.rfq_line
            PurchaseOrderLine.objects.create(
                order=order,
                line_number=index * 10,
                material=rfq_line.material,
                uom=rfq_line.uom,
                quantity=rfq_line.quantity,
                unit_price=inquiry.unit_price,
                promised_date=inquiry.promised_date,
                source_requisition_line=rfq_line.requisition_line,
            )
            source_line = rfq_line.requisition_line
            source_line.converted_qty += rfq_line.quantity
            source_line.save(update_fields=["converted_qty"])
        total_requested = sum((line.requested_qty for line in requisition.lines.all()), Decimal("0"))
        total_converted = sum((line.converted_qty for line in requisition.lines.all()), Decimal("0"))
        requisition.conversion_percent = min(Decimal("100"), total_converted * Decimal("100") / total_requested) if total_requested else Decimal("0")
        requisition.save(update_fields=["conversion_percent", "updated_at"])
        AuditEvent.objects.create(
            model=order._meta.label_lower,
            object_id=str(order.pk),
            action="convert_from_requisition",
            actor=request.user.get_username() or "system",
            payload={"source_requisition_id": requisition.pk, "inquiry_ids": inquiry_ids},
        )
        return response.Response(PurchaseOrderSerializer(order).data, status=201)
