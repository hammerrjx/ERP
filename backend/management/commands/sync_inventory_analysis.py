"""Capture source inventory analysis without posting to either stock ledger."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pyodbc
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from backend.domain.inventory_analysis import InventoryAnalysisSnapshot
from backend.inventory_analysis import reconcile_bulk

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from inspect_source_schema import connection_string


def records(conn, sql, *params):
    cur = conn.execute(sql, *params)
    while cur.description is None:
        if not cur.nextset():
            return []
    keys = [c[0] for c in cur.description]
    return [{k: v.rstrip() if isinstance(v, str) else v for k, v in zip(keys, row)} for row in cur]


class Command(BaseCommand):
    help = '只读同步 dgyzx1 批量库存及月度进销存，不生成库存流水'

    def add_arguments(self, parser):
        parser.add_argument('--site', default='1000')
        parser.add_argument('--period', action='append', help='YYYY-MM; omitted imports all available monthly tables')
        parser.add_argument('--skip-bulk', action='store_true')

    def handle(self, *args, **opts):
        site = opts['site']
        snapshots = []
        with pyodbc.connect(connection_string('coerp_dgyzx1'), readonly=True, timeout=10) as conn:
            conn.timeout = 180
            state = conn.execute('SELECT snapshot_isolation_state FROM sys.databases WHERE name=DB_NAME()').fetchone()[0]
            conn.commit()
            isolation = 'SNAPSHOT' if state == 1 else 'READ COMMITTED'
            conn.execute('SET TRANSACTION ISOLATION LEVEL '+isolation)
            metadata = {'source': 'coerp_dgyzx1', 'isolation': isolation, 'consistent_snapshot': state == 1,
                        'started_at': datetime.now().astimezone().isoformat()}
            materials = records(conn, 'SELECT pt_part,pt_desc1,pt_spec,pt_um FROM pt_mstr')
            unit_names = {r['um_um']: r['um_desc'] for r in records(conn, 'SELECT um_um,um_desc FROM um_mstr')}
            for row in materials:
                row['pt_um'] = unit_names.get(row['pt_um'], row['pt_um'])
            locations = records(conn, 'SELECT l.loc_loc,l.loc_desc,l.loc_ac_code_inv,v.loc_type,v.loc_type_name,v.loc_cost_type FROM loc_mstr l JOIN v_loc_mstr_type v ON l.loc_site=v.loc_site AND l.loc_loc=v.loc_loc WHERE l.loc_site=?', site)
            categories = records(conn, 'SELECT pl_prod_line,pl_desc,pl_ac_code_inv,pl_ac_code_wcost,pl_ac_code_comm FROM pl_mstr')
            dictionaries = records(conn, "SELECT gend_gen,gend_option,gend_name,gend_property2 FROM gend_det WHERE gend_gen IN ('LOC_KIND','PT_GROUP','PART_TYPE')")
            accounts = {r['ac_code']: r for r in records(conn, 'SELECT ac_code,ac_name,ac_upper_ac,ac_level FROM ac_mstr')}
            names = {}
            for code in accounts:
                path, current = [], code
                for _ in range(20):
                    account = accounts.get(current)
                    if not account:
                        break
                    path.insert(0, account['ac_name'])
                    if not account['ac_level'] or not account['ac_upper_ac']:
                        break
                    current = account['ac_upper_ac']
                names[code] = '\\'.join(path)
            masters = {'materials': {r.pop('pt_part'): r for r in materials},
                       'locations': {r['loc_loc']: r for r in locations},
                       'categories': {r['pl_prod_line']: r for r in categories}, 'accounts': names,
                       'cost_types': {r['tp_code']: r['tp_name'] for r in records(conn, 'SELECT tp_code,tp_name FROM v_loc_type')},
                       'suppliers': [r['vd_addr'] for r in records(conn, 'SELECT vd_addr FROM vd_mstr')],
                       'groups': {r['gend_option']: r['gend_name'] for r in dictionaries if r['gend_gen'] == 'PT_GROUP'},
                       'part_types': {r['gend_option']: r['gend_name'] for r in dictionaries if r['gend_gen'] == 'PART_TYPE'}}
            if not opts['skip_bulk']:
                rows = records(conn, (ROOT / 'backend/sql/inventory_bulk.sql').read_text(encoding='utf-8'), site)
                details = records(conn, (ROOT / 'backend/sql/inventory_bulk_details.sql').read_text(encoding='utf-8'), site)
                differences = reconcile_bulk(rows, details)
                for row in rows:
                    row['pt_um'] = unit_names.get(row['pt_um'], row['pt_um'])
                snapshots.append(('bulk', '', {**metadata, 'rows': rows, 'details': details,
                    'capture_differences': differences, 'summary_basis': 'captured_detail_contributions'}))
                self.stdout.write(f'bulk: {len(rows)} materials, {len(details)} detail rows')
            tables = [r['name'] for r in records(conn, "SELECT name FROM sys.tables WHERE name LIKE 'inb_hist_%'") if re.fullmatch(r'inb_hist_\d{6}', r['name'])]
            periods = opts['period'] or [name[-6:-2]+'-'+name[-2:] for name in tables]
            for period in sorted(periods):
                if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', period):
                    raise CommandError('期间格式必须为 YYYY-MM')
                table = 'inb_hist_'+period.replace('-', '')
                if table not in tables:
                    raise CommandError(f'{period}: 源库未生成月度账表')
                rows = records(conn, f'''SELECT T.*,p.pt_prod_line,p.pt_part_type,p.pt_group,
                    v.loc_type AS loc_type_code,v.loc_type_name AS loc_type,v.loc_cost_type
                    FROM [{table}] T JOIN pt_mstr p ON p.pt_part=T.inb_part
                    JOIN v_loc_mstr_type v ON v.loc_site=T.inb_site AND v.loc_loc=T.inb_loc
                    WHERE T.inb_site=? AND NOT EXISTS(SELECT 1 FROM gend_det g
                        WHERE g.gend_gen='LOC_KIND' AND g.gend_option=v.loc_cost_type AND g.gend_property2='')''', site)
                snapshots.append(('monthly', period, {**metadata, 'source_table': table, 'rows': rows, 'masters': masters}))
                self.stdout.write(f'{period}: {len(rows)} monthly rows')
            conn.rollback()
        # Publish only once the complete source read succeeds; readers retain the prior capture on failure.
        with transaction.atomic():
            for kind, period, payload in snapshots:
                payload['finished_at'] = datetime.now().astimezone().isoformat()
                InventoryAnalysisSnapshot.objects.update_or_create(kind=kind, site=site, period=period,
                    defaults={'payload': json.loads(json.dumps(payload, ensure_ascii=False, default=str))})
        self.stdout.write(self.style.SUCCESS(f'Published {len(snapshots)} reports; operational inventory unchanged'))
