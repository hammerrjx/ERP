"""Diagnostic probes, run explicitly with manage.py test in an isolated test DB.

Assertions describe required boundaries and intentionally fail until fixed.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from backend.models import Department, Role, SalesOrder, SalesQuote, UserRole
from backend import test_sales_quote
from backend.test_support import SourceDatabaseIsolatedMixin


class QuoteOrderBoundaryProbes(SourceDatabaseIsolatedMixin, APITestCase):
    setUp = test_sales_quote.SalesQuoteApiTests.setUp
    payload = test_sales_quote.SalesQuoteApiTests.payload
    create_quote = test_sales_quote.SalesQuoteApiTests.create_quote
    action = test_sales_quote.SalesQuoteApiTests.action

    def ratified_quote(self):
        quote = self.create_quote(str(timezone.localdate() - timedelta(days=10)))
        for action in ("confirm", "approve", "ratify"):
            self.action(quote["id"], action)
        return quote

    def conversion(self, quote):
        return self.client.post(f"/api/sales-quote/{quote['id']}/convert/", {
            "customer_po": "ISOLATED-PROBE", "delivery_address": "Test warehouse",
            "promised_date": str(timezone.localdate() + timedelta(days=10)),
        }, format="json")

    def test_expired_quote_conversion_must_be_rejected(self):
        quote = self.ratified_quote()
        SalesQuote.objects.filter(pk=quote["id"]).update(expiry_date=timezone.localdate() - timedelta(days=1))
        response = self.conversion(quote)
        self.assertEqual(response.status_code, 400, "Expired quote conversion created an order")

    def test_conversion_requires_target_order_create_permission(self):
        quote = self.ratified_quote()
        user = get_user_model().objects.create_user("quote-only-probe")
        department = Department.objects.create(code="PROBE", name="Probe")
        role = Role.objects.create(code="PROBE", name="Probe", department=department,
                                   status="approved", permissions=["sales_quote.view", "sales_quote.create"])
        UserRole.objects.create(user=user, role=role, department=department)
        self.client.force_authenticate(user)
        direct = self.client.post("/api/sales-order/", {}, format="json")
        self.assertEqual(direct.status_code, 403)
        response = self.conversion(quote)
        self.assertEqual(response.status_code, 403, "Quote permission bypasses sales_order.create")

    def test_header_customer_change_must_revalidate_existing_lines(self):
        quote = self.ratified_quote()
        order = self.conversion(quote)
        self.assertEqual(order.status_code, 201, order.data)
        response = self.client.patch(f"/api/sales-order/{order.data['id']}/", {
            "customer": self.other_customer.pk,
        }, format="json")
        changed = SalesOrder.objects.get(pk=order.data["id"])
        self.assertEqual(response.status_code, 400,
                         f"Header customer={changed.customer_id}, quote customer={self.customer.pk}")
