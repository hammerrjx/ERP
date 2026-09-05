from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport


class PurchaseFlowApiTests(CoreFlowSupport, APITestCase):
    def test_requisition_keeps_unaggregated_mrp_snapshot_and_source_order_line(self):
        context = self.base_context()
        department = self.post("department", {"code": "PMC", "name": "PMC"})
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-001", "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        requisition = self.post("purchase-requisition", {
            "department": department["id"], "request_date": "2026-08-20",
            "needed_date": "2026-08-28", "aggregation_mode": "none",
            "quantity_rule": "mrp", "only_positive": True, "source_sales_order": order["id"],
        })
        line = self.post("purchase-requisition-line", {
            "requisition": requisition["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "mrp_demand_qty": "10", "on_order_qty": "2", "available_qty": "3",
            "safety_stock_qty": "1", "source_sales_order_line": order_line["id"],
        })
        self.assertEqual(line["requested_qty"], "6.000000")
        self.assertEqual(line["source_sales_order_line"], order_line["id"])
        self.assertEqual(line["calculation_snapshot"]["rule"], "mrp")

    def test_approved_purchase_order_generates_receipt_draft_with_supplier_delivery_number(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "月结30天",
        })
        self.approve("partner", supplier["id"])
        order = self.post("purchase-order", {
            "supplier": supplier["id"], "currency": context["currency"]["id"],
            "department": department["id"], "payment_method": "月结30天", "tax_rate": "13",
            "promised_date": "2026-09-05",
        })
        order_line = self.post("purchase-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "12", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        self.approve("purchase-order", order["id"])
        generated = self.client.post(f"/api/purchase-order/{order['id']}/generate-receipt/", {
            "receipt_date": "2026-09-01", "supplier_delivery_number": "DN-001",
        }, format="json")
        self.assertEqual(generated.status_code, 201, generated.data)
        self.assertEqual(generated.data["supplier_delivery_number"], "DN-001")
        self.assertEqual(generated.data["source_object"], "prh_receiver")
        line = self.client.get("/api/goods-receipt-line/").data[0]
        self.assertEqual(line["purchase_order_line"], order_line["id"])
        self.assertEqual(line["quantity"], "12.000000")
        self.assertEqual(line["location"], context["location"]["id"])
        self.assertEqual(line["source_object"], "prh_hist")

    def test_approved_requisition_uses_selected_inquiry_to_create_traceable_purchase_order(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "供应商月结30天",
        })
        self.approve("partner", supplier["id"])
        requisition = self.post("purchase-requisition", {
            "department": department["id"], "request_date": "2026-08-20",
            "needed_date": "2026-08-30", "aggregation_mode": "material", "quantity_rule": "mrp",
        })
        requisition_line = self.post("purchase-requisition-line", {
            "requisition": requisition["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "mrp_demand_qty": "10", "on_order_qty": "1", "available_qty": "2",
            "safety_stock_qty": "0",
        })
        self.approve("purchase-requisition", requisition["id"])
        rfq = self.post("rfq", {
            "requisition": requisition["id"], "currency": context["currency"]["id"],
            "inquiry_date": "2026-08-20", "response_due_date": "2026-08-23",
        })
        rfq_line = self.post("rfq-line", {
            "rfq": rfq["id"], "line_number": 10, "requisition_line": requisition_line["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"], "quantity": "7",
        })
        inquiry = self.post("supplier-inquiry", {
            "rfq_line": rfq_line["id"], "supplier": supplier["id"], "unit_price": "18.50",
            "tax_rate": "13", "promised_date": "2026-08-28", "selected": True,
        })
        converted = self.client.post(f"/api/purchase-requisition/{requisition['id']}/convert/", {
            "supplier_inquiry_ids": [inquiry["id"]],
        }, format="json")
        self.assertEqual(converted.status_code, 201, converted.data)
        self.assertEqual(converted.data["supplier"], supplier["id"])
        self.assertEqual(converted.data["department"], department["id"])
        self.assertEqual(converted.data["payment_method"], "供应商月结30天")
        purchase_lines = self.client.get("/api/purchase-order-line/")
        self.assertEqual(purchase_lines.status_code, 200, purchase_lines.data)
        self.assertEqual(purchase_lines.data[0]["source_requisition_line"], requisition_line["id"])
        refreshed = self.client.get(f"/api/purchase-requisition/{requisition['id']}/")
        self.assertEqual(refreshed.data["conversion_percent"], "100.00")

    def test_payable_vouchers_auto_generate_from_approved_receipts_and_split_payment_methods(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "月结30天",
        })
        self.approve("partner", supplier["id"])
        receipt_lines = []
        for index, payment_method in enumerate(("月结30天", "现结"), 1):
            order = self.post("purchase-order", {
                "supplier": supplier["id"], "currency": context["currency"]["id"],
                "department": department["id"], "payment_method": payment_method,
                "tax_rate": "13", "promised_date": "2026-08-28",
            })
            order_line = self.post("purchase-order-line", {
                "order": order["id"], "line_number": 10, "material": context["material"]["id"],
                "uom": context["uom"]["id"], "quantity": str(index), "unit_price": "100",
                "promised_date": "2026-08-28",
            })
            self.approve("purchase-order", order["id"])
            receipt = self.post("goods-receipt", {
                "supplier": supplier["id"], "purchase_order": order["id"],
                "receipt_date": "2026-08-28", "receipt_type": "normal",
            })
            receipt_lines.append(self.post("goods-receipt-line", {
                "receipt": receipt["id"], "line_number": 10,
                "purchase_order_line": order_line["id"], "material": context["material"]["id"],
                "uom": context["uom"]["id"], "quantity": str(index),
                "location": context["location"]["id"],
            }))
            self.approve("goods-receipt", receipt["id"])

        manual_voucher = self.post("payable-voucher", {
            "voucher_date": "2026-08-29", "supplier": supplier["id"],
            "currency": context["currency"]["id"], "payment_method": "月结30天", "tax_rate": "13",
        })
        tampered = self.client.post("/api/payable-voucher-line/", {
            "voucher": manual_voucher["id"], "line_number": 99,
            "source_receipt_line": receipt_lines[0]["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "quantity": "999", "unit_price": "0.01",
        }, format="json")
        self.assertEqual(tampered.status_code, 400, tampered.data)
        deleted = self.client.delete(f"/api/payable-voucher/{manual_voucher['id']}/")
        self.assertEqual(deleted.status_code, 204)

        generated = self.client.post("/api/payable-voucher/auto-generate/", {
            "voucher_date": "2026-08-29", "receipt_line_ids": [line["id"] for line in receipt_lines],
        }, format="json")
        self.assertEqual(generated.status_code, 201, getattr(generated, "data", generated.content))
        self.assertEqual({row["payment_method"] for row in generated.data}, {"月结30天", "现结"})
        self.assertEqual({row["gross_amount"] for row in generated.data}, {"113.00", "226.00"})
        voucher_lines = self.client.get("/api/payable-voucher-line/")
        self.assertEqual(voucher_lines.status_code, 200, voucher_lines.data)
        self.assertEqual({row["source_receipt_line"] for row in voucher_lines.data}, {line["id"] for line in receipt_lines})

        duplicate = self.client.post("/api/payable-voucher/auto-generate/", {
            "voucher_date": "2026-08-29", "receipt_line_ids": [receipt_lines[0]["id"]],
        }, format="json")
        self.assertEqual(duplicate.status_code, 400, duplicate.data)

    def test_payable_voucher_records_approved_purchase_return_as_negative_source(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "月结30天",
        })
        self.approve("partner", supplier["id"])
        order = self.post("purchase-order", {
            "supplier": supplier["id"], "currency": context["currency"]["id"],
            "department": department["id"], "payment_method": "月结30天",
            "tax_rate": "13", "promised_date": "2026-08-28",
        })
        order_line = self.post("purchase-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "2", "unit_price": "100",
            "promised_date": "2026-08-28",
        })
        self.approve("purchase-order", order["id"])
        self.post("stock-balance", {
            "material": context["material"]["id"], "location": context["location"]["id"],
            "uom": context["uom"]["id"], "quantity": "2", "batch_number": "",
        })
        purchase_return = self.post("purchase-return", {
            "supplier": supplier["id"], "purchase_order": order["id"],
            "return_date": "2026-08-29", "replenishment": False, "reason": "来料不良",
        })
        return_line = self.post("purchase-return-line", {
            "purchase_return": purchase_return["id"], "line_number": 10,
            "purchase_order_line": order_line["id"], "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "1",
            "source_location": context["location"]["id"], "reason": "尺寸超差",
        })
        self.approve("purchase-return", purchase_return["id"])

        generated = self.client.post("/api/payable-voucher/auto-generate/", {
            "voucher_date": "2026-08-29", "purchase_return_line_ids": [return_line["id"]],
        }, format="json")
        self.assertEqual(generated.status_code, 201, generated.data)
        self.assertEqual(generated.data[0]["net_amount"], "-100.00")
        self.assertEqual(generated.data[0]["tax_amount"], "-13.00")
        self.assertEqual(generated.data[0]["gross_amount"], "-113.00")
        voucher_line = self.client.get("/api/payable-voucher-line/").data[0]
        self.assertEqual(voucher_line["source_purchase_return_line"], return_line["id"])
        self.assertIsNone(voucher_line["source_receipt_line"])

    def test_non_production_purchase_requires_special_receipt_and_never_posts_stock(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        cost_center = self.post("department", {"code": "PD2", "name": "生产部（吸塑）"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "供应商月结30天",
        })
        self.approve("partner", supplier["id"])
        self.client.post(f"/api/material/{context['material']['id']}/unapprove/", {}, format="json")
        material_update = self.client.patch(f"/api/material/{context['material']['id']}/", {
            "non_production": True,
        }, format="json")
        self.assertEqual(material_update.status_code, 200, material_update.data)
        order = self.post("purchase-order", {
            "supplier": supplier["id"], "currency": context["currency"]["id"],
            "department": department["id"], "payment_method": "供应商月结30天",
            "tax_rate": "13", "promised_date": "2026-08-28", "purchase_type": "non_production",
            "cost_center": cost_center["id"],
        })
        self.assertEqual(order["cost_center"], cost_center["id"])
        order_line = self.post("purchase-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "1", "unit_price": "1000",
            "promised_date": "2026-08-28",
        })
        self.approve("purchase-order", order["id"])
        invalid = self.client.post("/api/goods-receipt/", {
            "supplier": supplier["id"], "purchase_order": order["id"],
            "receipt_date": "2026-08-28", "receipt_type": "normal",
        }, format="json")
        self.assertEqual(invalid.status_code, 400, invalid.data)
        receipt = self.post("goods-receipt", {
            "supplier": supplier["id"], "purchase_order": order["id"],
            "receipt_date": "2026-08-28", "receipt_type": "non_production",
        })
        self.post("goods-receipt-line", {
            "receipt": receipt["id"], "line_number": 10, "purchase_order_line": order_line["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "quantity": "1", "location": context["location"]["id"],
        })
        self.approve("goods-receipt", receipt["id"])
        self.assertEqual(self.client.get("/api/stock-balance/").data, [])
        self.assertEqual(self.client.get("/api/stock-transaction/").data, [])

    def test_approved_purchase_return_defaults_to_traceable_replacement_order(self):
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
            "uom": context["uom"]["id"], "quantity": "5", "unit_price": "18.50",
            "promised_date": "2026-08-28",
        })
        self.approve("purchase-order", order["id"])
        self.post("stock-balance", {
            "material": context["material"]["id"], "location": context["location"]["id"],
            "uom": context["uom"]["id"], "quantity": "5", "batch_number": "",
        })
        purchase_return = self.post("purchase-return", {
            "supplier": supplier["id"], "purchase_order": order["id"],
            "return_date": "2026-08-29", "reason": "来料不良",
        })
        self.assertTrue(purchase_return["replenishment"])
        self.post("purchase-return-line", {
            "purchase_return": purchase_return["id"], "line_number": 10,
            "purchase_order_line": order_line["id"], "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "2",
            "source_location": context["location"]["id"], "reason": "尺寸超差",
        })
        self.approve("purchase-return", purchase_return["id"])
        self.assertEqual(self.client.get("/api/stock-balance/").data[0]["quantity"], "3.000000")
        orders = self.client.get("/api/purchase-order/").data
        replacement = next(row for row in orders if row["source_purchase_return"] == purchase_return["id"])
        replacement_lines = self.client.get("/api/purchase-order-line/").data
        replacement_line = next(row for row in replacement_lines if row["order"] == replacement["id"])
        self.assertEqual(replacement_line["quantity"], "2.000000")

    def test_selected_receipt_lines_require_evidence_before_confirmation(self):
        context = self.base_context()
        department = self.post("department", {"code": "PO", "name": "执行采购"})
        supplier = self.post("partner", {
            "code": "S001", "name": "供应商一", "short_name": "供应商一", "kind": "supplier",
            "currency": context["currency"]["id"], "payment_method": "月结30天",
        })
        self.approve("partner", supplier["id"])
        order = self.post("purchase-order", {
            "supplier": supplier["id"], "currency": context["currency"]["id"], "department": department["id"],
            "payment_method": "月结30天", "tax_rate": "13", "promised_date": "2026-09-05",
        })
        line = self.post("purchase-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "unit_price": "12", "promised_date": "2026-09-05",
        })
        self.approve("purchase-order", order["id"])
        receipt = self.client.post(f"/api/purchase-order/{order['id']}/generate-receipt/", {
            "receipt_date": "2026-09-01", "supplier_delivery_number": "PS-001",
            "lines": [{"purchase_order_line": line["id"], "quantity": "3", "location": context["location"]["id"]}],
        }, format="json")
        self.assertEqual(receipt.status_code, 201, receipt.data)
        receipt_line = self.client.get("/api/goods-receipt-line/").data[0]
        self.assertEqual(receipt_line["quantity"], "3.000000")
        self.approve("goods-receipt", receipt.data["id"])
        blocked = self.client.post(f"/api/goods-receipt/{receipt.data['id']}/confirm/", {}, format="json")
        self.assertEqual(blocked.status_code, 400, blocked.data)
        evidence = self.client.post("/api/document-evidence/", {
            "document_type": "goodsreceipt", "document_id": receipt.data["id"], "document_number": receipt.data["number"],
            "evidence_type": "supplier_delivery", "file": SimpleUploadedFile("ps-001.pdf", b"signed"),
        }, format="multipart")
        self.assertEqual(evidence.status_code, 201, evidence.data)
        confirmed = self.client.post(f"/api/goods-receipt/{receipt.data['id']}/confirm/", {}, format="json")
        self.assertEqual(confirmed.status_code, 200, confirmed.data)
        self.assertTrue(confirmed.data["is_confirmed"])
