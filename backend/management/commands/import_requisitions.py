"""Import a captured 2026 dgyzx1 requisition set without posting inventory."""
import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from backend.models import PurchaseRequisition, PurchaseRequisitionLine, PurchaseRequisitionSource, Material, Uom, AuditEvent
from backend.live_inventory import live_batch


def day(value):
    return str(value)[:10] if value else None


def moment(value):
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    return timezone.make_aware(dt) if timezone.is_naive(dt) else dt


class Command(BaseCommand):
    help = '预检/导入dgyzx1的2026年请购；使用只读抓取文件，保留全部原始字段'

    def add_arguments(self, parser):
        parser.add_argument('--capture', required=True)
        parser.add_argument('--apply', action='store_true')

    @transaction.atomic
    def handle(self, *args, **opts):
        capture = json.loads(Path(opts['capture']).read_text(encoding='utf-8'))
        headers, lines, sources = (capture[k] for k in ('headers','lines','sources'))
        if any(not ('2026-01-01' <= day(r['pr_rel_date']) < '2027-01-01') for r in headers):
            raise CommandError('抓取范围必须为2026年')
        numbers = {r['pr_nbr'] for r in headers}
        if len(numbers) != len(headers):
            raise CommandError('源表头重复')
        existing = list(PurchaseRequisition.objects.filter(number__in=numbers).values_list('number','source_profile'))
        if existing:
            if len(existing)==len(headers) and all(profile=='coerp_dgyzx1' for _,profile in existing):
                self.stdout.write('Already imported; no updates to edited local documents')
                return
            raise CommandError('存在部分导入或同号本地单据，禁止覆盖')
        materials = {r.code:r for r in Material.objects.select_related('uom')}
        snapshots = {r['pt_part']:r for r in capture['materials']}
        units = {r.code:r for r in Uom.objects.all()}
        unmapped = sorted({r['req_part'] for r in lines if r['req_part'] not in materials})
        self.stdout.write(json.dumps({'headers':len(headers),'lines':len(lines),'sources':len(sources),
            'unmapped_materials':len(unmapped)},ensure_ascii=False))
        if not opts['apply']:
            return
        batch = live_batch()
        if not batch:
            raise CommandError('请先启用本地库存账以标记源请购基准替换范围')
        objs = []
        for row in headers:
            objs.append(PurchaseRequisition(number=row['pr_nbr'], request_date=day(row['pr_rel_date']),
                site=row['pr_site'], requisition_type=row['pr_type'], document_type=row['pr_doc_code'],
                requester=row['pr_req_by'], notes=row['pr_rmks'], status='approved' if row['pr_pst'] else 'draft',
                approved_by=row['pr_pst_by'], approved_at=moment(row['pr_pst_date']),
                created_by=row['pr_crt_by'],updated_by=row['pr_mod_by'],
                source_profile='coerp_dgyzx1',source_snapshot=row,quantity_rule='source',version=row['pr_mod_times']))
        PurchaseRequisition.objects.bulk_create(objs,batch_size=100)
        by_number = {r.number:r for r in PurchaseRequisition.objects.filter(number__in=numbers)}
        # bulk_create auto timestamps are replaced with source audit times in one bulk update.
        for row in headers:
            obj=by_number[row['pr_nbr']]
            obj.created_at=moment(row['pr_crt_date']) or obj.created_at
            obj.updated_at=moment(row['pr_mod_date']) or obj.updated_at
        PurchaseRequisition.objects.bulk_update(by_number.values(),['created_at','updated_at'],batch_size=100)
        objs=[]
        for row in lines:
            mat=materials.get(row['req_part'])
            snapshot=snapshots.get(row['req_part'],{'pt_part':row['req_part'],'pt_desc1':row['req_pt_desc'],'pt_um':row['req_um']})
            unit=units.get(row['req_um'])
            # A source-only or conflicting unit remains an explicit source reference, not a fabricated master.
            if mat and mat.uom.code != row['req_um'] and mat.uom.name != row['req_um']:
                mat=None
            objs.append(PurchaseRequisitionLine(requisition=by_number[row['req_pr_nbr']],line_number=row['req_line'],
                material=mat,uom=mat.uom if mat else unit,needed_date=day(row['req_need']),
                requested_qty=Decimal(row['req_qty']),converted_qty=Decimal(row['req_qty_applied']),
                mrp_demand_qty=Decimal(row['req_mrp_req_self']),on_order_qty=Decimal(row['req_mrp_ord']),
                available_qty=Decimal(row['req_mrp_ld_net']),safety_stock_qty=Decimal(row['req_mrp_safe']),
                line_status=row['req_status'],source_kind='source',source_snapshot=row,material_snapshot=snapshot,
                created_by=row['req_crt_by'],created_at=moment(row['req_crt_date']) or timezone.now(),
                updated_by=row['req_mod_by'],updated_at=moment(row['req_mod_date']) or timezone.now(),modification_count=row['req_mod_times'],
                calculation_snapshot={k:v for k,v in row.items() if k.startswith('req_mrp_')},notes=row['req_rmks'],
                closed_by=row['req_close_by'],closed_at=moment(row['req_close_date']),close_reason=row['req_close_reason']))
        PurchaseRequisitionLine.objects.bulk_create(objs,batch_size=100)
        identities={(r.requisition.number,r.line_number):r for r in PurchaseRequisitionLine.objects.filter(requisition__number__in=numbers).select_related('requisition')}
        objs=[]
        for row in sources:
            parent=identities.get((row['reqd_pr_nbr'],row['reqd_req_line']))
            if not parent:
                raise CommandError('来源明细父行缺失')
            objs.append(PurchaseRequisitionSource(line=parent,sequence=row['reqd_line'],source_number=row['reqd_wod_nbr'],
                source_marker=row['reqd_wod_lot'],source_sequence=row['reqd_wod_seq'],quantity=Decimal(row['reqd_pr_qty']),snapshot=row))
        PurchaseRequisitionSource.objects.bulk_create(objs,batch_size=100)
        manifest=dict(batch.manifest)
        manifest['requisition_import']={'source':'coerp_dgyzx1','year':2026,'numbers':sorted(numbers),
            'headers':len(headers),'lines':len(lines),'sources':len(sources)}
        batch.manifest=manifest
        batch.save(update_fields=['manifest'])
        AuditEvent.objects.create(model='backend.purchaserequisition',object_id='import-2026',action='import',actor='dgyzx1-import',
            payload={'headers':len(headers),'lines':len(lines),'sources':len(sources),'unmapped_materials':unmapped})
        self.stdout.write('Imported; source snapshots and inventory balances preserved')
