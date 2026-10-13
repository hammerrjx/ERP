"""Exercise public sales APIs in an isolated test database."""
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APITestCase

from backend.models import SalesOrderLine, StockBalance, StockTransaction
from backend.test_support import CoreFlowSupport


class SalesLineChainTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.context = self.base_context()
        self.day = timezone.localdate().isoformat()

    def order(self, lines, po="CHAIN-A"):
        return self.post("sales-order", {
            "customer": self.context["customer"]["id"], "currency": self.context["currency"]["id"],
            "customer_po": po, "order_date": self.day, "promised_date": self.day,
            "delivery_address": "Chain test warehouse", "lines": lines,
        })

    def line(self, **changes):
        return {"material": self.context["material"]["id"], "uom": self.context["uom"]["id"],
                "quantity": "100", "unit_price": "12", "promised_date": self.day, **changes}

    def delivery(self, lines):
        reserved = self.client.post("/api/delivery-order/reserve-number/", {
            "request_id": str(uuid.uuid4()), "delivery_date": self.day,
        }, format="json")
        self.assertEqual(reserved.status_code, 201, reserved.data)
        payload = {**reserved.data, "customer": self.context["customer"]["id"],
                   "delivery_date": self.day, "delivery_address": "Chain test warehouse", "lines": lines}
        result = self.client.post("/api/delivery-order/save-sheet/", payload, format="json")
        self.assertEqual(result.status_code, 201, result.data)
        return result.data

    def test_material_customer_quote_multiple_orders_and_deliveries(self):
        category = self.post("product-category", {"code": "CHAIN", "name": "Chain test", "code_prefix": "CHAIN"})
        materials, customer_materials = [], []
        for index in range(2):
            material = self.post("material", {
                "name": f"Chain material {index + 1}", "category": category["id"], "specification": "Chain test specification",
                "uom": self.context["uom"]["id"], "default_location": self.context["location"]["id"],
                "tax_code": "1001",
            })
            self.assertEqual(material["code"], f"CHAIN-{index + 1:04d}")
            self.approve("material", material["id"])
            materials.append(material)
            customer_materials.append(self.post("customer-material", {
                "customer": self.context["customer"]["id"], "material": material["id"],
                "customer_code": f"CUSTOMER-CHAIN-{index + 1}", "customer_uom": self.context["uom"]["id"],
            }))
        quotes = []
        for number, material, cm, price in zip([15, 35], materials, customer_materials, ["12", "25"]):
            quote = self.post("sales-quote", {
                "customer": self.context["customer"]["id"], "effective_date": self.day,
                "lines": [{"line_number": number, "material": material["id"], "customer_material": cm["id"],
                           "quantity": "100", "unit_price": price}],
            })
            for action in ("confirm", "approve", "ratify"):
                result = self.client.post(f"/api/sales-quote/{quote['id']}/{action}/", {}, format="json")
                self.assertEqual(result.status_code, 200, result.data)
            quotes.append(quote)
        quote = quotes[0]
        converted = self.client.post(f"/api/sales-quote/{quote['id']}/convert/", {
            "customer_po": "CHAIN-CONVERT", "delivery_address": "Chain test warehouse", "promised_date": self.day,
        }, format="json")
        self.assertEqual(converted.status_code, 201, converted.data)
        self.assertEqual([row["line_number"] for row in converted.data["lines"]], [10])
        self.assertEqual([row["source_quote_line"] for row in converted.data["lines"]], [row["id"] for row in quote["lines"]])
        rows = [self.line(material=materials[i]["id"], customer_material=customer_materials[i]["id"],
                          source_quote_line=quotes[i]["lines"][0]["id"], spare_quantity="5") for i in (0, 0, 1)]
        order = self.order(rows)
        self.assertEqual([row["line_number"] for row in order["lines"]], [10, 20, 30])
        self.assertEqual([Decimal(row["unit_price"]) for row in order["lines"]], [12, 12, 25])
        self.approve("sales-order", order["id"])
        self.approve("sales-order", converted.data["id"])
        sources = [order["lines"][1], order["lines"][2], converted.data["lines"][0]]
        saved = self.delivery([{"sales_order_line": row["id"], "actual_quantity": "20",
                                "actual_spare_quantity": "2" if i < 2 else "0"} for i, row in enumerate(sources)])
        self.assertEqual([row["line_number"] for row in saved["lines"]], [10, 20, 30])
        self.assertEqual([row["order_line_number"] for row in saved["lines"]], [20, 30, 10])
        self.assertEqual([row["order_number"] for row in saved["lines"]], [order["number"], order["number"], converted.data["number"]])
        self.assertEqual([row["customer_material_code"] for row in saved["lines"]],
                         [customer_materials[i]["customer_code"] for i in (0, 1, 0)])
        self.approve("delivery-order", saved["id"])
        self.assertFalse(StockTransaction.objects.exists())
        self.assertEqual(SalesOrderLine.objects.get(pk=order["lines"][0]["id"]).delivered_quantity, 0)
        for row in sources:
            self.assertEqual(SalesOrderLine.objects.get(pk=row["id"]).delivered_quantity, 20)
        second = self.delivery([{"sales_order_line": sources[0]["id"], "actual_quantity": "30", "batch_number": "A"},
                                {"sales_order_line": sources[0]["id"], "actual_quantity": "10", "batch_number": "B"}])
        self.approve("delivery-order", second["id"])
        repeat = self.client.post(f"/api/delivery-order/{second['id']}/approve/", {}, format="json")
        self.assertEqual(repeat.status_code, 200, repeat.data)
        self.assertEqual(SalesOrderLine.objects.get(pk=sources[0]["id"]).delivered_quantity, 60)
        reverse = self.delivery([{"sales_order_line": sources[0]["id"], "actual_quantity": "-5"}])
        self.approve("delivery-order", reverse["id"])
        self.assertEqual(SalesOrderLine.objects.get(pk=sources[0]["id"]).delivered_quantity, 55)
        detail = self.client.get(f"/api/delivery-order/{saved['id']}/").data
        self.assertEqual([row["order_line_number"] for row in detail["lines"]], [20, 30, 10])

    def test_order_edit_uses_ids_retains_numbers_and_allocates_after_deleted_max(self):
        order = self.order([self.line(line_number=999), self.line(line_number=999), self.line()])
        self.assertEqual([row["line_number"] for row in order["lines"]], [10, 20, 30])
        rows = [order["lines"][1], order["lines"][0], self.line(line_number=1)]
        rows[0]["line_number"] = 777
        result = self.client.patch(f"/api/sales-order/{order['id']}/", {"lines": rows}, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual([row["line_number"] for row in result.data["lines"]], [10, 20, 40])
        self.assertEqual([row["id"] for row in result.data["lines"][:2]], [row["id"] for row in order["lines"][:2]])
        first = result.data["lines"][0]
        changed = self.client.patch(f"/api/sales-order-line/{first['id']}/", {"line_number": 999}, format="json")
        self.assertEqual(changed.status_code, 200, changed.data)
        self.assertEqual(changed.data["line_number"], 10)
        added = self.post("sales-order-line", {"order": order["id"], **self.line(line_number=7)})
        self.assertEqual(added["line_number"], 50)

    def test_invalid_or_duplicate_nested_ids_roll_back_header_and_lines(self):
        order = self.order([self.line(), self.line()])
        other = self.order([self.line()], "OTHER")
        for rows in ([other["lines"][0]], [order["lines"][0], order["lines"][0]]):
            result = self.client.patch(f"/api/sales-order/{order['id']}/", {"notes": "must roll back", "lines": rows}, format="json")
            self.assertEqual(result.status_code, 400, result.data)
            saved = self.client.get(f"/api/sales-order/{order['id']}/").data
            self.assertEqual(saved["notes"], "")
            self.assertEqual([r["id"] for r in saved["lines"]], [r["id"] for r in order["lines"]])

    def test_imported_number_survives_and_new_line_uses_max_plus_ten(self):
        order = self.order([self.line()])
        SalesOrderLine.objects.filter(pk=order["lines"][0]["id"]).update(line_number=15)
        imported = self.client.get(f"/api/sales-order/{order['id']}/").data["lines"][0]
        result = self.client.patch(f"/api/sales-order/{order['id']}/", {"lines": [imported, self.line()]}, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual([row["line_number"] for row in result.data["lines"]], [15, 25])
        self.approve("sales-order", order["id"])
        saved = self.delivery([{"sales_order_line": imported["id"], "actual_quantity": "10"}])
        self.assertEqual(saved["lines"][0]["line_number"], 10)
        self.assertEqual(saved["lines"][0]["order_line_number"], 15)
        independent = self.client.get(f"/api/delivery-order-line/{saved['lines'][0]['id']}/")
        self.assertEqual(independent.data["order_line_number"], 15)

    def test_delivery_edit_and_standalone_creation_share_numbering(self):
        order = self.order([self.line(), self.line()])
        self.approve("sales-order", order["id"])
        saved = self.delivery([{"sales_order_line": row["id"], "actual_quantity": "10"} for row in order["lines"]])
        retained = {**saved["lines"][0], "line_number": 999, "order_line_number": 999}
        result = self.client.post(f"/api/delivery-order/{saved['id']}/save-sheet/", {
            **saved, "lines": [retained, {"sales_order_line": order["lines"][1]["id"], "actual_quantity": "5"}],
        }, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual([row["line_number"] for row in result.data["lines"]], [10, 30])
        self.assertEqual([row["order_line_number"] for row in result.data["lines"]], [10, 20])
        added = self.post("delivery-order-line", {**retained, "line_number": 3, "batch_number": "SPLIT"})
        self.assertEqual(added["line_number"], 40)
        edited = self.client.patch(f"/api/delivery-order-line/{added['id']}/", {"line_number": 5, "order_line_number": 55}, format="json")
        self.assertEqual(edited.status_code, 200, edited.data)
        self.assertEqual((edited.data["line_number"], edited.data["order_line_number"]), (40, 10))

    def test_database_uniqueness_and_foreign_key_protection(self):
        order = self.order([self.line()])
        row = SalesOrderLine.objects.get(pk=order["lines"][0]["id"])
        row.pk = None
        with self.assertRaises(IntegrityError), transaction.atomic():
            row.save()
        self.approve("sales-order", order["id"])
        self.delivery([{"sales_order_line": order["lines"][0]["id"], "actual_quantity": "10"}])
        from django.db.models.deletion import ProtectedError
        with self.assertRaises(ProtectedError):
            SalesOrderLine.objects.get(pk=order["lines"][0]["id"]).delete()

    def test_stock_enabled_counts_each_source_line_and_spares(self):
        order = self.order([self.line(spare_quantity="5"), self.line(spare_quantity="5")])
        self.approve("sales-order", order["id"])
        balance = StockBalance.objects.create(material_id=self.context["material"]["id"],
            location_id=self.context["location"]["id"], uom_id=self.context["uom"]["id"], quantity=100)
        saved = self.delivery([{"sales_order_line": row["id"], "actual_quantity": "10", "actual_spare_quantity": "2"}
                               for row in order["lines"]])
        with self.settings(ERP_DELIVERY_POST_STOCK=True):
            self.approve("delivery-order", saved["id"])
        balance.refresh_from_db()
        self.assertEqual(balance.quantity, 76)
        for row in order["lines"]:
            source = SalesOrderLine.objects.get(pk=row["id"])
            self.assertEqual((source.delivered_quantity, source.delivered_spare_quantity), (10, 2))
