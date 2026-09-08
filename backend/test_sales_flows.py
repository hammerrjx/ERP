from django.test import override_settings
from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport


class SalesFlowApiTests(CoreFlowSupport, APITestCase):
    def test_order_can_be_created_with_nested_linked_line(self):
        context = self.base_context()
        customer_material = self.post("customer-material", {
            "customer": context["customer"]["id"], "material": context["material"]["id"],
            "customer_code": "CUST-NESTED-001", "customer_uom": context["uom"]["id"],
        })
        quote = self.post("sales-quote", {
            "customer": context["customer"]["id"], "effective_date": "2026-08-20",
            "lines": [{"material": context["material"]["id"], "customer_material": customer_material["id"], "unit_price": "25"}],
        })
        self.client.post(f"/api/sales-quote/{quote['id']}/confirm/", {}, format="json")
        self.client.post(f"/api/sales-quote/{quote['id']}/approve/", {}, format="json")
        self.client.post(f"/api/sales-quote/{quote['id']}/ratify/", {}, format="json")
        response = self.client.post("/api/sales-order/", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-NESTED-001", "delivery_address": "客户仓", "promised_date": "2026-09-05",
            "lines": [{"line_number": 10, "material": context["material"]["id"], "customer_material": customer_material["id"],
                       "uom": context["uom"]["id"], "quantity": "2", "promised_date": "2026-09-05",
                       "source_quote_line": quote["lines"][0]["id"]}],
        }, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["source_quote"], quote["id"])
        line = self.client.get("/api/sales-order-line/").data[0]
        self.assertEqual(line["customer_material_code"], "CUST-NESTED-001")

    def test_order_line_keeps_customer_material_code_and_quote_price_type(self):
        context = self.base_context()
        customer_material = self.post("customer-material", {
            "customer": context["customer"]["id"], "material": context["material"]["id"],
            "customer_code": "T-AC8836-F1-AB1", "customer_name": "客户侧名称",
        })
        quote = self.post("sales-quote", {
            "customer": context["customer"]["id"], "effective_date": "2026-08-20",
            "lines": [{"material": context["material"]["id"], "customer_material": customer_material["id"], "unit_price": "15", "price_type": "3"}],
        })
        self.client.post(f"/api/sales-quote/{quote['id']}/confirm/", {}, format="json")
        self.client.post(f"/api/sales-quote/{quote['id']}/approve/", {}, format="json")
        self.client.post(f"/api/sales-quote/{quote['id']}/ratify/", {}, format="json")
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-CM-001", "delivery_address": "客户仓", "promised_date": "2026-09-05", "order_date": "2026-09-01",
        })
        self.post("sales-order-line", {"order": order["id"], "line_number": 10, "material": context["material"]["id"], "customer_material": customer_material["id"], "source_quote_line": quote["lines"][0]["id"], "uom": context["uom"]["id"], "quantity": "100", "promised_date": "2026-09-05"})
        line = self.client.get("/api/sales-order-line/").data[0]
        self.assertEqual(line["customer_material_code"], "T-AC8836-F1-AB1")
        self.assertEqual(line["price_type"], "3")
        self.assertEqual(line["tax_included_amount"], "1500.00000000")
        self.assertEqual(line["untaxed_amount"], "1500.00000000")

    def test_manual_quote_line_rejects_invalid_date_or_currency_without_writes(self):
        from backend.models import SalesOrder, SalesOrderLine
        context = self.base_context()
        usd = self.post("currency", {"code": "USD", "name": "美元", "symbol": "$"})
        scenarios = [
            ("date", "2026-10-01", context["currency"]["id"], "来源销售报价在订单日期无效"),
            ("currency", "2026-08-20", usd["id"], "来源报价的客户、物料、客户料号或币种与订单不一致"),
        ]
        for name, effective_date, currency, message in scenarios:
            with self.subTest(scenario=name):
                quote = self.post("sales-quote", {
                    "customer": context["customer"]["id"], "currency": currency,
                    "effective_date": effective_date,
                    "lines": [{"material": context["material"]["id"], "unit_price": "15"}],
                })
                for action in ("confirm", "approve", "ratify"):
                    response = self.client.post(f"/api/sales-quote/{quote['id']}/{action}/", {}, format="json")
                    self.assertEqual(response.status_code, 200, response.data)
                response = self.client.post("/api/sales-order/", {
                    "customer": context["customer"]["id"], "currency": context["currency"]["id"],
                    "customer_po": "PO-" + name, "delivery_address": "客户仓",
                    "order_date": "2026-09-01", "promised_date": "2026-09-05",
                    "lines": [{"material": context["material"]["id"], "uom": context["uom"]["id"],
                               "quantity": "1", "promised_date": "2026-09-05",
                               "source_quote_line": quote["lines"][0]["id"]}],
                }, format="json")
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(message, str(response.data))
                self.assertFalse(SalesOrder.objects.exists())
                self.assertFalse(SalesOrderLine.objects.exists())

    def test_approved_sales_quote_converts_to_order_with_delivery_promise(self):
        context = self.base_context()
        customer_material = self.post("customer-material", {
            "customer": context["customer"]["id"], "material": context["material"]["id"],
            "customer_code": "CUST-FG-001", "customer_uom": context["uom"]["id"],
        })
        quote = self.post("sales-quote", {
            "customer": context["customer"]["id"], "effective_date": "2026-08-20",
            "expiry_date": "2026-09-20", "lines": [{
                "line_number": 10, "material": context["material"]["id"],
                "customer_material": customer_material["id"], "quantity": "12",
                "unit_price": "25.50", "promised_date": "2026-09-05",
            }],
        })
        quote_line = quote["lines"][0]
        confirmed = self.client.post(f"/api/sales-quote/{quote['id']}/confirm/", {}, format="json")
        self.assertEqual(confirmed.status_code, 200, confirmed.data)
        approved = self.client.post(f"/api/sales-quote/{quote['id']}/approve/", {}, format="json")
        self.assertEqual(approved.status_code, 200, approved.data)
        ratified = self.client.post(f"/api/sales-quote/{quote['id']}/ratify/", {}, format="json")
        self.assertEqual(ratified.status_code, 200, ratified.data)
        converted = self.client.post(f"/api/sales-quote/{quote['id']}/convert/", {
            "customer_po": "PO-CUSTOMER-001", "delivery_address": "客户一收货仓",
            "promised_date": "2026-09-05",
        }, format="json")
        self.assertEqual(converted.status_code, 201, converted.data)
        self.assertEqual(converted.data["source_quote"], quote["id"])
        self.assertEqual(converted.data["customer_po"], "PO-CUSTOMER-001")
        self.assertEqual(converted.data["currency"], quote["currency"])
        self.assertEqual(converted.data["tax_included"], quote["tax_included"])
        self.assertEqual(converted.data["tax_rate"], quote["tax_rate"])
        order_lines = self.client.get("/api/sales-order-line/")
        self.assertEqual(order_lines.status_code, 200, order_lines.data)
        self.assertEqual(order_lines.data[0]["source_quote_line"], quote_line["id"])

    def test_approved_sales_order_generates_unaggregated_mrp_requisition(self):
        context = self.base_context()
        department = self.post("department", {"code": "PMC", "name": "PMC"})
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-MRP-001", "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        blocked = self.client.patch(f"/api/sales-order/{order['id']}/", {"customer_po": "PO-BLOCKED"}, format="json")
        self.assertEqual(blocked.status_code, 400, blocked.data)
        blocked_line = self.client.patch(f"/api/sales-order-line/{order_line['id']}/", {"quantity": "11"}, format="json")
        self.assertEqual(blocked_line.status_code, 400, blocked_line.data)
        generated = self.client.post(f"/api/sales-order/{order['id']}/generate-requisition/", {
            "department": department["id"], "needed_date": "2026-09-05",
        }, format="json")
        self.assertEqual(generated.status_code, 201, generated.data)
        self.assertEqual(generated.data["aggregation_mode"], "none")
        self.assertEqual(generated.data["source_sales_order"], order["id"])
        line = self.client.get("/api/purchase-requisition-line/").data[0]
        self.assertEqual(line["source_sales_order_line"], order_line["id"])
        self.assertEqual(line["requested_qty"], "10.000000")

    def test_approved_sales_order_generates_delivery_draft_from_remaining_lines(self):
        context = self.base_context()
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-DEL-001", "srm_number": "SRM-DEL-001",
            "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "8", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        generated = self.client.post("/api/delivery-order/generate-from-order/", {
            "sales_order": order["id"], "delivery_date": "2026-09-01",
            "delivery_address": "客户仓", "delivery_mode": "direct",
            "srm_number": "SRM-DEL-001", "customer_po": "PO-DEL-001",
        }, format="json")
        self.assertEqual(generated.status_code, 201, generated.data)
        line = self.client.get("/api/delivery-order-line/").data[0]
        self.assertEqual(line["sales_order_line"], order_line["id"])
        self.assertEqual(line["actual_quantity"], "8.00000000")
        self.assertEqual(line["source_location"], context["location"]["id"])

    def test_order_delivery_return_then_redelivery_reopens_order_quantity(self):
        context = self.base_context()
        self.post("stock-balance", {
            "material": context["material"]["id"], "location": context["location"]["id"],
            "uom": context["uom"]["id"], "quantity": "100", "batch_number": "",
        })
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-ROUNDTRIP", "srm_number": "SRM-ROUNDTRIP",
            "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "100", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        first_delivery = self.post("delivery-order", {
            "customer": context["customer"]["id"], "sales_order": order["id"],
            "delivery_date": "2026-09-01", "delivery_address": "客户仓",
            "delivery_mode": "direct", "srm_number": "SRM-ROUNDTRIP-1", "customer_po": "PO-ROUNDTRIP",
        })
        first_line = self.post("delivery-order-line", {
            "delivery": first_delivery["id"], "sales_order_line": order_line["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "actual_quantity": "50", "source_location": context["location"]["id"],
            "srm_customer_po": "PO-ROUNDTRIP", "srm_material_code": "FG-001",
            "srm_material_name": "交付产品", "srm_quantity": "50",
        })
        self.approve("delivery-order", first_delivery["id"])
        returned = self.post("sales-return", {
            "customer": context["customer"]["id"], "return_date": "2026-09-02",
            "srm_number": "SRM-ROUNDTRIP-R", "reason": "客户退回", "no_order": False,
            "source_delivery": first_delivery["id"],
        })
        self.post("sales-return-line", {
            "sales_return": returned["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "50",
            "original_location": context["location"]["id"], "return_location": context["location"]["id"],
            "source_delivery_line": first_line["id"],
        })
        self.approve("sales-return", returned["id"])
        refreshed = self.client.get(f"/api/sales-order-line/{order_line['id']}/")
        self.assertEqual(refreshed.data["delivered_quantity"], "0.00000000")
        self.assertEqual(refreshed.data["returned_quantity"], "50.00000000")
        second_delivery = self.client.post("/api/delivery-order/generate-from-order/", {
            "sales_order": order["id"], "delivery_date": "2026-09-03", "delivery_address": "客户仓",
            "delivery_mode": "direct", "srm_number": "SRM-ROUNDTRIP-2", "customer_po": "PO-ROUNDTRIP",
        }, format="json")
        self.assertEqual(second_delivery.status_code, 201, second_delivery.data)
        second_line = next(line for line in self.client.get("/api/delivery-order-line/").data if line["delivery"] == second_delivery.data["id"])
        self.assertEqual(second_line["actual_quantity"], "100.00000000")
        self.approve("delivery-order", second_delivery.data["id"])
        refreshed = self.client.get(f"/api/sales-order-line/{order_line['id']}/")
        self.assertEqual(refreshed.data["delivered_quantity"], "100.00000000")
        balance = self.client.get("/api/stock-balance/").data[0]
        self.assertEqual(balance["quantity"], "100.000000")

    def test_order_return_can_reference_order_line_without_delivery_header(self):
        context = self.base_context()
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-DIRECT-RETURN", "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "100", "unit_price": "20", "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        delivery = self.post("delivery-order", {
            "customer": context["customer"]["id"], "sales_order": order["id"], "delivery_address": "客户仓",
            "delivery_mode": "direct", "srm_number": "SRM-DIRECT-RETURN", "customer_po": "PO-DIRECT-RETURN",
        })
        self.post("delivery-order-line", {
            "delivery": delivery["id"], "sales_order_line": order_line["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"], "actual_quantity": "50",
            "source_location": context["location"]["id"], "srm_customer_po": "PO-DIRECT-RETURN",
            "srm_material_code": "FG-001", "srm_material_name": "交付产品", "srm_quantity": "50",
        })
        self.approve("delivery-order", delivery["id"])
        returned = self.post("sales-return", {
            "customer": context["customer"]["id"], "srm_number": "SRM-DIRECT-RETURN-R",
            "reason": "直接订单行退货", "no_order": False,
        })
        line = self.post("sales-return-line", {
            "sales_return": returned["id"], "line_number": 10, "sales_order_line": order_line["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"], "quantity": "50",
            "original_location": context["location"]["id"], "return_location": context["location"]["id"],
        })
        self.assertEqual(line["sales_order_line"], order_line["id"])
        self.approve("sales-return", returned["id"])
        refreshed = self.client.get(f"/api/sales-order-line/{order_line['id']}/")
        self.assertEqual(refreshed.data["delivered_quantity"], "0.00000000")
        self.assertEqual(refreshed.data["returned_quantity"], "50.00000000")

    def test_delivery_validates_srm_fields_and_posts_exact_actual_quantity(self):
        context = self.base_context()
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "CPO-001", "srm_number": "SRM-001",
            "delivery_address": "客户收货仓", "promised_date": "2026-09-05",
        })
        order_line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "8", "unit_price": "25",
            "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        self.post("stock-balance", {
            "material": context["material"]["id"], "location": context["location"]["id"],
            "uom": context["uom"]["id"], "quantity": "10", "batch_number": "",
        })
        delivery = self.post("delivery-order", {
            "customer": context["customer"]["id"], "sales_order": order["id"],
            "delivery_date": "2026-09-01", "delivery_address": "客户收货仓",
            "delivery_mode": "direct", "srm_number": "SRM-001", "customer_po": "CPO-001",
        })
        delivery_line = self.post("delivery-order-line", {
            "delivery": delivery["id"], "line_number": 10, "sales_order_line": order_line["id"],
            "material": context["material"]["id"], "uom": context["uom"]["id"],
            "actual_quantity": "4", "source_location": context["location"]["id"],
            "srm_customer_po": "CPO-001", "srm_material_code": "FG-001",
            "srm_material_name": "交付产品", "srm_quantity": "4",
        })
        self.approve("delivery-order", delivery["id"])
        balance = self.client.get("/api/stock-balance/").data[0]
        self.assertEqual(balance["quantity"], "10.000000")
        refreshed_line = self.client.get(f"/api/delivery-order-line/{delivery_line['id']}/")
        self.assertEqual(refreshed_line.data["actual_quantity"], "4.00000000")
        sales_line = self.client.get(f"/api/sales-order-line/{order_line['id']}/")
        self.assertEqual(sales_line.data["delivered_quantity"], "4.00000000")

    @override_settings(ERP_DELIVERY_POST_STOCK=True)
    def test_no_order_sales_return_from_fg01_must_enter_quarantine_location(self):
        context = self.base_context()
        quarantine = self.post("location", {
            "code": "RMA", "name": "不良品仓", "location_type": "ng", "quarantine_return": True,
        })
        sales_return = self.post("sales-return", {
            "customer": context["customer"]["id"], "return_date": "2026-09-03",
            "srm_number": "SRM-RETURN-001", "reason": "品质异常退货",
        })
        invalid = self.client.post("/api/sales-return-line/", {
            "sales_return": sales_return["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"], "quantity": "2",
            "original_location": context["location"]["id"], "return_location": context["location"]["id"],
        }, format="json")
        self.assertEqual(invalid.status_code, 400, invalid.data)
        self.post("sales-return-line", {
            "sales_return": sales_return["id"], "line_number": 10,
            "material": context["material"]["id"], "uom": context["uom"]["id"], "quantity": "2",
            "original_location": context["location"]["id"], "return_location": quarantine["id"],
        })
        self.approve("sales-return", sales_return["id"])
        balance = self.client.get("/api/stock-balance/").data[0]
        self.assertEqual(balance["location"], quarantine["id"])
        self.assertEqual(balance["quantity"], "2.000000")

    def test_selected_delivery_lines_keep_requested_quantity_and_location(self):
        context = self.base_context()
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "CPO-SELECT", "srm_number": "SRM-SELECT", "delivery_address": "客户仓", "promised_date": "2026-09-05",
        })
        line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "8", "unit_price": "20", "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])
        delivery = self.client.post("/api/delivery-order/generate-from-order/", {
            "sales_order": order["id"], "delivery_date": "2026-09-01", "delivery_address": "客户仓",
            "delivery_mode": "direct", "srm_number": "SRM-SELECT", "customer_po": "CPO-SELECT",
            "lines": [{"sales_order_line": line["id"], "actual_quantity": "2", "source_location": context["location"]["id"]}],
        }, format="json")
        self.assertEqual(delivery.status_code, 201, delivery.data)
        generated = self.client.get("/api/delivery-order-line/").data[0]
        self.assertEqual(generated["actual_quantity"], "2.00000000")
        self.assertEqual(generated["source_location"], context["location"]["id"])

        detail = self.client.get(f"/api/delivery-order/{delivery.data['id']}/")
        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertEqual(len(detail.data["lines"]), 1)
        self.assertEqual(detail.data["lines"][0]["sales_order_line"], line["id"])
        self.assertEqual(detail.data["lines"][0]["order_number"], order["number"])
        self.assertEqual(detail.data["lines"][0]["order_line_number"], 10)
        self.assertEqual(detail.data["lines"][0]["material_code"], "FG-001")

    def test_delivery_sheet_legacy_required_fields_support_delivery_return_redelivery(self):
        context = self.base_context()
        order = self.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": "PO-LEGACY", "delivery_address": "客户收货仓",
            "promised_date": "2026-09-05",
        })
        line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 10, "material": context["material"]["id"],
            "uom": context["uom"]["id"], "quantity": "100", "unit_price": "20",
            "promised_date": "2026-09-05",
        })
        self.approve("sales-order", order["id"])

        def generate(document_type, quantity, address_code="ADDR-001"):
            response = self.client.post("/api/delivery-order/generate-from-order/", {
                "sales_order": order["id"], "customer": context["customer"]["id"],
                "delivery_mode": "direct", "address_code": address_code, "delivery_address": "客户收货仓",
                "source_location": context["location"]["id"], "document_type": document_type,
                "lines": [{"sales_order_line": str(line["id"]), "actual_quantity": quantity}],
            }, format="json")
            self.assertEqual(response.status_code, 201, response.data)
            self.approve("delivery-order", response.data["id"])
            return response.data["id"]

        generate("normal", "50", "01")
        generate("return", "-50")
        generate("normal", "100")
        refreshed = self.client.get(f"/api/sales-order-line/{line['id']}/")
        self.assertEqual(refreshed.data["delivered_quantity"], "100.00000000")
        self.assertEqual(refreshed.data["returned_quantity"], "0.00000000")

        invalid = self.client.post("/api/delivery-order/generate-from-order/", {
            "sales_order": order["id"], "customer": context["customer"]["id"],
            "delivery_mode": "direct", "address_code": "ADDR-001",
            "source_location": context["location"]["id"], "document_type": "normal",
            "lines": [{"sales_order_line": line["id"], "actual_quantity": "1"}],
        }, format="json")
        self.assertEqual(invalid.status_code, 400, invalid.data)
