from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport


class InventoryFlowApiTests(CoreFlowSupport, APITestCase):
    def test_approved_goods_receipt_posts_stock_balance_and_ledger(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "供应商月结30天",
        })
        self.approve("partner", supplier["id"])
        order = self.post("purchase-order", {
            "supplier": supplier["id"], "currency": context["currency"]["id"],
            "department": department["id"], "payment_method": "供应商月结30天",
            "tax_rate": "13", "promised_date": "2026-08-28",
        })
        order_line = self.post("purchase-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "unit_price": "18.50",
            "promised_date": "2026-08-28",
        })
        self.approve("purchase-order", order["id"])
        receipt = self.post("goods-receipt", {
            "supplier": supplier["id"], "purchase_order": order["id"],
            "receipt_date": "2026-08-27", "receipt_type": "normal",
        })
        receipt_line = self.post("goods-receipt-line", {
            "receipt": receipt["id"], "line_number": 10, "purchase_order_line": order_line["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "quantity": "6", "location": context["location"]["id"], "batch_number": "B-20260827",
        })
        self.approve("goods-receipt", receipt["id"])
        balances = self.client.get("/api/stock-balance/")
        self.assertEqual(balances.status_code, 200, balances.data)
        self.assertEqual(balances.data[0]["quantity"], "6.000000")
        ledger = self.client.get("/api/stock-transaction/")
        self.assertEqual(ledger.status_code, 200, ledger.data)
        self.assertEqual(ledger.data[0]["source_line_id"], str(receipt_line["id"]))
        refreshed_line = self.client.get(f"/api/purchase-order-line/{order_line['id']}/")
        self.assertEqual(refreshed_line.data["received_quantity"], "6.000000")

    def test_transfer_count_and_shortage_alert_share_the_stock_ledger(self):
        context = self.base_context()
        destination = self.post("location", {"code": "FG02", "name": "二号成品仓", "location_type": "fg"})
        self.client.post(f"/api/material/{context['material']['id']}/unapprove/", {}, format="json")
        material_update = self.client.patch(f"/api/material/{context['material']['id']}/", {
            "stock_warning_qty": "5",
        }, format="json")
        self.assertEqual(material_update.status_code, 200, material_update.data)
        self.post("stock-balance", {
            "material": context["material"]["id"], "location": context["location"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "batch_number": "",
        })
        transfer = self.post("stock-transfer", {
            "transfer_date": "2026-09-01", "from_location": context["location"]["id"],
            "to_location": destination["id"],
        })
        self.post("stock-transfer-line", {
            "transfer": transfer["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "4",
        })
        self.approve("stock-transfer", transfer["id"])
        count = self.post("stock-count", {
            "count_date": "2026-09-02", "location": destination["id"],
        })
        count_line = self.post("stock-count-line", {
            "stock_count": count["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "counted_quantity": "3", "batch_number": "",
        })
        self.assertEqual(count_line["system_quantity"], "4.000000")
        self.assertEqual(count_line["variance_quantity"], "-1.000000")
        self.approve("stock-count", count["id"])
        balances = self.client.get("/api/stock-balance/").data
        by_location = {row["location"]: row["quantity"] for row in balances}
        self.assertEqual(by_location[context["location"]["id"]], "6.000000")
        self.assertEqual(by_location[destination["id"]], "3.000000")
        alerts = self.client.get("/api/inventory-alert/")
        self.assertEqual(alerts.status_code, 200, alerts.data)
        alert = next(row for row in alerts.data if row["location"] == destination["id"])
        self.assertEqual(alert["shortage_quantity"], "2.000000")
