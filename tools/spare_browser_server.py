"""Disposable local database for browser acceptance, never the business database."""
import os
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_backend.settings")
import django
from django.conf import settings

(ROOT / "tmp").mkdir(exist_ok=True)
settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
    "NAME": ROOT / "tmp" / f"spare-browser-{uuid.uuid4().hex}.sqlite3",
    "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20}}}
settings.ALLOWED_HOSTS.append("testserver")
django.setup()
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from backend.test_support import CoreFlowSupport

call_command("migrate", interactive=False, verbosity=0)


class Seed(CoreFlowSupport, unittest.TestCase):
    pass


seed = Seed()
seed.client = APIClient()
with patch("backend.material_codes._source_codes", return_value=None):
    seed.setUp()
    context = seed.base_context()
    for po, formal, spare in (("QA-MIXED-950", "950", "50"), ("QA-SPARE-50", "0", "50")):
        order = seed.post("sales-order", {
            "customer": context["customer"]["id"], "currency": context["currency"]["id"],
            "customer_po": po, "delivery_address": "验收收货仓", "promised_date": "2026-09-08",
            "lines": [{"line_number": 10, "material": context["material"]["id"],
                       "uom": context["uom"]["id"], "quantity": formal, "spare_quantity": spare,
                       "unit_price": "20", "promised_date": "2026-09-08"}],
        })
        seed.approve("sales-order", order["id"])
    Token.objects.create(user=seed.user, key="spare-isolated-browser-test-token")
print("Isolated spare acceptance server ready", flush=True)
test_url = urlparse(os.getenv("ERP_TEST_API_URL", "http://127.0.0.1:8013"))
if test_url.hostname not in {"127.0.0.1", "localhost"}:
    raise SystemExit("The acceptance server must run on localhost")
call_command("runserver", f"{test_url.hostname}:{test_url.port or 8013}", use_reloader=False)
