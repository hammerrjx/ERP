"""Purchase workspace. Source contracts: PUPRMT02_qry, insert_req_pod_det, tri_podr_req."""
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_CEILING
import hashlib
import json

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone

from backend.models import (PurchaseOrder, PurchaseOrderLine, PurchaseOrderAllocation,
    PurchaseGeneration, PurchaseRequisitionLine, Partner, Currency, Department, Material,
    SupplierQuote, AuditEvent)
from backend.currencies import exchange_rate


def number(value, label='数量', positive=False):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or n < 0 or (positive and n == 0) or n >= Decimal('10000000000'):
            raise ValueError()
        if n != n.quantize(Decimal('.00000001')):
            raise ValueError()
        return n.normalize()
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f'{label}必须为有效的非负数字（最多8位小数）')


def day(value, default=None):
    try:
        return date.fromisoformat(str(value)) if value else default or timezone.localdate()
    except ValueError:
        raise ValidationError('日期格式必须为YYYY-MM-DD')


def text(value):
    if value is None: return ''
    return format(value, 'f') if isinstance(value, Decimal) else str(value)


def audit(obj, action, actor, payload=None):
    AuditEvent.objects.create(model=obj._meta.label_lower, object_id=str(obj.pk),
        action=action, actor=actor, payload=payload or {})


def material_values(material, req=None):
    old = req.material_snapshot if req else {}
    return dict(inspection_required=material.inspection_required,material_code=old.get('pt_part') or material.code,
        material_name=old.get('pt_desc1') or material.name,
        english_name=old.get('pt_desc2') or material.english_name,
        specification=old.get('pt_spec') or material.specification,
        tax_code=material.tax_code, tax_name=material.tax_name, invoice_name=material.invoice_name,
        inventory_account=material.category.inventory_account, inventory_account_name='',
        inventory_uom=material.uom.name, category=old.get('pt_prod_line') or material.category.code)


def source_values(req):
    s = req.source_snapshot or {}
    values = dict(requisition_number=req.requisition.number, requisition_line_number=req.line_number,
        source_profile=req.requisition.source_profile, site=req.requisition.site,
        source_order=s.get('req_wo_nbr') or s.get('req_so_nbr') or '',
        source_order_line=s.get('req_wo_lot') or s.get('req_so_line') or '',
        parent_code='', parent_name='',
        parent_specification='', original_quantity='',
        customer_material=s.get('cp_cust_part', ''))
    so = req.source_sales_order_line
    if so:
        values.update(source_order=so.order.number, source_order_line=so.line_number,
            parent_code=so.material.code, parent_name=so.material.name,
            parent_specification=so.material.specification, original_quantity=text(so.quantity))
        values['customer_material'] = so.customer_material.customer_code if so.customer_material_id else ''
    if hasattr(req, 'purchase_source'):
        values.update({k: req.purchase_source[k] for k in ('parent_code','parent_name','parent_specification','original_quantity','customer_material','business_type')})
    # Imported req_mstr includes these source fields; reqd_det remains a separate drill-down.
    return values


def resolve(req, supplier_id=None, quantity=None, at=None, lowest=False):
    material = req.material
    at = at or timezone.localdate()
    quantity = quantity if quantity is not None else req.requested_qty - req.converted_qty
    quotes = SupplierQuote.objects.filter(material=material, quote_type='purchase', status='approved',
        is_confirmed=True, is_ratified=True, effective_date__lte=at).filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gte=at)).select_related('supplier__currency', 'currency', 'purchase_uom')
    if supplier_id: quotes = quotes.filter(supplier_id=supplier_id)
    elif not lowest and getattr(req, 'purchase_price_clue', '1') == '2': quotes = quotes.filter(supplier_id=material.default_supplier_id)
    choices = []
    for q in quotes:
        if q.supplier.status != 'approved': continue
        if q.uom_rate_m <= 0 or q.uom_rate_d <= 0: raise ValidationError('报价单位换算分子和分母必须大于0')
        qty = quantity * q.uom_rate_d / q.uom_rate_m
        price, tier = q.price_for(qty)
        if not q.tax_included: price *= 1 + q.tax_rate / 100
        choices.append((price / (1 + q.tax_rate / 100) * exchange_rate(q.currency, at) * q.uom_rate_d / q.uom_rate_m, q, price, tier))
    chosen = min(choices, key=lambda c: (c[0], -c[1].pk)) if choices else None
    supplier = Partner.objects.filter(pk=supplier_id or material.default_supplier_id,
        kind__in=['supplier', 'both'], status='approved').select_related('currency').first()
    if chosen: _, quote, price, tier = chosen; supplier = quote.supplier
    else: quote, price, tier = None, Decimal(0), None
    return supplier, quote, price, tier


