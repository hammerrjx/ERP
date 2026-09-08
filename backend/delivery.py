"""Delivery drafts share order-line identities and signed execution quantities."""
from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum

from backend.models import (
    ApprovalStatus, AuditEvent, DeliveryOrderLine, SalesOrderLine,
    SalesReturnLine,
)


OPEN_STATUSES = (ApprovalStatus.DRAFT, ApprovalStatus.PENDING, ApprovalStatus.REJECTED)


def execution_summary(source):
    totals = source.delivery_lines.filter(delivery__posted=True).aggregate(
        formal=Sum("actual_quantity"), spare=Sum("actual_spare_quantity"),
    )
    separate_returns = SalesReturnLine.objects.filter(
        Q(sales_order_line=source) | Q(source_delivery_line__sales_order_line=source),
        sales_return__posted=True,
    ).aggregate(total=Sum("quantity"))["total"] or Decimal(0)
    formal_history = source.delivered_quantity - (totals["formal"] or 0) + separate_returns
    spare_history = source.delivered_spare_quantity - (totals["spare"] or 0)
    formal_remaining = source.quantity - source.delivered_quantity
    spare_remaining = source.spare_quantity - source.delivered_spare_quantity
    return {
        "formal_net": str(source.delivered_quantity), "spare_net": str(source.delivered_spare_quantity),
        "formal_remaining": str(formal_remaining), "spare_remaining": str(spare_remaining),
        "total_net": str(source.delivered_quantity + source.delivered_spare_quantity),
        "formal_unrepresented": str(formal_history), "spare_unrepresented": str(spare_history),
        "has_history_gap": bool(formal_history or spare_history),
        "fulfilled": formal_remaining == 0 and spare_remaining == 0,
    }


def commitments(order_ids, exclude_delivery=None, exclude_line=None, exclude_return_line=None):
    rows = DeliveryOrderLine.objects.filter(
        sales_order_line_id__in=order_ids, delivery__status__in=OPEN_STATUSES, delivery__posted=False,
    )
    if exclude_delivery:
        rows = rows.exclude(delivery_id=exclude_delivery)
    if exclude_line:
        rows = rows.exclude(pk=exclude_line)
    totals = defaultdict(lambda: [Decimal(0), Decimal(0), Decimal(0), Decimal(0)])
    for row in rows.values("sales_order_line_id").annotate(
        positive=Sum("actual_quantity", filter=Q(actual_quantity__gt=0)),
        negative=Sum("actual_quantity", filter=Q(actual_quantity__lt=0)),
        spare_positive=Sum("actual_spare_quantity", filter=Q(actual_spare_quantity__gt=0)),
        spare_negative=Sum("actual_spare_quantity", filter=Q(actual_spare_quantity__lt=0)),
    ):
        totals[row["sales_order_line_id"]] = [
            row["positive"] or Decimal(0), abs(row["negative"] or Decimal(0)),
            row["spare_positive"] or Decimal(0), abs(row["spare_negative"] or Decimal(0)),
        ]
    returns = SalesReturnLine.objects.filter(
        Q(sales_order_line_id__in=order_ids) | Q(source_delivery_line__sales_order_line_id__in=order_ids),
        sales_return__status__in=OPEN_STATUSES, sales_return__posted=False,
    ).select_related("source_delivery_line")
    if exclude_return_line:
        returns = returns.exclude(pk=exclude_return_line)
    for row in returns:
        key = row.sales_order_line_id or row.source_delivery_line.sales_order_line_id
        totals[key][1] += row.quantity
    return totals


