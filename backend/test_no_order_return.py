from datetime import date
from decimal import Decimal

from django.test import override_settings
from rest_framework.test import APITestCase

from backend.models import (Employee, InventoryPostingControl, Location, StockBalance,
    StockTransaction, CustomerMaterial, Partner, SalesReturn, SalesReturnHistory, Uom)
from backend.test_support import CoreFlowSupport


@override_settings(ERP_NO_ORDER_RETURN_POST_STOCK=True)
class NoOrderReturnApiTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.context = self.base_context()
        self.location = Location.objects.get(pk=self.context['location']['id'])
        self.location.source_site = '1000'
        self.location.save(update_fields=['source_site'])
        Employee.objects.create(code='IT01', name='测试业务员', group_code='SDGROUP')
        self.control = InventoryPostingControl.objects.create(
            site='1000', min_date=date(2026, 1, 1), max_date=date(2026, 12, 31),
            calendar=[{'start': '2026-09-01', 'end': '2026-09-30', 'year': 2026, 'month': 9, 'frozen': False}],
            location_permissions={'FG01': ['*']},
        )

    def sheet(self, **changes):
        data = {
            'customer': self.context['customer']['id'], 'currency': self.context['currency']['id'],
            'return_date': '2026-09-18', 'customer_po': 'CPO-RETURN', 'business_group': 'IT01',
            'lines': [{'material': self.context['material']['id'], 'quantity': '2', 'spare_quantity': '1',
                       'unit_price': '5', 'return_location': self.location.pk}],
        }
        data.update(changes)
        return data

    def create_doc(self, data=None):
        saved = self.client.post('/api/no-order-return/', data or self.sheet(), format='json')
        self.assertEqual(saved.status_code, 201, saved.data)
        return saved.data

    def act(self, doc, action, status=200):
        result = self.client.post(f"/api/no-order-return/{doc['id']}/{action}/", {'revision': doc['revision']}, format='json')
        self.assertEqual(result.status_code, status, result.data)
        return result.data

    def test_rate_fallback_and_saved_snapshot(self):
        from backend.models import Currency, CurrencyRate
        usd = Currency.objects.create(code='USD', name='美元')
        saved = self.create_doc(self.sheet(currency=usd.pk))
        self.assertEqual(Decimal(saved['exchange_rate']), 1)
        CurrencyRate.objects.create(currency=usd, effective_date=date(2026,1,1), rate_to_company=Decimal('6.23'))
        data = self.sheet(currency=usd.pk, revision=saved['revision'], reason='仅修改备注')
        response = self.client.patch(f"/api/no-order-return/{saved['id']}/", data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data['exchange_rate']), 1)
        data.update(return_date='2026-09-19', revision=response.data['revision'])
        response = self.client.patch(f"/api/no-order-return/{saved['id']}/", data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data['exchange_rate']), Decimal('6.23'))

    def test_native_sign_spares_nonunit_conversion_and_reaudit(self):
        cp = CustomerMaterial.objects.create(customer_id=self.context['customer']['id'], material_id=self.context['material']['id'],
            customer_code='CUST-01', terminal_customer_code='END-01', terminal_customer_name='终端物料',
            customer_uom_id=self.context['uom']['id'], customer_uom_rate_m=3, customer_uom_rate_d=2)
        saved = self.create_doc()
        self.assertEqual(saved['lines'][0]['terminal_customer_code'], 'END-01')
        self.assertEqual(saved['lines'][0]['uom_rate_m'], '3.00000000')
        cp.customer_uom_rate_m = 7
        cp.save()
        approved = self.act(saved, 'approve')
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('4.5'))
        self.assertEqual(StockTransaction.objects.get().movement_type, '261')
        self.assertEqual(SalesReturnHistory.objects.get().quantity, -2)
        self.assertEqual(SalesReturnHistory.objects.get().spare_quantity, -1)
        self.assertEqual(SalesReturnHistory.objects.get().snapshot['amount'], '-10.00')
        self.act(approved, 'approve')
        self.assertEqual(StockTransaction.objects.count(), 1)
        unposted = self.act(approved, 'unapprove')
        self.assertEqual(StockBalance.objects.get().quantity, 0)
        self.assertFalse(SalesReturnHistory.objects.get().active)
        reposted = self.act(unposted, 'approve')
        self.assertEqual(reposted['posting_version'], 2)
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('4.5'))
        self.assertEqual(SalesReturnHistory.objects.filter(active=True).count(), 1)

    def test_consignment_transfer_and_rollback_even_if_location_allows_negative(self):
        Partner.objects.filter(pk=self.context['customer']['id']).update(consignment=True)
        customer_location = Location.objects.create(code='C001', name='客户寄售仓', source_site='1000', allow_negative=True)
        doc = self.create_doc()
        self.act(doc, 'approve', 400)
        self.assertFalse(StockTransaction.objects.exists())
        self.assertEqual(SalesReturn.objects.get(pk=doc['id']).status, 'draft')
        self.post('stock-balance', {'material': self.context['material']['id'], 'location': customer_location.pk,
            'uom': self.context['uom']['id'], 'quantity': '3'})
        doc = self.act(doc, 'approve')
        postings = StockTransaction.objects.filter(source_model='backend.salesreturn')
        self.assertEqual(set(postings.values_list('movement_type', 'quantity')), {('250', Decimal(-3)), ('150', Decimal(3))})
        self.assertFalse(SalesReturnHistory.objects.exists())
        # Reversal follows the original stock records even when current partner settings differ.
        Partner.objects.filter(pk=self.context['customer']['id']).update(consignment=False)
        self.act(doc, 'unapprove')
        self.assertEqual(StockBalance.objects.get(location=customer_location).quantity, 3)
        self.assertEqual(StockBalance.objects.get(location=self.location).quantity, 0)

    def test_insufficient_stock_on_unapprove_preserves_audit_and_history(self):
        doc = self.act(self.create_doc(), 'approve')
        StockBalance.adjust(material=StockBalance.objects.get().material, location=self.location,
            uom=StockBalance.objects.get().uom, quantity=-1, movement_type='260', source_model='test',
            source_id='1', source_line_id='1', actor='test')
        self.act(doc, 'unapprove', 400)
        self.assertTrue(SalesReturn.objects.get(pk=doc['id']).posted)
        self.assertTrue(SalesReturnHistory.objects.get().active)
        self.assertEqual(StockBalance.objects.get().quantity, 2)
        self.assertEqual(StockTransaction.objects.count(), 2)

    def test_derived_fields_sources_and_multimatch_are_protected(self):
        data = self.sheet()
        data['lines'][0]['uom_rate_m'] = '99'
        self.assertEqual(self.client.post('/api/no-order-return/', data, format='json').status_code, 400)
        data = self.sheet(source_delivery=99)
        self.assertEqual(self.client.post('/api/no-order-return/', data, format='json').status_code, 400)
        for code in ('A', 'B'):
            CustomerMaterial.objects.create(customer_id=self.context['customer']['id'], material_id=self.context['material']['id'], customer_code=code)
        self.assertEqual(self.client.post('/api/no-order-return/', self.sheet(), format='json').status_code, 400)
        self.assertFalse(SalesReturn.objects.exists())
        data = self.sheet()
        data['lines'][0]['customer_material'] = CustomerMaterial.objects.get(customer_code='B').pk
        doc = self.create_doc(data)
        self.assertEqual(doc['lines'][0]['customer_material_code'], 'B')
        raw = self.client.patch(f"/api/sales-return-line/{doc['lines'][0]['id']}/", {'quantity': '50'}, format='json')
        self.assertEqual(raw.status_code, 400)
        raw = self.client.patch(f"/api/sales-return/{doc['id']}/", {'no_order': False}, format='json')
        self.assertEqual(raw.status_code, 400)

    def test_period_permissions_and_financial_references(self):
        doc = self.create_doc()
        self.control.closed_year, self.control.closed_month = 2026, 9
        self.control.save()
        self.act(doc, 'approve', 400)
        self.control.closed_year = self.control.closed_month = 0
        self.control.calendar[0]['frozen'] = True
        self.control.save()
        self.act(doc, 'approve', 400)
        self.control.calendar[0]['frozen'] = False
        self.control.location_permissions = {}
        self.control.save()
        self.act(doc, 'approve', 400)
        self.control.location_permissions = {'FG01': ['*']}
        self.control.save()
        doc = self.act(doc, 'approve')
        SalesReturn.objects.filter(pk=doc['id']).update(downstream_references=['AR-1'])
        self.act(doc, 'unapprove', 400)
        self.assertTrue(SalesReturn.objects.get(pk=doc['id']).posted)

    def test_receipt_actions_dont_post_and_export_has_correct_amount(self):
        doc = self.act(self.create_doc(), 'approve')
        for action in ('confirm', 'sign', 'unsign', 'unconfirm'):
            doc = self.act(doc, action)
        self.assertEqual(StockTransaction.objects.count(), 1)
        export = self.client.post(f"/api/no-order-return/{doc['id']}/export/", {}, format='json')
        self.assertEqual(export.status_code, 200)
        from io import BytesIO
        from openpyxl import load_workbook
        sheet = load_workbook(BytesIO(export.content), data_only=True).active
        rows = list(sheet.values)
        self.assertEqual(rows[1][13], 10)

    def test_batch_site_and_stale_revision(self):
        from backend.models import Material
        Material.objects.filter(pk=self.context['material']['id']).update(batch_control=True, batch_rule='LOT')
        doc = self.create_doc()
        self.act(doc, 'approve', 400)
        body = self.sheet(revision=doc['revision'])
        body['lines'][0].update(id=doc['lines'][0]['id'], batch_number='LOT-001')
        update = self.client.patch(f"/api/no-order-return/{doc['id']}/", body, format='json')
        self.assertEqual(update.status_code, 200, update.data)
        self.act(doc, 'approve', 400)
        self.act(update.data, 'approve')
        self.assertEqual(StockTransaction.objects.get().batch_number, 'LOT-001')
        self.assertEqual(self.client.post('/api/no-order-return/', self.sheet(site='2000'), format='json').status_code, 400)

    @override_settings(ERP_NO_ORDER_RETURN_POST_STOCK=False)
    def test_disabled_posting_fails_explicitly_without_status_change(self):
        doc = self.create_doc()
        self.act(doc, 'approve', 400)
        self.assertFalse(StockTransaction.objects.exists())
        self.assertEqual(SalesReturn.objects.get().status, 'draft')
