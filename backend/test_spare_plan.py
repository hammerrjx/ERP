from decimal import Decimal

from rest_framework.test import APITestCase

from backend.models import SalesOrderLine, SalesQuoteLine
from backend.test_support import CoreFlowSupport


class SparePlanTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.context = self.base_context()
        self.header = {
            "customer": self.context["customer"]["id"], "currency": self.context["currency"]["id"],
            "customer_po": "PLAN", "delivery_address": "Customer warehouse", "promised_date": "2026-09-08",
            "order_date": "2026-09-08",
        }
        self.line = {"line_number": 10, "material": self.context["material"]["id"],
                     "uom": self.context["uom"]["id"], "quantity": "0", "spare_quantity": "50",
                     "promised_date": "2026-09-08"}

    def quote(self):
        quote = self.post("sales-quote", {
            "customer": self.context["customer"]["id"], "effective_date": "2026-08-20",
            "lines": [{"material": self.context["material"]["id"], "unit_price": "20"}],
        })
        for action in ("confirm", "approve", "ratify"):
            result = self.client.post(f"/api/sales-quote/{quote['id']}/{action}/")
            self.assertEqual(result.status_code, 200, result.data)
        return quote

    def test_material_to_customer_material_quote_order_and_spare_delivery_chain(self):
        import uuid
        # base_context creates and approves the material through the public API.
        material_id = self.context["material"]["id"]
        material = self.client.get(f"/api/material/{material_id}/").data
        self.assertTrue(material["code"])
        self.assertEqual(material["status"], "approved")
        customer_material = self.post("customer-material", {
            "customer": self.header["customer"], "material": material_id,
            "customer_code": "CUSTOMER-FULL-CHAIN", "customer_uom": self.context["uom"]["id"],
            "enabled": True,
        })
        quote = self.post("sales-quote", {
            "customer": self.header["customer"], "currency": self.header["currency"],
            "effective_date": "2026-09-01", "discount_rate": "100",
            "lines": [{"material": material_id, "customer_material": customer_material["id"],
                       "quantity": "950", "unit_price": "20"}],
        })
        for action in ("confirm", "approve", "ratify"):
            result = self.client.post(f"/api/sales-quote/{quote['id']}/{action}/")
            self.assertEqual(result.status_code, 200, result.data)
        lookup = self.client.get("/api/sales-quote/previous/", {
            "customer": self.header["customer"], "material": material_id,
            "customer_material": customer_material["id"], "currency": self.header["currency"],
            "date": self.header["order_date"],
        })
        self.assertEqual(lookup.status_code, 200, lookup.data)
        self.assertEqual(lookup.data["quote_line_id"], quote["lines"][0]["id"])
        order = self.post("sales-order", {**self.header, "lines": [{
            **self.line, "quantity": "950", "spare_quantity": "50",
            "customer_material": customer_material["id"], "source_quote_line": lookup.data["quote_line_id"],
        }]})
        line = order["lines"][0]
        self.assertEqual(order["source_quote"], quote["id"])
        self.assertEqual(Decimal(line["tax_included_amount"]), 19000)
        self.assertEqual((line["material"], line["customer_material"]), (material_id, customer_material["id"]))
        self.approve("sales-order", order["id"])

        def deliver(formal, spare, expected_formal, expected_spare):
            reservation = self.client.post("/api/delivery-order/reserve-number/", {
                "request_id": str(uuid.uuid4()), "delivery_date": "2026-09-08",
            }, format="json")
            self.assertEqual(reservation.status_code, 201, reservation.data)
            payload = {**reservation.data, "customer": self.header["customer"],
                       "delivery_date": "2026-09-08", "delivery_address": self.header["delivery_address"],
                       "document_type": "return" if formal < 0 else "normal",
                       "lines": [{"sales_order_line": line["id"], "actual_quantity": str(formal),
                                  "actual_spare_quantity": str(spare)}]}
            before = SalesOrderLine.objects.get(pk=line["id"])
            saved = self.client.post("/api/delivery-order/save-sheet/", payload, format="json")
            self.assertEqual(saved.status_code, 201, saved.data)
            before.refresh_from_db()
            self.assertEqual((before.delivered_quantity, before.delivered_spare_quantity),
                             (expected_formal - formal, expected_spare - spare))
            delivery_line = saved.data["lines"][0]
            self.assertEqual(delivery_line["sales_order_line"], line["id"])
            self.assertEqual(Decimal(delivery_line["delivery_amount"]), formal * 20)
            self.approve("delivery-order", saved.data["id"])
            repeat = self.client.post(f"/api/delivery-order/{saved.data['id']}/approve/")
            self.assertEqual(repeat.status_code, 200, repeat.data)
            before.refresh_from_db()
            self.assertEqual((before.delivered_quantity, before.delivered_spare_quantity),
                             (expected_formal, expected_spare))

        candidates = self.client.get("/api/delivery-order/order-candidates/", {
            "customer": self.header["customer"], "customer_po": self.header["customer_po"],
        })
        self.assertEqual(candidates.status_code, 200, candidates.data)
        candidate = next(row for row in candidates.data["results"] if row["sales_order_line"] == line["id"])
        self.assertEqual((Decimal(candidate["available_quantity"]), Decimal(candidate["available_spare_quantity"])), (950, 50))
        deliver(950, 50, 950, 50)
        deliver(-1, -1, 949, 49)
        deliver(1, 1, 950, 50)
        summary = self.client.get(f"/api/sales-order-line/{line['id']}/").data["execution_summary"]
        self.assertEqual(Decimal(summary["total_net"]), 1000)
        self.assertTrue(summary["fulfilled"])
        self.assertFalse(summary["has_history_gap"])

    def test_nested_pure_spare_zero_and_eight_decimals(self):
        order = self.post("sales-order", {**self.header, "lines": [self.line]})
        line = order["lines"][0]
        self.assertEqual(Decimal(line["quantity"]), 0)
        self.assertEqual(Decimal(line["tax_included_amount"]), 0)
        original_id = line["id"]
        changed = self.client.patch(f"/api/sales-order/{order['id']}/", {
            "lines": [{**self.line, "spare_quantity": "50.00000001", "delivered_quantity": "900",
                       "delivered_spare_quantity": "800"}],
        }, format="json")
        self.assertEqual(changed.status_code, 200, changed.data)
        updated = changed.data["lines"][0]
        self.assertEqual(updated["id"], original_id)
        self.assertEqual(Decimal(updated["spare_quantity"]), Decimal("50.00000001"))
        self.assertEqual(Decimal(updated["delivered_quantity"]), 0)
        self.assertEqual(Decimal(updated["delivered_spare_quantity"]), 0)
        patch = self.client.patch(f"/api/sales-order-line/{original_id}/", {
            "delivered_quantity": "100", "delivered_spare_quantity": "100",
        }, format="json")
        self.assertEqual(patch.status_code, 200, patch.data)
        self.assertEqual(Decimal(patch.data["delivered_quantity"]), 0)
        invalid = self.client.patch(f"/api/sales-order-line/{original_id}/", {"spare_quantity": "0"}, format="json")
        self.assertEqual(invalid.status_code, 400, invalid.data)

    def test_quote_is_explicit_and_snapshot_survives_nested_save(self):
        quote = self.quote()
        order = self.post("sales-order", {**self.header, "lines": [self.line]})
        self.assertIsNone(order["lines"][0]["source_quote_line"])
        formal = {**self.line, "quantity": "950", "source_quote_line": quote["lines"][0]["id"]}
        selected = self.client.patch(f"/api/sales-order/{order['id']}/", {"lines": [formal]}, format="json")
        self.assertEqual(selected.status_code, 200, selected.data)
        self.assertEqual(Decimal(selected.data["lines"][0]["unit_price"]), 20)
        SalesQuoteLine.objects.filter(pk=quote["lines"][0]["id"]).update(unit_price=99)
        resaved = self.client.patch(f"/api/sales-order/{order['id']}/", {"lines": [formal]}, format="json")
        self.assertEqual(resaved.status_code, 200, resaved.data)
        self.assertEqual(Decimal(resaved.data["lines"][0]["unit_price"]), 20)
        self.assertEqual(Decimal(resaved.data["lines"][0]["tax_included_amount"]), 19000)

    def test_quote_conversion_accepts_manual_spare_and_zero_formal(self):
        quote = self.quote()
        result = self.client.post(f"/api/sales-quote/{quote['id']}/convert/", {
            **self.header, "lines": {str(quote["lines"][0]["id"]): {"quantity": "0", "spare_quantity": "50"}},
        }, format="json")
        self.assertEqual(result.status_code, 201, result.data)
        line = SalesOrderLine.objects.get(order_id=result.data["id"])
        self.assertEqual((line.quantity, line.spare_quantity, line.unit_price, line.tax_included_amount), (0, 50, 0, 0))

    def test_two_order_entry_paths_reject_zero_and_negative_plans(self):
        for quantity, spare in (("0", "0"), ("-1", "50"), ("1", "-1")):
            result = self.client.post("/api/sales-order/", {
                **self.header, "lines": [{**self.line, "quantity": quantity, "spare_quantity": spare}],
            }, format="json")
            self.assertEqual(result.status_code, 400, result.data)
        order = self.post("sales-order", self.header)
        result = self.client.post("/api/sales-order-line/", {
            **self.line, "order": order["id"], "spare_quantity": "0",
        }, format="json")
        self.assertEqual(result.status_code, 400, result.data)

    def test_order_import_preserves_zero_price_quantity_and_no_guessed_quote(self):
        from datetime import date
        from backend.management.commands.import_customer_orders import Command
        self.quote()
        Command().import_rows({
            "customers": [], "materials": [], "customer_materials": [], "addresses": [],
            "orders": [{"so_nbr": "SOURCE-SPARE", "so_cust": "C001", "so_curr": "CNY",
                        "so_ord_date": date(2026, 9, 8), "so_po": "SOURCE-PO"}],
            "lines": [{"sod_nbr": "SOURCE-SPARE", "sod_line": 10, "sod_part": "FG-001", "sod_um": "JIAN",
                       "sod_qty_ord": 0, "sod_qty_spare": 50, "sod_price": 0, "sod_list_price": 99}],
        })
        line = SalesOrderLine.objects.get(order__number="SOURCE-SPARE")
        self.assertEqual((line.quantity, line.spare_quantity, line.unit_price), (0, 50, 0))
        self.assertIsNone(line.source_quote_line_id)