def validate_quantities(delivery, lines, exclude_line=None, whole=True):
    totals = commitments([line.sales_order_line_id for line in lines], delivery.pk if whole else None, exclude_line)
    sources = {}
    for line in lines:
        source = line.sales_order_line
        sources[source.pk] = source
        if source.order.customer_id != delivery.customer_id:
            raise ValidationError("送货明细客户与表头不一致")
        if source.order.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核订单可以送货")
        returning = line.actual_quantity <= 0 and line.actual_spare_quantity <= 0
        if source.line_status not in ("normal", "") and not (returning and source.line_status in ("C", "closed")):
            raise ValidationError("订单行已关闭或不可执行")
        for quantity, offset in ((line.actual_quantity, 0), (line.actual_spare_quantity, 2)):
            totals[source.pk][offset + (quantity < 0)] += abs(quantity)
    for key, source in sources.items():
        positive, negative, spare_positive, spare_negative = totals[key]
        label = f"{source.order.number} / {source.line_number}"
        if positive > max(source.quantity - source.delivered_quantity, 0):
            raise ValidationError(f"{label}：本次送货与其他未审核占用合计超过可送数量")
        if negative > source.delivered_quantity:
            raise ValidationError(f"{label}：退回与其他未审核退回合计超过净已送数量")
        if spare_positive > max(source.spare_quantity - source.delivered_spare_quantity, 0):
            raise ValidationError(f"{label}：本次备品与未审核占用合计超过可送备品")
        if spare_negative > source.delivered_spare_quantity:
            raise ValidationError(f"{label}：退回备品超过净已送备品")
    reversals = defaultdict(lambda: [Decimal(0), Decimal(0)])
    originals = {}
    for line in lines:
        if line.source_delivery_line_id and (line.actual_quantity < 0 or line.actual_spare_quantity < 0):
            originals[line.source_delivery_line_id] = line.source_delivery_line
            reversals[line.source_delivery_line_id][0] += abs(min(line.actual_quantity, 0))
            reversals[line.source_delivery_line_id][1] += abs(min(line.actual_spare_quantity, 0))
    for key, original in originals.items():
        others = DeliveryOrderLine.objects.filter(
            source_delivery_line_id=key,
            delivery__status__in=(*OPEN_STATUSES, ApprovalStatus.APPROVED),
        )
        if whole:
            others = others.exclude(delivery_id=delivery.pk)
        elif exclude_line:
            others = others.exclude(pk=exclude_line)
        reversed_totals = others.aggregate(
            quantity=Sum("actual_quantity", filter=Q(actual_quantity__lt=0)),
            spare=Sum("actual_spare_quantity", filter=Q(actual_spare_quantity__lt=0)),
        )
        reversed_amount = abs(reversed_totals["quantity"] or 0)
        returned = SalesReturnLine.objects.filter(
            source_delivery_line_id=key, sales_return__status__in=(*OPEN_STATUSES, ApprovalStatus.APPROVED),
        ).aggregate(total=Sum("quantity"))["total"] or 0
        if reversals[key][0] + reversed_amount + returned > max(original.actual_quantity, 0):
            raise ValidationError("负数送货与独立退货合计超过所关联原送货行数量")
        if reversals[key][1] + abs(reversed_totals["spare"] or 0) > max(original.actual_spare_quantity, 0):
            raise ValidationError("退回备品合计超过所关联原送货行备品数")