def candidates(params):
    qs = PurchaseRequisitionLine.objects.filter(requisition__requisition_type='P',
        requisition__status='approved', line_status='', requested_qty__gt=F('converted_qty'))
    qs = qs.select_related('requisition', 'uom', 'material__category', 'material__uom', 'material__default_supplier',
        'source_sales_order_line__order', 'source_sales_order_line__material')
    if params.get('site'): qs = qs.filter(requisition__site=params['site'])
    if params.get('ids'): qs = qs.filter(pk__in=[int(v) for v in params['ids'].split(',')])
    ranges = {'number':'requisition__number', 'part':'material_snapshot__pt_part',
        'category':'material_snapshot__pt_prod_line', 'request_date':'requisition__request_date', 'needed_date':'needed_date'}
    for name, field in ranges.items():
        for end, op in [('from','gte'), ('to','lte')]:
            if params.get(f'{name}_{end}'): qs = qs.filter(**{field+'__'+op:params[f'{name}_{end}']})
    if params.get('number'): qs = qs.filter(requisition__number=params['number'])
    if params.get('buyer'): qs = qs.filter(material__buyer=params['buyer'])
    if params.get('q'): qs = qs.filter(Q(requisition__number__icontains=params['q']) | Q(material_snapshot__pt_part__icontains=params['q']))
    page = max(1, int(params.get('page') or 1)); count = qs.count()
    rows = []
    page_rows=list(qs.order_by('requisition__number','line_number')[(page-1)*50:page*50])
    from backend.purchase_source import enrich_requests
    enrich_requests(page_rows)
    for req in page_rows:
        remaining = req.requested_qty-req.converted_qty
        m = req.material
        row = dict(id=req.pk, requisition_id=req.requisition_id, number=req.requisition.number, line_number=req.line_number,
            request_date=text(req.requisition.request_date), needed_date=text(req.needed_date), requester=req.requisition.requester,
            requested_qty=text(req.requested_qty), converted_qty=text(req.converted_qty), remaining=text(remaining),
            quantity=text(remaining), department=req.requisition.department_id, material=req.material_id,
            uom_name=req.uom.name if req.uom else req.material_snapshot.get('pt_um',''),
            material_code=req.material_snapshot.get('pt_part',''), material_name=req.material_snapshot.get('pt_desc1',''),
            reason='', supplier=None, unit_price='', original_price='0')
        if not m: row['reason']='物料尚未映射本地主档'
        elif m.status != 'approved' or not m.active: row['reason']='物料未审核或已停用'
        else:
            at=day(params.get('order_date'))
            supplier, quote, price, tier = resolve(req,params.get('supplier'),at=at)
            if quote and supplier.currency_id:
                price=price*exchange_rate(quote.currency,at)/exchange_rate(supplier.currency,at)
            row.update(material_values(m, req), **source_values(req))
            row['supplier_material']=getattr(req,'purchase_supplier_materials',{}).get(supplier.code,'') if supplier else ''
            row.update(supplier=supplier.pk if supplier else None, supplier_code=supplier.code if supplier else '',
                supplier_name=supplier.short_name or supplier.name if supplier else '',
                currency=supplier.currency_id if supplier else None, currency_code=supplier.currency.code if supplier and supplier.currency_id else '',
                tax_rate=text(quote.tax_rate if quote else supplier.tax_rate if supplier else 0),
                payment_method=supplier.payment_method if supplier else '',
                department_name=req.requisition.department.name if req.requisition.department_id else '',
                purchase_uom_name=(quote.purchase_uom or m.uom).name if quote else m.uom.name,
                uom_rate_m=text(quote.uom_rate_m if quote else 1),uom_rate_d=text(quote.uom_rate_d if quote else 1),
                original_price=text(price), min_purchase_qty=text(quote.min_purchase_qty if quote else m.min_purchase_qty),
                min_pack_qty=text(quote.min_pack_qty if quote else m.min_pack_qty))
        rows.append(row)
    return dict(count=count, page=page, page_size=50, results=rows)


