from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from backend.test_support import CoreFlowSupport
from backend.models import PurchaseOrder, PurchaseOrderLine, GoodsReceipt, PurchaseReturn, StockBalance, StockTransaction


class ReceivingTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        c=self.base_context(); self.c=c
        supplier=self.post('partner',dict(code='RC-S',name='收退货测试供应商',short_name='RC-S',payment_method='30 days',kind='supplier',currency=c['currency']['id']))
        self.supplier=supplier['id']
        self.order=PurchaseOrder.objects.create(number='RC-PO',supplier_id=self.supplier,currency_id=c['currency']['id'],
            order_date='2026-09-01',promised_date='2026-09-23',payment_method='30 days',tax_rate=0,status='approved')
        self.line=PurchaseOrderLine.objects.create(order=self.order,line_number=10,material_id=c['material']['id'],
            uom_id=c['uom']['id'],quantity=10,spare_quantity=2,unit_price=1,promised_date='2026-09-23',
            uom_rate_m=2,uom_rate_d=1,allocation_managed=True)

    def payload(self,q='4',spare='1',ret=False):
        return dict(supplier=self.supplier,site='1000',supplier_delivery_number='DN-123',
            return_location=self.c['location']['id'],reason='不良',replenishment=True,
            lines=[dict(purchase_order_line=self.line.pk,line_number=10,quantity=q,spare_quantity=spare,
                location=self.c['location']['id'],source_location=self.c['location']['id'],reason='不良')])

    def action(self,resource,doc,action,status=200):
        result=self.client.post(f'/api/{resource}/{doc["id"]}/{action}/',{},format='json')
        self.assertEqual(result.status_code,status,result.data)
        return result.data

    def test_post_confirm_reverse_repost_and_attachment_integrity(self):
        doc=self.post('goods-receipt',self.payload())
        self.assertFalse(StockBalance.objects.exists())
        self.action('goods-receipt',doc,'approve')
        self.action('goods-receipt',doc,'approve')
        self.line.refresh_from_db()
        self.assertEqual((self.line.received_quantity,self.line.received_spare_quantity),(4,1))
        self.assertEqual(StockBalance.objects.get().quantity,10)
        self.assertEqual(StockTransaction.objects.count(),1)
        self.action('goods-receipt',doc,'confirm',400)
        fake=self.client.post('/api/document-evidence/',dict(document_type='goodsreceipt',document_id=doc['id'],
            evidence_type='supplier_delivery',file=SimpleUploadedFile('fake.pdf',b'not pdf')),format='multipart')
        self.assertEqual(fake.status_code,400)
        uploaded=self.client.post('/api/document-evidence/',dict(document_type='goodsreceipt',document_id=doc['id'],
            evidence_type='supplier_delivery',file=SimpleUploadedFile('signed.pdf',b'%PDF-1.4\n document')),format='multipart')
        self.assertEqual(uploaded.status_code,201,uploaded.data)
        self.action('goods-receipt',doc,'confirm')
        self.action('goods-receipt',doc,'unapprove',400)
        self.assertEqual(self.client.delete(f'/api/document-evidence/{uploaded.data["id"]}/').status_code,400)
        self.action('goods-receipt',doc,'unconfirm')
        self.action('goods-receipt',doc,'unapprove')
        self.assertEqual(StockBalance.objects.get().quantity,0)
        self.action('goods-receipt',doc,'approve')
        self.assertEqual(StockBalance.objects.get().quantity,10)
        self.assertEqual(StockTransaction.objects.count(),3)

    def test_reservations_stale_version_spare_only_and_rollback(self):
        doc=self.post('goods-receipt',self.payload('8','0'))
        denied=self.client.post('/api/goods-receipt/',self.payload('3','0'),format='json')
        self.assertEqual(denied.status_code,400,denied.data)
        self.assertEqual(GoodsReceipt.objects.count(),1)
        data=self.payload('7','0');data['version']=0
        result=self.client.put(f'/api/goods-receipt/{doc["id"]}/',data,format='json')
        self.assertEqual(result.status_code,400)
        spare=self.post('goods-receipt',self.payload('0','2'))
        self.action('goods-receipt',spare,'approve')
        self.line.refresh_from_db();self.assertEqual(self.line.received_spare_quantity,2)
        self.assertEqual(StockBalance.objects.get().quantity,4)
        self.assertEqual(self.client.delete(f'/api/goods-receipt/{doc["id"]}/').status_code,204)
        self.post('goods-receipt',self.payload('10','0'))

    def test_return_replenishes_original_order_and_blocks_receipt_reversal(self):
        doc=self.post('goods-receipt',self.payload())
        self.action('goods-receipt',doc,'approve')
        ret=self.post('purchase-return',self.payload('2','1',True))
        self.action('goods-receipt',doc,'unapprove',400)
        self.action('purchase-return',ret,'approve')
        self.assertEqual(PurchaseOrder.objects.count(),1)
        replacement=PurchaseReturn.objects.get().lines.get().replacement_line
        self.assertEqual(replacement.order_id,self.order.pk)
        self.assertEqual(replacement.allocations.get().quantity,2)
        self.assertEqual(StockBalance.objects.get().quantity,4)
        self.action('purchase-return',ret,'unapprove')
        self.assertFalse(PurchaseOrderLine.objects.filter(pk=replacement.pk).exists())
        self.assertEqual(StockBalance.objects.get().quantity,10)
        self.action('purchase-return',ret,'approve')
        self.assertEqual(StockBalance.objects.get().quantity,4)

    def test_imported_posted_is_not_reposted_or_reversed(self):
        doc=self.post('goods-receipt',self.payload())
        GoodsReceipt.objects.filter(pk=doc['id']).update(imported=True,status='approved',posted=True)
        self.action('goods-receipt',doc,'approve')
        self.action('goods-receipt',doc,'unapprove',400)
        self.assertEqual(StockTransaction.objects.count(),0)

    def test_inspection_and_source_system_fields(self):
        self.line.snapshot={'inspection_required':True};self.line.save()
        data=self.payload();data.update(posted=True,status='approved',imported=True,approved_by='forged')
        data['lines'][0].update(material=999,uom_rate_m='1000',accepted_quantity='100')
        doc=self.post('goods-receipt',data)
        self.assertFalse(doc['posted']);self.assertEqual(doc['status'],'draft');self.assertFalse(doc['imported'])
        self.assertEqual(doc['lines'][0]['uom_rate_m'],'2.00000000')
        self.action('goods-receipt',doc,'approve')
        self.line.refresh_from_db();self.assertEqual(self.line.accepted_quantity,0)
        self.assertEqual(GoodsReceipt.objects.get().lines.get().pending_quantity,5)
        self.assertEqual(StockTransaction.objects.get().movement_type,'120')

    def test_closed_purchase_line_can_return_but_cannot_receive(self):
        self.line.line_status='C';self.line.received_quantity=2;self.line.save()
        blocked=self.client.post('/api/goods-receipt/',self.payload('1','0'),format='json')
        self.assertEqual(blocked.status_code,400)
        ret=self.post('purchase-return',self.payload('1','0',True))
        rows=self.client.get(f'/api/purchase-return/candidates/?supplier={self.supplier}').data
        self.assertEqual(rows[0]['purchase_order_line'],self.line.pk)

    def test_inspection_negative_receipt_releases_pending_and_reverses(self):
        self.line.snapshot={'inspection_required':True};self.line.save()
        first=self.post('goods-receipt',self.payload('4','0'))
        self.action('goods-receipt',first,'approve')
        negative=self.post('goods-receipt',self.payload('-1','0'))
        self.action('goods-receipt',negative,'approve')
        self.assertEqual(GoodsReceipt.objects.get(pk=first['id']).lines.get().pending_quantity,3)
        self.action('goods-receipt',first,'unapprove',400)
        self.action('goods-receipt',negative,'unapprove')
        self.assertEqual(GoodsReceipt.objects.get(pk=first['id']).lines.get().pending_quantity,4)
        self.assertEqual(StockBalance.objects.get().quantity,8)

    def test_multiple_order_sources_prevent_source_order_unapproval(self):
        other=PurchaseOrder.objects.create(number='RC-PO-2',supplier_id=self.supplier,currency=self.order.currency,
            order_date='2026-09-01',promised_date='2026-09-23',payment_method='30 days',tax_rate=0,status='approved')
        line=PurchaseOrderLine.objects.create(order=other,line_number=10,material=self.line.material,uom=self.line.uom,
            quantity=5,unit_price=1,promised_date='2026-09-23',allocation_managed=True)
        data=self.payload('1','0');data['lines'].append(dict(data['lines'][0],purchase_order_line=line.pk,line_number=20))
        doc=self.post('goods-receipt',data)
        self.assertIsNone(doc['purchase_order'])
        denied=self.client.post(f'/api/purchase-order/{other.pk}/unapprove/',{},format='json')
        self.assertEqual(denied.status_code,400,denied.data)

    def test_batch_and_cross_supplier_validation_rolls_back(self):
        self.line.material.batch_control=True;self.line.material.save()
        denied=self.client.post('/api/goods-receipt/',self.payload(),format='json')
        self.assertEqual(denied.status_code,400)
        self.assertFalse(GoodsReceipt.objects.exists())
        self.line.material.batch_control=False;self.line.material.save()
        data=self.payload();data['supplier']=self.c['customer']['id']
        denied=self.client.post('/api/goods-receipt/',data,format='json')
        self.assertEqual(denied.status_code,400)
        self.assertFalse(GoodsReceipt.objects.exists())
