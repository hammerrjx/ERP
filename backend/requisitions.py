"""Purchase requisition rules and live supply. Source: xgyzx tri_req_mrp/tri_podr_req."""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from backend.domain.purchase import PurchaseRequisition, PurchaseRequisitionLine, PurchaseOrderLine


def material_snapshot(material):
    return dict(pt_part=material.code, pt_desc1=material.name, pt_desc2=getattr(material, 'english_name', ''),
        pt_spec=material.specification, pt_um=material.uom.name,
        pt_prod_line=material.category.code, pt_group=getattr(material, 'product_group', ''),
        pt_part_type=getattr(material, 'part_type', ''), pt_ord_min=str(material.min_purchase_qty),
        pt_ord_mult=str(material.min_pack_qty), pt_iss_batch=str(material.min_issue_qty))


def assert_editable(document):
    if document.requisition_type != 'P':
        raise ValidationError('仅P采购请购可以维护；S外协及其他历史类型只读')
    if document.status not in ('draft', 'rejected'):
        raise ValidationError('只有草稿或已驳回单据可以修改')
    if document.lines.filter(converted_qty__gt=0).exists() or document.lines.filter(purchase_order_lines__isnull=False).exists():
        raise ValidationError('已存在采购引用，不能修改或删除请购')


def supply_contributions(site, part=None):
    """Return requisition supply with an explicit approval boundary."""
    result = []
    lines = PurchaseRequisitionLine.objects.filter(requisition__site=site, line_status='',
        requisition__status__in=['draft', 'pending', 'approved', 'rejected']).select_related('requisition', 'material__uom')
    if part is not None:
        from django.db.models import Q
        parts = {part} if isinstance(part, str) else set(part)
        lines = lines.filter(Q(material_snapshot__pt_part__in=parts) | Q(material__code__in=parts))
    for line in lines:
        if part is not None and (line.material_snapshot.get('pt_part') or line.material.code) not in parts:
            continue
        qty = line.requested_qty - line.converted_qty
        if qty:
            approved = line.requisition.status == 'approved'
            result.append(dict(tab='requisition', part=line.material_snapshot.get('pt_part') or line.material.code,
                quantity=str(qty), kind='请购中' if approved else '请购中（草稿，仅显示）',
                document=line.requisition.number, line=str(line.line_number),
                location='', location_name='', lot='', nettable=False, location_type='', origin='local',
                status=line.requisition.status, eligible_for_balance=approved))
    return result


def update_applied(line_id, delta):
    """Call while the purchase mutation holds an atomic transaction and parent lock."""
    line = PurchaseRequisitionLine.objects.select_for_update().select_related('requisition', 'material').get(pk=line_id)
    if line.requisition.requisition_type != 'P':
        raise ValidationError('当前仅支持P采购请购转采')
    value = line.converted_qty + delta
    if value < 0 or value > line.requested_qty:
        raise ValidationError('转采数量超过请购剩余量，或累计已采购数量不一致')
    if delta > 0 and (line.requisition.status != 'approved' or line.line_status):
        raise ValidationError('只允许引用已审核且正常状态的请购行')
    threshold = Decimal(str(line.material_snapshot.get('pt_iss_batch', '0')))
    close = value >= line.requested_qty or (threshold > 0 and line.requested_qty - value < threshold)
    line.converted_qty = value
    if close and not line.line_status:
        line.line_status, line.closed_by, line.closed_at = 'C', 'SYSTEM', timezone.now()
    if not close:
        line.line_status = ''
    # tri_podr_req recomputes status on both increases and decreases; audit stamps remain.
    line.save(update_fields=['converted_qty', 'line_status', 'closed_by', 'closed_at'])
    header = PurchaseRequisition.objects.select_for_update().get(pk=line.requisition_id)
    totals = header.lines.aggregate(requested=Sum('requested_qty'), applied=Sum('converted_qty'))
    header.conversion_percent = min(Decimal(100), totals['applied'] * 100 / totals['requested']) if totals['requested'] else Decimal(0)
    header.version += 1
    header.save(update_fields=['conversion_percent', 'version', 'updated_at'])


def purchase_quantity(line):
    if not line.source_requisition_line_id:
        return Decimal(0)
    req = line.source_requisition_line
    if line.material_id != req.material_id:
        raise ValidationError('采购物料与请购物料不一致')
    if line.uom_id == req.uom_id:
        return line.quantity
    quote = line.source_supplier_quote if line.source_supplier_quote_id else None
    if not quote or quote.purchase_uom_id != line.uom_id or quote.uom_rate_d <= 0:
        raise ValidationError('不同单位转采必须有明确的供应商报价换算比例')
    return line.quantity * quote.uom_rate_m / quote.uom_rate_d
