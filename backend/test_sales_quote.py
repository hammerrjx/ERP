from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from backend.models import (
    Currency, CustomerAddress, CustomerMaterial, Location, Material, Partner, ProductCategory,
    SalesQuote, Uom, UomCategory,
)
from backend.test_support import SourceDatabaseIsolatedMixin


class SalesQuoteApiTests(SourceDatabaseIsolatedMixin, APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("quote-user", password="pass")
        self.client.force_authenticate(self.user)
        category = UomCategory.objects.create(code="COUNT-Q", name="数量")
        self.uom = Uom.objects.create(code="PCS-Q", name="个", category=category)
        location = Location.objects.create(code="FG-Q", name="报价成品库")
        product_category = ProductCategory.objects.create(
            code="QUOTE", name="报价产品", default_uom=self.uom, default_location=location,
        )
        self.currency = Currency.objects.create(code="RMB-Q", name="人民币")
        self.customer = Partner.objects.create(
            code="Q-CUST", name="报价客户", short_name="报价客户", kind="customer",
            currency=self.currency, quote_tax_included=True, tax_rate="13", discount_rate="90",
            backup_ratio="2", delivery_address="客户收货仓", payment_terms="月结30天",
        )
        self.other_customer = Partner.objects.create(
            code="Q-OTHER", name="其他客户", short_name="其他客户", kind="customer", currency=self.currency,
        )
        self.material = Material.objects.create(
            code="Q-MAT", name="透明载带", specification="T1.6xL360", category=product_category,
            uom=self.uom, default_location=location, tax_code="TAX-Q",
        )
        self.customer_material = CustomerMaterial.objects.create(
            customer=self.customer, material=self.material, customer_code="CUST-PART-01",
            customer_name="客户透明载带", customer_uom=self.uom,
            terminal_customer_code="END-01", terminal_customer_name="终端客户",
        )
        self.other_customer_material = CustomerMaterial.objects.create(
            customer=self.other_customer, material=self.material, customer_code="OTHER-PART",
        )
        self.address = CustomerAddress.objects.create(customer=self.customer, code="0001", address="客户一收货仓")
        self.other_address = CustomerAddress.objects.create(customer=self.other_customer, code="0001", address="其他客户仓")

    def payload(self, effective_date="2026-01-01", customer_material=None):
        return {
            "customer": self.customer.id,
            "effective_date": effective_date,
            "usage": "生产",
            "notes": "报价测试",
            "lines": [{
                "material": self.material.id,
                "customer_material": customer_material or self.customer_material.id,
                "unit_price": "45.00000000",
                "tiers": [
                    {"min_quantity": "4000", "unit_price": "43.00000000", "backup_ratio": "1"},
                    {"min_quantity": "6000", "unit_price": "40.00000000", "backup_ratio": "0"},
                ],
            }],
        }

    def create_quote(self, effective_date="2026-01-01"):
        response = self.client.post("/api/sales-quote/", self.payload(effective_date), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def action(self, quote_id, name, body=None):
        response = self.client.post(f"/api/sales-quote/{quote_id}/{name}/", body or {}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        return response.data

    def test_nested_quote_autofills_customer_material_and_calculations(self):
        quote = self.create_quote()
        self.assertTrue(quote["number"].startswith(f"MYSQ{timezone.localdate():%y%m}"))
        self.assertEqual(quote["currency"], self.currency.id)
        self.assertEqual(quote["tax_rate"], "13.00000000")
        self.assertEqual(quote["discount_rate"], "90.00000000")
        self.assertEqual(quote["address"], "客户收货仓")
        self.assertEqual(quote["material_code"], "Q-MAT")
        self.assertEqual(quote["customer_material_code"], "CUST-PART-01")
        self.assertEqual(quote["unit_price"], "45.00000000")
        line = quote["lines"][0]
        self.assertEqual(line["customer_material_code"], "CUST-PART-01")
        self.assertEqual(line["terminal_customer_code"], "END-01")
        self.assertEqual(line["material_name"], "透明载带")
        self.assertEqual(line["material_specification"], "T1.6xL360")
        self.assertEqual(line["discounted_unit_price"], "40.50000000")
        self.assertEqual(line["untaxed_unit_price"], "39.82300885")
        self.assertEqual(line["tiers"][0]["untaxed_unit_price"], "38.05309735")

    def test_quote_rejects_customer_material_from_another_customer(self):
        response = self.client.post(
            "/api/sales-quote/", self.payload(customer_material=self.other_customer_material.id), format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("三端一致", str(response.data))

    def test_quote_address_is_optional_and_snapshotted(self):
        payload = self.payload()
        payload.update({"address_code": self.address.id})
        response = self.client.post("/api/sales-quote/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["address_code"], self.address.id)
        self.assertEqual(response.data["address_snapshot"], "客户一收货仓")
        self.assertEqual(response.data["address"], "客户一收货仓")

        temporary = self.payload()
        temporary["address"] = "临时收货地址"
        response = self.client.post("/api/sales-quote/", temporary, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["address_code"])
        self.assertEqual(response.data["address"], "临时收货地址")

    def test_quote_rejects_address_from_another_customer(self):
        response = self.client.post("/api/sales-quote/", {**self.payload(), "address_code": self.other_address.id}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("地址", str(response.data))

    def test_quote_currency_and_tax_override_are_snapshots(self):
        usd = Currency.objects.create(code="USD-Q", name="美元")
        response = self.client.post(
            "/api/sales-quote/",
            {**self.payload(), "currency": usd.id, "tax_included": False, "tax_rate": "6"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["currency"], usd.id)
        self.assertFalse(response.data["tax_included"])
        self.assertEqual(response.data["tax_rate"], "6.00000000")
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.currency_id, self.currency.id)
        self.assertEqual(str(self.customer.tax_rate), "13.00000000")

    def test_quote_allows_missing_customer_material(self):
        payload = self.payload()
        payload["lines"][0].pop("customer_material")
        response = self.client.post("/api/sales-quote/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        line = response.data["lines"][0]
        self.assertIsNone(line["customer_material"])
        self.assertEqual(line["customer_material_code"], "")
        self.assertEqual(line["material_code"], "Q-MAT")

    def test_quote_discount_override_is_snapshot_and_does_not_change_customer(self):
        response = self.client.post(
            "/api/sales-quote/",
            {**self.payload(), "discount_rate": "85"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["discount_rate"], "85.00000000")
        self.assertEqual(response.data["lines"][0]["discounted_unit_price"], "38.25000000")
        self.customer.refresh_from_db()
        self.assertEqual(str(self.customer.discount_rate), "90.00000000")

    def test_workflow_uses_authenticated_actor_and_ratification_closes_previous_quote(self):
        first = self.create_quote("2026-01-01")
        confirmed = self.action(first["id"], "confirm", {"actor": "伪造确认人"})
        self.assertEqual(confirmed["confirmed_by"], self.user.username)
        approved = self.action(first["id"], "approve", {"actor": "伪造审核人"})
        self.assertEqual(approved["approved_by"], self.user.username)
        ratified = self.action(first["id"], "ratify", {"actor": "伪造核准人"})
        self.assertEqual(ratified["ratified_by"], self.user.username)

        previous = self.client.get("/api/sales-quote/previous/", {
            "customer": self.customer.id, "material": self.material.id,
            "customer_material": self.customer_material.id,
        })
        self.assertEqual(previous.status_code, 200, previous.data)
        self.assertEqual(previous.data["quote_number"], first["number"])

        second = self.create_quote("2026-02-01")
        self.action(second["id"], "confirm")
        self.action(second["id"], "approve")
        self.action(second["id"], "ratify")
        self.assertEqual(SalesQuote.objects.get(pk=first["id"]).expiry_date.isoformat(), "2026-01-31")

    def ratify_quote(self, effective_date, currency=None, price="45"):
        payload = self.payload(effective_date)
        if currency:
            payload["currency"] = currency.id
        payload["lines"][0]["unit_price"] = price
        quote = self.client.post("/api/sales-quote/", payload, format="json")
        self.assertEqual(quote.status_code, 201, quote.data)
        for action in ("confirm", "approve", "ratify"):
            self.action(quote.data["id"], action)
        return quote.data

    def test_quote_versions_are_date_resolved_and_currency_scoped(self):
        first = self.ratify_quote("2026-05-20", price="5")
        second = self.ratify_quote("2026-08-10", price="4.5")
        self.assertEqual(SalesQuote.objects.get(pk=first["id"]).expiry_date.isoformat(), "2026-08-09")
        self.assertIsNone(SalesQuote.objects.get(pk=second["id"]).expiry_date)
        old = self.client.get("/api/sales-quote/previous/", {
            "customer": self.customer.id, "material": self.material.id,
            "customer_material": self.customer_material.id, "date": "2026-06-17",
        })
        self.assertEqual(old.status_code, 200, old.data)
        self.assertEqual(str(old.data["unit_price"]), "5.00000000")
        current = self.client.get("/api/sales-quote/previous/", {
            "customer": self.customer.id, "material": self.material.id,
            "customer_material": self.customer_material.id, "date": "2026-08-10",
        })
        self.assertEqual(str(current.data["unit_price"]), "4.50000000")
        usd = Currency.objects.create(code="USD-V", name="美元")
        foreign = self.ratify_quote("2026-07-01", currency=usd, price="6")
        self.assertIsNone(SalesQuote.objects.get(pk=foreign["id"]).expiry_date)
        self.assertIsNone(SalesQuote.objects.get(pk=second["id"]).expiry_date)

    def test_draft_version_does_not_close_previous_until_ratified(self):
        first = self.ratify_quote("2026-05-20", price="5")
        draft = self.create_quote("2026-08-10")
        self.assertIsNone(SalesQuote.objects.get(pk=first["id"]).expiry_date)
        self.action(draft["id"], "confirm")
        self.action(draft["id"], "approve")
        self.action(draft["id"], "ratify")
        self.assertEqual(SalesQuote.objects.get(pk=first["id"]).expiry_date.isoformat(), "2026-08-09")

    def test_each_new_ratified_version_closes_only_prior_versions(self):
        first = self.ratify_quote("2026-01-01", price="5")
        second = self.ratify_quote("2026-02-01", price="4.5")
        third = self.ratify_quote("2026-03-01", price="6")
        self.assertEqual(SalesQuote.objects.get(pk=first["id"]).expiry_date.isoformat(), "2026-01-31")
        self.assertEqual(SalesQuote.objects.get(pk=second["id"]).expiry_date.isoformat(), "2026-02-28")
        self.assertIsNone(SalesQuote.objects.get(pk=third["id"]).expiry_date)
    def test_ratified_quote_cannot_be_deleted(self):
        quote = self.ratify_quote("2026-05-20")
        response = self.client.delete(f"/api/sales-quote/{quote['id']}/")
        self.assertEqual(response.status_code, 400, response.data)
