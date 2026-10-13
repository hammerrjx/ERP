"""Run the real API against a disposable database for sales-chain browser QA."""
import os
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_backend.settings")
import django
from django.conf import settings

(ROOT / "tmp").mkdir(exist_ok=True)
settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
    "NAME": ROOT / "tmp" / f"line-chain-{uuid.uuid4().hex}.sqlite3",
    "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20}}}
settings.ALLOWED_HOSTS.append("testserver")
settings.ERP_DELIVERY_POST_STOCK = False
django.setup()
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from backend.test_support import CoreFlowSupport

call_command("migrate", interactive=False, verbosity=0)


class Seed(CoreFlowSupport, unittest.TestCase):
    pass


with patch("backend.material_codes._source_codes", return_value=None):
    seed = Seed()
    seed.client = APIClient()
    seed.setUp()
    seed.base_context()
    seed.post("product-category", {"code": "BCHAIN", "name": "Browser chain", "code_prefix": "BCHAIN"})
    seed.post("tax-code", {"code": "1001", "name": "Browser tax", "invoice_name": "Test goods"})
    Token.objects.create(user=seed.user, key="line-chain-isolated-test-token")
    print(f"Isolated database: {settings.DATABASES['default']['NAME']}", flush=True)
    call_command("runserver", "127.0.0.1:8014", use_reloader=False)
