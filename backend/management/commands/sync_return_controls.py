"""Read native inventory calendar and expanded location permissions; never post stock."""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import InventoryPostingControl, InventoryDictionary, Employee, Partner, CustomerMaterial, SalesReturnSequence


class Command(BaseCommand):
    help = '从 dgyzx1 只读同步退货参考配置，默认预检；--commit 仅更新本地配置，不启用库存过账'

    def add_arguments(self, parser):
        parser.add_argument('--profile', default='coerp_dgyzx1', choices=['coerp_dgyzx1', 'coerp_xgyzx'])
        parser.add_argument('--site', default='1000')
        parser.add_argument('--commit', action='store_true')

    def handle(self, *args, **opts):
        import pyodbc
        from tools.inspect_source_schema import connection_string
        def text(value):
            return str(value or '').strip()
        try:
            with pyodbc.connect(connection_string(opts['profile']), readonly=True, autocommit=True) as conn:
                cur = conn.cursor()
                system = cur.execute('SELECT sys_min_date,sys_max_date,sys_inv_lyear,sys_inv_lmonth FROM sys_ctrl').fetchone()
                calendar = [{'year': int(y), 'month': int(m), 'start': start.date().isoformat(), 'end': end.date().isoformat(), 'frozen': bool(frozen)}
                    for y, m, start, end, frozen in cur.execute('SELECT glc_year,glc_month,glc_start,glc_end,glc_frozen_inv FROM glc_cal')]
                locations = list(cur.execute('SELECT loc_loc,loc_perm,loc_disabled FROM loc_mstr WHERE loc_site=?', opts['site']))
                permissions = {}
                for code, perm, disabled in locations:
                    if disabled:
                        permissions[text(code)] = []
                    elif '*' in text(perm).replace('，', ',').replace(' ', '').split(','):
                        permissions[text(code)] = ['*']
                    else:
                        # Source expands both groups and delegated users; do not guess delimiters locally.
                        permissions[text(code)] = [text(r[0]) for r in cur.execute('SELECT usr_user FROM dbo.GetPermUsers(?)', perm or '')]
                groups = list(cur.execute("SELECT usr_user,CAST(usr_name AS nvarchar(80)),usr_lock FROM usr_mstr WHERE usr_group='SDGROUP'"))
                addresses = list(cur.execute("SELECT gend_option,CAST(gend_name AS nvarchar(255)),gend_disabled FROM gend_det WHERE gend_gen='DN_ADDR'"))
                customers = list(cur.execute('SELECT cm_addr,cm_consignment FROM cm_mstr'))
                materials = list(cur.execute('SELECT cp_cust,cp_part,cp_cust_part,CAST(cp_char1 AS nvarchar(80)),CAST(cp_char2 AS nvarchar(160)) FROM cp_mstr'))
                printer = cur.execute("SELECT CAST(udf_default AS nvarchar(255)) FROM udf_mstr WHERE udf_prog='SLCRMTA2' AND udf_field='cr_char6'").fetchone()
                numbers = [text(r[0]) for r in cur.execute("SELECT cr_cr FROM cr_mstr WHERE cr_prog_code='SLCRMTA2' AND cr_cr LIKE 'MYSN%'")]
        except pyodbc.Error as exc:
            raise CommandError('源库连接或只读配置查询失败；未更新本地配置') from exc
        if not system:
            raise CommandError('源库缺少 sys_ctrl')
        self.stdout.write(f"预检：日历 {len(calendar)}，库位权限 {len(permissions)}，业务组别 {len(groups)}，客户地址 {len(addresses)}")
        if not opts['commit']:
            return
        with transaction.atomic():
            baselines = {}
            for number in numbers:
                if len(number) == 12 and number[4:].isdigit():
                    period = '20' + number[4:8]
                    baselines[period] = max(baselines.get(period, 0), int(number[8:]))
            for period, maximum in baselines.items():
                seq, _ = SalesReturnSequence.objects.select_for_update().get_or_create(period=period)
                if maximum > seq.last_value:
                    seq.last_value = maximum
                    seq.save(update_fields=['last_value'])
            InventoryPostingControl.objects.update_or_create(site=opts['site'], defaults={
                'min_date': system[0].date(), 'max_date': system[1].date(), 'closed_year': int(system[2] or 0),
                'closed_month': int(system[3] or 0), 'calendar': calendar, 'location_permissions': permissions,
                'source_database': opts['profile'],
            })
            for code, name, locked in groups:
                Employee.objects.update_or_create(code=text(code), defaults={'name': text(name), 'group_code': 'SDGROUP', 'is_locked': bool(locked)})
            for code, name, disabled in addresses:
                # Native validation uses gend_name, not gend_code.
                if len(text(code)) > 30:
                    raise CommandError('DN_ADDR 代码超过本地字段长度，事务已回滚')
                InventoryDictionary.objects.update_or_create(dictionary='DN_ADDR', code=text(code), defaults={'name': text(name), 'disabled': bool(disabled)})
            for code, consignment in customers:
                Partner.objects.filter(code=text(code)).update(consignment=bool(consignment))
            for customer, part, code, terminal_code, terminal_name in materials:
                CustomerMaterial.objects.filter(customer__code=text(customer), material__code=text(part), customer_code=text(code)).update(
                    terminal_customer_code=text(terminal_code), terminal_customer_name=text(terminal_name))
            if printer:
                import re
                match = re.fullmatch(r"\s*select\s*N?'((?:[^']|'')*)'\s*", text(printer[0]), re.IGNORECASE)
                if match:
                    InventoryDictionary.objects.update_or_create(dictionary='RETURN_DEFAULT', code='printer', defaults={'name': match[1].replace("''", "'"), 'disabled': False})
        self.stdout.write('已同步到本地参考配置；库存过账开关保持原值。')
