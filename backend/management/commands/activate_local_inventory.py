"""Initialize a local test ledger from an explicitly selected warehouse baseline."""
from collections import defaultdict
from copy import copy
from decimal import Decimal
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import Material, Location, StockBalance, StockTransaction, AuditEvent
from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportRow, InventoryReportLookup
from backend.domain.inventory_analysis import InventoryAnalysisSnapshot
from backend.live_inventory import live_batch, local_contributions


class Command(BaseCommand):
    help = '从已核对的本地库存报表建立测试账；默认预检，--apply执行；保留源快照和原期初审计'

    def add_arguments(self, parser):
        parser.add_argument('--baseline', type=int, required=True)
        parser.add_argument('--apply', action='store_true')

    @transaction.atomic
    def handle(self, *args, **opts):
        existing = live_batch()
        if existing:
            if existing.manifest.get('baseline_batch_id') != opts['baseline']:
                raise CommandError('本地账已启用，不能换期初或重复导入')
            self.stdout.write(f'Local ledger {existing.pk} already active; no changes')
            return
        source = InventoryReportBatch.objects.select_for_update().get(pk=opts['baseline'])
        if source.source == 'local':
            raise CommandError('期初必须来自源快照')
        if StockTransaction.objects.exclude(movement_type='opening').exists():
            raise CommandError('已有非期初库存流水，必须先对账，禁止覆盖余额')
        materials = list(Material.objects.select_related('uom'))
        by_code = {m.code: m for m in materials}
        by_old = defaultdict(list)
        for material in materials:
            if material.old_code:
                by_old[material.old_code].append(material)
        locations = {(l.source_site, l.code): l for l in Location.objects.all()}
        rows = list(InventoryReportRow.objects.filter(batch=source, kind='inventory'))
        mapped, deferred, codes, blocked = [], [], {}, {}
        for row in rows:
            candidates = [by_code[row.material_code]] if row.material_code in by_code else by_old[row.material_code]
            if len(candidates) > 1:
                raise CommandError('物料期初映射不唯一：' + row.material_code)
            location = locations.get((row.site, row.location_code))
            if not location:
                raise CommandError(f'缺少库位：{row.site}/{row.location_code}')
            if not candidates:
                deferred.append(row.material_code)
                continue
            material = candidates[0]
            if row.payload.get('uom_code') != material.uom.code and row.payload.get('uom_name') != material.uom.name:
                blocked[str(material.pk)] = {'material': row.material_code,
                    'source_unit': row.payload.get('uom_code'), 'local_unit': material.uom.code}
                continue
            previous_code = codes.setdefault(str(material.pk), row.material_code)
            if previous_code != row.material_code:
                raise CommandError(f'多个源编码映射同一物料：{previous_code}/{row.material_code}')
            mapped.append((row, material, location))
        sites = sorted({row.site for row in rows})
        snapshots = list(InventoryAnalysisSnapshot.objects.filter(kind='bulk', site__in=sites))
        if {s.site for s in snapshots} != set(sites):
            raise CommandError('缺少同站点的批量查询基准')
        report = {'inventory_keys': len(rows), 'operational_keys': len(mapped),
            'source_only_materials': len(set(deferred)), 'blocked_materials': blocked, 'sites': sites}
        self.stdout.write(json.dumps(report, ensure_ascii=False))
        if not opts['apply']:
            self.stdout.write('Preflight only; no changes')
            return
        day = timezone.localdate()
        batch = InventoryReportBatch.objects.create(source='local', active=False,
            manifest={'operational': True, 'baseline_batch_id': source.pk, 'opening_date': str(day),
                'date_from': str(day), 'date_to': '', 'material_codes': codes,
                'baseline_captured_at': source.manifest.get('finished_at'), 'scope': 'test', **report})
        pending = []
        for row in rows:
            row = copy(row)
            row.pk = None
            row.batch = batch
            pending.append(row)
        InventoryReportRow.objects.bulk_create(pending, batch_size=100)
        lookups = []
        for row in InventoryReportLookup.objects.filter(batch=source).iterator(chunk_size=1000):
            row.pk, row.batch = None, batch
            lookups.append(row)
        InventoryReportLookup.objects.bulk_create(lookups, batch_size=100)
        balances = {(b.material_id, b.location_id, b.batch_number): b for b in StockBalance.objects.all()}
        for row, material, location in mapped:
            quantity = Decimal(row.payload['quantity'])
            key = (material.pk, location.pk, row.batch_number)
            balance = balances.get(key)
            before = balance.quantity if balance else Decimal(0)
            if balance and balance.reserved_quantity:
                raise CommandError('期初库存有预留，请先核对')
            if balance:
                if balance.uom_id != material.uom_id:
                    raise CommandError('现有余额单位不同')
                balance.quantity = quantity
                balance.save(update_fields=['quantity', 'updated_at'])
            else:
                balance = StockBalance.objects.create(material=material, location=location,
                    uom=material.uom, batch_number=row.batch_number, quantity=quantity)
            if not balances.get(key) or before != quantity:
                StockTransaction.objects.create(material=material, location=location, uom=material.uom,
                    batch_number=row.batch_number, quantity=quantity-before, balance_after=quantity,
                    movement_type='opening', source_model='backend.inventoryreportbatch',
                    source_id=str(batch.pk), source_line_id=str(row.pk),
                    actor='local-test-cutover', effective_date=day)
        for snapshot in snapshots:
            InventoryAnalysisSnapshot.objects.create(kind='localbulk', site=snapshot.site, payload=snapshot.payload)
        batch.manifest['local_contributions'] = local_contributions(batch)
        batch.active = True
        InventoryReportBatch.objects.filter(active=True).update(active=False)
        batch.save(update_fields=['active', 'manifest'])
        AuditEvent.objects.create(model=batch._meta.label_lower, object_id=str(batch.pk),
            action='activate_test_ledger', actor='local-test-cutover', payload=batch.manifest)
        self.stdout.write(f'Activated local test ledger {batch.pk}; source batch {source.pk} preserved')