def order_line_data(source, occupied=None):
    material, order, customer_material = source.material, source.order, source.customer_material
    occupied = occupied or [Decimal(0)] * 4
    location = material.default_location
    return {
        "sales_order_line": source.pk, "order": order.pk, "order_number": order.number,
        "order_line_number": source.line_number, "customer_po": order.customer_po,
        "material": material.pk, "material_code": material.code,
        "material_name": source.material_name or material.name,
        "material_specification": source.material_specification or material.specification,
        "customer_material": source.customer_material_id,
        "customer_material_code": customer_material.customer_code if customer_material else "",
        "customer_material_name": source.customer_material_name or (customer_material.customer_name if customer_material else ""),
        "terminal_material_code": customer_material.terminal_customer_code if customer_material else source.terminal_customer_code,
        "terminal_material_name": customer_material.terminal_customer_name if customer_material else source.terminal_customer_name,
        "uom": source.uom_id, "uom_code": source.uom.code,
        "inventory_uom_code": source.inventory_uom.code if source.inventory_uom_id else material.uom.code,
        "uom_rate_m": str(source.uom_rate_m), "uom_rate_d": str(source.uom_rate_d),
        "source_location": location.pk if location else None,
        "source_location_code": location.code if location else "",
        "source_location_name": location.name if location else "",
        "batch_control": material.batch_control,
        "quantity": str(source.quantity), "ordered_quantity": str(source.quantity),
        "spare_quantity": str(source.spare_quantity), "delivered_quantity": str(source.delivered_quantity),
        "delivered_spare_quantity": str(source.delivered_spare_quantity),
        "pending_quantity": str(occupied[0]), "pending_return_quantity": str(occupied[1]),
        "pending_spare_quantity": str(occupied[2]),
        "remaining_quantity": str(source.quantity - source.delivered_quantity),
        "remaining_spare_quantity": str(source.spare_quantity - source.delivered_spare_quantity),
        "available_quantity": str(max(source.quantity - source.delivered_quantity - occupied[0], 0) if source.line_status in ("normal", "") else 0),
        "returnable_quantity": str(max(source.delivered_quantity - occupied[1], 0)),
        "available_spare_quantity": str(max(source.spare_quantity - source.delivered_spare_quantity - occupied[2], 0) if source.line_status in ("normal", "") else 0),
        "returnable_spare_quantity": str(max(source.delivered_spare_quantity - occupied[3], 0)),
        "unit_price": str(source.unit_price), "currency_code": order.currency.code,
        "tax_rate": str(order.tax_rate), "order_date": str(order.order_date),
        "promised_date": str(source.promised_date), "order_notes": order.notes,
        "stock_quantity": None,
    }


SOURCE_RELATED = (
    "order__currency", "customer_material", "material__default_location", "material__uom", "uom", "inventory_uom",
)


