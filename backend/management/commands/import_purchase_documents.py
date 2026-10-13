"""Import 2026 ordinary purchase receipts and returns from read-only dgyzx1.

The command is deliberately staged: without --commit it only reads the source and
reports missing local dependencies. Historical approved rows are marked as already
posted so the import cannot replay them into the local inventory ledger.
"""
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import (
    ApprovalStatus, GoodsReceipt, GoodsReceiptLine, Location, Material, Partner,
    PurchaseOrder, PurchaseOrderLine, PurchaseReturn, PurchaseReturnLine, Uom,
    UomCategory, ProductCategory, Currency, Department,
)


def text(value):
    return str(value or "").strip()


def key(value):
    return text(value).upper()


def boolish(value):
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'y'}


def as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    return value


def timestamp(value):
    if not value: return None
    if isinstance(value,str): value=datetime.fromisoformat(value)
    return timezone.make_aware(value) if timezone.is_naive(value) else value


class Command(BaseCommand):
    help = "导入 dgyzx1 2026 年普通采购收退货（默认只读预检，--commit 才写入本地）"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--source-file", help="离线 JSON 抓取文件；字段结构与本命令输出一致")
        parser.add_argument("--limit", type=int, default=0, help="每类单据最多读取数量，0 表示全部")

    def rows(self, cursor, sql, params=()):
        result = cursor.execute(sql, params)
        fields = [item[0] for item in result.description]
        return [dict(zip(fields, row)) for row in result.fetchall()]

    def source(self, options):
        if options.get("source_file"):
            with open(options["source_file"], encoding="utf-8") as stream:
                return json.load(stream)
        import pyodbc
        from tools.inspect_source_schema import connection_string
        with pyodbc.connect(connection_string("coerp_dgyzx1"), readonly=True, timeout=10) as connection:
            connection.timeout = 120
            cursor = connection.cursor()
            def related(table, column, values):
                result=[]; values=sorted(set(text(v) for v in values if text(v)))
                for start in range(0,len(values),500):
                    batch=values[start:start+500]
                    result.extend(self.rows(cursor, f"SELECT * FROM dbo.{table} WHERE {column} IN ("+','.join('?' for _ in batch)+')',batch))
                return result
            headers=self.rows(cursor,"SELECT * FROM grn_mstr WHERE grn_date>='20260101' AND grn_date<'20270101' ORDER BY grn_date,grn_grn")
            returns=self.rows(cursor,"SELECT * FROM rts_mstr WHERE rts_date>='20260101' AND rts_date<'20270101' ORDER BY rts_date,rts_rts")
            if options['limit']: headers,returns=headers[:options['limit']],returns[:options['limit']]
            receipt_lines=related('grnd_det','grnd_grn',[r['grn_grn'] for r in headers])
            return_lines=related('rtsd_det','rtsd_rts',[r['rts_rts'] for r in returns])
            orders=related('po_mstr','po_nbr',[r['grnd_po'] for r in receipt_lines]+[r['rtsd_po'] for r in return_lines])
            normal={text(r['po_nbr']) for r in orders if text(r['po_type'])=='' and text(r['po_type2'])=='' and text(r['po_prog_code'])=='PUPOMTA1'}
            excluded=[]
            def select(heads,lines,hkey,lkey,pkey,program):
                grouped=defaultdict(list)
                for row in lines:grouped[text(row[lkey])].append(row)
                kept=[]
                for h in heads:
                    rows=grouped[text(h[hkey])]
                    if text(h.get(hkey.split('_')[0]+'_prog_code'))!=program or not rows or any(text(r[pkey]) not in normal for r in rows):
                        excluded.append({'number':text(h[hkey]),'reason':'非普通采购、空明细或采购来源缺失'})
                    else:kept.append(h)
                ids={text(h[hkey]) for h in kept}
                return kept,[r for r in lines if text(r[lkey]) in ids]
            headers,receipt_lines=select(headers,receipt_lines,'grn_grn','grnd_grn','grnd_po','PUGRMTA1')
            returns,return_lines=select(returns,return_lines,'rts_rts','rtsd_rts','rtsd_po','PURTMTA1')
            used={text(r['grnd_po']) for r in receipt_lines}|{text(r['rtsd_po']) for r in return_lines}
            orders=[r for r in orders if text(r['po_nbr']) in used]
            order_lines=related('pod_det','pod_nbr',used)
            suppliers=related('vd_mstr','vd_addr',[r['po_vend'] for r in orders])
            materials=related('pt_mstr','pt_part',[r['pod_part'] for r in order_lines])
            locations=self.rows(cursor,'SELECT * FROM loc_mstr')
            units=self.rows(cursor,'SELECT * FROM um_mstr')
            categories=self.rows(cursor,'SELECT * FROM pl_mstr')
            currencies=self.rows(cursor,'SELECT * FROM ex_mstr')
            prints=self.rows(cursor,"SELECT print_prog,print_key1,COUNT(*) AS times FROM print_hist WHERE print_prog IN ('PUGRMTA1','PURTMTA1') GROUP BY print_prog,print_key1")
        return dict(receipts=headers,receipt_lines=receipt_lines,returns=returns,return_lines=return_lines,
            orders=orders,order_lines=order_lines,suppliers=suppliers,materials=materials,locations=locations,
            units=units,categories=categories,currencies=currencies,prints=prints,excluded=excluded)

    def dependencies(self, source):
        suppliers = {key(x.code): x for x in Partner.objects.all()}
        materials = {key(x.code): x for x in Material.objects.all()}
        units = {key(x.code): x for x in Uom.objects.all()}
        locations = {key(x.code): x for x in Location.objects.all()}
        orders = {key(x.number): x for x in PurchaseOrder.objects.all()}
        order_lines = {(key(x.order.number), int(x.line_number)): x for x in PurchaseOrderLine.objects.select_related("order")}
        missing = set()
        for row in source["receipts"]:
            if key(row.get("grn_vend")) not in suppliers: missing.add(f"供应商:{row.get('grn_vend')}")
        for row in source["returns"]:
            if key(row.get("rts_vend")) not in suppliers: missing.add(f"供应商:{row.get('rts_vend')}")
        for row in source["receipt_lines"]:
            if key(row.get("grnd_po")) not in orders: missing.add(f"采购单:{row.get('grnd_po')}")
            if (key(row.get("grnd_po")), int(row.get("grnd_po_line") or 0)) not in order_lines: missing.add(f"采购行:{row.get('grnd_po')}/{row.get('grnd_po_line')}")
            if key(row.get("grnd_part")) not in materials: missing.add(f"物料:{row.get('grnd_part')}")
            if key(row.get("grnd_um")) not in units: missing.add(f"单位:{row.get('grnd_um')}")
            if key(row.get("grnd_loc")) not in locations: missing.add(f"库位:{row.get('grnd_loc')}")
        for row in source["return_lines"]:
            if (key(row.get("rtsd_po")), int(row.get("rtsd_po_line") or 0)) not in order_lines: missing.add(f"采购行:{row.get('rtsd_po')}/{row.get('rtsd_po_line')}")
            if key(row.get("rtsd_part")) not in materials: missing.add(f"物料:{row.get('rtsd_part')}")
            if key(row.get("rtsd_um")) not in units: missing.add(f"单位:{row.get('rtsd_um')}")
            if key(row.get("rtsd_loc")) not in locations: missing.add(f"库位:{row.get('rtsd_loc')}")
        return suppliers, materials, units, locations, orders, order_lines, sorted(missing)

    def bootstrap(self, source):
        actor='dgyzx1-receiving-import'
        approved={'status':'approved','created_by':actor}
        unit_category,_=UomCategory.objects.get_or_create(code='SOURCE',defaults={'name':'源计量单位',**approved})
        for row in source['currencies']:
            Currency.objects.get_or_create(code=text(row['ex_curr']),defaults={'name':text(row.get('ex_desc')) or text(row['ex_curr']),**approved})
        units={key(x.code):x for x in Uom.objects.all()}
        for row in source['units']:
            code=text(row['um_um'])
            if key(code) not in units: units[key(code)]=Uom.objects.create(code=code,name=text(row['um_desc']) or code,category=unit_category,**approved)
        locations={key(x.code):x for x in Location.objects.all()}
        for row in source['locations']:
            code=text(row['loc_loc']);site=text(row['loc_site'])
            if key(code) in locations:
                if locations[key(code)].source_site not in ('',site): raise CommandError(f'库位跨站点冲突:{code}')
            else:
                locations[key(code)]=Location.objects.create(code=code,name=text(row['loc_desc']),source_site=site,
                    disabled_for_inventory=boolish(row['loc_disabled']),allow_negative=boolish(row['loc_overissue']),
                    participate_mrp=boolish(row['loc_nettable']),usable=boolish(row['loc_avail']),**approved)
        categories={key(x.code):x for x in ProductCategory.objects.all()}
        for row in source['categories']:
            code=text(row['pl_prod_line'])
            if key(code) not in categories: categories[key(code)]=ProductCategory.objects.create(code=code,name=text(row['pl_desc']),**approved)
        materials={key(x.code):x for x in Material.objects.all()}
        for row in source['materials']:
            code=text(row['pt_part'])
            if key(code) in materials:
                Material.objects.filter(pk=materials[key(code)].pk).update(inspection_required=boolish(row['pt_insp_rqd']))
                continue
            if key(row['pt_um']) not in units or (text(row['pt_loc']) and key(row['pt_loc']) not in locations) or key(row['pt_prod_line']) not in categories:
                raise CommandError(f'物料基础关联缺失:{code} 单位={row["pt_um"]} 库位={row["pt_loc"]} 分类={row["pt_prod_line"]}')
            materials[key(code)]=Material.objects.create(code=code,name=text(row['pt_desc1']),specification=text(row['pt_spec']),
                uom=units[key(row['pt_um'])],default_location=locations.get(key(row['pt_loc'])),category=categories[key(row['pt_prod_line'])],
                inspection_required=boolish(row['pt_insp_rqd']),tax_code=text(row.get('pt_char1')),no_stock_movement=boolish(row['pt_memo_item']),batch_control=boolish(row['pt_lot_serial']),**approved)
        currencies={key(x.code):x for x in Currency.objects.all()}
        suppliers={key(x.code):x for x in Partner.objects.all()}
        for row in source['suppliers']:
            code=text(row['vd_addr'])
            if key(code) in suppliers:
                if suppliers[key(code)].kind not in ('supplier','both'): raise CommandError(f'已有同编码客户与供应商冲突:{code}')
                continue
            suppliers[key(code)]=Partner.objects.create(code=code,name=text(row['vd_name']),short_name=text(row['vd_sort']),kind='supplier',
                currency=currencies.get(key(row['vd_curr'])),payment_method=text(row['vd_cr_terms']),tax_rate=row['vd_vat'],**approved)
        orders={key(x.number):x for x in PurchaseOrder.objects.all()}
        new_orders=set()
        for row in source['orders']:
            code=text(row['po_nbr'])
            if key(code) in orders:
                if orders[key(code)].source_object!='dgyzx1.po_mstr': raise CommandError(f'采购单编号与本地业务冲突:{code}')
                continue
            orders[key(code)]=PurchaseOrder.objects.create(number=code,supplier=suppliers[key(row['po_vend'])],currency=currencies[key(row['po_curr'])],
                department=None,order_date=as_date(row['po_ord_date']),promised_date=as_date(row['po_ord_date']),payment_method=text(row['po_cr_terms']),
                tax_rate=row['po_vat'],exchange_rate=row['po_ex_rate'],buyer=text(row['po_buyer']),site=text(row['po_site']),
                notes=text(row['po_rmks']),source_object='dgyzx1.po_mstr',status='approved' if boolish(row['po_pst']) else 'draft',
                approved_by=text(row['po_pst_by']),approved_at=timestamp(row['po_pst_date']),created_by=text(row['po_crt_by']) or actor)
            new_orders.add(key(code))
        raw_materials={key(r['pt_part']):r for r in source['materials']}
        lines=[]
        for row in source['order_lines']:
            if key(row['pod_nbr']) not in new_orders:continue
            raw=raw_materials[key(row['pod_part'])]
            lines.append(PurchaseOrderLine(order=orders[key(row['pod_nbr'])],line_number=int(row['pod_line']),material=materials[key(row['pod_part'])],
                uom=units[key(row['pod_um'])],quantity=row['pod_qty_ord'],spare_quantity=row['pod_qty_spare'],unit_price=row['pod_pur_cost'],
                promised_date=as_date(row['pod_promise_date'] or row['pod_due_date']) or orders[key(row['pod_nbr'])].order_date,
                due_date=as_date(row['pod_due_date']),received_quantity=row['pod_qty_rcvd'],received_spare_quantity=row['pod_qty_spare_rcvd'],
                returned_quantity=row['pod_qty_rtnd'],returned_spare_quantity=row['pod_qty_spare_rtn'],
                accepted_quantity=row['pod_qty_rcvd_acpt'],accepted_inventory_quantity=row['pod_qty_rcvd_acpt_inv'],
                accepted_spare_quantity=row['pod_qty_rcvd_spare_acpt'],accepted_spare_inventory_quantity=row['pod_qty_rcvd_spare_acpt_inv'],
                over_receipt_quantity=row['pod_qty_ex'],uom_rate_m=row['pod_um_rate_m'],uom_rate_d=row['pod_um_rate_d'],allocation_managed=True,
                line_status=text(row['pod_status']),notes=text(row['pod_rmks']),source_object='dgyzx1.pod_det',
                snapshot={'inspection_required':boolish(raw['pt_insp_rqd']),'source_order':text(row['pod_so_nbr']),
                    'source_order_line':row['pod_so_line'],'replenishment':boolish(row['pod_rtn_flag']),'price_includes_tax':True},
                created_by=text(row['pod_crt_by']) or actor))
        PurchaseOrderLine.objects.bulk_create(lines,batch_size=100)

    @transaction.atomic
    def import_rows(self, source, commit=False):
        normal={key(r['po_nbr']) for r in source['orders'] if text(r['po_type'])=='' and text(r['po_type2'])=='' and text(r['po_prog_code'])=='PUPOMTA1'}
        for heads, lines, prefix, program in ((source['receipts'],source['receipt_lines'],'grn','PUGRMTA1'),(source['returns'],source['return_lines'],'rts','PURTMTA1')):
            if any(text(r[prefix+'_prog_code'])!=program for r in heads): raise CommandError('源文件包含范围外单据')
            if any(key(r[prefix+'d_po']) not in normal for r in lines): raise CommandError('源文件包含范围外采购来源')
        if any(text(r.get('rtsd_src_nbr')) for r in source['return_lines']):
            raise CommandError('源数据出现IQC引用，必须先补齐真实检验关联再导入')
        self.bootstrap(source)
        suppliers, materials, units, locations, orders, order_lines, missing=self.dependencies(source)
        if missing: raise CommandError(f'本地依赖缺失 {len(missing)} 项：'+ '; '.join(missing[:30]))
        prints={(text(r['print_prog']),text(r['print_key1'])):int(r['times']) for r in source.get('prints',[])}
        counts={};errors=[]
        for ret,heads,rawlines in [(False,source['receipts'],source['receipt_lines']),(True,source['returns'],source['return_lines'])]:
            model=PurchaseReturn if ret else GoodsReceipt;line_model=PurchaseReturnLine if ret else GoodsReceiptLine
            h='rts' if ret else 'grn';d='rtsd' if ret else 'grnd';grouped=defaultdict(list)
            for row in rawlines:grouped[text(row[d+'_'+h])].append(row)
            created=skipped=0;new_lines=[]
            existing={obj.number:obj for obj in model.objects.all()}
            for row in heads:
                number=text(row[h+'_'+h]);date_=as_date(row[h+'_date'])
                if not date(2026,1,1)<=date_<date(2027,1,1):raise CommandError('源文件包含非2026年单据')
                if number in existing:
                    if not existing[number].imported: raise CommandError(f'与本地单号冲突:{number}')
                    skipped+=1;continue
                rs=grouped[number]
                if not rs:raise CommandError(f'空明细:{number}')
                supplier=suppliers[key(row[h+'_vend'])];site=text(row[h+'_site'])
                values=dict(number=number,supplier=supplier,site=site,imported=True,posted=boolish(row[h+'_pst']),
                    status='approved' if boolish(row[h+'_pst']) else 'draft',approved_by=text(row[h+'_pst_by']),approved_at=timestamp(row[h+'_pst_date']),
                    created_by=text(row[h+'_crt_by']),updated_by=text(row[h+'_mod_by']),default_print_person=text(row[h+'_char6']),
                    print_count=prints.get(('PURTMTA1' if ret else 'PUGRMTA1',number),0))
                if ret:values.update(return_date=date_,reason=text(row['rts_rmks']),replenishment=boolish(row['rts_replace']),return_location=locations.get(key(row['rts_loc'])))
                else:values.update(receipt_date=date_,notes=text(row['grn_rmks']),supplier_delivery_number=text(row['grn_ps_nbr']),
                    is_confirmed=boolish(row['grn_cfm']),confirmed_by=text(row['grn_cfm_by']),confirmed_at=timestamp(row['grn_cfm_date']),
                    iqc_location=locations.get(key(row['grn_loc_iqc'])),raw_location=locations.get(key(row['grn_loc_raw'])),source_object='dgyzx1.grn_mstr')
                ids={order_lines[(key(r[d+'_po']),int(r[d+'_po_line']))].order_id for r in rs}
                values['purchase_order_id']=next(iter(ids)) if len(ids)==1 else None
                doc=model.objects.create(**values)
                model.objects.filter(pk=doc.pk).update(created_at=timestamp(row[h+'_crt_date']) or doc.created_at,updated_at=timestamp(row[h+'_mod_date']) or doc.updated_at)
                for r in rs:
                    po=order_lines[(key(r[d+'_po']),int(r[d+'_po_line']))];loc=locations[key(r[d+'_loc'])]
                    if po.order.supplier_id!=supplier.pk or po.order.site!=site or (loc.source_site and loc.source_site!=site):raise CommandError(f'供应商/站点不一致:{number}/{r[d+"_line"]}')
                    material=materials[key(r[d+'_part'])];unit=units[key(r[d+'_um'])]
                    if material.pk!=po.material_id or unit.pk!=po.uom_id:raise CommandError(f'采购物料/单位不一致:{number}/{r[d+"_line"]}')
                    fields=dict(line_number=int(r[d+'_line']),purchase_order_line=po,material=material,uom=unit,
                        quantity=r[d+('_qty' if ret else '_qty_rcvd')],spare_quantity=r[d+('_qty_spare' if ret else '_qty_spare_rcvd')],
                        uom_rate_m=r[d+'_um_rate_m'],uom_rate_d=r[d+'_um_rate_d'],batch_number=text(r[d+'_lot']))
                    if ret:fields.update(purchase_return=doc,source_location=loc,reason=text(r['rtsd_rmks']),iqc_number=text(r['rtsd_src_nbr']),iqc_line=int(r['rtsd_src_line']))
                    else:fields.update(receipt=doc,location=loc,notes=text(r['grnd_rmks']),pending_quantity=r['grnd_qty_pending'],
                        accepted_quantity=0 if po.snapshot.get('inspection_required') else r['grnd_qty_rcvd'],source_object='dgyzx1.grnd_det')
                    new_lines.append(line_model(**fields))
                created+=1
            line_model.objects.bulk_create(new_lines,batch_size=100)
            counts[model._meta.model_name]={'created':created,'skipped':skipped,'lines':len(new_lines)}
        if not commit:transaction.set_rollback(True)
        return counts

    def handle(self, *args, **options):
        if options['limit']<0:raise CommandError('limit不能为负')
        source=self.source(options)
        result={'source':'coerp_dgyzx1','year':2026,'receipts':len(source['receipts']),'returns':len(source['returns']),
            'receipt_lines':len(source['receipt_lines']),'return_lines':len(source['return_lines']),'excluded':len(source.get('excluded',[])),
            'committed':False}
        from pathlib import Path
        out=Path('outputs/purchase-receipt-return-import');out.mkdir(parents=True,exist_ok=True)
        if not options.get('source_file'):
            (out/'source.json').write_text(json.dumps(source,ensure_ascii=False,default=str),encoding='utf-8')
        from backend.models import StockBalance, StockTransaction
        def ledger_signature():
            rows=list(StockBalance.objects.order_by('pk').values_list('pk','material_id','location_id','batch_number','quantity','reserved_quantity'))
            return {'balances':len(rows),'transactions':StockTransaction.objects.count(),
                'sha256':hashlib.sha256(json.dumps(rows,default=str).encode()).hexdigest()}
        result['inventory_before']=ledger_signature()
        result['imported']=self.import_rows(source,options['commit']);result['committed']=options['commit']
        result['inventory_after']=ledger_signature()
        result['inventory_unchanged']=result['inventory_before']==result['inventory_after']
        result['source_totals']={name:{field:str(sum((Decimal(str(r[field])) for r in source[name]),Decimal(0))) for field in fields}
            for name,fields in [('receipt_lines',['grnd_qty_rcvd','grnd_qty_spare_rcvd']),('return_lines',['rtsd_qty','rtsd_qty_spare'])]}
        result['cross_year_orders']=sum(as_date(r['po_ord_date']).year!=2026 for r in source['orders'])
        result['historical_confirmed_without_uploaded_attachment']=sum(boolish(r['grn_cfm']) for r in source['receipts'])
        result['iqc_references']=0
        result['excluded_documents']=source.get('excluded',[])
        (out/('import-report.json' if options['commit'] else 'preflight-report.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
        self.stdout.write(json.dumps({k:v for k,v in result.items() if k != "excluded_documents"},ensure_ascii=False,default=str))
