from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.db import connection, connections, transaction
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APITransactionTestCase

from backend.domain.inventory import StockBalance, StockTransaction
from backend.models import Employee, Material, Location, Uom
from backend.test_support import CoreFlowSupport


class WarehouseDocumentTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.ctx = self.base_context()
        self.dest = self.post("location", {"code": "SCR01", "name": "报废仓"})
        self.checker = Employee.objects.create(code="ST01", name="盘点员")

    def document(self, kind, quantity="10.00000001", **extra):
        line = {"line_number": 10, "material": self.ctx["material"]["id"], "uom": self.ctx["uom"]["id"], "quantity": quantity}
        payload = {"kind": kind, "from_location": self.ctx["location"]["id"],
                   "to_location": self.dest["id"] if kind in {"transfer", "scrap"} else self.ctx["location"]["id"], "lines": [line], **extra}
        if kind == "count":
            payload.setdefault("checker", self.checker.id)
        return self.post("inventory-document", payload)

    def action(self, doc, action, expected=200, **data):
        result = self.client.post(f"/api/inventory-document/{doc['id']}/transition/", {"action": action, **data}, format="json")
        self.assertEqual(result.status_code, expected, result.data)
        return result.data

    def test_initial_count_uses_unplanned_receipt_once_and_can_reverse(self):
        from backend.domain.warehouse_documents import InventoryDictionary
        InventoryDictionary.objects.create(dictionary='MOV_CAT', code='001', name='初盘导入')
        line = {'line_number': 10, 'material': self.ctx['material']['id'], 'quantity': '1000', 'reference_cost': '10'}
        doc = self.document('receipt', category_code='001', lines=[line])
        self.action(doc, 'approve')
        self.action(doc, 'approve')
        self.assertEqual(StockTransaction.objects.count(), 1)
        self.assertEqual(StockTransaction.objects.get().movement_type, '110')
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('1000'))
        self.action(doc, 'reverse', reason='初盘录入纠正')
        self.assertEqual(StockBalance.objects.get().quantity, 0)

    def test_source_overissue_flag_allows_negative_balance(self):
        Location.objects.filter(pk=self.ctx['location']['id']).update(allow_negative=True)
        issue = self.document('issue', '3')
        self.action(issue, 'approve')
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('-3'))
        self.assertEqual(StockTransaction.objects.get().movement_type, '210')
        self.action(issue, 'reverse', reason='数量纠正')
        reversal = StockTransaction.objects.get(reversal_of__isnull=False)
        self.assertEqual(reversal.movement_type, '210')
        self.assertEqual(reversal.quantity, Decimal('3'))

    def test_positive_reservations_remain_protected_on_overissue_location(self):
        self.action(self.document('receipt', '10'), 'approve')
        Location.objects.filter(pk=self.ctx['location']['id']).update(allow_negative=True)
        StockBalance.objects.update(reserved_quantity=2)
        self.action(self.document('issue', '11'), 'approve', expected=400)
        self.assertEqual(StockBalance.objects.get().quantity, Decimal('10'))

    def test_receipt_issue_transfer_scrap_and_reversal_preserve_ledger(self):
        receipt = self.document("receipt")
        self.action(receipt, "approve")
        self.action(receipt, "approve")
        self.assertEqual(StockTransaction.objects.count(), 1)
        issue = self.document("issue", "2")
        self.action(issue, "approve")
        transfer = self.document("transfer", "3")
        self.action(transfer, "confirm")
        self.action(transfer, "approve")
        scrap = self.document("scrap", "1")
        self.action(scrap, "approve")
        self.assertEqual(sum(StockBalance.objects.values_list("quantity", flat=True)), Decimal("8.00000001"))
        self.action(scrap, "reverse", reason="测试恢复")
        self.action(scrap, "reverse", reason="重复请求")
        self.assertEqual(StockTransaction.objects.filter(reversal_of__isnull=False).count(), 2)
        for balance in StockBalance.objects.all():
            ledger = sum(StockTransaction.objects.filter(material=balance.material, location=balance.location, batch_number=balance.batch_number).values_list("quantity", flat=True))
            self.assertEqual(balance.quantity, ledger)

    def test_overissue_and_direct_ledger_edits_are_rejected(self):
        issue = self.document("issue", "1")
        self.action(issue, "approve", expected=400)
        self.assertFalse(StockBalance.objects.exists())
        self.assertFalse(StockTransaction.objects.exists())
        self.assertEqual(self.client.post("/api/stock-balance/", {}, format="json").status_code, 405)
        self.assertEqual(self.client.post("/api/stock-transaction/", {}, format="json").status_code, 405)

    def test_count_freezes_shared_posting_entry_and_releases_after_posting(self):
        receipt = self.document("receipt", "10")
        self.action(receipt, "approve")
        count = self.document("count", "0")
        count = self.action(count, "confirm")
        blocked = self.document("issue", "1")
        self.action(blocked, "approve", expected=400)
        self.action(count, "count-results", results={str(count["lines"][0]["id"]): "8.12345678"})
        self.action(count, "approve")
        self.assertEqual(StockBalance.objects.get().quantity, Decimal("8.12345678"))
        self.action(blocked, "approve")
        self.assertEqual(StockBalance.objects.get().quantity, Decimal("7.12345678"))

    def test_atomic_sheet_and_posted_immutability(self):
        receipt = self.document("receipt", "5")
        self.action(receipt, "approve")
        self.assertEqual(self.client.patch(f"/api/inventory-document/{receipt['id']}/", {"notes": "change"}, format="json").status_code, 400)
        self.assertEqual(self.client.delete(f"/api/inventory-document/{receipt['id']}/").status_code, 400)
        count = self.document("count", "0", count_basis="1")
        self.action(count, "confirm", expected=400)

    def test_count_checker_is_a_linked_active_user_profile(self):
        count = self.document("count", "0")
        self.assertEqual(count["checker"], self.checker.id)
        self.assertEqual(count["checker_code"], "ST01")
        self.assertEqual(count["checker_name"], "盘点员")
        self.checker.is_locked = True
        self.checker.save(update_fields=["is_locked", "updated_at"])
        response = self.client.post("/api/inventory-document/", {
            "kind": "count", "from_location": self.ctx["location"]["id"],
            "lines": [{"line_number": 10, "material": self.ctx["material"]["id"], "uom": self.ctx["uom"]["id"], "quantity": "0"}],
            "checker": self.checker.id,
        }, format="json")
        self.assertEqual(response.status_code, 400, response.data)
        self.checker.is_locked = False
        self.checker.is_left = True
        self.checker.save(update_fields=["is_locked", "is_left", "updated_at"])
        response = self.client.post("/api/inventory-document/", {
            "kind": "count", "from_location": self.ctx["location"]["id"],
            "lines": [{"line_number": 10, "material": self.ctx["material"]["id"], "uom": self.ctx["uom"]["id"], "quantity": "0"}],
            "checker": self.checker.id,
        }, format="json")
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data["checker"][0], "锁定或出差/请假用户不可作为盘点人")

    def test_stock_adjust_rolls_back_on_duplicate_source(self):
        params = dict(material=Material.objects.get(pk=self.ctx["material"]["id"]), location=Location.objects.get(pk=self.ctx["location"]["id"]),
                      uom=Uom.objects.get(pk=self.ctx["uom"]["id"]), quantity=Decimal("3"), movement_type="test", source_model="test", source_id=1, source_line_id=1, actor="test")
        StockBalance.adjust(**params)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError), transaction.atomic():
            StockBalance.adjust(**params)
        self.assertEqual(StockBalance.objects.get().quantity, 3)

    def test_business_unit_conversion_and_report_reconcile(self):
        unit = Uom.objects.get(pk=self.ctx["uom"]["id"])
        box = Uom.objects.create(code="BOX", name="箱", category=unit.category)
        StockBalance.adjust(material=Material.objects.get(pk=self.ctx["material"]["id"]),
            location=Location.objects.get(pk=self.ctx["location"]["id"]), uom=box,
            quantity=Decimal("2.5"), uom_rate_m=1, uom_rate_d=12, movement_type="receipt",
            source_model="test", source_id=1, source_line_id=1, actor="test")
        row = StockTransaction.objects.get()
        self.assertEqual(row.quantity, 30)
        self.assertEqual(row.business_quantity, Decimal("2.5"))
        self.assertEqual(row.business_uom, box)
        report = self.client.get("/api/inventory-report/")
        self.assertEqual(report.status_code, 200, report.data)
        self.assertEqual(Decimal(report.data[0]["closing"]), 30)

    def test_transfer_choices_and_line_audit_preserve_identity(self):
        doc = self.document("transfer", "1")
        self.assertEqual(doc["transfer_class"], "1")
        original = doc["lines"][0]
        self.assertEqual(original["created_by"], self.user.username)
        payload = {"transfer_class": "3", "lines": [{**original, "quantity": "2", "created_by": "forged", "modified_by": "forged", "modification_count": 99, "material_name": "forged"}]}
        url = f"/api/inventory-document/{doc['id']}/"
        result = self.client.patch(url, payload, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        line = result.data["lines"][0]
        self.assertEqual(line["id"], original["id"])
        self.assertEqual(line["created_at"], original["created_at"])
        self.assertEqual(line["created_by"], self.user.username)
        self.assertEqual(line["modified_by"], self.user.username)
        self.assertEqual(line["modification_count"], 1)
        self.assertEqual(line["material_name"], self.ctx["material"]["name"])
        repeat = self.client.patch(url, payload, format="json")
        self.assertEqual(repeat.data["lines"][0]["modification_count"], 1)
        payload["transfer_class"] = "4"
        self.assertEqual(self.client.patch(url, payload, format="json").status_code, 400)
        payload["transfer_class"] = "2"
        payload["lines"][0]["id"] = 9999999
        self.assertEqual(self.client.patch(url, payload, format="json").status_code, 400)

    def test_material_unit_is_derived_and_source_field_limits_are_checked(self):
        doc = self.document("receipt", "1")
        line = doc["lines"][0]
        different = Uom.objects.create(code="ALT", name="备用", category=Uom.objects.get(pk=self.ctx["uom"]["id"]).category)
        result = self.client.patch(f"/api/inventory-document/{doc['id']}/", {"lines": [{**line, "uom": different.pk}]}, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(result.data["lines"][0]["uom"], self.ctx["uom"]["id"])
        for key, value in [("grade", "ABC"), ("batch_number", "X" * 19)]:
            result = self.client.patch(f"/api/inventory-document/{doc['id']}/", {"lines": [{**line, key: value}]}, format="json")
            self.assertEqual(result.status_code, 400, result.data)

    def test_inventory_query_views_keep_document_and_ledger_trace(self):
        receipt = self.document("receipt", "4")
        self.action(receipt, "approve")
        transfer = self.document("transfer", "1")
        self.action(transfer, "confirm")
        self.action(transfer, "approve")
        count = self.document("count", "0")
        self.action(count, "confirm")
        self.action(count, "count-results", results={str(count["lines"][0]["id"]): "3"})
        self.action(count, "approve")
        for endpoint in ("material-inventory-detail", "material-movement-detail", "transfer-detail", "count-result"):
            result = self.client.get(f"/api/{endpoint}/", {"q": self.ctx["material"]["code"]})
            self.assertEqual(result.status_code, 200, result.data)
            self.assertTrue(result.data, endpoint)
        transfer_rows = self.client.get("/api/transfer-detail/").data
        self.assertEqual(transfer_rows[0]["number"], transfer["number"])
        self.assertEqual(transfer_rows[0]["from_location_code"], self.ctx["location"]["code"])
        count_rows = self.client.get("/api/count-result/").data
        self.assertEqual(count_rows[0]["checker_code"], self.checker.code)
        self.assertEqual(Decimal(count_rows[0]["variance_quantity"]), Decimal("0"))


class ConcurrentInventoryTests(CoreFlowSupport, APITransactionTestCase):
    def test_two_simultaneous_issues_cannot_overdraw(self):
        if connection.vendor != "microsoft":
            self.skipTest("Requires SQL Server row locking")
        ctx = self.base_context()
        params = dict(material=Material.objects.get(pk=ctx["material"]["id"]),
            location=Location.objects.get(pk=ctx["location"]["id"]),
            uom=Uom.objects.get(pk=ctx["uom"]["id"]), source_model="concurrency", actor="test")
        StockBalance.adjust(**params, quantity=10, movement_type="opening", source_id=1, source_line_id=1)
        barrier = Barrier(2)

        def issue(line_id):
            try:
                barrier.wait(timeout=10)
                StockBalance.adjust(**params, quantity=-7, movement_type="issue", source_id=line_id, source_line_id=line_id)
                return "posted"
            except ValidationError:
                return "rejected"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(issue, [2, 3]))
        self.assertCountEqual(results, ["posted", "rejected"])
        self.assertEqual(StockBalance.objects.get().quantity, 3)
        self.assertEqual(StockTransaction.objects.count(), 2)
