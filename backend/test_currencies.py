from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

from django.core.management.base import CommandError
from rest_framework.test import APITestCase

from backend.currencies import exchange_rate
from backend.management.commands.sync_currencies import SOURCES, reconcile
from backend.models import Currency, CurrencyRate, Partner, SalesOrder
from backend.test_support import CoreFlowSupport


class CurrencyTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.context = self.base_context()
        self.currency = Currency.objects.get(pk=self.context['currency']['id'])
        self.currency.code = 'RMB'
        self.currency.save()

    def source(self):
        data = {table: [] for table in SOURCES}
        now = datetime(2013, 4, 4)
        data['ex_mstr'] = [dict(ex_curr=c, ex_desc=n, ex_symbol=s, ex_crt_by='IT01', ex_crt_date=now)
                           for c, n, s in [('RMB', '人民币', '￥'), ('HKD', '港币', 'HK$'), ('USD', '美元', '$')]]
        data['exd_det'] = [dict(exd_curr=c, exd_eff_date=start, exd_end_date=end, exd_rate=Decimal(rate),
            exd_end_rate=Decimal(rate), exd_crt_by='IT01', exd_crt_date=now, exd_mod_by='', exd_mod_date=None)
            for c, start, end, rate in [('HKD', now, datetime(2013, 5, 16), '.818'),
                ('HKD', datetime(2013, 5, 17), datetime(2069, 12, 31), '.9'),
                ('USD', now, datetime(2069, 12, 31), '6.23')]]
        data['cm_mstr'] = [dict(cm_addr='C001', cm_curr='HKD', cm_cu_curr='RMB')]
        return data

    def test_dry_run_idempotent_sync_preserves_ids_and_links(self):
        source = self.source()
        preview = reconcile(source)
        self.assertTrue(preview['changes'])
        self.assertEqual(Currency.objects.count(), 1)
        self.assertFalse(CurrencyRate.objects.exists())
        self.assertEqual(Partner.objects.get(code='C001').currency_id, self.currency.pk)
        reconcile(source, True)
        self.assertEqual(Currency.objects.get(code='RMB').pk, self.currency.pk)
        self.assertEqual(Partner.objects.get(code='C001').currency.code, 'HKD')
        self.assertEqual(reconcile(source)['changes'], [])
        self.assertEqual(CurrencyRate.objects.count(), 3)

    def test_effective_date_boundaries_and_native_fallback(self):
        reconcile(self.source(), True)
        hkd = Currency.objects.get(code='HKD')
        for day, rate in [(date(2013,4,3), '1'), (date(2013,4,4), '.818'),
                         (date(2013,5,16), '.818'), (date(2013,5,17), '.9'),
                         (date(2069,12,31), '.9'), (date(2070,1,1), '1')]:
            self.assertEqual(exchange_rate(hkd, day), Decimal(rate))

    def test_native_master_and_rates_cannot_be_overwritten_via_api(self):
        reconcile(self.source(), True)
        for method, path, data in [
            ('patch', f'currency/{self.currency.pk}/', {'code':'CNY', 'source_object':''}),
            ('delete', f'currency/{self.currency.pk}/', {}),
            ('post', 'currency/', {'code':'EUR','name':'欧元'}),
            ('post', f'currency/{self.currency.pk}/unapprove/', {}),
        ]:
            response = getattr(self.client, method)('/api/' + path, data, format='json')
            self.assertEqual(response.status_code, 400, response.data)
        rate = CurrencyRate.objects.first()
        response = self.client.patch(f'/api/currency-rate/{rate.pk}/', {'rate_to_company':'7'}, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        rate.refresh_from_db()
        self.assertNotEqual(rate.rate_to_company, 7)
        self.currency.refresh_from_db()
        self.assertEqual(self.currency.code, 'RMB')

    def test_order_rate_snapshot_and_source_number_collision(self):
        reconcile(self.source(), True)
        usd = Currency.objects.get(code='USD')
        order = self.post('sales-order', {'customer': self.context['customer']['id'], 'currency':usd.pk,
            'order_date':'2026-09-01', 'customer_po':'TEST', 'delivery_address':'仓库', 'promised_date':'2026-09-30'})
        self.assertEqual(Decimal(order['exchange_rate']), Decimal('6.23'))
        CurrencyRate.objects.filter(currency=usd).update(rate_to_company=8)
        response = self.client.patch(f"/api/sales-order/{order['id']}/", {
            'currency':usd.pk, 'order_date':'2026-09-01', 'notes':'只改备注'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data['exchange_rate']), Decimal('6.23'))
        source = self.source()
        source['so_mstr'] = [dict(so_nbr=order['number'], so_curr='RMB', so_ex_rate=1, so_cust='OTHER')]
        result = reconcile(source, True)
        self.assertEqual(SalesOrder.objects.get(pk=order['id']).currency_id, usd.pk)
        self.assertIn('source_number_collision_partner_mismatch', str(result['local_only_documents']))

    def test_unknown_local_currency_and_stale_rates_abort(self):
        Currency.objects.create(code='CNY', name='人民币别名')
        with self.assertRaises(CommandError):
            reconcile(self.source(), True)
        self.assertFalse(CurrencyRate.objects.exists())
        Currency.objects.filter(code='CNY').delete()
        CurrencyRate.objects.create(currency=self.currency, effective_date=date(2020,1,1), rate_to_company=1)
        with self.assertRaises(CommandError):
            reconcile(self.source(), True)

    def test_excel_import_keeps_native_currency_master(self):
        from backend.management.commands.import_legacy_master_data import LegacyImporter
        reconcile(self.source(), True)
        importer = LegacyImporter({})
        with patch('backend.management.commands.import_legacy_master_data.WorkbookRows') as workbook:
            importer.import_currencies()
            workbook.assert_not_called()
        self.assertEqual(set(importer.currencies), {'RMB', 'HKD', 'USD'})

    def test_quote_conversion_uses_effective_currency_rate(self):
        reconcile(self.source(), True)
        quote = self.post('sales-quote', {'customer':self.context['customer']['id'],
            'effective_date':'2026-01-01',
            'lines':[{'material':self.context['material']['id'], 'unit_price':'10'}]})
        for action in ('confirm', 'approve', 'ratify'):
            response = self.client.post(f"/api/sales-quote/{quote['id']}/{action}/", {}, format='json')
            self.assertEqual(response.status_code, 200, response.data)
        order = self.client.post(f"/api/sales-quote/{quote['id']}/convert/", {
            'customer_po':'PO-FX', 'delivery_address':'客户仓库', 'promised_date':'2026-09-30'}, format='json')
        self.assertEqual(order.status_code, 201, order.data)
        self.assertEqual(Decimal(order.data['exchange_rate']), Decimal('.9'))
