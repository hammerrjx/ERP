"""Behavior checks for the complete PR -> PO allocation workflow."""

from decimal import Decimal

import uuid

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport

from backend.models import (PurchaseRequisition, PurchaseRequisitionLine, PurchaseOrder, PurchaseOrderLine,

    PurchaseOrderAllocation, PurchaseGeneration, StockBalance, StockTransaction, Material, Partner, SupplierQuote)





class PurchaseWorkspaceTests(CoreFlowSupport, APITestCase):

    def setUp(self):

        super().setUp();self.ctx=self.base_context()

        self.department=self.post('department',{'code':'PTEST','name':'采购测试部门'})

        self.supplier=self.post('partner',{'code':'PSUP','name':'转单测试供应商','short_name':'转单','kind':'supplier',

            'currency':self.ctx['currency']['id'],'payment_method':'月结30天','tax_rate':'13'})

        self.approve('partner',self.supplier['id'])



    def req(self,qty='10',needed='2026-09-22'):

        r=self.client.post('/api/purchase-requisition/',{'request_date':'2026-09-22','lines':[

            {'material':self.ctx['material']['id'],'line_number':10,'requested_qty':qty,'needed_date':needed}]},format='json')

        self.assertEqual(r.status_code,201,r.data);self.approve('purchase-requisition',r.data['id'])

        return r.data



    def body(self,docs,**options):

        return dict(supplier=self.supplier['id'],department=self.department['id'],consider_pack=False,grouping='2',

            lines=[dict(line_id=d['lines'][0]['id'],quantity=d['lines'][0]['requested_qty'],unit_price='12') for d in docs],**options)



    def preview(self,body):

        r=self.client.post('/api/purchase-requisition/purchase-preview/',body,format='json')

        self.assertEqual(r.status_code,200,r.data);return r.data



    def generate(self,body):

        preview=self.preview(body);body=dict(body,fingerprint=preview['fingerprint'],idempotency_key=str(uuid.uuid4()))

        r=self.client.post('/api/purchase-requisition/purchase-generate/',body,format='json')

        self.assertEqual(r.status_code,201,r.data);return r.data['orders'],body



    def test_merge_multiple_sources_and_idempotent_retry(self):

        a,b=self.req('2'),self.req('6','2026-09-25');body=self.body([a,b])

        before=(StockBalance.objects.count(),StockTransaction.objects.count())

        preview=self.preview(body);self.assertEqual(len(preview['groups'][0]['lines']),1)

        self.assertFalse(PurchaseOrder.objects.exists())

        orders,payload=self.generate(body);order=orders[0]

        self.assertEqual(len(order['lines']),1);self.assertEqual(len(order['lines'][0]['allocations']),2)

        self.assertEqual(Decimal(order['totals']['quantity']),8)

        retry=self.client.post('/api/purchase-requisition/purchase-generate/',payload,format='json')

        self.assertEqual(retry.status_code,200,retry.data);self.assertEqual(PurchaseOrder.objects.count(),1)

        self.assertEqual(before,(StockBalance.objects.count(),StockTransaction.objects.count()))

        self.assertEqual(self.client.delete(f"/api/purchase-order/{order['id']}/").status_code,204)

        self.assertFalse(PurchaseOrderAllocation.objects.exists())

        self.assertEqual(list(PurchaseRequisitionLine.objects.values_list('converted_qty',flat=True)),[Decimal(0),Decimal(0)])



    def test_three_grouping_modes_and_stale_preview(self):

        a,b=self.req('2'),self.req('6','2026-09-25');body=self.body([a,b])

        for grouping,expected in [('1',2),('2',1),('3',2)]:

            body['grouping']=grouping;self.assertEqual(len(self.preview(body)['groups'][0]['lines']),expected)

        token=self.preview(body)['fingerprint']

        PurchaseRequisitionLine.objects.filter(pk=a['lines'][0]['id']).update(converted_qty=1)

        r=self.client.post('/api/purchase-requisition/purchase-generate/',dict(body,fingerprint=token,idempotency_key=str(uuid.uuid4())),format='json')

        self.assertEqual(r.status_code,400);self.assertFalse(PurchaseOrder.objects.exists());self.assertFalse(PurchaseGeneration.objects.exists())



    def test_pack_extra_does_not_consume_request_and_quantity_edit_is_atomic(self):

        Material.objects.filter(pk=self.ctx['material']['id']).update(min_pack_qty=12)

        a=self.req('10');body=self.body([a]);body['consider_pack']=True

        orders,_=self.generate(body);o=orders[0];line=o['lines'][0]

        self.assertEqual(Decimal(line['quantity']),12);self.assertEqual(Decimal(line['extra_quantity']),2)

        self.assertEqual(PurchaseRequisitionLine.objects.get(pk=a['lines'][0]['id']).converted_qty,10)

        line['quantity']='13'

        bad=self.client.put(f"/api/purchase-order/{o['id']}/",o,format='json');self.assertEqual(bad.status_code,400,bad.data)

        self.assertEqual(PurchaseOrderLine.objects.get(pk=line['id']).quantity,12)

        line['quantity']='11';line['allocations'][0]['quantity']='9'

        good=self.client.put(f"/api/purchase-order/{o['id']}/",o,format='json');self.assertEqual(good.status_code,200,good.data)

        self.assertEqual(PurchaseRequisitionLine.objects.get(pk=a['lines'][0]['id']).converted_qty,9)

        stale=self.client.put(f"/api/purchase-order/{o['id']}/",o,format='json');self.assertEqual(stale.status_code,400)



    def test_supplier_split_and_original_quote_not_last_loop_quote(self):

        other=self.post('partner',{'code':'PSUP2','name':'另一供应商','kind':'supplier','short_name':'另一','currency':self.ctx['currency']['id'],'payment_method':'现付','tax_rate':'0'})

        self.approve('partner',other['id'])

        a,b=self.req(),self.req();body=self.body([a,b]);body['lines'][1]['supplier']=other['id']

        orders,_=self.generate(body);self.assertEqual(len(orders),2)

        self.assertEqual({o['supplier'] for o in orders},{self.supplier['id'],other['id']})



    def test_sample_amounts_and_approval_has_no_inventory_movement(self):

        docs=[self.req(q) for q in ['2','850','6']];body=self.body(docs);body['grouping']='1'

        for row,price in zip(body['lines'],['2340','12','720']):row['unit_price']=price

        orders,_=self.generate(body);o=orders[0]

        self.assertEqual(Decimal(o['totals']['amount']),Decimal('19200'))

        self.assertEqual(Decimal(o['totals']['untaxed_amount']),Decimal('16991.18'))

        count=StockTransaction.objects.count()

        r=self.client.post(f"/api/purchase-order/{o['id']}/approve/",format='json')

        self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['status'],'approved')

        self.assertEqual(StockTransaction.objects.count(),count)

        self.assertEqual(self.client.put(f"/api/purchase-order/{o['id']}/",o,format='json').status_code,400)

        self.assertEqual(self.client.post(f"/api/purchase-order/{o['id']}/delivery-approve/").status_code,200)

        self.assertEqual(self.client.post(f"/api/purchase-order/{o['id']}/unapprove/").status_code,400)

        self.assertEqual(self.client.post(f"/api/purchase-order/{o['id']}/delivery-unapprove/").status_code,200)

        self.assertEqual(self.client.post(f"/api/purchase-order/{o['id']}/unapprove/").status_code,200)



    def test_candidate_ranges_unmapped_and_read_only_permission(self):

        a=self.req();r=self.client.get('/api/purchase-requisition/purchase-candidates/',{'number':a['number']})

        self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['count'],1)

        r=self.client.get('/api/purchase-requisition/purchase-candidates/',{'number':'not-exist'});self.assertEqual(r.data['count'],0)

        user=get_user_model().objects.create_user('no-permissions')

        self.client.force_authenticate(user)

        r=self.client.post('/api/purchase-requisition/purchase-generate/',{},format='json');self.assertEqual(r.status_code,403)



    def test_nonfinite_negative_duplicate_and_zero_denominator_input(self):

        a=self.req();body=self.body([a])

        for value in ['NaN','Infinity','-1','0']:

            body['lines'][0]['quantity']=value

            r=self.client.post('/api/purchase-requisition/purchase-preview/',body,format='json');self.assertEqual(r.status_code,400)

        body=self.body([a,a]);r=self.client.post('/api/purchase-requisition/purchase-preview/',body,format='json');self.assertEqual(r.status_code,400)



    def test_export_contains_both_tables_and_all_columns(self):

        from openpyxl import load_workbook

        from io import BytesIO

        orders,_=self.generate(self.body([self.req()]))

        r=self.client.get(f"/api/purchase-order/{orders[0]['id']}/export/")

        self.assertEqual(r.status_code,200)

        book=load_workbook(BytesIO(b''.join(r.streaming_content)))

        self.assertEqual(book['采购明细'].max_column,55)

        self.assertEqual(book['关联请购明细'].max_column,18)



    def test_receipt_return_replacement_and_payable_use_frozen_units_and_tax(self):

        a=self.req('20')

        quote=SupplierQuote.objects.create(supplier_id=self.supplier['id'],material_id=self.ctx['material']['id'],

            currency_id=self.ctx['currency']['id'],purchase_uom_id=self.ctx['uom']['id'],quote_type='purchase',

            effective_date='2026-01-01',status='approved',is_confirmed=True,is_ratified=True,

            uom_rate_m=10,uom_rate_d=1,unit_price=113,material_unit_price=113,tax_rate=13)

        body=self.body([a]);body['lines'][0]['unit_price']='113'

        orders,_=self.generate(body);o=orders[0];line=o['lines'][0]

        self.assertEqual(Decimal(line['quantity']),2)

        self.approve('purchase-order',o['id'])

        SupplierQuote.objects.filter(pk=quote.pk).update(uom_rate_m=99)

        receipt=self.post('goods-receipt',{'supplier':self.supplier['id'],'purchase_order':o['id'],'receipt_date':'2026-09-22','supplier_delivery_number':'DN-TEST'})

        received=self.post('goods-receipt-line',{'receipt':receipt['id'],'line_number':10,'purchase_order_line':line['id'],

            'material':self.ctx['material']['id'],'uom':self.ctx['uom']['id'],'quantity':'2','location':self.ctx['location']['id']})

        self.approve('goods-receipt',receipt['id'])

        self.assertEqual(StockBalance.objects.get(material_id=self.ctx['material']['id']).quantity,20)

        voucher=self.client.post('/api/payable-voucher/auto-generate/',{'voucher_date':'2026-09-22','receipt_line_ids':[received['id']]},format='json')

        self.assertEqual(voucher.status_code,201,voucher.data)

        self.assertEqual(voucher.data[0]['gross_amount'],'226.00')

        self.assertEqual(voucher.data[0]['net_amount'],'200.00')

        ret=self.post('purchase-return',{'supplier':self.supplier['id'],'purchase_order':o['id'],'reason':'退货补货','replenishment':True,'return_location':self.ctx['location']['id']})

        self.post('purchase-return-line',{'purchase_return':ret['id'],'line_number':10,'purchase_order_line':line['id'],

            'material':self.ctx['material']['id'],'uom':self.ctx['uom']['id'],'quantity':'1','source_location':self.ctx['location']['id'],'reason':'退货补货'})

        self.approve('purchase-return',ret['id'])

        self.assertEqual(StockBalance.objects.get(material_id=self.ctx['material']['id']).quantity,10)

        self.assertEqual(PurchaseRequisitionLine.objects.get(pk=a['lines'][0]['id']).converted_qty,20)

        replacement=PurchaseOrder.objects.get(pk=o['id']).lines.exclude(pk=line['id']).get()

        self.assertTrue(replacement.allocation_managed);self.assertEqual(replacement.allocations.get().kind,'2')

        self.assertEqual(replacement.uom_rate_m,10)

        self.assertEqual(self.client.post(f"/api/purchase-order/{o['id']}/unapprove/").status_code,400)



    def test_lowest_price_supplier_precedes_default_and_rejects_bad_ratio(self):
        a=self.req()

        other=self.post('partner',{'code':'LOW','name':'低价供应商','short_name':'低价','kind':'supplier','currency':self.ctx['currency']['id'],'payment_method':'现付'})

        self.approve('partner',other['id'])

        Material.objects.filter(pk=self.ctx['material']['id']).update(default_supplier_id=self.supplier['id'])

        for supplier,price in [(self.supplier['id'],20),(other['id'],10)]:

            SupplierQuote.objects.create(supplier_id=supplier,material_id=self.ctx['material']['id'],currency_id=self.ctx['currency']['id'],

                quote_type='purchase',effective_date='2026-01-01',unit_price=price,material_unit_price=price,

                status='approved',is_confirmed=True,is_ratified=True)

        body=self.body([a]);body.pop('supplier');body['lines'][0].pop('unit_price')

        self.assertEqual(self.preview(body)['groups'][0]['supplier'],other['id'])

        SupplierQuote.objects.filter(supplier_id=other['id']).update(uom_rate_d=0)

        bad=self.client.post('/api/purchase-requisition/purchase-preview/',body,format='json')

        self.assertEqual(bad.status_code,400)

    def test_supplier_spare_and_over_receipt_round_to_issue_batch(self):
        Partner.objects.filter(pk=self.supplier['id']).update(backup_ratio=5,over_receipt_ratio=12)
        Material.objects.filter(pk=self.ctx['material']['id']).update(min_issue_qty=1)
        orders,_=self.generate(self.body([self.req('10')]))
        line=orders[0]['lines'][0]
        self.assertEqual(Decimal(line['spare_quantity']),1)
        self.assertEqual(Decimal(line['over_receipt_quantity']),2)
        self.assertEqual(Decimal(line['quantity']),10)

    def test_supplier_refresh_keeps_purchase_unit_and_quote_price(self):
        a=self.req('20')
        SupplierQuote.objects.create(supplier_id=self.supplier['id'],material_id=self.ctx['material']['id'],
            currency_id=self.ctx['currency']['id'],purchase_uom_id=self.ctx['uom']['id'],quote_type='purchase',
            effective_date='2026-01-01',status='approved',is_confirmed=True,is_ratified=True,
            uom_rate_m=10,uom_rate_d=1,unit_price=113,material_unit_price=113,tax_rate=13)
        response=self.client.get('/api/purchase-requisition/purchase-candidates/',
            {'ids':str(a['lines'][0]['id']),'supplier':self.supplier['id'],'order_date':'2026-09-22'})
        self.assertEqual(response.status_code,200,response.data)
        row=response.data['results'][0]
        self.assertEqual(Decimal(row['original_price']),113)
        self.assertEqual(Decimal(row['uom_rate_m']),10)
        body=self.body([a]);body['lines'][0].pop('unit_price')
        preview=self.preview(body)['groups'][0]['lines'][0]
        self.assertEqual(Decimal(preview['quantity']),2)
        self.assertEqual(Decimal(preview['amount']),226)
        orders,_=self.generate(body)
        saved=orders[0];line=saved['lines'][0]
        line['allocations']=[line['allocations'][0],line['allocations'][0]]
        bad=self.client.put(f"/api/purchase-order/{saved['id']}/",saved,format='json')
        self.assertEqual(bad.status_code,400)
        self.assertEqual(PurchaseRequisitionLine.objects.get(pk=a['lines'][0]['id']).converted_qty,20)
