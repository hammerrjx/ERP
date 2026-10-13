"""Load a verified source export into an isolated report batch, never stock ledgers."""
import gzip
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportLookup, InventoryReportRow
from backend.inventory_report_source import SourceReportMapper


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--input', type=Path, required=True)
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--activate', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path('outputs/inventory-report-backups'))

    def handle(self, *args, **options):
        if options['activate'] and InventoryReportBatch.objects.filter(source='local', active=True).exists():
            raise CommandError('本地业务账已启用，源数据只能导入历史批次，不能覆盖活动业务账')
        if options['activate'] and not options['apply']:
            raise CommandError('--activate requires --apply')
        root = options['input']
        manifest = json.loads((root / 'manifest.json').read_text(encoding='utf8'))
        if manifest.get('source') != 'coerp_dgyzx1' or manifest.get('date_from') != '2026-01-01' or manifest.get('date_to') != '2026-12-31':
            raise CommandError('Expected the approved dgyzx1 2026 report export')
        required = {'masters.json', 'ld_det.jsonl.gz', 'tr_hist.jsonl.gz', 'tr_hist_rec.jsonl.gz'}
        if set(manifest.get('sha256', {})) != required:
            raise CommandError('Export file manifest is incomplete')
        for name in required:
            with (root / name).open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != manifest['sha256'][name]:
                    raise CommandError('Export checksum mismatch: ' + name)
        digest = hashlib.sha256(json.dumps(manifest['sha256'], sort_keys=True).encode()).hexdigest()
        for existing in InventoryReportBatch.objects.all():
            if existing.manifest.get('export_digest') == digest:
                if options['apply'] and options['activate'] and not existing.active:
                    with transaction.atomic():
                        InventoryReportBatch.objects.filter(active=True).update(active=False)
                        existing.active = True
                        existing.save(update_fields=['active'])
                self.stdout.write(f'Already imported as batch {existing.pk}; no duplicate data created')
                return
        mapper = SourceReportMapper(json.loads((root / 'masters.json').read_text(encoding='utf8')), manifest['finished_at'])
        apply = options['apply']
        if apply and connection.vendor == 'sqlite':
            options['backup_dir'].mkdir(parents=True, exist_ok=True)
            backup = options['backup_dir'] / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sqlite3')
            with sqlite3.connect(str(settings.DATABASES['default']['NAME'])) as source, sqlite3.connect(backup) as target:
                source.backup(target)
            self.stdout.write('Database backup: ' + str(backup))
        batch = InventoryReportBatch.objects.create(manifest=manifest) if apply else None
        fields = {field.name for field in InventoryReportRow._meta.fields} - {'id', 'batch', 'payload', 'kind'}
        counts, statuses = Counter(), Counter()
        try:
            lookups = [InventoryReportLookup(batch=batch, **row) for row in mapper.lookups()]
            if apply:
                InventoryReportLookup.objects.bulk_create(lookups, batch_size=500)
            for table in ('ld_det', 'tr_hist', 'tr_hist_rec'):
                pending = []
                with gzip.open(root / (table + '.jsonl.gz'), 'rt', encoding='utf8') as stream:
                    for line in stream:
                        raw = json.loads(line)
                        payload = mapper.map(table, raw)
                        values = {key: payload[key] for key in fields if key in payload}
                        if values.get('posted_at'):
                            stamp = datetime.fromisoformat(values['posted_at'])
                            values['posted_at'] = timezone.make_aware(stamp) if timezone.is_naive(stamp) else stamp
                        else:
                            values['posted_at'] = None
                        if not values.get('document_date'):
                            values['document_date'] = None
                        counts[table] += 1
                        if table == 'ld_det':
                            statuses['有效报价' if payload['price_status'].startswith('报价 ') else payload['price_status']] += 1
                        if apply:
                            pending.append(InventoryReportRow(batch=batch, kind='inventory' if table == 'ld_det' else 'movement', payload=payload, **values))
                            if len(pending) >= 500:
                                InventoryReportRow.objects.bulk_create(pending, batch_size=100)
                                pending.clear()
                if pending:
                    InventoryReportRow.objects.bulk_create(pending, batch_size=100)
                if counts[table] != manifest['counts'][table]:
                    raise CommandError('Row count mismatch: ' + table)
                self.stdout.write(f'{table}: {counts[table]}')
            if apply:
                manifest.update(export_digest=digest, price_status_counts=dict(statuses))
                with transaction.atomic():
                    if options['activate']:
                        InventoryReportBatch.objects.filter(active=True).update(active=False)
                    batch.manifest = manifest
                    batch.active = options['activate']
                    batch.save(update_fields=['manifest', 'active'])
                self.stdout.write(f'Imported batch {batch.pk}, active={batch.active}')
            else:
                self.stdout.write('Dry run passed; no database writes')
        except Exception:
            if batch:
                batch.delete()
            raise
