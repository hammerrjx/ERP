"""Reconcile native currency masters and existing document links without replacing IDs."""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone
from backend.models import Company, Currency, CurrencyRate, Partner, SalesQuote, SupplierQuote, SalesOrder, PurchaseOrder, SalesReturn, AccountingAccount, DeliveryOrderLine, AuditEvent


def clean(v):
    return str(v or '').strip()


def aware(v):
    return timezone.make_aware(v) if v and timezone.is_naive(v) else v


SOURCES = {
    'ex_mstr': 'ex_curr,ex_desc,ex_symbol,ex_crt_by,ex_crt_date',
    'exd_det': 'exd_curr,exd_eff_date,exd_end_date,exd_rate,exd_end_rate,exd_crt_by,exd_crt_date,exd_mod_by,exd_mod_date',
    'cm_mstr': 'cm_addr,cm_curr,cm_cu_curr', 'vd_mstr': 'vd_addr,vd_curr',
    'sc_mstr': 'sc_nbr,sc_curr,sc_cust,sc_part', 'pc_mstr': 'pc_nbr,pc_curr,pc_vend,pc_part',
    'so_mstr': 'so_nbr,so_curr,so_ex_rate,so_cust', 'po_mstr': 'po_nbr,po_curr,po_vend',
    'cr_mstr': 'cr_cr,cr_curr,cr_exch_rate,cr_cust', 'ac_mstr': 'ac_code,ac_curr',
    'en_mstr': 'en_company,en_curr',
}


def read_source():
    import pyodbc
    from tools.inspect_source_schema import connection_string
    data = {}
    with pyodbc.connect(connection_string('coerp_dgyzx1'), readonly=True, autocommit=True) as conn:
        conn.timeout = 60
        for table, fields in SOURCES.items():
            cur = conn.execute(f'SELECT {fields} FROM dbo.{table}')
            columns = [d[0] for d in cur.description]
            data[table] = [dict(zip(columns, row)) for row in cur.fetchall()]
    return data


