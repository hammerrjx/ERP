import os,sys,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(root),str(root/'backend')]
expected=root/'outputs/purchase-receipt-return-import/browser.sqlite3'
assert Path(os.environ['ERP_SQLITE_PATH']).resolve()==expected.resolve()
os.environ.setdefault('DJANGO_SETTINGS_MODULE','erp_backend.settings')
import django
django.setup()
from django.core.management import call_command
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']
call_command('migrate',verbosity=0);call_command('flush',interactive=False,verbosity=0)
from backend.test_receiving import ReceivingTests
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch
case=ReceivingTests('test_inspection_and_source_system_fields');case.client=APIClient()
with patch('backend.material_codes._source_codes',return_value=None):case.setUp()
token=Token.objects.create(user=case.user)
(root/'outputs/purchase-receipt-return-import/browser-fixture.json').write_text(json.dumps({'token':token.key,'supplier':case.supplier,'order':case.order.pk}),encoding='utf-8')
print('Isolated fixture ready')
