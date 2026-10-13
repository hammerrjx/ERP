"""Preview/import source ptp2 site overrides into the web ledger only."""
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.utils import timezone

from backend.models import Material, TradeMrpSiteParameter


class Command(BaseCommand):
    help = '只读获取dgyzx1站点MRP参数；默认仅预检，--apply写入网页本地参数表'

    def add_arguments(self, parser):
        parser.add_argument('--site', default='1000')
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **options):
        import pyodbc
        from tools.inspect_source_schema import connection_string

        profile, site = 'coerp_dgyzx1', options['site']
        if str(connections['default'].settings_dict['NAME']).lower() in {'dgyzx1', 'xgyzx', 'coerp_dgyzx1', 'coerp_xgyzx'}:
            raise CommandError('目标不能是源ERP数据库')
        with pyodbc.connect(connection_string(profile), readonly=True, timeout=10) as conn:
            conn.timeout = 30
            rows = list(conn.execute('SELECT ptp2_part,ptp2_sfty_stk,ptp2_ord_min,ptp2_ord_mult FROM ptp2_det WHERE ptp2_site=? ORDER BY ptp2_part', site))
        materials = dict(Material.objects.filter(code__in=[r[0] for r in rows]).values_list('code', 'id'))
        missing = [r[0] for r in rows if r[0] not in materials]
        if any(v is not None and v < 0 for r in rows for v in r[1:]):
            raise CommandError('源站点计划参数存在负值，停止导入')
        self.stdout.write(f'站点{site}：源参数{len(rows)}，已映射{len(rows)-len(missing)}，缺物料映射{len(missing)}')
        if missing:
            self.stdout.write('未映射编码（最多20个）：' + ','.join(missing[:20]))
        if not options['apply']:
            self.stdout.write('仅预检，未写入网页或源数据库。')
            return
        if missing:
            raise CommandError('请先补齐物料映射；本次未写入')
        with transaction.atomic():
            for part, safety, minimum, package in rows:
                TradeMrpSiteParameter.objects.update_or_create(site=site, material_id=materials[part], defaults={
                    'safety_stock_qty': safety, 'min_purchase_qty': minimum, 'min_pack_qty': package,
                    'source_profile': profile, 'checked_at': timezone.now()})
            # Only this source's obsolete overrides are cleared; null means master fallback.
            TradeMrpSiteParameter.objects.filter(site=site, source_profile=profile).exclude(material_id__in=materials.values()).update(
                safety_stock_qty=None, min_purchase_qty=None, min_pack_qty=None, checked_at=timezone.now())
        self.stdout.write('网页站点参数已同步；源ERP只读。')
