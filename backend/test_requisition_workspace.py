from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.test import APITestCase
from backend.test_support import CoreFlowSupport
from backend.models import PurchaseRequisition, PurchaseRequisitionLine, PurchaseOrder, PurchaseOrderLine, StockBalance, StockTransaction
from backend.requisitions import supply_contributions


class RequisitionWorkspaceTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.ctx = self.base_context()
        self.ctx['supplier'] = self.post('partner', {'code':'RQSUP','name':'请购测试供应商','short_name':'测试','kind':'supplier', 'currency':self.ctx['currency']['id'], 'payment_method':'月结30天'})
        self.approve('partner', self.ctx['supplier']['id'])

    def create(self, qty='410'):
        result = self.client.post('/api/purchase-requisition/', {'request_date':'2026-09-21',
            'lines':[{'material':self.ctx['material']['id'],'line_number':10,'requested_qty':qty,'needed_date':'2026-09-20'}]},format='json')
        self.assertEqual(result.status_code,201,result.data)
        return result.data

    def test_manual_edit_keeps_quantity_and_leaves_stock_alone(self):
        before=(StockBalance.objects.count(),StockTransaction.objects.count())
        doc=self.create()
        self.assertTrue(doc['number'].startswith('MYPR2609'))
        self.assertEqual(Decimal(supply_contributions('1000')[0]['quantity']),410)
        doc['lines'][0]['requested_qty']='820'
        result=self.client.put(f"/api/purchase-requisition/{doc['id']}/",doc,format='json')
        self.assertEqual(result.status_code,200,result.data)
        self.assertEqual(Decimal(result.data['lines'][0]['requested_qty']),820)
        stale=self.client.put(f"/api/purchase-requisition/{doc['id']}/",doc,format='json')
        self.assertEqual(stale.status_code,400)
        self.approve('purchase-requisition',doc['id'])
        self.assertEqual(before,(StockBalance.objects.count(),StockTransaction.objects.count()))
        self.assertEqual(Decimal(supply_contributions('1000')[0]['quantity']),820)

    def test_failed_second_line_rolls_back_header_and_number(self):
        data={'lines':[{'material':self.ctx['material']['id'],'requested_qty':'1'},
                       {'material':self.ctx['material']['id'],'requested_qty':'-1'}]}
        result=self.client.post('/api/purchase-requisition/',data,format='json')
        self.assertEqual(result.status_code,400)
        self.assertFalse(PurchaseRequisition.objects.exists())

    def test_manual_requisition_requires_normal_document_and_local_material(self):
        result = self.client.post('/api/purchase-requisition/', {
            'document_type':'S', 'lines':[{'material':self.ctx['material']['id'], 'requested_qty':'1'}]
        }, format='json')
        self.assertEqual(result.status_code, 400)
        result = self.client.post('/api/purchase-requisition/', {
            'lines':[{'source_material_code':'UNMAPPED', 'requested_qty':'1'}]
        }, format='json')
        self.assertEqual(result.status_code, 400)

    def test_new_row_cannot_reuse_saved_row_number(self):
        doc = self.create()
        original_id = doc['lines'][0]['id']
        doc['lines'] = [{'material': self.ctx['material']['id'], 'line_number': 10, 'requested_qty': '1'}]
        result = self.client.put(f"/api/purchase-requisition/{doc['id']}/", doc, format='json')
        self.assertEqual(result.status_code, 400)
        row = PurchaseRequisitionLine.objects.get(pk=original_id)
        self.assertEqual(row.requested_qty, Decimal('410'))

    def test_other_type_read_only_and_metadata_not_client_writable(self):
        doc=self.create()
        PurchaseRequisition.objects.filter(pk=doc['id']).update(requisition_type='S')
        self.assertEqual(self.client.patch(f"/api/purchase-requisition/{doc['id']}/",{'version':doc['version'],'requisition_type':'P'},format='json').status_code,400)
        self.assertEqual(self.client.post(f"/api/purchase-requisition/{doc['id']}/submit/").status_code,400)
        self.assertEqual(self.client.delete(f"/api/purchase-requisition/{doc['id']}/").status_code,400)

    def test_partial_purchase_update_delete_and_overconversion(self):
        doc=self.create()
        self.approve('purchase-requisition',doc['id'])
        req=PurchaseRequisitionLine.objects.get(pk=doc['lines'][0]['id'])
        po=PurchaseOrder.objects.create(supplier_id=self.ctx['supplier']['id'],currency_id=self.ctx['currency']['id'],
            department_id=self.ctx['department']['id'] if 'department' in self.ctx else self.post('department',{'code':'RQ','name':'采购'})['id'],promised_date='2026-09-21',tax_rate=0)
        line=PurchaseOrderLine.objects.create(order=po,line_number=10,material=req.material,uom=req.uom,
            quantity=100,unit_price=1,promised_date='2026-09-21',source_requisition_line=req)
        req.refresh_from_db();self.assertEqual(req.converted_qty,100)
        self.assertEqual(Decimal(supply_contributions('1000')[0]['quantity']),310)
        line.quantity=200;line.save();req.refresh_from_db();self.assertEqual(req.converted_qty,200)
        with self.assertRaises(ValidationError),transaction.atomic():
            line.quantity=500;line.save()
        req.refresh_from_db();self.assertEqual(req.converted_qty,200)
        self.assertEqual(self.client.post(f"/api/purchase-requisition/{doc['id']}/unapprove/").status_code,400)
        PurchaseOrderLine.objects.filter(pk=line.pk).delete()
        req.refresh_from_db();self.assertEqual(req.converted_qty,0)

    def test_source_close_threshold_and_reopen_on_purchase_delete(self):
        doc=self.create('10');self.approve('purchase-requisition',doc['id'])
        req=PurchaseRequisitionLine.objects.get(pk=doc['lines'][0]['id'])
        req.material_snapshot['pt_iss_batch']='3';req.save()
        department=self.post('department',{'code':'RQ','name':'采购'})
        po=PurchaseOrder.objects.create(supplier_id=self.ctx['supplier']['id'],currency_id=self.ctx['currency']['id'],department_id=department['id'],promised_date='2026-09-21',tax_rate=0)
        PurchaseOrderLine.objects.create(order=po,line_number=10,material=req.material,uom=req.uom,quantity=8,unit_price=1,promised_date='2026-09-21',source_requisition_line=req)
        req.refresh_from_db();self.assertEqual(req.line_status,'C')
        self.assertEqual(supply_contributions('1000'),[])
        po.delete();req.refresh_from_db();self.assertEqual(req.converted_qty,0);self.assertEqual(req.line_status,'')

    def test_line_endpoint_cannot_edit_approved_parent(self):
        doc=self.create();self.approve('purchase-requisition',doc['id'])
        row=doc['lines'][0]
        self.assertEqual(self.client.patch(f"/api/purchase-requisition-line/{row['id']}/",{'requested_qty':'99'},format='json').status_code,400)

    def test_convert_purchase_creates_source_link_and_updates_supply(self):
        doc = self.create('10')
        self.approve('purchase-requisition', doc['id'])
        department = self.post('department', {'code': 'BUY', 'name': '采购部'})
        result = self.client.post(f"/api/purchase-requisition/{doc['id']}/convert-purchase/", {
            'supplier_id': self.ctx['supplier']['id'], 'department_id': department['id'],
            'lines': [{'line_id': doc['lines'][0]['id'], 'quantity': '4', 'unit_price': '2.50'}]
        }, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        order = PurchaseOrder.objects.get(pk=result.data['id'])
        line = PurchaseOrderLine.objects.get(order=order)
        self.assertEqual(line.source_requisition_line_id, doc['lines'][0]['id'])
        self.assertEqual(line.quantity, Decimal('4'))
        req = PurchaseRequisitionLine.objects.get(pk=doc['lines'][0]['id'])
        self.assertEqual(req.converted_qty, Decimal('4'))
        self.assertEqual(Decimal(supply_contributions('1000')[0]['quantity']), Decimal('6'))
        order.delete()
        req.refresh_from_db()
        self.assertEqual(req.converted_qty, Decimal('0'))
