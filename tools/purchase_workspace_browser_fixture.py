"""Seed the explicitly selected isolated browser database, never the normal ERP ledger."""
import json
import os
from pathlib import Path
from unittest.mock import patch

import django
from rest_framework.test import APIClient

root=Path(__file__).resolve().parent.parent
expected=root/'outputs/purchase-replan-20260922/browser.sqlite3'
assert Path(os.environ['ERP_SQLITE_PATH']).resolve()==expected.resolve()
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS += ["testserver"]
from django.contrib.auth import get_user_model
from django.core.management import call_command
call_command("flush", interactive=False, verbosity=0)
from backend.test_purchase_workspace import PurchaseWorkspaceTests
from backend.models import Material, PurchaseRequisition, PurchaseRequisitionLine, SalesOrder, SalesOrderLine, Uom
from rest_framework.authtoken.models import Token

case=PurchaseWorkspaceTests('test_export_contains_both_tables_and_all_columns');case.client=APIClient()
with patch('backend.material_codes._source_codes',return_value=None):
    case.setUp()
    base=Material.objects.get(pk=case.ctx['material']['id'])
    names=[('RHY-000018','微乳切削液CML-UT8480','200L/桶','2','2340'),
        ('RHY-000015','润滑油*68#导轨油','170KG/桶','850','12'),
        ('RHY-000011','磨削液Hysol/EP690/18L/桶/品牌：嘉实多','18L/桶','6','720')]
    barrel=Uom.objects.create(code='BARREL',name='桶',category=base.uom.category)
    kg=Uom.objects.create(code='KG',name='千克',category=base.uom.category)
    sales=SalesOrder.objects.create(number='BLSO24050001',customer_id=case.ctx['customer']['id'],currency_id=case.ctx['currency']['id'],customer_po='测试来源',promised_date='2024-05-13')
    mats=[]
    for code,name,spec,qty,price in names:
        m=Material.objects.get(pk=base.pk);m.pk=None;m.code=code;m.name=name;m.specification=spec
        m.uom=kg if code=='RHY-000015' else barrel;m.tax_code='1070101990000000000';m.tax_name='*石油制品*'
        m.default_supplier_id=case.supplier['id'];m.min_issue_qty=0;m.min_pack_qty=0;m.min_purchase_qty=0;m.save();mats.append(m)
    req=PurchaseRequisition.objects.create(number='BLPR24050001',request_date='2024-05-09',status='approved',
        department_id=case.department['id'],requester='PO08')
    for i,((code,name,spec,qty,price),m) in enumerate(zip(names,mats),1):
        so=SalesOrderLine.objects.create(order=sales,line_number=i*10,material=m,uom=m.uom,quantity=qty,promised_date=f'2024-05-{11+i}')
        PurchaseRequisitionLine.objects.create(requisition=req,line_number=i*10,material=m,uom=m.uom,
            mrp_demand_qty=0,requested_qty=qty,needed_date=f'2024-05-{11+i}',source_kind='manual',source_sales_order_line=so,
            material_snapshot={'pt_part':code,'pt_desc1':name,'pt_spec':spec,'pt_um':m.uom.name},
            source_snapshot={'req_wo_nbr':'BLSO24050001','req_wo_lot':i*10,'req_wo_part':code,'req_wo_desc':name,'req_wo_spec':spec,'req_wo_qty':qty})
    token=Token.objects.create(user=case.user)
    (expected.parent/'browser-fixture.json').write_text(json.dumps({'token':token.key,'supplier':case.supplier['id'],
        'department':case.department['id'],'request_number':req.number}),encoding='utf8')
print('Isolated browser fixture created: three requisition rows; no purchase orders.')
