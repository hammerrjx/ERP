"""Ordinary purchase receipt/return rules, shared by all HTTP entry points."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Max
from django.utils import timezone

from backend.models import (
    GoodsReceipt, GoodsReceiptLine, PurchaseReturn, PurchaseReturnLine,
    PurchaseOrderLine, PurchaseOrderAllocation, StockBalance, StockTransaction, PayableVoucherLine, AuditEvent,
)

ZERO = Decimal(0)


def decimal(value):
    try:
        n = Decimal(str(value or 0))
        if not n.is_finite() or n != n.quantize(Decimal('.00000001')) or abs(n) >= Decimal('100000000000'):
            raise ValueError()
        return n
    except (ValueError, InvalidOperation):
        raise ValidationError('数量必须是最多8位小数的有效数值')


def returning(obj):
    return isinstance(obj, (PurchaseReturn, PurchaseReturnLine))


def owner(line):
    return line.purchase_return if returning(line) else line.receipt


def audit(doc, action, actor):
    payload = {}
    if action in ('approve', 'unapprove'):
        payload = {'posting_version': doc.posting_version, 'number': doc.number,
            'pending_changes': getattr(doc, '_pending_changes', []),
            'lines': [{'id':l.pk, 'purchase_order_line':l.purchase_order_line_id,
                'quantity':str(l.quantity), 'spare_quantity':str(l.spare_quantity),
                'uom_rate_m':str(l.uom_rate_m), 'uom_rate_d':str(l.uom_rate_d)} for l in doc.lines.all()]}
    AuditEvent.objects.create(model=doc._meta.label_lower, object_id=str(doc.pk), action=action, actor=actor, payload=payload)


def editable(doc):
    if doc.status not in ('draft', 'rejected') or doc.posted:
        raise ValidationError('只有未审核单据可修改')


def available(po, is_return=False, exclude_document=None):
    model, parent = (PurchaseReturnLine, 'purchase_return') if is_return else (GoodsReceiptLine, 'receipt')
    qs = model.objects.filter(purchase_order_line=po, **{parent+'__posted': False}).exclude(**{parent+'__status': 'void'})
    if exclude_document:
        qs = qs.exclude(**{parent+'_id': exclude_document})
    sums = qs.aggregate(q=Sum('quantity'), s=Sum('spare_quantity'))
    if is_return:
        q, s = po.received_quantity-po.returned_quantity, po.received_spare_quantity-po.returned_spare_quantity
    else:
        q, s = po.quantity+po.over_receipt_quantity-po.received_quantity, po.spare_quantity-po.received_spare_quantity
    return q-(sums['q'] or ZERO), s-(sums['s'] or ZERO), sums['q'] or ZERO, sums['s'] or ZERO


def validate_line(line):
    if not line.purchase_order_line_id:
        raise ValidationError('请选择采购来源行')
    po, doc = line.purchase_order_line, owner(line)
    if po.order.purchase_type != 'production':
        raise ValidationError('外协和非生产收退货不在本期范围')
    if po.order.supplier_id != doc.supplier_id or po.order.site != doc.site:
        raise ValidationError('采购行供应商或站点与单据不一致')
    if line.material_id != po.material_id or line.uom_id != po.uom_id:
        raise ValidationError('物料和采购单位必须与采购来源行一致')
    loc = line.source_location if returning(line) else line.location
    if loc.disabled_for_inventory or (loc.source_site and loc.source_site != doc.site):
        raise ValidationError('库位已停用或不属于当前站点')
    if line.material.batch_control and not line.batch_number:
        raise ValidationError('批号控制物料必须填写批号')
    q, s = decimal(line.quantity), decimal(line.spare_quantity)
    if not q and not s:
        raise ValidationError('正式数量和备品数量不能同时为零')
    if q*s < 0 or (returning(line) and min(q, s) < 0):
        raise ValidationError('退货数量不能为负，正式数量与备品方向必须一致')
    if line.uom_rate_m <= 0 or line.uom_rate_d <= 0:
        raise ValidationError('单位换算率必须大于零')
    if returning(line) and not line.reason.strip():
        raise ValidationError('请填写每行不良原因')
    if returning(line) and line.iqc_number and not doc.imported:
        raise ValidationError('IQC来源必须通过已核实的检验关联选择，不能手工填写')


def validate_document(doc, lines, approval=False):
    if doc.site != '1000' or doc.supplier.kind not in ('supplier', 'both'):
        raise ValidationError('请选择站点1000的供应商')
    for field in ('return_location',) if returning(doc) else ('iqc_location', 'raw_location'):
        loc = getattr(doc, field)
        if loc and (loc.disabled_for_inventory or loc.source_site not in ('', doc.site)):
            raise ValidationError('单头库位已停用或不属于当前站点')
    if not lines:
        raise ValidationError('单据至少需要一条明细')
    if not returning(doc) and not doc.supplier_delivery_number.strip():
        raise ValidationError('供应商送货单号必填')
    if returning(doc) and not doc.return_location_id:
        raise ValidationError('退货暂存仓必填')
    totals = defaultdict(lambda: [ZERO, ZERO])
    pos = {p.pk:p for p in PurchaseOrderLine.objects.select_for_update().select_related('order').filter(
        pk__in=[l.purchase_order_line_id for l in lines]).order_by('pk')}
    for line in lines:
        line.purchase_order_line = pos[line.purchase_order_line_id]
        validate_line(line)
        po = line.purchase_order_line
        if po.order.status != 'approved':
            raise ValidationError('来源采购单必须已审核')
        if not returning(doc) and po.line_status.lower() in ('c','closed') and min(line.quantity, line.spare_quantity) >= 0:
            raise ValidationError(f'采购行 {po.order.number}/{po.line_number} 已关闭')
        totals[po.pk][0] += line.quantity
        totals[po.pk][1] += line.spare_quantity
    for pk, (q,s) in totals.items():
        po = pos[pk]
        aq, ass, _, _ = available(po, returning(doc), doc.pk)
        if q > max(aq, ZERO) or s > max(ass, ZERO):
            raise ValidationError(f'{po.order.number}/{po.line_number} 数量超出可用额度：正式 {aq}，备品 {ass}（已扣未审核占用）')
        if not returning(doc) and (po.received_quantity+q < po.returned_quantity or po.received_spare_quantity+s < po.returned_spare_quantity):
            raise ValidationError('冲销后已收数量不足以覆盖已退数量')
    return pos


def update_totals(po, line, sign, is_return):
    fields = ['returned_quantity','returned_spare_quantity'] if is_return else ['received_quantity','received_spare_quantity']
    for field, qty in zip(fields, (line.quantity, line.spare_quantity)):
        setattr(po, field, getattr(po,field)+qty*sign)
    if not is_return and not po.snapshot.get('inspection_required', po.material.inspection_required):
        rate = line.uom_rate_m/line.uom_rate_d
        for field, qty in [('accepted_quantity',line.quantity),('accepted_spare_quantity',line.spare_quantity),
                           ('accepted_inventory_quantity',line.quantity*rate),('accepted_spare_inventory_quantity',line.spare_quantity*rate)]:
            setattr(po,field,getattr(po,field)+qty*sign);fields.append(field)
    po.save(update_fields=fields)


@transaction.atomic
def approve_document(doc, actor):
    locked = type(doc).objects.select_for_update().get(pk=doc.pk)
    doc.__dict__.update(locked.__dict__)
    if doc.posted and doc.status == 'approved': return
    if doc.status not in ('draft','pending','rejected'):
        raise ValidationError('当前状态不能审核')
    lines = list(doc.lines.select_related('purchase_order_line__order','material','uom',
        'source_location' if returning(doc) else 'location'))
    pos = validate_document(doc,lines,True)
    doc._pending_changes=[]
    for line in lines:
        if returning(doc) or not pos[line.purchase_order_line_id].snapshot.get('inspection_required'):
            continue
        remaining=-(line.quantity+line.spare_quantity)
        if remaining <= 0: continue
        candidates=GoodsReceiptLine.objects.select_for_update().filter(purchase_order_line_id=line.purchase_order_line_id,
            receipt__posted=True,pending_quantity__gt=0).exclude(receipt=doc).order_by('-receipt__receipt_date','-receipt__number','-line_number')
        for candidate in candidates:
            old=candidate.pending_quantity;used=min(old,remaining)
            candidate.pending_quantity-=used;candidate.save(update_fields=['pending_quantity'])
            doc._pending_changes.append({'id':candidate.pk,'old':str(old),'new':str(candidate.pending_quantity)})
            remaining-=used
            if not remaining: break
        if remaining: raise ValidationError('负数冲销超过该采购行剩余待检数量')
    doc.posting_version += 1
    for line in lines:
        po = pos[line.purchase_order_line_id]
        if not line.material.no_stock_movement:
            StockBalance.adjust(material=line.material, location=line.source_location if returning(doc) else line.location,
                uom=line.uom, quantity=(line.quantity+line.spare_quantity)*(-1 if returning(doc) else 1),
                movement_type='220' if returning(doc) else '120',
                source_model=doc._meta.label_lower,source_id=doc.pk,source_line_id=f'{line.pk}:{doc.posting_version}',
                actor=actor,batch_number=line.batch_number,effective_date=doc.return_date if returning(doc) else doc.receipt_date,
                uom_rate_m=line.uom_rate_m,uom_rate_d=line.uom_rate_d,native_sales_rates=True,usage='purchase')
        update_totals(po,line,1,returning(doc))
        if not returning(doc):
            line.accepted_quantity = ZERO if po.snapshot.get('inspection_required', po.material.inspection_required) else line.quantity
            line.pending_quantity = max(line.quantity + line.spare_quantity, ZERO) if po.snapshot.get('inspection_required', po.material.inspection_required) else ZERO
            line.save(update_fields=['accepted_quantity','pending_quantity'])
        if returning(doc) and doc.replenishment:
            # Lock the order, not just its lines, before allocating a new line number.
            type(po.order).objects.select_for_update().get(pk=po.order_id)
            next_line=(po.order.lines.aggregate(n=Max('line_number'))['n'] or 0)//10*10+10
            replacement=PurchaseOrderLine.objects.create(order=po.order,line_number=next_line,material=line.material,uom=line.uom,
                quantity=line.quantity,spare_quantity=line.spare_quantity,unit_price=po.unit_price,promised_date=doc.return_date,
                allocation_managed=True,uom_rate_m=line.uom_rate_m,uom_rate_d=line.uom_rate_d,
                notes=f'{doc.number}/{line.line_number} 补货',snapshot=dict(po.snapshot,replenishment=True),created_by=actor)
            line.replacement_line=replacement;line.save(update_fields=['replacement_line'])
            PurchaseOrderAllocation.objects.create(line=replacement, sequence=10, kind='2',
                quantity=line.quantity, inventory_quantity=line.quantity*line.uom_rate_m/line.uom_rate_d,
                notes=f'{doc.number}/{line.line_number} 退货补货', created_by=actor)
    doc.posted=True;doc.status='approved';doc.approved_by=actor;doc.approved_at=timezone.now();doc.version+=1
    doc.save();audit(doc,'approve',actor)


@transaction.atomic
def unapprove_document(doc, actor):
    locked = type(doc).objects.select_for_update().get(pk=doc.pk)
    doc.__dict__.update(locked.__dict__)
    if doc.status != 'approved': raise ValidationError('只有已审核单据可反审核')
    if doc.is_confirmed: raise ValidationError('请先反回单确认')
    if not doc.posting_version: raise ValidationError('历史已审核单据未在本地过账，不能重复冲销期初库存')
    lines=list(doc.lines.select_related('purchase_order_line','replacement_line') if returning(doc) else doc.lines.select_related('purchase_order_line'))
    field='source_purchase_return_line' if returning(doc) else 'source_receipt_line'
    if PayableVoucherLine.objects.filter(**{field+'__in':lines}).exists(): raise ValidationError('单据已有应付凭单引用，不能反审核')
    pos={p.pk:p for p in PurchaseOrderLine.objects.select_for_update().filter(pk__in=[l.purchase_order_line_id for l in lines]).order_by('pk')}
    if not returning(doc):
        event=AuditEvent.objects.filter(model=doc._meta.label_lower,object_id=str(doc.pk),action='approve',
            payload__posting_version=doc.posting_version).first()
        for change in reversed((event.payload if event else {}).get('pending_changes',[])):
            candidate=GoodsReceiptLine.objects.select_for_update().get(pk=change['id'])
            if candidate.pending_quantity != Decimal(change['new']):
                raise ValidationError('冲销来源的待检数量已被后续业务修改，不能反审核')
            candidate.pending_quantity=Decimal(change['old']);candidate.save(update_fields=['pending_quantity'])
    for line in lines:
        if returning(doc) and line.replacement_line_id:
            repl=line.replacement_line
            if repl.receipt_lines.exists() or repl.return_lines.exists(): raise ValidationError('补货行已有收退货引用，不能反审核')
            line.replacement_line=None;line.save(update_fields=['replacement_line']);repl.delete()
        po=pos[line.purchase_order_line_id]
        if not returning(doc) and po.snapshot.get('inspection_required', po.material.inspection_required) and line.pending_quantity != max(line.quantity+line.spare_quantity,ZERO):
            raise ValidationError('收货待检数量已有后续检验或冲销，不能反审核')
        update_totals(po,line,-1,returning(doc))
        if not returning(doc):
            q, s, _, _ = available(po, True)
            if min(q, s) < 0:
                raise ValidationError('后续退货单已占用收货数量，不能反审核')
        if min(po.received_quantity-po.returned_quantity,po.received_spare_quantity-po.returned_spare_quantity)<0:
            raise ValidationError('后续退货已使用收货数量，不能反审核')
        if not returning(doc):
            line.pending_quantity=ZERO;line.accepted_quantity=ZERO
            line.save(update_fields=['pending_quantity','accepted_quantity'])
    movements=StockTransaction.objects.filter(source_model=doc._meta.label_lower,source_id=str(doc.pk),
        source_line_id__in=[f'{l.pk}:{doc.posting_version}' for l in lines]).select_related('material','location','uom','business_uom').order_by('location_id','id')
    for m in movements:
        StockBalance.adjust(material=m.material,location=m.location,uom=m.business_uom or m.uom,
            quantity=-m.business_quantity if m.business_quantity is not None else -m.quantity,movement_type=m.movement_type,
            source_model=doc._meta.label_lower,source_id=doc.pk,source_line_id=m.source_line_id+':reverse',actor=actor,
            batch_number=m.batch_number,effective_date=doc.return_date if returning(doc) else doc.receipt_date,reversal_of=m,
            uom_rate_m=m.uom_rate_m,uom_rate_d=m.uom_rate_d,native_sales_rates=True)
    doc.posted=False;doc.status='draft';doc.approved_by='';doc.approved_at=None;doc.version+=1
    doc.save();audit(doc,'unapprove',actor)