@transaction.atomic
def save_sheet(data, actor, instance=None, reservation=None):
    from backend.master_data.api_common import ensure_editable
    from backend.master_data.serializers.delivery import (
    DeliveryOrderSerializer,
)
    from rest_framework.exceptions import ValidationError as ApiValidationError

    selected = data.get("lines")
    if not isinstance(selected, list) or not selected or len(selected) > 500:
        raise ApiValidationError({"lines": "请选择1至500条明细"})
    if not all(isinstance(item, dict) for item in selected):
        raise ApiValidationError({"lines": "明细格式不正确"})
    if instance:
        ensure_editable(instance)
        if instance.posted or instance.status not in OPEN_STATUSES:
            raise ApiValidationError("该单已回写订单或已作废，不能编辑")
        if data.get("updated_at") != instance.updated_at.isoformat():
            # DRF uses Z for UTC while datetime.isoformat uses +00:00.
            from django.utils.dateparse import parse_datetime
            try:
                same_version = parse_datetime(data.get("updated_at", "")) == instance.updated_at
            except (TypeError, ValueError):
                same_version = False
            if not same_version:
                raise ApiValidationError("单据已被修改，请重新打开后保存")
    try:
        source_ids = {int(item["sales_order_line"]) for item in selected}
    except (KeyError, TypeError, ValueError):
        raise ApiValidationError({"lines": "每行必须选择有效订单明细"})
    sources = {item.pk: item for item in SalesOrderLine.objects.select_for_update().filter(
        pk__in=source_ids,
    ).order_by("pk").select_related(*SOURCE_RELATED)}
    if sources.keys() != source_ids:
        raise ApiValidationError({"lines": "来源订单明细不存在"})
    customer_ids = {line.order.customer_id for line in sources.values()}
    if len(customer_ids) != 1:
        raise ApiValidationError("一张送货单只能包含同一客户")
    orders = {line.order_id: line.order for line in sources.values()}
    if data.get("sales_order") and str(data["sales_order"]) not in {str(key) for key in orders}:
        raise ApiValidationError("所选明细不属于指定订单")
    header_fields = (
        "customer", "delivery_date", "address_code", "delivery_address", "source_location",
        "default_print_person", "document_type", "delivery_mode", "srm_number", "notes", "actual_ship_time", "source_delivery",
    )
    header = {key: data[key] for key in header_fields if key in data}
    if header.get("source_location") == "":
        header["source_location"] = None
    header.setdefault("customer", next(iter(customer_ids)))
    header["sales_order"] = next(iter(orders)) if len(orders) == 1 else None
    pos = {order.customer_po for order in orders.values()}
    header["customer_po"] = next(iter(pos)) if len(pos) == 1 else ""
    serializer = DeliveryOrderSerializer(instance=instance, data=header, partial=bool(instance))
    serializer.is_valid(raise_exception=True)
    save_args = {"updated_by" if instance else "created_by": actor.get_username()}
    if reservation:
        save_args["number"] = reservation.number
    delivery = serializer.save(**save_args)
    previous = {line.pk: line for line in delivery.lines.all()} if instance else {}
    keep, result, seen, identities = set(), [], set(), set()
    for index, item in enumerate(selected, 1):
        source = sources[int(item["sales_order_line"])]
        raw_id = item.get("id")
        try:
            line_id = int(raw_id) if raw_id else None
        except (TypeError, ValueError):
            raise ApiValidationError({"lines": f"第{index}行编号无效"})
        if line_id and (line_id not in previous or line_id in keep):
            raise ApiValidationError({"lines": f"第{index}行不属于当前单或重复"})
        line = previous.get(line_id) or DeliveryOrderLine(delivery=delivery, created_by=actor.get_username())
        if line_id:
            keep.add(line_id)
        line.sales_order_line = source
        line.material, line.customer_material, line.uom = source.material, source.customer_material, source.uom
        line.line_number = line.line_number if line_id else (max([0, *[r.line_number for r in previous.values()], *seen]) + 10)
        seen.add(line.line_number)
        from rest_framework import serializers
        quantity_field = serializers.DecimalField(max_digits=19, decimal_places=8)
        try:
            line.actual_quantity = quantity_field.run_validation(item.get("actual_quantity", 0))
            line.actual_spare_quantity = quantity_field.run_validation(item.get("actual_spare_quantity", 0))
            line.source_location_id = int(item.get("source_location") or source.material.default_location_id or delivery.source_location_id or 0) or None
        except (ValueError, TypeError, ApiValidationError):
            raise ApiValidationError({"lines": f"第{index}行数量或库位无效（最多8位小数）"})
        line.batch_number = item.get("batch_number", "")
        line.notes = item.get("notes", "")
        line.source_delivery_line_id = serializers.IntegerField(min_value=1, allow_null=True).run_validation(item.get("source_delivery_line") or None)
        line.ordered_spare_quantity = source.spare_quantity
        line.srm_customer_po = source.order.customer_po
        line.srm_material_code = source.customer_material.customer_code if source.customer_material_id else source.material.code
        line.srm_material_name = source.material.name
        line.srm_quantity = line.actual_quantity
        identity = (source.pk, line.source_location_id, line.batch_number)
        if identity in identities:
            raise ApiValidationError({"lines": f"第{index}行订单、库位、批号重复，请合并数量"})
        identities.add(identity)
        if not line.source_snapshot or not line_id or previous[line_id].source_snapshot.get("sales_order_line") != source.pk:
            line.source_snapshot = order_line_data(source)
        line.updated_by = actor.get_username()
        if line_id:
            line.modification_count += 1
        try:
            line.full_clean()
        except ValidationError as exc:
            raise ApiValidationError({"lines": f"第{index}行：{'；'.join(exc.messages)}"})
        result.append(line)
    try:
        validate_quantities(delivery, result)
    except ValidationError as exc:
        raise ApiValidationError({"lines": exc.messages})
    removed = delivery.lines.exclude(pk__in=keep)
    if removed.exists() and instance:
        from backend.master_data.api_common import ErpRolePermission
        from types import SimpleNamespace
        if not ErpRolePermission().has_permission(SimpleNamespace(user=actor), SimpleNamespace(action="destroy", basename="delivery-order")):
            raise ApiValidationError("删除明细需要送货单删除权限")
        removed.delete()
    for line in result:
        line.save()
    if reservation:
        reservation.delivery = delivery
        reservation.save(update_fields=["delivery"])
    AuditEvent.objects.create(model=delivery._meta.label_lower, object_id=str(delivery.pk),
                              action="save_sheet", actor=actor.get_username(),
                              payload={"order_line_ids": sorted(source_ids), "lines": len(result)})
    return delivery
