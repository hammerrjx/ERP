"""Read-only local API snapshot for reproducing quote/order lookup differences."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_backend.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import override_settings
from rest_framework.test import APIClient
from backend.models import SalesQuote, UserRole


def main():
    if connection.vendor != "sqlite":
        raise SystemExit("This local diagnostic requires SQLite query_only protection.")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA query_only = ON")
    quote = SalesQuote.objects.get(number="MYSQ26090010")
    line = quote.lines.get()
    user = get_user_model().objects.get(username=quote.created_by)
    client = APIClient()
    client.force_authenticate(user)
    snapshot = {}
    with override_settings(ALLOWED_HOSTS=["testserver"]):
        for resource, pk in (
            ("sales-quote", quote.pk), ("material", line.material_id),
            ("partner", quote.customer_id), ("customer-material", line.customer_material_id),
            ("currency", quote.currency_id), ("uom", line.uom_id),
        ):
            result = client.get(f"/api/{resource}/{pk}/")
            assert result.status_code == 200, (resource, result.status_code)
            snapshot[resource] = result.data
        for name, customer_material in (("exact", line.customer_material_id), ("without_customer_material", "")):
            result = client.get("/api/sales-quote/previous/", {
                "customer": quote.customer_id, "material": line.material_id,
                "customer_material": customer_material, "currency": quote.currency_id,
                "date": "2026-09-08",
            })
            assert result.status_code == 200, result.status_code
            snapshot[name] = result.data
    dependencies = {"partner.view", "material.view", "customer_material.view", "currency.view", "uom.view"}
    permissions = {}
    for user_id, values in UserRole.objects.filter(
        active=True, role__active=True, role__status="approved", user__is_active=True,
        user__is_superuser=False,
    ).values_list("user_id", "role__permissions"):
        permissions.setdefault(user_id, set()).update(values)
    operators = [p for p in permissions.values() if "sales_order.create" in p and "*" not in p]
    summary = {
        "quote": quote.number, "material": line.material.code,
        "quote_status": quote.status, "ratified": quote.is_ratified,
        "material_active": line.material.active, "actor_superuser": user.is_superuser,
        "exact_lookup_quote": snapshot["exact"].get("quote_number"),
        "lookup_without_customer_material": snapshot["without_customer_material"].get("quote_number"),
        "order_operators": len(operators),
        "operators_missing_lookup_permissions": sum(not dependencies.issubset(p) for p in operators),
    }
    snapshot["summary"] = summary
    path = ROOT / "tmp" / "quote-order-chain-snapshot.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