def prepare(data, lock=False):
    if data.get('document_type', 'standard') != 'standard':
        raise ValidationError('当前转单支持标准采购单')
    selections = data.get('lines')
    if not isinstance(selections, list) or not selections or len(selections)>5000:
        raise ValidationError('请选择1至5000条请购明细')
    if any(not isinstance(x,dict) for x in selections): raise ValidationError('请购明细格式无效')
    ids=[x.get('line_id') for x in selections]
    if len(set(ids)) != len(ids) or any(not isinstance(i,int) for i in ids):
        raise ValidationError('请购明细ID无效或重复')
    qs=PurchaseRequisitionLine.objects.select_related('requisition','material__uom','material__category',
        'source_sales_order_line__order','source_sales_order_line__material').filter(pk__in=ids).order_by('pk')
    if lock: qs=qs.select_for_update()
    requests={r.pk:r for r in qs}
    if len(requests)!=len(ids): raise ValidationError('请购明细已不存在')
    from backend.purchase_source import enrich_requests
    enrich_requests(list(requests.values()))
    grouping=str(data.get('grouping','3'))
    if grouping not in ('1','2','3'): raise ValidationError('汇总方式无效')
    at=day(data.get('order_date')); groups={}; fingerprints=[]
    for item in selections:
        req=requests[item['line_id']]; m=req.material
        if req.requisition.requisition_type!='P' or req.requisition.status!='approved' or req.line_status:
            raise ValidationError(f'{req.requisition.number}/{req.line_number}不是已审核的正常P采购行')
        if not m or m.status!='approved' or not m.active: raise ValidationError('物料未映射、未审核或停用')
        qty=number(item.get('quantity',req.requested_qty-req.converted_qty),positive=True)
        if qty>req.requested_qty-req.converted_qty: raise ValidationError(f'{req.requisition.number}/{req.line_number}超出剩余请购数量')
        supplier, quote, price, tier=resolve(req,item.get('supplier') or data.get('supplier'),qty,at)
        if not supplier or not supplier.currency_id: raise ValidationError('请选择已审核且有币种的供应商')
        department=Department.objects.filter(pk=item.get('department') or data.get('department') or req.requisition.department_id).first()
        if not department: raise ValidationError('请指定采购部门')
        currency=Currency.objects.filter(pk=item.get('currency') or supplier.currency_id).first()
        if not currency: raise ValidationError('币种不存在')
        tax=number(item.get('tax_rate',quote.tax_rate if quote else supplier.tax_rate),'税率')
        if tax>100: raise ValidationError('税率不能超过100%')
        payment=item.get('payment_method') or supplier.payment_method
        if not payment: raise ValidationError('供应商未维护支付方式，请补齐')
        rate_m=quote.uom_rate_m if quote else Decimal(1); rate_d=quote.uom_rate_d if quote else Decimal(1)
        if rate_m <= 0 or rate_d <= 0: raise ValidationError('报价单位换算分子和分母必须大于0')
        uom=quote.purchase_uom or m.uom if quote else m.uom
        original=price
        if quote:
            price=price/(1+quote.tax_rate/100)*(1+tax/100)*exchange_rate(quote.currency,at)/exchange_rate(currency,at)
        manual=item.get('unit_price') not in (None,'')
        if not quote and not manual: raise ValidationError(f'{m.code}没有有效报价，请明确填写本次单价')
        if manual: price=number(item['unit_price'],'单价')
        needed=day(item.get('needed_date'),req.needed_date or at)
        key=(req.requisition.site,supplier.pk,currency.pk,text(tax),department.pk,payment,data.get('document_type','standard'))
        group=groups.setdefault(key,dict(site=key[0],supplier=supplier.pk,supplier_code=supplier.code,supplier_name=supplier.name,
            currency=currency.pk,currency_code=currency.code,tax_rate=text(tax),department=department.pk,
            department_name=department.name,payment_method=payment,document_type=key[-1],order_date=text(at),lines={}))
        group['high_price_permission']=getattr(req,'purchase_high_price_permission','')
        line_key=(m.pk,uom.pk,text(rate_m),text(rate_d),text(price),needed if grouping=='3' else req.pk if grouping=='1' else '')
        row=group['lines'].setdefault(line_key,dict(material=m.pk,uom=uom.pk,uom_name=uom.name,quantity=Decimal(0),
            uom_rate_m=text(rate_m),uom_rate_d=text(rate_d),unit_price=text(price),original_price=text(original),
            needed_date=text(needed),due_date=text(needed),promised_date=text(needed),snapshot=material_values(m,req),
            quote_id=quote.pk if quote else None,manual_price=manual,min_purchase_qty=text(quote.min_purchase_qty if quote else m.min_purchase_qty),
            min_pack_qty=text(quote.min_pack_qty if quote else m.min_pack_qty),allocations=[]))
        row['snapshot']['supplier_material']=getattr(req,'purchase_supplier_materials',{}).get(supplier.code,'')
        row['snapshot']['price_includes_tax']=True
        row['snapshot']['inventory_account_name']=getattr(req,'purchase_inventory_account_name','')
        row['supplier_backup_ratio']=text(supplier.backup_ratio)
        row['supplier_over_receipt_ratio']=text(supplier.over_receipt_ratio)
        row['issue_batch']=str(req.material_snapshot.get('pt_iss_batch', m.min_issue_qty))
        row['issue_rate_m']=str(req.material_snapshot.get('pt_um_isu_m') or 1)
        row['issue_rate_d']=str(req.material_snapshot.get('pt_um_isu_d') or 1)
        pur_qty=qty*rate_d/rate_m
        if pur_qty != pur_qty.quantize(Decimal('.000001')):
            raise ValidationError('换算后的采购数量超过6位小数，请调整数量或采购单位')
        row['quantity']+=pur_qty
        row['allocations'].append(dict(kind='1',requisition_line=req.pk,quantity=text(pur_qty),inventory_quantity=text(qty),
            snapshot=source_values(req),notes=req.notes))
        row['needed_date']=min(row['needed_date'],text(needed)); row['due_date']=row['needed_date']
        fingerprints.append([req.pk,text(req.requested_qty),text(req.converted_qty),req.requisition.version,
            quote.pk if quote else None,text(quote.updated_at) if quote else '',text(supplier.updated_at)])
    result=[]
    for group in groups.values():
        group['lines']=list(group['lines'].values())
        for row in group['lines']:
            qty=row['quantity']; target=qty
            if data.get('consider_pack',True):
                # Minimum and pack quantities are stock-unit amounts in PUPRMT02_qry.
                stock=qty*Decimal(row['uom_rate_m'])/Decimal(row['uom_rate_d'])
                stock=max(stock,Decimal(row['min_purchase_qty']))
                pack=Decimal(row['min_pack_qty'])
                if pack: stock=(stock/pack).to_integral_value(rounding=ROUND_CEILING)*pack
                target=stock*Decimal(row['uom_rate_d'])/Decimal(row['uom_rate_m'])
                if target != target.quantize(Decimal('.000001')):
                    raise ValidationError('包装换算后的采购数量超过6位小数，请调整采购单位')
            extra=target-qty
            if extra: row['allocations'].append(dict(kind='2',requisition_line=None,quantity=text(extra),
                inventory_quantity=text(extra*Decimal(row['uom_rate_m'])/Decimal(row['uom_rate_d'])),snapshot={},notes='最小采购/包装取整'))
            row['quantity']=text(target); row['extra_quantity']=text(extra)
            for name,ratio in [('spare_quantity','supplier_backup_ratio'),('over_receipt_quantity','supplier_over_receipt_ratio')]:
                value=target*Decimal(row[ratio])/100
                batch=Decimal(row['issue_batch']); im=Decimal(row['issue_rate_m']); id_=Decimal(row['issue_rate_d'])
                if im<=0 or id_<=0: raise ValidationError('发出单位换算分子和分母必须大于0')
                scale=Decimal(row['uom_rate_m'])/Decimal(row['uom_rate_d'])*im/id_
                if batch: value=(value*scale/batch).to_integral_value(rounding=ROUND_CEILING)*batch/scale
                row[name]=text(value.quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP))
            if row['quote_id'] and not row['manual_price']:
                q=SupplierQuote.objects.get(pk=row['quote_id']); price,_=q.price_for(target)
                if not q.tax_included: price*=1+q.tax_rate/100
                c=Currency.objects.get(pk=group['currency'])
                row['unit_price']=text((price/(1+q.tax_rate/100)*(1+Decimal(group['tax_rate'])/100)*exchange_rate(q.currency,at)/exchange_rate(c,at)).quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP))
            row['unit_price']=text(Decimal(row['unit_price']).quantize(Decimal('.000001'),rounding=ROUND_HALF_UP))
            stock_qty=target*Decimal(row['uom_rate_m'])/Decimal(row['uom_rate_d'])
            _,lowest_quote,lowest_price,_=resolve(requests[row['allocations'][0]['requisition_line']],quantity=stock_qty,at=at,lowest=True)
            if lowest_quote:
                lowest_price=lowest_price/(1+lowest_quote.tax_rate/100)*(1+Decimal(group['tax_rate'])/100)
                lowest_price*=exchange_rate(lowest_quote.currency,at)/exchange_rate(Currency.objects.get(pk=group['currency']),at)
                lowest_price*=lowest_quote.uom_rate_d/lowest_quote.uom_rate_m*Decimal(row['uom_rate_m'])/Decimal(row['uom_rate_d'])
            row['minimum_price']=text(lowest_price.quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP))
            row['amount']=text((target*Decimal(row['unit_price'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
        try: limit=int(data.get('line_limit') or 0)
        except (TypeError,ValueError): raise ValidationError('采购单行数必须为整数')
        if limit<0 or limit>5000: raise ValidationError('采购单行数范围为0至5000；0不限制')
        chunk=limit or len(group['lines'])
        result.extend(dict(group,lines=group['lines'][i:i+chunk]) for i in range(0,len(group['lines']),chunk))
    digest=hashlib.sha256(json.dumps([result,fingerprints],sort_keys=True,default=str).encode()).hexdigest()
    return dict(groups=result,fingerprint=digest)


@transaction.atomic
def generate(data,actor):
    key=data.get('idempotency_key')
    if not isinstance(key,str) or not 8<=len(key)<=80: raise ValidationError('生成请求缺少有效幂等标识')
    request_hash=hashlib.sha256(json.dumps({k:v for k,v in data.items() if k!='idempotency_key'},sort_keys=True).encode()).hexdigest()
    previous=PurchaseGeneration.objects.select_for_update().filter(key=key).first()
    if previous:
        if previous.actor!=actor or previous.request_hash!=request_hash: raise ValidationError('该生成请求标识已用于其他内容')
        return [order_data(o) for o in PurchaseOrder.objects.filter(pk__in=previous.order_ids)],True
    # Unique key reservation is inside the same transaction; failed generation leaves no reservation.
    generation=PurchaseGeneration.objects.create(key=key,actor=actor,request_hash=request_hash)
    preview=prepare(data,lock=True)
    if data.get('fingerprint')!=preview['fingerprint']: raise ValidationError('来源数量或报价已变化，请重新提交预览')
    manual_number=data.get('number','').strip()
    if data.get('auto_number',True) is False and (not manual_number or len(preview['groups'])!=1):
        raise ValidationError('手工编号必须填写单号且只能生成一张采购单')
    orders=[]
    for g in preview['groups']:
        supplier=Partner.objects.get(pk=g['supplier']);currency=Currency.objects.get(pk=g['currency'])
        order=PurchaseOrder(supplier=supplier,currency=currency,department_id=g['department'],site=g['site'],
            document_type=g['document_type'],order_date=g['order_date'],buyer=actor,payment_method=g['payment_method'],
            tax_rate=Decimal(g['tax_rate']).normalize(),promised_date=max(r['promised_date'] for r in g['lines']),created_by=actor,
            exchange_rate=exchange_rate(currency,day(g['order_date'])))
        order.high_price_permission=str(g.get('high_price_permission',''))
        if not data.get('auto_number',True): order.number=manual_number
        order.full_clean();order.save()
        for i,r in enumerate(g['lines'],1):
            line=PurchaseOrderLine(order=order,line_number=i*10,material_id=r['material'],uom_id=r['uom'],
                quantity=Decimal(str(r['quantity'])).normalize(),unit_price=Decimal(str(r['unit_price'])).normalize(),promised_date=r['promised_date'],needed_date=r['needed_date'],
                due_date=r['due_date'],uom_rate_m=r['uom_rate_m'],uom_rate_d=r['uom_rate_d'],extra_quantity=r['extra_quantity'],
                spare_quantity=r['spare_quantity'],over_receipt_quantity=r['over_receipt_quantity'],
                snapshot=r['snapshot'],allocation_managed=True,created_by=actor,updated_by=actor,
                source_requisition_line_id=r['allocations'][0]['requisition_line'],source_supplier_quote_id=r['quote_id'])
            # Preserve existing six-decimal purchase fields for downstream compatibility.
            line.minimum_price=Decimal(r['minimum_price'])
            line.full_clean();line.save()
            for j,a in enumerate(r['allocations'],1):
                alloc=PurchaseOrderAllocation(line=line,sequence=j*10,created_by=actor,updated_by=actor,
                    **{k:v for k,v in a.items() if k!='requisition_line'},requisition_line_id=a['requisition_line'])
                alloc.full_clean();alloc.save()
        audit(order,'convert_from_requisition',actor,{'request':key});orders.append(order)
    generation.order_ids=[o.pk for o in orders];generation.save(update_fields=['order_ids'])
    return [order_data(o) for o in orders],False


def allocation_data(a):
    req=a.requisition_line
    return dict(a.snapshot,id=a.pk,sequence=a.sequence,kind=a.kind,type_label='1.请购单' if a.kind=='1' else '2.额外采购',
        requisition_line=a.requisition_line_id,quantity=text(a.quantity),inventory_quantity=text(a.inventory_quantity),
        notes=a.notes,created_by=a.created_by,created_at=text(a.created_at),updated_by=a.updated_by,
        updated_at=text(a.updated_at),modification_count=a.modification_count,
        requisition_number=req.requisition.number if req else '',requisition_line_number=req.line_number if req else '')


SUM_FIELDS=('quantity','spare_quantity','over_receipt_quantity','extra_quantity','amount','untaxed_amount',
    'received_quantity','accepted_quantity','returned_quantity')


def line_data(line):
    values=dict(material_values(line.material),**line.snapshot)
    for field in line._meta.fields:
        if not field.is_relation and field.name!='snapshot': values[field.name]=text(getattr(line,field.name))
    allocs=[allocation_data(a) for a in line.allocations.select_related('requisition_line__requisition').all()]
    if not allocs and line.source_requisition_line_id and not line.allocation_managed:
        req=line.source_requisition_line
        allocs=[dict(source_values(req),id=None,sequence=10,kind='1',type_label='1.请购单',requisition_line=req.pk,
            quantity=text(line.quantity),inventory_quantity=text(line.quantity*line.uom_rate_m/line.uom_rate_d),notes=req.notes)]
    source=next((a for a in allocs if a['kind']=='1'),{})
    gross_price=line.unit_price if line.snapshot.get('price_includes_tax') else line.unit_price*(1+line.order.tax_rate/100)
    amount=(line.quantity*gross_price).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    raw=(gross_price/(1+line.order.tax_rate/100)).quantize(Decimal('.0001'),rounding=ROUND_HALF_UP)
    values.update(id=line.pk,line_number=line.line_number,material=line.material_id,uom=line.uom_id,uom_name=line.uom.name,
        source_requisition_number=source.get('requisition_number',''),source_requisition_line_number=source.get('requisition_line_number',''),
        original_order=source.get('source_order',''),original_order_line=source.get('source_order_line',''),
        parent_code=source.get('parent_code',''),parent_name=source.get('parent_name',''),
        original_quantity=source.get('original_quantity',''),customer_material=source.get('customer_material',''),
        unit_price=text(gross_price.quantize(Decimal('.000001'),rounding=ROUND_HALF_UP)),amount=text(amount),untaxed_price=text(raw.quantize(Decimal('.0001'),rounding=ROUND_HALF_UP)),
        untaxed_amount=text((line.quantity*raw).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)),
        allocations=allocs,allocation_managed=line.allocation_managed,return_replacement=bool(line.order.source_purchase_return_id or line.snapshot.get('replenishment')),
        business_type=source.get('business_type',''))
    return values


def order_data(order):
    values={f.name:(getattr(order,f.attname) if f.is_relation else text(getattr(order,f.name))) for f in order._meta.fields}
    lines=[line_data(l) for l in order.lines.select_related('material__uom','material__category','uom','order',
        'source_requisition_line__requisition').prefetch_related('allocations__requisition_line__requisition')]
    values.update(id=order.pk,version=order.version,is_confirmed=order.is_confirmed,supplier_name=order.supplier.name,
        supplier_code=order.supplier.code,currency_code=order.currency.code,department_name=order.department.name if order.department_id else "",lines=lines,
        totals={key:text(sum((Decimal(l.get(key) or 0) for l in lines),Decimal(0))) for key in SUM_FIELDS})
    return values


def editable(order):
    if order.status not in ('draft','rejected'): raise ValidationError('请先反审核再修改采购单')
    if order.is_confirmed or order.delivery_approved_at: raise ValidationError('请先撤销总监确认/交期审核')
    if order.lines.filter(Q(receipt_lines__isnull=False)|Q(return_lines__isnull=False)).exists(): raise ValidationError('采购单已有收货或退货引用，不可修改或删除')


@transaction.atomic
def save_order(data,actor,pk=None):
    order=PurchaseOrder.objects.select_for_update().get(pk=pk) if pk else PurchaseOrder(created_by=actor)
    if pk:
        editable(order)
        if int(data.get('version',0))!=order.version: raise ValidationError('采购单已被其他人修改，请重新查询')
    for key in ('supplier_id','currency_id','department_id'):
        if key[:-3] in data: setattr(order,key,data[key[:-3]])
    for key in ('buyer','payment_method','notes','shipping_address','billing_address','revision_label','terms','document_type'):
        if key in data: setattr(order,key,str(data[key]))
    order.order_date=day(data.get('order_date'),order.order_date)
    order.promised_date=day(data.get('promised_date'),getattr(order,'promised_date',None))
    order.tax_rate=number(data.get('tax_rate',order.tax_rate or 0),'税率').normalize()
    if order.document_type != 'standard': raise ValidationError('当前支持标准采购单')
    if order.tax_rate>100: raise ValidationError('税率不能超过100%')
    if not order.payment_method: raise ValidationError('支付方式不能为空')
    order.exchange_rate=exchange_rate(order.currency,order.order_date)
    order.version+=1 if pk else 0;order.updated_by=actor
    order.full_clean();order.save()
    incoming=data.get('lines')
    if not isinstance(incoming,list) or not incoming: raise ValidationError('采购单至少需要一条明细')
    old={l.pk:l for l in order.lines.select_for_update()};seen=set();numbers=set()
    for i,row in enumerate(incoming,1):
        line=old.get(row.get('id'))
        if row.get('id') and not line: raise ValidationError('明细不属于当前采购单')
        if line and line.pk in seen: raise ValidationError('明细重复')
        new=line is None
        if new:
            m=Material.objects.select_related('uom','category').get(pk=row.get('material'))
            if m.status!='approved' or not m.active: raise ValidationError('物料未审核或已停用')
            line=PurchaseOrderLine(order=order,material=m,uom=m.uom,line_number=int(row.get('line_number') or i*10),
                snapshot=dict(material_values(m),price_includes_tax=True),created_by=actor,allocation_managed=True)
        elif row.get('material',line.material_id)!=line.material_id: raise ValidationError('已保存行物料不可替换，请删行后增加')
        if line.line_number in numbers: raise ValidationError('行号重复')
        numbers.add(line.line_number)
        old_qty=line.quantity
        line.quantity=number(row.get('quantity',line.quantity),'订购数量',True)
        line.unit_price=number(row.get('unit_price',line.unit_price),'含税单价')
        line.snapshot=dict(line.snapshot,price_includes_tax=True)
        if any(v != v.quantize(Decimal('.000001')) for v in (line.quantity,line.unit_price)):
            raise ValidationError('采购数量及单价最多6位小数')
        for key in ('extra_quantity','spare_quantity','over_receipt_quantity','copper_price'):
            setattr(line,key,number(row.get(key,getattr(line,key)),key))
        if line.extra_quantity>line.quantity: raise ValidationError('额外采购不能大于订购数量')
        line.promised_date=day(row.get('promised_date'),order.promised_date)
        line.needed_date=day(row.get('needed_date'),line.needed_date or order.order_date)
        line.due_date=day(row.get('due_date'),line.due_date or line.needed_date)
        line.notes=str(row.get('notes',line.notes));line.updated_by=actor;line.updated_at=timezone.now()
        line.modification_count+=0 if new else 1
        # A manually changed price is authoritative; a quote is a provenance snapshot, not an overwrite command.
        if line.source_supplier_quote_id and line.source_supplier_quote.supplier_id!=order.supplier_id:
            line.source_supplier_quote=None;line.source_supplier_quote_line=None
        line.full_clean();line.save();seen.add(line.pk)
        allocs=list(line.allocations.select_for_update().all())
        supplied=row.get('allocations')
        if allocs and line.allocation_managed:
            values=supplied or []
            if not isinstance(values,list) or any(not isinstance(a,dict) for a in values): raise ValidationError('来源分配格式无效')
            supplied={a['id']:a for a in values if a.get('id')}
            if len(supplied)!=len(values) or set(supplied)-{a.pk for a in allocs}: raise ValidationError('来源分配重复或不属于当前采购行')
            for a in allocs:
                value=supplied.get(a.pk,{})
                if value:
                    a.quantity=number(value.get('quantity',a.quantity),'来源分配数量')
                    a.inventory_quantity=(a.quantity*line.uom_rate_m/line.uom_rate_d).quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP)
                    a.updated_by=actor;a.updated_at=timezone.now();a.modification_count+=1;a.save()
            if sum((a.quantity for a in allocs),Decimal(0))!=line.quantity:
                raise ValidationError('订购数量必须等于下方来源分配合计，请同时调整分配数量')
            if sum((a.quantity for a in allocs if a.kind=='2'),Decimal(0))!=line.extra_quantity:
                raise ValidationError('额外采购量必须与类型2来源分配一致')
    for id,line in old.items():
        if id not in seen: line.delete()
    audit(order,'workspace_save',actor)
    return order_data(order)
