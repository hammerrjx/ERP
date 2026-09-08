import uuid
from rest_framework.test import APITestCase

from backend.models import DeliveryOrder, DeliveryOrderLine, DeliveryNumberReservation, SalesOrderLine
from backend.test_support import CoreFlowSupport


class DeliveryWorkflowTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.context = self.base_context()
        self.order, self.line = self.make_order("PO-ONE")

    def make_order(self, po, quantity="100", spare="0"):
        order = self.post("sales-order", {
            "customer": self.context["customer"]["id"], "currency": self.context["currency"]["id"],
            "customer_po": po, "delivery_address": "客户资料地址", "promised_date": "2026-09-07",
        })
        line = self.post("sales-order-line", {
            "order": order["id"], "line_number": 1, "material": self.context["material"]["id"],
            "uom": self.context["uom"]["id"], "quantity": quantity, "spare_quantity": spare, "unit_price": "12", "promised_date": "2026-09-07",
        })
        self.approve("sales-order", order["id"])
        return order, line

    def reserve(self, key=None):
        response = self.client.post("/api/delivery-order/reserve-number/", {
            "request_id": key or str(uuid.uuid4()), "delivery_date": "2026-09-07",
        }, format="json")
        self.assertIn(response.status_code, (200, 201), response.data)
        return response.data

    def payload(self, amount="25", line=None):
        return {**self.reserve(), "customer": self.context["customer"]["id"],
                "delivery_date": "2026-09-07", "delivery_address": "司机实际收货厂区", "address_code": "0",
                "lines": [{"sales_order_line": (line or self.line)["id"], "actual_quantity": amount, "notes": "免费样品说明"}]}

    def save(self, payload, status=201):
        response = self.client.post("/api/delivery-order/save-sheet/", payload, format="json")
        self.assertEqual(response.status_code, status, response.data)
        return response.data

    def test_reservation_is_early_idempotent_and_cancelled_numbers_are_not_reused(self):
        key = str(uuid.uuid4())
        first = self.reserve(key)
        self.assertEqual(self.reserve(key), first)
        self.assertEqual(DeliveryOrder.objects.count(), 0)
        self.assertRegex(first["number"], r"^MYSD2609\d{4}$")
        self.assertNotEqual(self.reserve()["number"], first["number"])

    def test_mixed_950_and_50_fulfilment_and_replacement(self):
        from decimal import Decimal
        _, line = self.make_order("MIXED", "950", "50")
        for formal, spare in (("330", "20"), ("285", "15"), ("335", "15")):
            payload = self.payload(formal, line)
            payload["lines"][0]["actual_spare_quantity"] = spare
            saved = self.save(payload)
            self.approve("delivery-order", saved["id"])
            duplicate = self.client.post(f"/api/delivery-order/{saved['id']}/approve/")
            self.assertEqual(duplicate.status_code, 200, duplicate.data)
        source = SalesOrderLine.objects.get(pk=line["id"])
        self.assertEqual((source.delivered_quantity, source.delivered_spare_quantity), (950, 50))
        summary = self.client.get(f"/api/sales-order-line/{source.pk}/").data["execution_summary"]
        self.assertTrue(summary["fulfilled"])
        self.assertFalse(summary["has_history_gap"])
        from backend.models import DocumentEvidence
        DocumentEvidence.objects.create(document_type="deliveryorder", document_id=saved["id"],
                                        evidence_type="customer_delivery", file="test-receipt.pdf")
        self.assertEqual(self.client.post(f"/api/delivery-order/{saved['id']}/confirm/").status_code, 200)
        source.refresh_from_db()
        self.assertEqual((source.delivered_quantity, source.delivered_spare_quantity), (950, 50))
        for action in ("void", "unapprove"):
            self.assertEqual(self.client.post(f"/api/delivery-order/{saved['id']}/{action}/").status_code, 400)
        source.line_status = "C"
        source.save(update_fields=["line_status"])
        returned = self.payload("-1", line)
        returned["document_type"] = "return"
        returned["lines"][0]["actual_spare_quantity"] = "-1"
        reversal = self.save(returned)
        detail = self.client.get(f"/api/delivery-order/{reversal['id']}/").data
        self.assertEqual(Decimal(detail["lines"][0]["delivery_amount"]), Decimal("-12"))
        self.approve("delivery-order", reversal["id"])
        source.refresh_from_db()
        self.assertEqual(source.line_status, "normal")
        self.assertEqual((source.delivered_quantity, source.delivered_spare_quantity), (949, 49))
        replacement = self.payload("1", line)
        replacement["lines"][0]["actual_spare_quantity"] = "1"
        self.approve("delivery-order", self.save(replacement)["id"])
        source.refresh_from_db()
        self.assertEqual((source.delivered_quantity, source.delivered_spare_quantity), (950, 50))

    def test_spare_only_plan_partial_delivery_and_no_unplanned_spare(self):
        _, line = self.make_order("SPARE", "0", "2097")
        self.assertEqual(float(line["unit_price"]), 0)
        payload = self.payload("0", line)
        payload["lines"][0]["actual_spare_quantity"] = "2000"
        saved = self.save(payload)
        source = SalesOrderLine.objects.get(pk=line["id"])
        self.assertEqual(source.delivered_spare_quantity, 0)
        self.approve("delivery-order", saved["id"])
        summary = self.client.get(f"/api/sales-order-line/{source.pk}/").data["execution_summary"]
        self.assertEqual(float(summary["spare_remaining"]), 97)
        self.assertFalse(summary["fulfilled"])
        unexpected = self.payload("0")
        unexpected["lines"][0]["actual_spare_quantity"] = "1"
        self.save(unexpected, 400)

    def test_execution_gap_uses_imported_baseline_and_posted_not_approval(self):
        source = SalesOrderLine.objects.get(pk=self.line["id"])
        source.delivered_spare_quantity = 250
        source.spare_quantity = 300
        source.save()
        summary = self.client.get(f"/api/sales-order-line/{source.pk}/").data["execution_summary"]
        self.assertTrue(summary["has_history_gap"])
        self.assertEqual(float(summary["spare_unrepresented"]), 250)
        self.assertEqual(float(summary["spare_remaining"]), 50)

    def test_imported_posted_draft_cannot_be_edited_deleted_or_executed(self):
        saved = self.save(self.payload("10"))
        DeliveryOrder.objects.filter(pk=saved["id"]).update(posted=True)
        self.assertEqual(self.client.patch(f"/api/delivery-order/{saved['id']}/", {"notes": "changed"}).status_code, 400)
        self.assertEqual(self.client.delete(f"/api/delivery-order/{saved['id']}/").status_code, 400)
        self.assertEqual(self.client.post(f"/api/delivery-order/{saved['id']}/submit/").status_code, 400)

    def test_reserved_draft_is_voided_without_reusing_number(self):
        saved = self.save(self.payload("10"))
        self.assertEqual(self.client.delete(f"/api/delivery-order/{saved['id']}/").status_code, 400)
        self.assertEqual(self.client.post(f"/api/delivery-order/{saved['id']}/void/").status_code, 200)
        self.assertTrue(DeliveryNumberReservation.objects.filter(delivery_id=saved["id"]).exists())
        candidates = self.client.get("/api/delivery-order/order-candidates/", {"customer": self.context["customer"]["id"]})
        self.assertEqual(float(candidates.data["results"][0]["available_quantity"]), 100)

    def test_save_defaults_notes_address_and_duplicate_request(self):
        payload = self.payload()
        saved = self.save(payload)
        self.assertEqual(saved["number"], payload["number"])
        self.assertEqual(saved["delivery_address"], "司机实际收货厂区")
        self.assertEqual(saved["lines"][0]["notes"], "免费样品说明")
        self.assertEqual(saved["lines"][0]["source_location"], self.context["location"]["id"])
        self.save(payload, 200)
        self.assertEqual(DeliveryOrder.objects.count(), 1)

    def test_multiple_orders_same_line_number_keep_each_po(self):
        _, second = self.make_order("PO-TWO")
        payload = self.payload()
        payload["lines"].append({"sales_order_line": second["id"], "actual_quantity": "30"})
        saved = self.save(payload)
        self.assertIsNone(saved["sales_order"])
        self.assertEqual([line["line_number"] for line in saved["lines"]], [10, 20])
        self.assertEqual([line["customer_po"] for line in saved["lines"]], ["PO-ONE", "PO-TWO"])

    def test_edit_is_atomic_and_deletes_omitted_lines(self):
        _, second = self.make_order("PO-TWO")
        payload = self.payload()
        payload["lines"].append({"sales_order_line": second["id"], "actual_quantity": "30"})
        saved = self.save(payload)
        edit = {**saved, "notes": "不能部分保存"}
        edit["lines"][1]["actual_quantity"] = "101"
        response = self.client.post(f"/api/delivery-order/{saved['id']}/save-sheet/", edit, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(DeliveryOrder.objects.get(pk=saved["id"]).notes, "")
        edit["lines"] = saved["lines"][:1]
        response = self.client.post(f"/api/delivery-order/{saved['id']}/save-sheet/", edit, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(DeliveryOrderLine.objects.filter(delivery_id=saved["id"]).count(), 1)
        stale = self.client.post(f"/api/delivery-order/{saved['id']}/save-sheet/", edit, format="json")
        self.assertEqual(stale.status_code, 400)

    def test_pending_drafts_reserve_capacity_but_preview_does_not(self):
        self.save(self.payload("60"))
        response = self.client.get("/api/delivery-order/order-candidates/", {
            "customer": self.context["customer"]["id"], "customer_po": "ONE", "match": "contains",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["available_quantity"], "40.00000000")
        self.save(self.payload("41"), 400)
        self.assertEqual(DeliveryOrder.objects.count(), 1)

    def test_return_sign_is_preserved_and_does_not_change_separate_return_total(self):
        first = self.save(self.payload("50"))
        self.approve("delivery-order", first["id"])
        negative = self.payload("-50")
        negative["document_type"] = "return"
        returned = self.save(negative)
        self.approve("delivery-order", returned["id"])
        source = SalesOrderLine.objects.get(pk=self.line["id"])
        self.assertEqual(source.delivered_quantity, 0)
        self.assertEqual(source.returned_quantity, 0)
        positive = self.payload("100")
        positive["document_type"] = "return"
        again = self.save(positive)
        self.assertEqual(again["lines"][0]["actual_quantity"], "100.00000000")

    def test_split_rows_are_checked_as_a_total(self):
        payload = self.payload("60")
        payload["lines"][0]["batch_number"] = "A"
        payload["lines"].append({"sales_order_line": self.line["id"], "actual_quantity": "60", "batch_number": "B"})
        self.save(payload, 400)
        self.assertFalse(DeliveryOrder.objects.exists())
        self.assertIsNone(DeliveryNumberReservation.objects.get(pk=payload["reservation"]).delivery_id)

    def test_cross_customer_cannot_save_and_bad_quantity_is_400(self):
        payload = self.payload("NaN")
        self.save(payload, 400)
        payload["lines"][0]["actual_quantity"] = "1"
        another = self.post("partner", {"code": "C002", "name": "客户二", "short_name": "客户二", "kind": "customer"})
        payload["customer"] = another["id"]
        self.save(payload, 400)

    def test_unit_price_snapshot_survives_later_order_price_change(self):
        saved = self.save(self.payload())
        SalesOrderLine.objects.filter(pk=self.line["id"]).update(unit_price="99")
        detail = self.client.get(f"/api/delivery-order/{saved['id']}/")
        self.assertEqual(detail.data["lines"][0]["unit_price"], "12.000000")

    def test_all_four_filters_resolve_the_same_source_line(self):
        cm = self.post("customer-material", {
            "customer": self.context["customer"]["id"], "material": self.context["material"]["id"],
            "customer_code": "690-FCXS202409-2228", "terminal_customer_code": "180-SBTPK902-0004",
        })
        SalesOrderLine.objects.filter(pk=self.line["id"]).update(customer_material_id=cm["id"])
        for key, value in (("customer_po", "PO-ONE"), ("material_code", "FG-001"),
                           ("customer_material_code", "690-FCXS202409-2228"),
                           ("terminal_material_code", "180-SBTPK902-0004")):
            with self.subTest(key=key):
                result = self.client.get("/api/delivery-order/order-candidates/", {
                    "customer": self.context["customer"]["id"], "match": "exact", key: value,
                })
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.data["results"][0]["sales_order_line"], self.line["id"])

    def test_source_precision_is_not_rounded_to_six_places(self):
        saved = self.save(self.payload("0.00000001"))
        self.assertEqual(saved["lines"][0]["actual_quantity"], "0.00000001")

    def test_user_without_create_permission_cannot_reserve_or_save(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user("reader", password="test")
        payload = self.payload()
        self.client.force_authenticate(user)
        reserve = self.client.post("/api/delivery-order/reserve-number/", {
            "request_id": str(uuid.uuid4()), "delivery_date": "2026-09-07",
        }, format="json")
        self.assertEqual(reserve.status_code, 403)
        self.save(payload, 403)

    def test_negative_delivery_and_separate_return_share_capacity(self):
        saved = self.save(self.payload("50"))
        self.approve("delivery-order", saved["id"])
        self.save(self.payload("-40"))
        header = self.post("sales-return", {
            "customer": self.context["customer"]["id"], "no_order": False,
            "srm_number": "RETURN-TEST", "reason": "退货",
        })
        response = self.client.post("/api/sales-return-line/", {
            "sales_return": header["id"], "sales_order_line": self.line["id"], "line_number": 1,
            "material": self.context["material"]["id"], "uom": self.context["uom"]["id"],
            "quantity": "11", "original_location": self.context["location"]["id"],
            "return_location": self.context["location"]["id"],
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_approval_keeps_inventory_unchanged_when_disabled(self):
        from backend.models import StockBalance, StockTransaction
        saved = self.save(self.payload("10"))
        self.approve("delivery-order", saved["id"])
        returned = self.save(self.payload("-10"))
        self.approve("delivery-order", returned["id"])
        self.assertFalse(StockBalance.objects.exists())
        self.assertFalse(StockTransaction.objects.exists())

    def test_standalone_detail_change_invalidates_open_sheet(self):
        saved = self.save(self.payload())
        response = self.client.patch(f"/api/delivery-order-line/{saved['lines'][0]['id']}/", {
            "actual_quantity": "30", "notes": "另一窗口修改",
        }, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        stale = self.client.post(f"/api/delivery-order/{saved['id']}/save-sheet/", saved, format="json")
        self.assertEqual(stale.status_code, 400, stale.data)
        self.assertEqual(DeliveryOrderLine.objects.get(pk=saved["lines"][0]["id"]).actual_quantity, 30)

    def test_original_delivery_capacity_is_shared_with_separate_returns(self):
        first = self.save(self.payload("50"))
        self.approve("delivery-order", first["id"])
        second = self.save(self.payload("50"))
        self.approve("delivery-order", second["id"])
        header = self.post("sales-return", {
            "customer": self.context["customer"]["id"], "no_order": False,
            "srm_number": "RETURN-ORIGINAL", "reason": "退货",
        })
        self.post("sales-return-line", {
            "sales_return": header["id"], "source_delivery_line": first["lines"][0]["id"],
            "line_number": 1, "material": self.context["material"]["id"],
            "uom": self.context["uom"]["id"], "quantity": "50",
            "original_location": self.context["location"]["id"], "return_location": self.context["location"]["id"],
        })
        self.approve("sales-return", header["id"])
        payload = self.payload("-1")
        payload["lines"][0]["source_delivery_line"] = first["lines"][0]["id"]
        rejected = self.save(payload, 400)
        self.assertIn("原送货行", str(rejected))

    def test_split_spare_reversals_cannot_exceed_original_line(self):
        SalesOrderLine.objects.filter(pk=self.line["id"]).update(spare_quantity=10)
        first_payload = self.payload("0")
        first_payload["lines"][0]["actual_spare_quantity"] = "5"
        first = self.save(first_payload)
        self.approve("delivery-order", first["id"])
        second_payload = self.payload("0")
        second_payload["lines"][0]["actual_spare_quantity"] = "5"
        second = self.save(second_payload)
        self.approve("delivery-order", second["id"])
        payload = self.payload("0")
        payload["lines"] = [
            {"sales_order_line": self.line["id"], "actual_quantity": "0", "actual_spare_quantity": "-3",
             "source_delivery_line": first["lines"][0]["id"], "batch_number": batch}
            for batch in ("A", "B")
        ]
        rejected = self.save(payload, 400)
        self.assertIn("原送货行备品", str(rejected))

    def test_spare_only_delivery_deducts_stock_when_enabled(self):
        from backend.models import StockBalance, StockTransaction
        SalesOrderLine.objects.filter(pk=self.line["id"]).update(spare_quantity=10)
        StockBalance.objects.create(
            material_id=self.context["material"]["id"], location_id=self.context["location"]["id"],
            uom_id=self.context["uom"]["id"], quantity=10,
        )
        payload = self.payload("0")
        payload["lines"][0]["actual_spare_quantity"] = "3"
        saved = self.save(payload)
        with self.settings(ERP_DELIVERY_POST_STOCK=True):
            self.approve("delivery-order", saved["id"])
        self.assertEqual(StockBalance.objects.get().quantity, 7)
        self.assertEqual(StockTransaction.objects.get().quantity, -3)

    def test_import_uses_actual_quantity_and_extension_fields(self):
        from datetime import date
        from backend.management.commands.import_deliveries import Command
        source = {
            "orders": [{"so_nbr": self.order["number"], "so_cust": "C001", "so_curr": "CNY", "so_po": "PO-ONE", "so_ord_date": date(2026, 9, 7)}],
            "order_lines": [{"sod_nbr": self.order["number"], "sod_line": 1, "sod_part": "FG-001", "sod_um": "JIAN", "sod_qty_ord": 100, "sod_qty_shp": 95}],
            "headers": [{"dn_dn": "MYSD26090001", "dn_cust": "C001", "dn_date": date(2026, 9, 7), "dn_char1": "2", "dn_char2": "SRM-EXACT", "dn_char3": "收货厂区", "dn_char4": "红冲单据", "dn_txt": "0", "dn_pst": True}],
            "lines": [{"dnd_dn": "MYSD26090001", "dnd_line": 10, "dnd_so": self.order["number"], "dnd_so_line": 1, "dnd_part": "FG-001", "dnd_um": "JIAN", "dnd_loc": "FG01", "dnd_qty_ship": -5, "dnd_qty_shipped": 95, "dnd_qty_spare_ship": 0, "dnd_qty_spared": 3, "dnd_rmks": "明细备注"}],
        }
        Command().import_rows(source)
        saved = DeliveryOrder.objects.get(number="MYSD26090001")
        self.assertEqual(saved.srm_number, "SRM-EXACT")
        self.assertEqual(saved.delivery_mode, "supplier")
        self.assertEqual(saved.document_type, "red_flush")
        self.assertEqual(saved.lines.get().actual_quantity, -5)
        self.assertEqual(saved.lines.get().actual_spare_quantity, 0)
        self.assertEqual(saved.lines.get().notes, "明细备注")
