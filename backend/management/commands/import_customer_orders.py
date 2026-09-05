"""Import the latest 20 linked customer orders from read-only dgyzx1."""
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import (ApprovalStatus, Currency, CustomerAddress, CustomerMaterial,
    Material, Partner, PaymentMethod, ProductCategory, SalesOrder, SalesOrderLine,
    SalesQuoteLine, Uom, UomCategory, Location)


def clean(value): return str(value or '').strip()
def key(value): return clean(value).upper()
def day(value): return value.date() if isinstance(value, datetime) else (value or timezone.localdate())
def aware(value): return timezone.make_aware(value) if isinstance(value, datetime) and timezone.is_naive(value) else value


class Command(BaseCommand):
    help = "导入 dgyzx1 最新20条不同客户优先的客户订单；默认只读预检"

    def add_arguments(self, parser): parser.add_argument('--commit', action='store_true')

    def read_source(self):
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
        load_dotenv(ENV_FILE)
        with pyodbc.connect(connection_string(), readonly=True, timeout=20) as cn:
            cur = cn.cursor()
            def rows(sql, params=()):
                result = cur.execute(sql, params); cols = [x[0] for x in result.description]
                return [dict(zip(cols, row)) for row in result.fetchall()]
            all_orders = rows("SELECT so_nbr,so_cust,so_addr,so_ord_date,so_po,so_cr_terms,so_slspsn,so_curr,so_vat,so_rmks,so_wf_status,so_crt_by,so_crt_date,so_mod_by,so_mod_date,so_pst,so_pst_by,so_pst_date,so_chk,so_chk_by,so_chk_date FROM dbo.so_mstr WHERE so_nbr LIKE 'MYSO%' ORDER BY so_mod_date DESC,so_nbr DESC")
            chosen=[]; customers=set()
            for row in all_orders:
                if key(row['so_cust']) not in customers:
                    chosen.append(row); customers.add(key(row['so_cust']))
                if len(chosen) == 20: break
            numbers=[clean(x['so_nbr']) for x in chosen]; ph=','.join('?' for _ in numbers) or '?'
            lines=rows(f"SELECT * FROM dbo.sod_det WHERE sod_nbr IN ({ph}) ORDER BY sod_nbr,sod_line", numbers or [''])
            cust_codes=sorted({clean(x['so_cust']) for x in chosen}); phc=','.join('?' for _ in cust_codes) or '?'
            customers=rows(f"SELECT * FROM dbo.cm_mstr WHERE cm_addr IN ({phc})", cust_codes or [''])
            addresses=rows(f"SELECT * FROM dbo.ca_mstr WHERE ca_cust IN ({phc})", cust_codes or [''])
            parts=sorted({clean(x['sod_part']) for x in lines}); php=','.join('?' for _ in parts) or '?'
            materials=rows(f"SELECT * FROM dbo.pt_mstr WHERE pt_part IN ({php})", parts or [''])
            cps=[]
            for cust in cust_codes: cps.extend(rows(f"SELECT * FROM dbo.cp_mstr WHERE cp_cust=? AND cp_part IN ({php})", [cust, *(parts or [''])]))
            currencies=rows("SELECT * FROM dbo.exr_mstr") if False else []
            return {'orders':chosen,'lines':lines,'customers':customers,'addresses':addresses,'materials':materials,'customer_materials':cps}

    def import_rows(self, source):
        customers={key(x.code):x for x in Partner.objects.filter(kind__in=('customer','both'))}
        currencies={key(x.code):x for x in Currency.objects.all()}
        materials={key(x.code):x for x in Material.objects.all()}
        units={key(x.code):x for x in Uom.objects.all()}
        for row in source['customers']:
            code=clean(row.get('cm_addr')); curr=key(row.get('cm_curr')) or 'RMB'
            currency=currencies.get(curr) or Currency.objects.create(code=curr,name=curr,status=ApprovalStatus.APPROVED,created_by='dgyzx1-import')
            currencies[curr]=currency
            customers[code]=Partner.objects.update_or_create(code=code,defaults={'name':clean(row.get('cm_name')) or code,'short_name':clean(row.get('cm_sort')) or code,'kind':'customer','currency':currency,'tax_rate':row.get('cm_vat') or 0,'discount_rate':row.get('cm_disc') or 100,'payment_terms':clean(row.get('cm_cr_terms')),'address':clean(row.get('cm_txt_run')),'delivery_address':clean(row.get('cm_txt_ship')),'invoice_address':clean(row.get('cm_txt_inv')),'quote_tax_included':clean(row.get('cm_price_vat')) != '0','status':ApprovalStatus.APPROVED,'created_by':'dgyzx1-import'})[0]
        for row in source['materials']:
            code=clean(row.get('pt_part')); material=materials.get(key(code))
            if not material:
                uom_code=clean(row.get('pt_um')) or 'EA'; uom=units.get(key(uom_code))
                if not uom:
                    cat=UomCategory.objects.filter(code='COUNT').first() or UomCategory.objects.create(code='COUNT',name='数量',status=ApprovalStatus.APPROVED,created_by='dgyzx1-import')
                    uom=Uom.objects.create(code=uom_code,name=clean(row.get('pt_um_desc')) or uom_code,description=clean(row.get('pt_um_desc')) or uom_code,category=cat,status=ApprovalStatus.APPROVED,created_by='dgyzx1-import'); units[key(uom_code)]=uom
                loc_code=clean(row.get('pt_loc')) or 'FG01'; loc=Location.objects.filter(code=loc_code).first()
                if not loc: loc=Location.objects.create(code=loc_code,name=clean(row.get('pt_loc_desc')) or loc_code,status=ApprovalStatus.APPROVED,created_by='dgyzx1-import')
                category=ProductCategory.objects.first() or ProductCategory.objects.create(code='LEGACY',name='历史物料',default_uom=uom,default_location=loc,status=ApprovalStatus.APPROVED,created_by='dgyzx1-import')
                material=Material.objects.create(code=code,name=clean(row.get('pt_desc1')) or code,specification=clean(row.get('pt_spec')),category=category,uom=uom,default_location=loc,tax_code='',active=True,status=ApprovalStatus.APPROVED,created_by='dgyzx1-import')
                materials[key(code)]=material
            materials[key(code)]=material
        for row in source['customer_materials']:
            customer=customers.get(key(row.get('cp_cust'))); material=materials.get(key(row.get('cp_part'))); code=clean(row.get('cp_cust_part'))
            if customer and material and code:
                CustomerMaterial.objects.update_or_create(customer=customer,material=material,customer_code=code,defaults={'customer_name':clean(row.get('cp_cust_desc')),'customer_uom':units.get(key(row.get('cp_um'))),'customer_uom_rate_m':row.get('cp_um_rate_m') or 1,'customer_uom_rate_d':row.get('cp_um_rate_d') or 1,'enabled':True,'created_by':'dgyzx1-import'})
        by_order={}; lines_by={}
        for row in source['lines']: lines_by.setdefault(key(row['sod_nbr']),[]).append(row)
        for header in source['orders']:
            customer=customers.get(key(header['so_cust'])); currency=currencies.get(key(header['so_curr']))
            if not customer or not currency: raise CommandError(f'订单客户/币种依赖缺失: {header["so_nbr"]}')
            address=next((x for x in source['addresses'] if key(x.get('ca_cust'))==key(header['so_cust']) and clean(x.get('ca_txt'))==clean(header.get('so_addr'))),None)
            address_obj=CustomerAddress.objects.filter(customer=customer,code=clean(address.get('ca_addr'))).first() if address else CustomerAddress.objects.filter(customer=customer,address=clean(header.get('so_addr'))).first()
            order,_=SalesOrder.objects.update_or_create(number=clean(header['so_nbr']),defaults={'customer':customer,'currency':currency,'tax_included':True,'tax_rate':header.get('so_vat') or 0,'order_date':day(header.get('so_ord_date')),'customer_po':clean(header.get('so_po')) or clean(header['so_nbr']),'srm_number':clean(header['so_nbr']),'address_code':address_obj,'address_snapshot':clean(header.get('so_addr')),'delivery_address':clean(header.get('so_addr')) or customer.delivery_address or customer.address,'delivery_mode':SalesOrder.DeliveryMode.DIRECT,'promised_date':day(header.get('so_ord_date')),'notes':clean(header.get('so_rmks')),'status':ApprovalStatus.APPROVED,'created_by':'dgyzx1-import','is_confirmed':bool(header.get('so_pst') or header.get('so_chk')),'confirmed_by':clean(header.get('so_pst_by') or header.get('so_chk_by')),'confirmed_at':aware(header.get('so_pst_date') or header.get('so_chk_date')),'approved_by':clean(header.get('so_chk_by')) if header.get('so_chk') else '','approved_at':aware(header.get('so_chk_date')) if header.get('so_chk') else None})
            by_order[key(header['so_nbr'])]=order
            for row in lines_by.get(key(header['so_nbr']),[]):
                material=materials.get(key(row.get('sod_part'))); uom=units.get(key(row.get('sod_um'))) or (material.uom if material else None)
                if not material or not uom: raise CommandError(f'订单行依赖缺失: {header["so_nbr"]}/{row.get("sod_line")}')
                cm=CustomerMaterial.objects.filter(customer=customer,material=material,customer_code=clean(row.get('sod_cust_part'))).first()
                quote_line=SalesQuoteLine.objects.filter(quote__customer=customer,quote__currency=currency,material=material,customer_material_code=clean(row.get('sod_cust_part')),quote__is_ratified=True).order_by('-quote__effective_date').first()
                SalesOrderLine.objects.update_or_create(order=order,line_number=int(row.get('sod_line') or 0),defaults={'material':material,'customer_material':cm,'uom':uom,'quantity':row.get('sod_qty_ord') or 1,'spare_quantity':row.get('sod_qty_spare') or 0,'unit_price':row.get('sod_price') or row.get('sod_list_price') or 0,'promised_date':day(row.get('sod_promise_date') or row.get('sod_due_date') or header.get('so_ord_date')),'delivered_quantity':row.get('sod_qty_shp') or 0,'delivered_spare_quantity':row.get('sod_qty_spare_shp') or 0,'source_quote_line':quote_line})
        return len(by_order), sum(len(v) for v in lines_by.values())

    def handle(self,*args,**opts):
        source=self.read_source(); self.stdout.write(f"源库候选订单 {len(source['orders'])} 条、明细 {len(source['lines'])} 行、客户 {len(source['customers'])} 个")
        if not opts['commit']: self.stdout.write('只读预检未写入；使用 --commit 提交'); return
        with transaction.atomic(): count,lines=self.import_rows(source)
        self.stdout.write(self.style.SUCCESS(f'已导入 {count} 条客户订单、{lines} 条订单明细'))
