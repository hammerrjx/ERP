"""One complete trade supply-chain path using one newly created material."""
from decimal import Decimal
import json
import os
from pathlib import Path

from django.test import override_settings
from rest_framework.test import APITestCase

from backend.domain.trade_mrp import calculate_trade_mrp, confirm_trade_mrp
from backend.models import (
    DeliveryOrder,
    GoodsReceipt,
    PurchaseOrder,
    PurchaseRequisition,
    SalesOrderLine,
    StockBalance,
    StockTransaction,
)
from backend.test_support import CoreFlowSupport


@override_settings(ERP_TRADE_MRP_GENERATION_ENABLED=True, ERP_DELIVERY_POST_STOCK=False)
class TradeSupplyChainE2ETests(CoreFlowSupport, APITestCase):
    """Verify document links and ledger balance across one project-sized demand."""

    def setUp(self):
        super().setUp()
        self.ctx = self.base_context()
        from backend.domain.inventory_reports import InventoryReportBatch
        from backend.domain.inventory_analysis import InventoryAnalysisSnapshot
        from backend.models import Location
        Location.objects.filter(pk=self.ctx['location']['id']).update(source_site='1000')
        InventoryReportBatch.objects.create(source='local', active=True, manifest={'site': '1000'})
        InventoryAnalysisSnapshot.objects.create(kind='bulk', site='1000', payload={'rows': [], 'details': []})
        self.department = self.post("department", {"code": "E2E", "name": "贸易项目采购"})
        self.supplier = self.post("partner", {
            "code": "E2E-SUP", "name": "贸易项目供应商", "short_name": "E2E供应商",
            "kind": "supplier", "currency": self.ctx["currency"]["id"], "payment_method": "月结30天",
        })
        self.approve("partner", self.supplier["id"])
        self.material = self.post("material", {
            "code": "E2E-NEW-001", "name": "贸易项目新物料", "specification": "E2E规格",
            "category": self.ctx["material"]["category"], "uom": self.ctx["uom"]["id"],
            "default_location": self.ctx["location"]["id"], "tax_code": "1001", "quality_control": "exempt",
        })
        self.approve("material", self.material["id"])
        self.stages = []

    def checkpoint(self, stage, stock, demand, purchase=0, requisition=0, pending=0, shortage=0):
        balances = StockBalance.objects.filter(material_id=self.material['id'])
        self.assertEqual(sum(b.quantity for b in balances), Decimal(stock), stage)
        ledger = StockTransaction.objects.filter(material_id=self.material['id'])
        self.assertEqual(sum(t.quantity for t in ledger), Decimal(stock), stage)
        run = self.client.post('/api/trade-mrp/preview/', {'site':'1000', 'material':self.material['code']}, format='json')
        self.assertEqual(run.status_code, 201, run.data)
        values = {'demand_qty': demand, 'available_qty': stock, 'on_order_qty':purchase,
                  'approved_requisition_qty':requisition, 'pending_requisition_qty':pending, 'shortage_qty':shortage}
        if demand:
            self.assertEqual(len(run.data['results']), 1, stage)
            for key, expected in values.items():
                self.assertEqual(Decimal(run.data['results'][0][key]), Decimal(expected), (stage, key))
        else:
            self.assertEqual(run.data['results'], [], stage)
        bulk = self.client.get('/api/material-inventory-batch/', {'site':'1000','source':'local',
            'material_from':self.material['code'], 'material_to':self.material['code']})
        self.assertEqual(bulk.status_code, 200, bulk.data)
        row = next((r for r in bulk.data['results'] if r['tmp_part']==self.material['code']), None)
        if row:
            for key, expected in [('tmp_qty_oh',stock),('tmp_qty_req_total',demand),('tmp_qty_on_order',purchase)]:
                self.assertEqual(Decimal(row[key]), Decimal(expected), (stage, key))
        else:
            self.fail((stage, '物料未出现在库存批量查询', bulk.data.get('results', [])[:3]))
        self.stages.append({'stage':stage, **values, 'ledger_sum':str(sum(t.quantity for t in ledger)), 'bulk_found':bool(row)})

    def test_demand_to_close_with_receipt_return_delivery_return_adjustments(self):
        order = self.post("sales-order", {
            "customer": self.ctx["customer"]["id"], "currency": self.ctx["currency"]["id"],
            "customer_po": "E2E-PROJECT", "delivery_address": "项目现场",
            "promised_date": "2026-10-20",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": self.material["id"],
            "uom": self.ctx["uom"]["id"], "quantity": "10", "unit_price": "100",
            "promised_date": "2026-10-20",
        })
        self.approve("sales-order", order["id"])
        self.checkpoint('需求审核/无库存', 0, 10, shortage=10)

        # The new material has no stock, so the trade MRP run must ask for ten.
        run = calculate_trade_mrp(site="1000", filters={"order": order["number"]}, actor="flow-admin")
        result = run.results.get(material_id=self.material["id"])
        self.assertEqual((result.demand_qty, result.available_qty, result.suggested_qty), (10, 0, 10))
        requisition = confirm_trade_mrp(run.pk, actor="flow-admin", header={"department_id": self.department["id"]})
        self.assertEqual(requisition.lines.get().source_sales_order_line_id, order_line["id"])
        self.checkpoint('MRP草稿覆盖', 0, 10, pending=10)
        self.approve("purchase-requisition", requisition.pk)
        self.checkpoint('请购审核', 0, 10, requisition=10)

        po_response = self.client.post(f"/api/purchase-requisition/{requisition.pk}/convert-purchase/", {
            "supplier_id": self.supplier["id"], "department_id": self.department["id"],
            "lines": [{"line_id": requisition.lines.get().pk, "quantity": "10", "unit_price": "100"}],
        }, format="json")
        self.assertEqual(po_response.status_code, 201, po_response.data)
        purchase = PurchaseOrder.objects.get(pk=po_response.data["id"])
        purchase_line = purchase.lines.get()
        self.approve("purchase-order", purchase.pk)
        self.checkpoint('请购转采购并审核', 0, 10, purchase=10)

        receipt = self.post("goods-receipt", {
            "supplier": self.supplier["id"], "purchase_order": purchase.pk,
            "receipt_date": "2026-10-05", "supplier_delivery_number": "E2E-DN-01",
        })
        receipt_line = self.post("goods-receipt-line", {
            "receipt": receipt["id"], "line_number": 10, "purchase_order_line": purchase_line.pk,
            "material": self.material["id"], "uom": self.ctx["uom"]["id"], "quantity": "10",
            "location": self.ctx["location"]["id"],
        })
        self.approve("goods-receipt", receipt["id"])
        self.checkpoint('采购收货', 10, 10)
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 10)
        self.assertEqual(GoodsReceipt.objects.get(pk=receipt["id"]).lines.get().purchase_order_line_id, purchase_line.pk)

        # Supplier return consumes two units and creates a traceable replacement line.
        purchase_return = self.post("purchase-return", {
            "supplier": self.supplier["id"], "purchase_order": purchase.pk,
            "return_location": self.ctx["location"]["id"], "return_date": "2026-10-06",
            "reason": "项目来料不良", "replenishment": True,
        })
        self.post("purchase-return-line", {
            "purchase_return": purchase_return["id"], "line_number": 10,
            "purchase_order_line": purchase_line.pk, "material": self.material["id"],
            "uom": self.ctx["uom"]["id"], "quantity": "2", "source_location": self.ctx["location"]["id"],
            "reason": "项目来料不良",
        })
        self.approve("purchase-return", purchase_return["id"])
        purchase.refresh_from_db()
        replacement = purchase.lines.exclude(pk=purchase_line.pk).get()
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 8)
        self.assertEqual(replacement.replacement_source.purchase_return_id, purchase_return["id"])
        self.checkpoint('采购退货/补货在途', 8, 10, purchase=2)

        replacement_receipt = self.post("goods-receipt", {
            "supplier": self.supplier["id"], "purchase_order": purchase.pk,
            "receipt_date": "2026-10-07", "supplier_delivery_number": "E2E-DN-02",
        })
        self.post("goods-receipt-line", {
            "receipt": replacement_receipt["id"], "line_number": 10,
            "purchase_order_line": replacement.pk, "material": self.material["id"],
            "uom": self.ctx["uom"]["id"], "quantity": "2", "location": self.ctx["location"]["id"],
        })
        self.approve("goods-receipt", replacement_receipt["id"])
        self.checkpoint('补货收货', 10, 10)
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 10)

        # Add and deduct inventory through warehouse documents; net effect is zero.
        def warehouse(kind, quantity):
            doc = self.post("inventory-document", {
                "kind": kind, "from_location": self.ctx["location"]["id"],
                "to_location": self.ctx["location"]["id"],
                "lines": [{"line_number": 10, "material": self.material["id"],
                           "uom": self.ctx["uom"]["id"], "quantity": str(quantity)}],
            })
            self.assertEqual(self.client.post(f"/api/inventory-document/{doc['id']}/transition/",
                {"action": "approve"}, format="json").status_code, 200)
        warehouse("receipt", 1)
        self.checkpoint('计划外增加库存', 11, 10)
        warehouse("issue", 1)
        self.checkpoint('计划外扣减库存', 10, 10)
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 10)

        # Deliver all ten, receive two back, then redeliver the replacement quantity.
        delivery = self.post("delivery-order", {
            "customer": self.ctx["customer"]["id"], "sales_order": order["id"],
            "delivery_date": "2026-10-08", "delivery_address": "项目现场",
            "delivery_mode": "direct", "customer_po": "E2E-PROJECT", "srm_number": "E2E-SRM-01",
        })
        delivery_line = self.post("delivery-order-line", {
            "delivery": delivery["id"], "sales_order_line": order_line["id"], "line_number": 10,
            "material": self.material["id"], "uom": self.ctx["uom"]["id"], "actual_quantity": "10",
            "source_location": self.ctx["location"]["id"], "srm_customer_po": "E2E-PROJECT",
            "srm_material_code": "E2E-NEW-001", "srm_material_name": "贸易项目新物料", "srm_quantity": "10",
        })
        self.approve("delivery-order", delivery["id"])
        self.checkpoint('销售送货', 0, 0)
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 0)

        sales_return = self.post("sales-return", {
            "customer": self.ctx["customer"]["id"], "source_delivery": delivery["id"],
            "return_date": "2026-10-09", "srm_number": "E2E-SRM-RET", "reason": "项目退回", "no_order": False,
        })
        self.post("sales-return-line", {
            "sales_return": sales_return["id"], "line_number": 10, "material": self.material["id"],
            "uom": self.ctx["uom"]["id"], "quantity": "2", "original_location": self.ctx["location"]["id"],
            "return_location": self.ctx["location"]["id"], "source_delivery_line": delivery_line["id"],
        })
        self.approve("sales-return", sales_return["id"])
        self.checkpoint('客户退货/恢复需求', 2, 2)
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 2)
        self.assertEqual(SalesOrderLine.objects.get(pk=order_line["id"]).delivered_quantity, 8)

        redelivery = self.post("delivery-order", {
            "customer": self.ctx["customer"]["id"], "sales_order": order["id"],
            "delivery_date": "2026-10-10", "delivery_address": "项目现场",
            "delivery_mode": "direct", "customer_po": "E2E-PROJECT", "srm_number": "E2E-SRM-02",
        })
        self.post("delivery-order-line", {
            "delivery": redelivery["id"], "sales_order_line": order_line["id"], "line_number": 10,
            "material": self.material["id"], "uom": self.ctx["uom"]["id"], "actual_quantity": "2",
            "source_location": self.ctx["location"]["id"], "srm_customer_po": "E2E-PROJECT",
            "srm_material_code": "E2E-NEW-001", "srm_material_name": "贸易项目新物料", "srm_quantity": "2",
        })
        self.approve("delivery-order", redelivery["id"])
        self.checkpoint('补送完成', 0, 0)

        final_line = SalesOrderLine.objects.get(pk=order_line["id"])
        self.assertEqual((final_line.delivered_quantity, final_line.quantity), (10, 10))
        self.assertEqual(StockBalance.objects.get(material_id=self.material["id"]).quantity, 0)
        self.assertEqual(StockTransaction.objects.filter(material_id=self.material["id"]).count(), 8)
        self.assertEqual(PurchaseRequisition.objects.get(pk=requisition.pk).lines.get().converted_qty, 10)
        self.assertTrue(DeliveryOrder.objects.filter(pk=delivery["id"], posted=True).exists())
        self.assertTrue(all(p.quantity==p.received_quantity for p in purchase.lines.all()))
        self.assertTrue(self.client.get(f"/api/sales-order-line/{order_line['id']}/").data['execution_summary']['fulfilled'])
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_key_check')
            self.assertEqual(cursor.fetchall(), [])
        if os.environ.get('ERP_CHAIN_EVIDENCE'):
            Path(os.environ['ERP_CHAIN_EVIDENCE']).write_text(json.dumps(self.stages,ensure_ascii=False,indent=2),encoding='utf-8')
