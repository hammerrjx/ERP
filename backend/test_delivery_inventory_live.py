from decimal import Decimal
import uuid

from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport
from backend.models import DeliveryOrder, Location, SalesOrderLine, StockBalance, StockTransaction
from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportRow
from backend.domain.inventory_analysis import InventoryAnalysisSnapshot


class LiveDeliveryInventoryTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.ctx = self.base_context()
        Location.objects.filter(pk=self.ctx['location']['id']).update(source_site='1000')
        self.post('stock-balance', {'material': self.ctx['material']['id'],
            'location': self.ctx['location']['id'], 'uom': self.ctx['uom']['id'], 'quantity': '150000'})
        self.history = InventoryReportBatch.objects.create(source='coerp_dgyzx1')
        self.batch = InventoryReportBatch.objects.create(source='local', active=True,
            manifest={'operational': True, 'baseline_batch_id': self.history.pk,
                      'local_contributions': {}, 'site': '1000'})
        self.code = self.ctx['material']['code']
        for batch in (self.history, self.batch):
            InventoryReportRow.objects.create(batch=batch, kind='inventory', source_table='ld_det',
                source_key='baseline', site='1000', material_code=self.code, location_code='FG01',
                location_type='FG', payload={'site': '1000', 'material_code': self.code,
                    'location_code': 'FG01', 'batch_number': '', 'quantity': '150000',
                    'location_type': 'FG', 'uom_code': 'JIAN'})
        InventoryAnalysisSnapshot.objects.create(kind='bulk', site='1000', payload={
            'rows': [{'tmp_part': self.code, 'pt_desc1': '产品', 'tmp_qty_oh': '150000',
                'tmp_qty_req_total': '0', 'tmp_qty_alloc': '0', 'tmp_qty_on_order': '0',
                'tmp_qty_req_open': '0', 'tmp_sfty_stk': '0', 'tmp_qty_remain': '150000',
                'tmp_qty_unalloc': '150000'}],
            'details': [{'tab': 'stock', 'part': self.code, 'quantity': '150000',
                'location': 'FG01', 'lot': '', 'nettable': True, 'location_type': 'FG'}]})
        self.order = self.post('sales-order', {'customer': self.ctx['customer']['id'],
            'currency': self.ctx['currency']['id'], 'customer_po': 'LIVE',
            'delivery_address': '测试', 'promised_date': '2026-09-21'})
        self.line = self.post('sales-order-line', {'order': self.order['id'], 'line_number': 10,
            'material': self.ctx['material']['id'], 'uom': self.ctx['uom']['id'],
            'quantity': '5000', 'unit_price': '1', 'promised_date': '2026-09-21'})
        self.approve('sales-order', self.order['id'])

    def delivery(self, quantity='5000'):
        reserved = self.client.post('/api/delivery-order/reserve-number/',
            {'request_id': str(uuid.uuid4()), 'delivery_date': '2026-09-21'}, format='json')
        self.assertEqual(reserved.status_code, 201, reserved.data)
        response = self.client.post('/api/delivery-order/save-sheet/', {**reserved.data,
            'customer': self.ctx['customer']['id'], 'delivery_date': '2026-09-21',
            'delivery_address': '测试', 'lines': [{'sales_order_line': self.line['id'],
                'actual_quantity': quantity}]}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def bulk(self):
        response = self.client.get('/api/material-inventory-batch/', {'site': '1000', 'source': 'local'})
        self.assertEqual(response.status_code, 200, response.data)
        return response.data['results'][0]

    def test_synced_sales_replace_source_baseline_once_and_keep_order_site(self):
        from backend.live_inventory import local_contributions
        self.batch.manifest['local_contributions']=local_contributions(self.batch)
        self.batch.manifest['trade_sync']={'source_sales_numbers':[self.order['number']], 'material_codes':[self.code]}
        self.batch.save()
        snapshot=InventoryAnalysisSnapshot.objects.get(kind='bulk')
        snapshot.payload['details'].append({'tab':'demand','part':self.code,'kind':'销售订单',
            'document':self.order['number'],'quantity':'5000'})
        snapshot.save()
        SalesOrderLine.objects.filter(pk=self.line['id']).update(quantity=6000)
        self.assertEqual(Decimal(self.bulk()['tmp_qty_req_total']),6000)
        Location.objects.filter(pk=self.ctx['location']['id']).update(source_site='2000')
        self.assertEqual(Decimal(self.bulk()['tmp_qty_req_total']),6000)
        from backend.models import Material
        Material.objects.filter(pk=self.ctx['material']['id']).update(default_location=None)
        self.assertEqual(Decimal(self.bulk()['tmp_qty_req_total']),6000)

    def test_approval_updates_balance_all_reports_and_order_once(self):
        delivery = self.delivery()
        self.approve('delivery-order', delivery['id'])
        self.assertEqual(StockBalance.objects.get(material_id=self.ctx['material']['id']).quantity, Decimal('145000'))
        self.assertTrue(DeliveryOrder.objects.get(pk=delivery['id']).stock_posted)
        report = self.client.get('/api/material-inventory-detail/', {'source': 'local', 'site': '1000'})
        self.assertEqual(Decimal(report.data['results'][0]['quantity']), Decimal('145000'))
        movements = self.client.get('/api/material-movement-detail/',
            {'source': 'local', 'site': '1000', 'document_number': delivery['number']})
        self.assertEqual(movements.data['count'], 1)
        movement = movements.data['results'][0]
        self.assertEqual((movement['movement_type'], Decimal(movement['issue_quantity'])), ('260', Decimal('5000')))
        self.assertEqual(movement['order_number'], self.order['number'])
        self.assertEqual(Decimal(self.bulk()['tmp_qty_oh']), Decimal('145000'))
        duplicate = self.client.post(f"/api/delivery-order/{delivery['id']}/approve/")
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(StockTransaction.objects.filter(movement_type='260').count(), 1)
        self.assertEqual(SalesOrderLine.objects.get(pk=self.line['id']).delivered_quantity, Decimal('5000'))
        self.assertEqual(InventoryReportRow.objects.get(batch=self.history).payload['quantity'], '150000')

    def test_live_material_missing_from_bulk_baseline(self):
        InventoryAnalysisSnapshot.objects.filter(kind='bulk').update(payload={'rows': [], 'details': []})
        row = self.bulk()
        self.assertEqual(Decimal(row['tmp_qty_oh']), Decimal('150000'))
        self.assertEqual(Decimal(row['tmp_qty_req_total']), Decimal('5000'))
        delivery = self.delivery()
        self.approve('delivery-order', delivery['id'])
        self.assertEqual(Decimal(self.bulk()['tmp_qty_oh']), Decimal('145000'))

    def test_order_demand_and_draft_allocation_release_on_approval(self):
        self.assertEqual(Decimal(self.bulk()['tmp_qty_req_total']), Decimal('5000'))
        delivery = self.delivery()
        self.assertEqual(Decimal(self.bulk()['tmp_qty_alloc']), Decimal('5000'))
        self.assertEqual(Decimal(self.bulk()['tmp_qty_oh']), Decimal('150000'))
        self.approve('delivery-order', delivery['id'])
        row = self.bulk()
        self.assertEqual(Decimal(row['tmp_qty_req_total']), 0)
        self.assertEqual(Decimal(row['tmp_qty_alloc']), 0)
        self.assertEqual(Decimal(row['tmp_qty_remain']), Decimal('145000'))

    def test_draft_requisition_drilldown_does_not_change_balance_until_approved(self):
        created = self.client.post('/api/purchase-requisition/', {
            'request_date':'2026-09-21', 'lines':[{'material':self.ctx['material']['id'],
                'line_number':10, 'requested_qty':'2000', 'needed_date':'2026-09-21'}]
        }, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        row = self.bulk()
        self.assertEqual(Decimal(row['tmp_qty_req_open']), Decimal('2000'))
        self.assertEqual(Decimal(row['tmp_qty_remain']), Decimal('145000'))
        details = self.client.get('/api/material-inventory-batch/details/', {
            'site':'1000', 'source':'local', 'part':self.code, 'tab':'requisition'})
        self.assertEqual(details.status_code, 200, details.data)
        self.assertEqual(Decimal(details.data['total']), Decimal('2000'))
        self.assertFalse(details.data['results'][0]['eligible_for_balance'])
        self.approve('purchase-requisition', created.data['id'])
        row = self.bulk()
        self.assertEqual(Decimal(row['tmp_qty_req_open']), Decimal('2000'))
        self.assertEqual(Decimal(row['tmp_qty_remain']), Decimal('147000'))

    def test_stock_failure_rolls_back_order_approval_and_reports(self):
        StockBalance.objects.filter(material_id=self.ctx['material']['id']).update(quantity=Decimal('100'))
        delivery = self.delivery()
        self.client.post(f"/api/delivery-order/{delivery['id']}/submit/")
        result = self.client.post(f"/api/delivery-order/{delivery['id']}/approve/")
        self.assertEqual(result.status_code, 400, result.data)
        self.assertEqual(SalesOrderLine.objects.get(pk=self.line['id']).delivered_quantity, 0)
        self.assertFalse(DeliveryOrder.objects.get(pk=delivery['id']).posted)
        self.assertFalse(StockTransaction.objects.filter(movement_type='260').exists())

    def test_negative_delivery_restores_stock_without_touching_history(self):
        sent = self.delivery()
        self.approve('delivery-order', sent['id'])
        returned = self.delivery('-2000')
        self.approve('delivery-order', returned['id'])
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('147000'))
        self.assertEqual(Decimal(self.bulk()['tmp_qty_oh']), Decimal('147000'))
        self.assertEqual(Decimal(self.bulk()['tmp_qty_req_total']), Decimal('2000'))
        self.assertEqual(set(StockTransaction.objects.filter(source_model='backend.deliveryorder')
            .values_list('movement_type', flat=True)), {'260'})

    def test_spares_and_non_one_native_rate_in_same_unit(self):
        SalesOrderLine.objects.filter(pk=self.line['id']).update(spare_quantity=100, uom_rate_m=2, uom_rate_d=1)
        sent = self.delivery()
        from backend.models import DeliveryOrderLine
        DeliveryOrderLine.objects.filter(delivery_id=sent['id']).update(actual_spare_quantity=100)
        self.approve('delivery-order', sent['id'])
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('139800'))
        transaction = StockTransaction.objects.get(movement_type='260')
        self.assertEqual((transaction.business_quantity, transaction.quantity), (Decimal('-5100'), Decimal('-10200')))

    def test_second_line_failure_rolls_back_first_line(self):
        from backend.models import DeliveryOrderLine
        StockBalance.objects.update(quantity=4000)
        sent = self.delivery('2500')
        second = DeliveryOrderLine.objects.get(delivery_id=sent['id'])
        second.pk, second.line_number = None, 20
        second.save()
        self.client.post(f"/api/delivery-order/{sent['id']}/submit/")
        response = self.client.post(f"/api/delivery-order/{sent['id']}/approve/")
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(StockBalance.objects.get().quantity, 4000)
        self.assertEqual(SalesOrderLine.objects.get(pk=self.line['id']).delivered_quantity, 0)
        self.assertFalse(StockTransaction.objects.filter(movement_type='260').exists())

    def test_consignment_posts_both_warehouses(self):
        from backend.models import SalesOrder
        SalesOrder.objects.filter(pk=self.order['id']).update(consignment=True)
        Location.objects.create(code=self.ctx['customer']['code'], name='客户寄售仓', source_site='1000', participate_mrp=False)
        sent = self.delivery()
        self.approve('delivery-order', sent['id'])
        values = list(StockTransaction.objects.filter(source_model='backend.deliveryorder')
            .order_by('movement_type').values_list('movement_type', 'quantity'))
        self.assertEqual(values, [('150', Decimal('5000')), ('250', Decimal('-5000'))])
        self.assertEqual(sum(StockBalance.objects.values_list('quantity', flat=True)), Decimal('150000'))

    def test_lazy_opening_for_newly_available_material(self):
        StockTransaction.objects.all().delete()
        StockBalance.objects.all().delete()
        sent = self.delivery()
        self.approve('delivery-order', sent['id'])
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('145000'))
        self.assertEqual(StockTransaction.objects.get(movement_type='opening').quantity, Decimal('150000'))

    def test_unapprove_and_reapprove_preserve_audit_and_do_not_double_post(self):
        sent = self.delivery()
        self.approve('delivery-order', sent['id'])
        result = self.client.post(f"/api/delivery-order/{sent['id']}/unapprove/")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('150000'))
        self.assertEqual(SalesOrderLine.objects.get(pk=self.line['id']).delivered_quantity, 0)
        self.assertEqual(StockTransaction.objects.filter(reversal_of__isnull=False).count(), 1)
        self.approve('delivery-order', sent['id'])
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('145000'))
        self.assertEqual(DeliveryOrder.objects.get(pk=sent['id']).posting_version, 2)
        self.assertEqual(StockTransaction.objects.filter(movement_type='260').count(), 3)
        self.assertEqual(Decimal(self.bulk()['tmp_qty_oh']), Decimal('145000'))

    def test_source_reimport_cannot_disable_local_posting(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        with self.assertRaisesMessage(CommandError, '本地业务账已启用'):
            call_command('import_inventory_reports', input='not-read', apply=True, activate=True)

    def test_activation_preserves_visible_opening_and_is_idempotent(self):
        from django.core.management import call_command
        from io import StringIO
        self.batch.active = False
        self.batch.save()
        StockTransaction.objects.update(movement_type='opening')
        call_command('activate_local_inventory', baseline=self.history.pk, apply=True, stdout=StringIO())
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('150000'))
        count = StockTransaction.objects.count()
        call_command('activate_local_inventory', baseline=self.history.pk, apply=True, stdout=StringIO())
        self.assertEqual(StockTransaction.objects.count(), count)

    def test_export_uses_current_quantity(self):
        from io import BytesIO
        from openpyxl import load_workbook
        sent = self.delivery()
        self.approve('delivery-order', sent['id'])
        response = self.client.post('/api/material-inventory-detail/export/',
            {'filters': {'source': 'local'}}, format='json')
        self.assertEqual(response.status_code, 200)
        book = load_workbook(BytesIO(b''.join(response.streaming_content)), read_only=True)
        rows = list(book['明细'].values)
        self.assertEqual(rows[1][rows[0].index('库存数量')], 145000)
        response.close()
