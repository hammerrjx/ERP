"""Remove only records identifiable from the supplied legacy Excel exports."""
from pathlib import Path
import xlrd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from backend.models import (Currency, CustomerMaterial, DeliveryOrder, Department, Location, Material,
    Partner, PaymentMethod, ProductCategory, SalesQuote, SupplierQuote, Uom, UomCategory)

FILES = {
    'department': '1.4 -- 部门(AMDPMTA1).xls', 'payment': '1.9 -- 支付方式(AMCTMTA1).xls',
    'currency': '2.1 -- 货币(AMCUMTA1).xls', 'location': '2.2 -- 库位(AMLOMTA1).xls',
    'category': '2.3 -- 产品类(AMPLMTA1).xls', 'uom': '2.4 -- 计量单位(AMUNMTA1).xls',
    'material': '2.5 -- 物料信息(AMPTMTA1).xls', 'customer': '3.1 -- 客户资料(SLCMMTA1).xls',
    'customer_material': '3.3 -- 客户物料(SLCPMTA1).xls', 'sales_quote': '3.5 -- 销售报价(SLPRMTA1).xls',
    'delivery': '3.14 -- 送货单(SLDNMTA1).xls', 'supplier': '6.1 -- 供应商资料(PUVDMTA1).xls',
    'supplier_quote': '6.5 -- 供应商报价(PUVQMTA1).xls',
}

def text(v): return str(v or '').strip()
def rows(path):
    book=xlrd.open_workbook(path, on_demand=True); sheet=book.sheet_by_index(0)
    heads=[text(sheet.cell_value(0,c)) for c in range(sheet.ncols)]
    result=[dict(zip(heads,[sheet.cell_value(r,c) for c in range(sheet.ncols)])) for r in range(1,sheet.nrows)]
    book.release_resources(); return result

class Command(BaseCommand):
    help='清理指定 Excel 导入数据；默认只读预览'
    def add_arguments(self, parser):
        parser.add_argument('--source-dir', required=True, type=Path); parser.add_argument('--commit', action='store_true')
    def handle(self,*args,**opts):
        paths={k:opts['source_dir']/v for k,v in FILES.items()}
        missing=[str(p) for p in paths.values() if not p.exists()]
        if missing: raise CommandError('缺少 Excel 文件: '+', '.join(missing))
        data={k:rows(p) for k,p in paths.items()}
        targets={
            SalesQuote: {text(r.get('报价单号')) for r in data['sales_quote'] if text(r.get('报价单号')).startswith('BL')},
            SupplierQuote: {text(r.get('报价单号')) for r in data['supplier_quote'] if text(r.get('报价单号')).startswith('BL')},
            DeliveryOrder: {text(r.get('送货单号')) for r in data['delivery'] if text(r.get('送货单号')).startswith('BL')},
        }
        self.stdout.write('删除预览：' + '; '.join(f'{m.__name__} {len(v)} 条' for m,v in targets.items()))
        if not opts['commit']:
            self.stdout.write('只读预览未删除；确认后使用 --commit'); return
        deleted={}; skipped={}
        with transaction.atomic():
            for model, numbers in targets.items():
                qs=model.objects.filter(number__in=numbers)
                deleted[model.__name__]=0; skipped[model.__name__]=0
                for obj in list(qs):
                    try: obj.delete(); deleted[model.__name__]+=1
                    except Exception: skipped[model.__name__]+=1
            # Remove exact customer-material rows from the workbook only when they are not tagged as source imports.
            material_codes = {text(r.get('物料编码')) for r in data['customer_material']}
            customer_codes = {text(r.get('客户代码')) for r in data['customer_material']}
            customer_part_codes = {text(r.get('客户物料编码')) for r in data['customer_material']}
            for obj in list(CustomerMaterial.objects.filter(customer__code__in=customer_codes, material__code__in=material_codes, customer_code__in=customer_part_codes)):
                if obj.created_by == 'dgyzx1-import':
                    skipped['CustomerMaterial'] = skipped.get('CustomerMaterial', 0) + 1
                    continue
                try: obj.delete(); deleted['CustomerMaterial'] = deleted.get('CustomerMaterial', 0) + 1
                except Exception: skipped['CustomerMaterial'] = skipped.get('CustomerMaterial', 0) + 1
            # Master rows are removed only when no surviving business object protects them.
            code_sets={
                Currency:{text(r.get('货币')) for r in data['currency']}, Location:{text(r.get('库位')) for r in data['location']},
                ProductCategory:{text(r.get('产品类')) for r in data['category']}, Uom:{text(r.get('单位')) for r in data['uom']},
                Material:{text(r.get('物料编码')) for r in data['material']}, Partner:{text(r.get('客户代码')) for r in data['customer']} | {text(r.get('供应商代码')) for r in data['supplier']},
            }
            for model,codes in code_sets.items():
                count=0; blocked=0
                for obj in list(model.objects.filter(code__in={c for c in codes if c})):
                    if getattr(obj, 'created_by', '') == 'dgyzx1-import':
                        skipped[model.__name__]=skipped.get(model.__name__,0)+1
                        continue
                    try: obj.delete(); count+=1
                    except Exception: blocked+=1
                deleted[model.__name__]=deleted.get(model.__name__,0)+count; skipped[model.__name__]=skipped.get(model.__name__,0)+blocked
            for model, codes, field in ((Department, {text(r.get('部门代码')) for r in data.get('department', [])}, 'code'), (PaymentMethod, {text(r.get('支付方式')) for r in data.get('payment', [])}, 'code')):
                for obj in list(model.objects.filter(**{f'{field}__in': {c for c in codes if c}})):
                    try: obj.delete(); deleted[model.__name__] = deleted.get(model.__name__, 0) + 1
                    except Exception: skipped[model.__name__] = skipped.get(model.__name__, 0) + 1
        self.stdout.write(self.style.SUCCESS(f'已删除: {deleted}；因历史关系保留: {skipped}'))
