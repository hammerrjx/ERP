"""Real API on a fresh disposable SQLite ledger for MRP browser checks."""
import os
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_backend.settings')
import django
from django.conf import settings

folder = ROOT / 'outputs/trade-mrp-review-20261006'
folder.mkdir(parents=True, exist_ok=True)
settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
    'NAME': folder / f'browser-{uuid.uuid4().hex}.sqlite3',
    'OPTIONS': {'transaction_mode': 'IMMEDIATE', 'timeout': 20}}}
settings.ALLOWED_HOSTS.append('testserver')
settings.ERP_DELIVERY_POST_STOCK = False
settings.ERP_TRADE_MRP_GENERATION_ENABLED = True
django.setup()
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from backend.test_trade_mrp import TradeMrpTests
from backend.models import Material

call_command('migrate', interactive=False, verbosity=0)
case = TradeMrpTests('test_shared_stock_global_demand_and_source_filter')
case.client = APIClient()
with patch('backend.material_codes._source_codes', return_value=None):
    case.setUp()
    case.order('MRP-TEST-01', '10', due='2026-10-10')
    case.order('MRP-TEST-02', '20', due='2026-10-20')
    case.stock(5)
    Material.objects.filter(pk=case.material.pk).update(name='MRP浏览器隔离测试物料')
    blocked = Material.objects.get(pk=case.material.pk)
    blocked.pk = None
    blocked.code = 'UNIT-BLOCK'
    blocked.name = '非1:1单位阻断测试物料'
    blocked.save()
    case.material = blocked
    case.order('MRP-UNIT-01', '5', uom_rate_m=2)
    Token.objects.create(user=case.user, key='trade-mrp-isolated-test-token')
    print(f'Isolated MRP database: {settings.DATABASES["default"]["NAME"]}', flush=True)
    call_command('runserver', '127.0.0.1:8026', use_reloader=False)
