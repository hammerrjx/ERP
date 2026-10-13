from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport
from backend.models import (GoodsReceipt, PurchaseReturn, InventoryDocument, StockBalance,
    StockTransaction, Material, Location, Uom, Partner, DocumentNumberSequence,
    PurchaseOrder, SalesOrder, SalesReturn, PayableVoucher, StockTransfer, StockCount)
from backend.domain.document_numbers import next_document_number


class WarehouseLoadingNumberTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        data = self.base_context()
        self.context = data
        self.material = Material.objects.get(pk=data['material']['id'])
        self.location = Location.objects.get(pk=data['location']['id'])
        self.uom = Uom.objects.get(pk=data['uom']['id'])
        self.supplier = Partner.objects.create(code='NUMBER-SUP', name='Supplier', kind='supplier')

    def test_business_date_month_reset_import_collision_and_preservation(self):
        imported = GoodsReceipt.objects.create(number='MYPG26092118', supplier=self.supplier, receipt_date=date(2026, 9, 21))
        doc = GoodsReceipt.objects.create(supplier=self.supplier, receipt_date=date(2026, 9, 30))
        self.assertEqual(doc.number, 'MYPG26092119')
        doc.receipt_date = date(2026, 10, 1)
        doc.save()
        self.assertEqual(doc.number, 'MYPG26092119')
        self.assertEqual(GoodsReceipt.objects.create(supplier=self.supplier, receipt_date=date(2026, 10, 1)).number, 'MYPG26100001')
        self.assertEqual(GoodsReceipt.objects.create(supplier=self.supplier, receipt_type='non_production', receipt_date=date(2026, 10, 1)).number, 'MYPUG26100001')
        PurchaseReturn.objects.create(number='MYPT26090113', supplier=self.supplier, return_date=date(2026, 9, 1))
        self.assertEqual(PurchaseReturn.objects.create(supplier=self.supplier, return_date=date(2026, 9, 30)).number, 'MYPT26090114')
        imported.refresh_from_db()
        self.assertEqual(imported.number, 'MYPG26092118')
        DocumentNumberSequence.objects.create(prefix_period='MYMG2609', last_value=9999)
        with self.assertRaises(ValidationError):
            next_document_number('MYMG', date(2026, 9, 1), 'InventoryDocument')

    def test_warehouse_types_and_lightweight_list(self):
        for kind, prefix in [('receipt', 'MYMG'), ('issue', 'MYMU'), ('transfer', 'MYMT'), ('count', 'MYMJ'), ('scrap', 'MYMC')]:
            doc = InventoryDocument.objects.create(kind=kind, document_date=date(2026, 9, 1))
            self.assertEqual(doc.number, prefix + '26090001')
            doc.lines.create(line_number=10, material=self.material, uom=self.uom, quantity=1)
        result = self.client.get('/api/inventory-document/', {'kind': 'receipt', 'summary': '1'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data), 1)
        self.assertNotIn('lines', result.data[0])
        detail = self.client.get(f"/api/inventory-document/{result.data[0]['id']}/")
        self.assertEqual(len(detail.data['lines']), 1)
        compact = self.client.get('/api/material/', {'lookup': 'warehouse'})
        self.assertEqual(compact.status_code, 200)
        self.assertIn('uom', compact.data[0])
        self.assertNotIn('used_in_companies', compact.data[0])

    def test_remote_material_search_bounds_candidates_and_keeps_selected(self):
        Material.objects.bulk_create([Material(code=f'SEARCH-{i:03d}', name='候选物料',
            specification='SPEC', category=self.material.category, uom=self.uom,
            default_location=self.location) for i in range(80)])
        page = self.client.get('/api/material/', {'lookup': 'warehouse'})
        self.assertEqual(len(page.data), 50)
        last = Material.objects.get(code='SEARCH-079')
        found = self.client.get('/api/material/', {'lookup': 'warehouse', 'q': 'SEARCH-079', 'ids': self.material.pk})
        self.assertEqual({r['id'] for r in found.data}, {last.pk, self.material.pk})

    def test_other_source_document_prefixes_and_shared_warehouse_sequence(self):
        day = date(2026, 9, 1)
        currency = self.context['currency']['id']
        for kind, prefix in [('production', 'MYPO'), ('non_production', 'MYPUO'), ('outsource', 'MYPS')]:
            doc = PurchaseOrder.objects.create(supplier=self.supplier, currency_id=currency,
                order_date=day, promised_date=day, tax_rate=0, purchase_type=kind)
            self.assertEqual(doc.number, prefix + '26090001')
        voucher = PayableVoucher.objects.create(supplier=self.supplier, currency_id=currency, voucher_date=day, tax_rate=0)
        self.assertEqual(voucher.number, 'MYAP26090001')
        customer = self.context['customer']['id']
        order = SalesOrder.objects.create(customer_id=customer, currency_id=currency,
            order_date=day, promised_date=day, order_type='2')
        self.assertEqual(order.number, 'MYYP26090001')
        returned = SalesReturn.objects.create(customer_id=customer, no_order=False, return_date=day)
        self.assertEqual(returned.number, 'MYSR26090001')
        transfer = StockTransfer.objects.create(transfer_date=day, from_location=self.location, to_location=self.location)
        self.assertEqual(transfer.number, 'MYMT26090001')
        self.assertEqual(InventoryDocument.objects.create(kind='transfer', document_date=day).number, 'MYMT26090002')
        count = StockCount.objects.create(count_date=day, location=self.location)
        self.assertEqual(count.number, 'MYMJ26090001')
        self.assertEqual(InventoryDocument.objects.create(kind='count', document_date=day).number, 'MYMJ26090002')

    def test_stock_pages_labels_search_and_dates_are_server_side(self):
        for i in range(105):
            StockBalance.objects.create(material=self.material, location=self.location, uom=self.uom, batch_number=str(i), quantity=Decimal(i))
            StockTransaction.objects.create(material=self.material, location=self.location, uom=self.uom,
                batch_number=str(i), quantity=1, balance_after=i, effective_date=date(2026, 9, 1),
                source_model='test', source_id=str(i), source_line_id=str(i), movement_type='110')
        for resource in ['stock-balance', 'stock-transaction']:
            with CaptureQueriesContext(connection) as queries:
                result = self.client.get(f'/api/{resource}/', {'page': 2, 'page_size': 100})
            self.assertEqual(result.status_code, 200, result.data)
            self.assertEqual(result.data['count'], 105)
            self.assertEqual(len(result.data['results']), 5)
            self.assertEqual(result.data['results'][0]['material_code'], self.material.code)
            self.assertLess(len(queries), 8)
            empty = self.client.get(f'/api/{resource}/', {'page': 1, 'q': 'not-found'})
            self.assertEqual(empty.data['count'], 0)
        empty = self.client.get('/api/stock-transaction/', {'page': 1, 'start': '2026-10-01'})
        self.assertEqual(empty.data['count'], 0)