def reconcile(source, commit=False):
    counts, changes, missing = Counter(), [], []
    codes = {clean(r['ex_curr']) for r in source['ex_mstr']}
    extra = list(Currency.objects.exclude(code__in=codes).values('id', 'code', 'name'))
    if extra:
        raise CommandError(f'存在源库外币种，需明确映射后才能同步，未自动合并：{extra}')
    native_periods = {}
    for row in sorted(source['exd_det'], key=lambda r: (clean(r['exd_curr']), r['exd_eff_date'])):
        code, start, end = clean(row['exd_curr']), row['exd_eff_date'].date(), row['exd_end_date'].date()
        periods = native_periods.setdefault(code, [])
        if end < start or (periods and start <= periods[-1][1]):
            raise CommandError(f'源汇率有效期间无效或重叠：{code}/{start}')
        periods.append((start, end))
    native_keys = {(code, start) for code, periods in native_periods.items() for start, end in periods}
    for code, start in CurrencyRate.objects.values_list('currency__code', 'effective_date'):
        if (code, start) not in native_keys:
            raise CommandError(f'存在源库外汇率期间，需核对后处理，未自动删除：{code}/{start}')
    for table, fields in SOURCES.items():
        currency_fields = [f for f in fields.split(',') if f.endswith('_curr') and f not in ('ex_curr',)]
        for row in source[table]:
            for field in currency_fields:
                value = clean(row[field])
                if value and value not in codes:
                    raise CommandError(f'源数据引用未定义币种：{table}.{field}={value}')
    with transaction.atomic():
        currencies = {}
        for row in source['ex_mstr']:
            code = clean(row['ex_curr'])
            obj = Currency.objects.filter(code=code).first()
            values = dict(name=clean(row['ex_desc']), symbol=clean(row['ex_symbol']), status='approved', source_object='dgyzx1.ex_mstr')
            if not obj:
                obj = Currency.objects.create(code=code, **values)
                changes.append({'model': 'Currency', 'key': code, 'action': 'create'})
            else:
                delta = {k: {'before': getattr(obj,k), 'after': v} for k,v in values.items() if getattr(obj,k) != v}
                if delta:
                    changes.append({'model': 'Currency', 'key': code, 'fields': delta})
                    Currency.objects.filter(pk=obj.pk).update(**values)
            Currency.objects.filter(pk=obj.pk).update(created_by=clean(row['ex_crt_by']), created_at=aware(row['ex_crt_date']) or obj.created_at)
            currencies[code] = obj
        for row in source['exd_det']:
            currency = currencies[clean(row['exd_curr'])]
            start = row['exd_eff_date'].date()
            values = dict(expiry_date=row['exd_end_date'].date(), rate_to_company=row['exd_rate'], end_rate=row['exd_end_rate'], source_object='dgyzx1.exd_det')
            existing = CurrencyRate.objects.filter(currency=currency, effective_date=start).first()
            if existing is None or any(getattr(existing,k) != v for k,v in values.items()):
                changes.append({'model':'CurrencyRate', 'key':f'{currency.code}/{start}', 'fields':values})
            rate, _ = CurrencyRate.objects.update_or_create(currency=currency, effective_date=start, defaults=values)
            CurrencyRate.objects.filter(pk=rate.pk).update(created_by=clean(row['exd_crt_by']), created_at=aware(row['exd_crt_date']) or rate.created_at,
                updated_by=clean(row['exd_mod_by']), updated_at=aware(row['exd_mod_date'] or row['exd_crt_date']) or rate.updated_at)

        def link(model, obj, code, table, rate=None):
            values = {'currency_id': currencies[code].pk if code else None}
            if rate is not None:
                values['exchange_rate'] = rate
            delta = {k:{'before':getattr(obj,k),'after':v} for k,v in values.items() if getattr(obj,k) != v}
            counts[model.__name__] += 1
            if delta:
                changes.append({'model':model.__name__, 'id':obj.pk, 'key':getattr(obj,'number',getattr(obj,'code','')), 'source':table,'fields':delta})
                model.objects.filter(pk=obj.pk).update(**values)

        for row in source['en_mstr']:
            obj = Company.objects.filter(code=clean(row['en_company'])).first()
            if obj:
                link(Company, obj, clean(row['en_curr']), 'en_mstr')

        partner_targets = {}
        for table, prefix, kinds in [('cm_mstr','cm',('customer','both')),('vd_mstr','vd',('supplier','both'))]:
            local = {p.code:p for p in Partner.objects.filter(kind__in=kinds)}
            for row in source[table]:
                obj = local.get(clean(row[f'{prefix}_addr']))
                if not obj:
                    continue
                code = clean(row[f'{prefix}_curr'])
                if obj.pk in partner_targets and partner_targets[obj.pk] != code:
                    raise CommandError(f'客户供应商共用伙伴 {obj.code} 的源币种不同，不能合并覆盖')
                partner_targets[obj.pk] = code
                link(Partner,obj,code,table)
                if prefix == 'cm' and obj.copper_currency != clean(row['cm_cu_curr']):
                    changes.append({'model':'Partner','key':obj.code,'field':'copper_currency','before':obj.copper_currency,'after':clean(row['cm_cu_curr'])})
                    Partner.objects.filter(pk=obj.pk).update(copper_currency=clean(row['cm_cu_curr']))

        for model,table,key,curr,partner,relation,rate in [
            (SalesQuote,'sc_mstr','sc_nbr','sc_curr','sc_cust','customer',None),
            (SupplierQuote,'pc_mstr','pc_nbr','pc_curr','pc_vend','supplier',None),
            (SalesOrder,'so_mstr','so_nbr','so_curr','so_cust','customer','so_ex_rate'),
            (PurchaseOrder,'po_mstr','po_nbr','po_curr','po_vend','supplier',None),
            (SalesReturn,'cr_mstr','cr_cr','cr_curr','cr_cust','customer','cr_exch_rate'),
        ]:
            native = {clean(r[key]):r for r in source[table]}
            for obj in model.objects.select_related(relation):
                row = native.get(obj.number)
                if not row:
                    missing.append({'model':model.__name__, 'key':obj.number, 'reason':'no_source_document'})
                    continue
                if getattr(obj,relation).code != clean(row[partner]):
                    missing.append({'model':model.__name__, 'key':obj.number, 'reason':'source_number_collision_partner_mismatch'})
                    continue
                if model is SupplierQuote and obj.material.code != clean(row['pc_part']):
                    missing.append({'model':model.__name__, 'key':obj.number, 'reason':'source_number_collision_material_mismatch'})
                    continue
                if model is SalesQuote and obj.lines.exclude(material__code=clean(row['sc_part'])).exists():
                    missing.append({'model':model.__name__, 'key':obj.number, 'reason':'source_number_collision_material_mismatch'})
                    continue
                code = clean(row[curr])
                if not code:
                    raise CommandError(f'{table}/{obj.number} 源单据币种为空')
                link(model,obj,code,table,row[rate] if rate else None)

        local_accounts = {a.code:a for a in AccountingAccount.objects.all()}
        for row in source['ac_mstr']:
            obj = local_accounts.get(clean(row['ac_code']))
            if obj:
                link(AccountingAccount,obj,clean(row['ac_curr']),'ac_mstr')
        # Delivery has no header currency in dn_mstr. Each line follows its order, including a saved display snapshot.
        for line in DeliveryOrderLine.objects.select_related('sales_order_line__order__currency'):
            code = line.sales_order_line.order.currency.code
            if 'currency_code' in line.source_snapshot and line.source_snapshot['currency_code'] != code:
                snapshot = dict(line.source_snapshot)
                changes.append({'model':'DeliveryOrderLine','id':line.pk,'field':'source_snapshot.currency_code', 'before':snapshot['currency_code'],'after':code})
                snapshot['currency_code'] = code
                DeliveryOrderLine.objects.filter(pk=line.pk).update(source_snapshot=snapshot)
            counts['DeliveryOrderLine'] += 1
        inventory = {}
        for model in apps.get_app_config('backend').get_models():
            for field in model._meta.fields:
                if field.is_relation and field.related_model is Currency:
                    inventory[f'{model.__name__}.{field.name}'] = dict(Counter(model.objects.values_list(field.name+'__code',flat=True)))
        result = {'database':str(connection.settings_dict['NAME']), 'commit':commit, 'currencies':list(Currency.objects.values('id','code','name','symbol')),
            'rates':list(CurrencyRate.objects.values('currency__code','effective_date','expiry_date','rate_to_company','end_rate')),
            'checked':dict(counts),'changes':changes,'local_only_documents':missing,'all_currency_relations':inventory}
        if not commit:
            transaction.set_rollback(True)
        else:
            AuditEvent.objects.create(model='backend.currency',object_id='sync',action='sync_dgyzx1',actor='dgyzx1-currency-sync',payload={'counts':dict(counts),'changes':len(changes)})
    return result


class Command(BaseCommand):
    help = '同步dgyzx1货币、汇率及已有单据币种引用；默认事务回滚预检，--commit仅写本地账套'

    def add_arguments(self, parser):
        parser.add_argument('--commit',action='store_true')
        parser.add_argument('--output',type=Path,required=True)

    def handle(self,*args,**opts):
        name = str(connection.settings_dict['NAME'])
        if name.lower() in ('dgyzx1','xgyzx'):
            raise CommandError('禁止修改源库')
        if connection.vendor != 'sqlite' and name != 'erp_inventory_pilot':
            raise CommandError('仅允许当前本地SQLite或erp_inventory_pilot')
        source = read_source()
        result = reconcile(source, opts['commit'])
        opts['output'].parent.mkdir(parents=True,exist_ok=True)
        opts['output'].write_text(json.dumps(result,ensure_ascii=False,default=str,indent=2),encoding='utf8')
        self.stdout.write(f"{'已同步' if opts['commit'] else '预检已回滚'}：币种 {len(result['currencies'])}，汇率 {len(result['rates'])}，差异 {len(result['changes'])}；详见 {opts['output']}")
