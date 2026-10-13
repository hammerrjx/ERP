"""Synchronise verified legacy master fields into the isolated SQL Server pilot."""
from collections import Counter
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from backend.models import AccountingAccount, Currency, Partner, PartnerBankAccount, PaymentMethod
from .import_supplier_quotes import clean, key, source_yes, aware, source_date


class Command(BaseCommand):
    help = 'Read dgyzx1 currencies/accounts and existing partner links; --commit writes only erp_inventory_pilot'

    def add_arguments(self, parser):
        parser.add_argument('--commit', action='store_true')

    def handle(self, *args, **options):
        import pyodbc
        from tools.inspect_source_schema import connection_string
        if options['commit'] and (connection.vendor != 'microsoft' or connection.settings_dict['NAME'] != 'erp_inventory_pilot'):
            raise CommandError('Only erp_inventory_pilot may be updated')
        source = {}
        with pyodbc.connect(connection_string('coerp_dgyzx1'), readonly=True, timeout=10) as conn:
            conn.timeout = 30
            for table in ('ex_mstr','ac_mstr','vd_mstr','vdd_det','ct_mstr'):
                cursor = conn.execute(f'SELECT * FROM dbo.{table}')
                source[table] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
            cursor = conn.execute('SELECT cm_addr,cm_curr FROM dbo.cm_mstr')
            source['cm_mstr'] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
        self.stdout.write(str({table: len(rows) for table,rows in source.items()}))
        if not options['commit']:
            return
        tally = Counter()
        with transaction.atomic():
            currencies = {}
            for row in source['ex_mstr']:
                currency, _ = Currency.objects.update_or_create(code=clean(row['ex_curr']), defaults={
                    'name':clean(row['ex_desc']), 'symbol':clean(row['ex_symbol']), 'status':'approved',
                })
                currencies[key(row['ex_curr'])] = currency
                tally['currencies'] += 1
            for row in source['ac_mstr']:
                code = key(row['ac_curr'])
                if code and code not in currencies:
                    raise CommandError(f'Unknown account currency: {code}')
                AccountingAccount.objects.update_or_create(code=clean(row['ac_code']), defaults={
                    'name':clean(row['ac_name']), 'parent_code':clean(row['ac_upper_ac']),
                    'currency':currencies.get(code), 'active':source_yes(row['ac_valid']),
                    'posting_allowed':source_yes(row['ac_trans']), 'status':'approved',
                })
                tally['accounts'] += 1
            # Keep existing IDs so all order/quote/rate foreign keys continue to reference the same currency.
            for table, prefix, kinds in [('cm_mstr','cm',('customer','both')),('vd_mstr','vd',('supplier','both'))]:
                for row in source[table]:
                    partner = Partner.objects.filter(code=clean(row[f'{prefix}_addr']),kind__in=kinds).first()
                    if not partner:
                        continue
                    code = key(row[f'{prefix}_curr'])
                    if code and code not in currencies:
                        raise CommandError(f'Unknown partner currency: {code}')
                    fields = {'currency':currencies.get(code)}
                    if prefix == 'vd':
                        mapping = {'buyer':'vd_buyer','quote_method':'vd_quot_type','invoice_type':'vd_inv_type',
                                   'supplier_type':'vd_kind','material_price_method':'vd_mtl_sales',
                                   'purchase_account':'vd_ap_ac','temporary_payable_account':'vd_tap_ac',
                                   'outsource_fee_account':'vd_sub_ac','outsource_material_account':'vd_comm_ac'}
                        fields.update({target:clean(row[src]) for target,src in mapping.items()})
                        fields.update(strategic_supplier=clean(row['vd_strategic']) == '2',
                                      quote_tax_included=clean(row['vd_quot_type']) == '1',
                                      material_price_factor=row['vd_mtl_rate'], tax_rate=row['vd_vat'],
                                      backup_ratio=row['vd_spare_pct'],over_receipt_ratio=row['vd_tol_pct'],
                                      service_score=row['vd_service'],registered_capital=row['vd_reg_fund'],
                                      annual_revenue=row['vd_tunrover'],employee_count=row['vd_employees'],
                                      opening_date=source_date(row['vd_open_date']))
                        method = PaymentMethod.objects.filter(code=clean(row['vd_cr_terms'])).first()
                        if method:
                            fields.update(payment_method_master=method,payment_method=method.code)
                        elif clean(row['vd_cr_terms']):
                            tally['unmapped_payment_method'] += 1
                    Partner.objects.filter(pk=partner.pk).update(**fields)
                    tally[f'{prefix}_linked'] += 1
            suppliers = {key(p.code):p for p in Partner.objects.filter(kind__in=('supplier','both'))}
            for row in source['vdd_det']:
                partner = suppliers.get(key(row['vdd_addr']))
                if not partner:
                    continue
                kind = clean(row['vdd_type'])
                if kind not in ('1','2'):
                    raise CommandError(f'Unknown bank account type: {kind}')
                PartnerBankAccount.objects.update_or_create(partner=partner,line_number=row['vdd_line'], defaults={
                    'account_type':'company' if kind == '1' else 'personal',
                    'bank_name':clean(row['vdd_bank']),'account_name':clean(row['vdd_name']),
                    'account_number':clean(row['vdd_account']),'other_info':clean(row['vdd_oth_info']),
                    'notes':clean(row['vdd_rmks']),'created_by':clean(row['vdd_crt_by']),
                    'created_at':aware(row['vdd_crt_date']),'updated_by':clean(row['vdd_mod_by']),
                    'updated_at':aware(row['vdd_mod_date']),'modification_count':row['vdd_mod_times'],
                })
                tally['bank_lines'] += 1
        self.stdout.write(str(dict(tally)))
