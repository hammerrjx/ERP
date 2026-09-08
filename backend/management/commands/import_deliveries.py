"""Import linked delivery history from read-only dgyzx1 source."""
from collections import defaultdict
from datetime import datetime
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import (
    ApprovalStatus, Currency, CustomerAddress, CustomerMaterial, DeliveryOrder,
    DeliveryOrderLine, Location, Material, Partner, ProductCategory, SalesOrder,
    SalesOrderLine, Uom, UomCategory,
)

def clean(value):
    return str(value or "").strip()

def key(value):
    return clean(value).upper()

def date_value(value):
    if isinstance(value, datetime):
        return value.date()
    return value

def datetime_value(value):
    if value is None:
        return None
    return timezone.make_aware(value) if timezone.is_naive(value) else value

class Command(BaseCommand):
    help = "导入 dgyzx1 关联送货单；默认只读预检，--commit 才写入本地"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--bootstrap-dependencies", action="store_true")
        parser.add_argument("--source-file")

    def read_source(self, limit, source_file=None):
        if source_file:
            return json.loads(open(source_file, encoding="utf-8").read())
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
        load_dotenv(ENV_FILE)
        try:
            connection = pyodbc.connect(connection_string(), readonly=True)
        except Exception as exc:
            raise CommandError(f"无法连接 dgyzx1 源库（源库只读预检未执行）：{exc}") from exc
        with connection:
            cursor = connection.cursor()
            def rows(sql, params=()):
                result = cursor.execute(sql, params)
                columns = [item[0] for item in result.description]
                return [dict(zip(columns, row)) for row in result.fetchall()]
            headers = rows(f"""SELECT TOP {limit} * FROM dbo.dn_mstr
                WHERE EXISTS (SELECT 1 FROM dbo.dnd_det d WHERE d.dnd_dn=dn_mstr.dn_dn)
                ORDER BY dn_date,dn_dn""")
            dn_numbers = [clean(r["dn_dn"]) for r in headers]
            ph = ",".join("?" for _ in dn_numbers) or "?"
            lines = rows(f"SELECT * FROM dbo.dnd_det WHERE dnd_dn IN ({ph}) ORDER BY dnd_dn,dnd_line", dn_numbers or [""])
            prints = rows(f"SELECT print_key1,print_by,print_date FROM dbo.print_hist WHERE print_prog='SLDNMTA1' AND print_key1 IN ({ph}) ORDER BY print_date DESC", dn_numbers or [""])
            so_numbers = sorted({clean(r.get("dnd_so")) for r in lines if clean(r.get("dnd_so"))})
            ph = ",".join("?" for _ in so_numbers) or "?"
            orders = rows(f"SELECT * FROM dbo.so_mstr WHERE so_nbr IN ({ph})", so_numbers or [""])
            order_lines = rows(f"SELECT * FROM dbo.sod_det WHERE sod_nbr IN ({ph})", so_numbers or [""])
            customers = sorted({clean(r.get("dn_cust")) for r in headers if clean(r.get("dn_cust"))} | {clean(r.get("so_cust")) for r in orders if clean(r.get("so_cust"))})
            ph = ",".join("?" for _ in customers) or "?"
            customer_rows = rows(f"SELECT * FROM dbo.cm_mstr WHERE cm_addr IN ({ph})", customers or [""])
            addresses = rows(f"SELECT * FROM dbo.ca_mstr WHERE ca_cust IN ({ph})", customers or [""])
            materials_codes = sorted({clean(r.get("dnd_part")) for r in lines if clean(r.get("dnd_part"))} | {clean(r.get("sod_part")) for r in order_lines if clean(r.get("sod_part"))})
            ph = ",".join("?" for _ in materials_codes) or "?"
            materials = rows(f"SELECT * FROM dbo.pt_mstr WHERE pt_part IN ({ph})", materials_codes or [""])
            customer_materials = []
            for cust in customers:
                customer_materials.extend(rows(f"SELECT * FROM dbo.cp_mstr WHERE cp_cust=? AND cp_part IN ({ph})", [cust, *(materials_codes or [""])]))
            locations_codes = sorted({clean(r.get("dn_loc")) for r in headers if clean(r.get("dn_loc"))} | {clean(r.get("dnd_loc")) for r in lines if clean(r.get("dnd_loc"))} | {clean(r.get("pt_loc")) for r in materials if clean(r.get("pt_loc"))})
            ph = ",".join("?" for _ in locations_codes) or "?"
            locations = rows(f"SELECT * FROM dbo.loc_mstr WHERE loc_loc IN ({ph})", locations_codes or [""])
            uom_codes = sorted({clean(r.get("dnd_um")) for r in lines} | {clean(r.get("sod_um")) for r in order_lines} | {clean(r.get("pt_um")) for r in materials} | {clean(r.get("cp_um")) for r in customer_materials})
            ph = ",".join("?" for _ in uom_codes) or "?"
            units = rows(f"SELECT * FROM dbo.um_mstr WHERE um_um IN ({ph})", uom_codes or [""])
        return {"headers": headers, "lines": lines, "orders": orders, "order_lines": order_lines,
                "customers": customer_rows, "addresses": addresses, "materials": materials, "prints": prints,
                "customer_materials": customer_materials, "locations": locations, "units": units}

    def bootstrap(self, source):
        currencies = {key(x.code): x for x in Currency.objects.all()}
        for row in source["customers"]:
            code = clean(row.get("cm_addr")); curr = key(row.get("cm_curr")) or "RMB"
            currency = currencies.get(curr) or Currency.objects.create(code=curr, name=curr, status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
            currencies[curr] = currency
            Partner.objects.update_or_create(code=code, defaults={"name": clean(row.get("cm_name")) or code, "short_name": clean(row.get("cm_sort")) or code, "kind": "customer", "currency": currency, "address": clean(row.get("cm_txt_run")), "delivery_address": clean(row.get("cm_txt_ship")), "invoice_address": clean(row.get("cm_txt_inv")), "tax_rate": row.get("cm_vat") or 0, "discount_rate": row.get("cm_disc") or 100, "quote_tax_included": clean(row.get("cm_price_vat")) != "0", "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"})
        category = ProductCategory.objects.first()
        unit_category = UomCategory.objects.filter(code="COUNT").first() or UomCategory.objects.create(code="COUNT", name="数量", status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
        units = {key(x.code): x for x in Uom.objects.all()}
        for index, row in enumerate(source["units"], 1):
            code = clean(row.get("um_um"))
            if code and key(code) not in units:
                name = clean(row.get("um_desc"))
                if not name or Uom.objects.filter(name=name).exists() or any(ch.isascii() and ch.isalpha() for ch in name):
                    name = f"计量单位{index}"
                units[key(code)] = Uom.objects.create(code=code, name=name[:32], description=clean(row.get("um_desc"))[:160], category=unit_category, status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
        locations = {key(x.code): x for x in Location.objects.all()}
        for row in source["locations"]:
            code = clean(row.get("loc_loc"))
            if code and key(code) not in locations:
                locations[key(code)] = Location.objects.create(code=code, source_site=clean(row.get("loc_site")), name=clean(row.get("loc_desc")) or code, usable=bool(row.get("loc_avail")), participate_mrp=bool(row.get("loc_nettable")), disabled_for_inventory=bool(row.get("loc_disabled")), status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
        if not category:
            category = ProductCategory.objects.create(code="LEGACY", name="历史物料", default_uom=next(iter(units.values()), None), default_location=next(iter(locations.values()), None), status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
        materials = {key(x.code): x for x in Material.objects.all()}
        for row in source["materials"]:
            code = clean(row.get("pt_part")); uom = units.get(key(row.get("pt_um"))) or category.default_uom; loc = locations.get(key(row.get("pt_loc"))) or category.default_location
            if code and code not in materials and uom and loc:
                materials[key(code)] = Material.objects.create(code=code, name=clean(row.get("pt_desc1")) or code, specification=clean(row.get("pt_spec")), category=category, uom=uom, default_location=loc, active=bool(row.get("pt_status")), batch_control=bool(row.get("pt_lot_serial")), tax_code="", status=ApprovalStatus.APPROVED, created_by="dgyzx1-import")
        partners = {key(x.code): x for x in Partner.objects.filter(kind__in=("customer", "both"))}
        for row in source["customer_materials"]:
            customer, material, code = partners.get(key(row.get("cp_cust"))), materials.get(key(row.get("cp_part"))), clean(row.get("cp_cust_part"))
            if customer and material and code:
                CustomerMaterial.objects.update_or_create(customer=customer, material=material, customer_code=code, defaults={"customer_name": clean(row.get("cp_cust_desc")), "customer_uom": units.get(key(row.get("cp_um"))), "customer_uom_rate_m": row.get("cp_um_rate_m") or 1, "customer_uom_rate_d": row.get("cp_um_rate_d") or 1, "terminal_customer_code": clean(row.get("cp_char1")), "terminal_customer_name": clean(row.get("cp_char2")), "notes": clean(row.get("cp_cmmt")), "enabled": True, "created_by": "dgyzx1-import"})
        for row in source["addresses"]:
            customer = partners.get(key(row.get("ca_cust"))); code = clean(row.get("ca_addr"))
            if customer and code:
                CustomerAddress.objects.update_or_create(customer=customer, code=code, defaults={"address": clean(row.get("ca_txt")), "notes": clean(row.get("ca_rmks")), "enabled": True, "source_object": "ca_mstr", "source_key": f"{customer.code}|{code}", "created_by": clean(row.get("ca_crt_by")) or "dgyzx1-import"})

    def import_rows(self, source):
        customers = {key(x.code): x for x in Partner.objects.filter(kind__in=("customer", "both"))}
        currencies = {key(x.code): x for x in Currency.objects.all()}
        materials = {key(x.code): x for x in Material.objects.all()}
        units = {key(x.code): x for x in Uom.objects.all()}
        locations = {key(x.code): x for x in Location.objects.all()}
        order_map, order_line_map = {}, {}
        for row in source["orders"]:
            customer = customers.get(key(row.get("so_cust"))); currency = currencies.get(key(row.get("so_curr")))
            if not customer or not currency: raise CommandError(f"销售订单依赖缺失: {row.get('so_nbr')}")
            order, _ = SalesOrder.objects.update_or_create(number=clean(row.get("so_nbr")), defaults={"customer": customer, "currency": currency, "tax_included": True, "tax_rate": row.get("so_vat") or 0, "order_date": date_value(row.get("so_ord_date")) or timezone.localdate(), "customer_po": clean(row.get("so_po")) or clean(row.get("so_nbr")), "srm_number": clean(row.get("so_nbr")), "delivery_address": clean(row.get("so_addr")) or customer.delivery_address or customer.address, "delivery_mode": SalesOrder.DeliveryMode.DIRECT, "promised_date": date_value(row.get("so_ord_date")) or timezone.localdate(), "notes": clean(row.get("so_rmks")), "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"})
            order_map[key(row.get("so_nbr"))] = order
        for row in source["order_lines"]:
            order, material, uom = order_map.get(key(row.get("sod_nbr"))), materials.get(key(row.get("sod_part"))), units.get(key(row.get("sod_um")))
            if not order or not material or not uom: raise CommandError(f"销售订单行依赖缺失: {row.get('sod_nbr')}/{row.get('sod_line')}")
            cm = CustomerMaterial.objects.filter(customer=order.customer, material=material, customer_code=clean(row.get("sod_cust_part"))).first()
            line, _ = SalesOrderLine.objects.update_or_create(order=order, line_number=int(row.get("sod_line") or 0), defaults={"material": material, "customer_material": cm, "uom": uom, "quantity": row.get("sod_qty_ord") or 0, "spare_quantity": row.get("sod_qty_spare") or 0, "unit_price": row.get("sod_price") or 0, "promised_date": date_value(row.get("sod_promise_date")) or order.promised_date, "delivered_quantity": row.get("sod_qty_shp") or 0, "delivered_spare_quantity": row.get("sod_qty_spare_shp") or 0, "returned_quantity": row.get("sod_qty_rtn") or 0, "returned_spare_quantity": row.get("sod_qty_spare_rtn") or 0})
            order_line_map[(key(row.get("sod_nbr")), int(row.get("sod_line") or 0))] = line
        lines_by_dn = defaultdict(list)
        for row in source["lines"]: lines_by_dn[key(row.get("dnd_dn"))].append(row)
        imported = 0
        prints = {}
        for row in source.get("prints", []):
            prints.setdefault(key(row.get("print_key1")), clean(row.get("print_by")))
        for header in source["headers"]:
            dn = clean(header.get("dn_dn")); customer = customers.get(key(header.get("dn_cust")))
            if not customer: raise CommandError(f"送货客户依赖缺失: {dn}")
            first = lines_by_dn[key(dn)][0]; order_line = order_line_map.get((key(first.get("dnd_so")), int(first.get("dnd_so_line") or 0)))
            if not order_line: raise CommandError(f"送货来源订单行缺失: {dn}")
            address_code = clean(header.get("dn_txt"))
            address = CustomerAddress.objects.filter(customer=customer, code=address_code, enabled=True).first()
            modes = {"1": SalesOrder.DeliveryMode.DIRECT, "2": SalesOrder.DeliveryMode.SUPPLIER}
            types = {"正常送货": "normal", "正常退货": "return", "红冲单据": "red_flush"}
            if clean(header.get("dn_char1")) not in modes or clean(header.get("dn_char4")) not in types:
                raise CommandError(f"{dn}: 源库送货模式或业务模式不在已确认字典中")
            source_orders = {order_line_map[(key(r["dnd_so"]), int(r["dnd_so_line"]))].order_id for r in lines_by_dn[key(dn)]}
            line_locations = [locations.get(key(row.get("dnd_loc")) or key(header.get("dn_loc"))) for row in lines_by_dn[key(dn)]]
            head_location = line_locations[0] if line_locations and all(item and item.id == line_locations[0].id for item in line_locations) else None
            delivery, _ = DeliveryOrder.objects.update_or_create(number=dn, defaults={"customer": customer, "sales_order": order_line.order if len(source_orders) == 1 else None, "delivery_date": date_value(header.get("dn_date")) or timezone.localdate(), "delivery_address": clean(header.get("dn_char3")), "address_code": address_code, "address_snapshot": address.address if address else "", "source_location": head_location, "default_print_person": clean(header.get("dn_char6")), "document_type": types[clean(header.get("dn_char4"))], "delivery_mode": modes[clean(header.get("dn_char1"))], "srm_number": clean(header.get("dn_char2")), "customer_po": order_line.order.customer_po if len(source_orders) == 1 else "", "notes": clean(header.get("dn_rmks")), "status": ApprovalStatus.APPROVED if header.get("dn_pst") else ApprovalStatus.DRAFT, "posted": bool(header.get("dn_pst")), "created_by": clean(header.get("dn_crt_by")) or "dgyzx1-import", "approved_by": clean(header.get("dn_sig_by")) if header.get("dn_sig") else "", "approved_at": datetime_value(header.get("dn_sig_date")) if header.get("dn_sig") else None, "confirmed_by": clean(header.get("dn_cfm_by")) if header.get("dn_cfm") else "", "confirmed_at": datetime_value(header.get("dn_cfm_date")) if header.get("dn_cfm") else None, "is_confirmed": bool(header.get("dn_cfm"))})
            for row in lines_by_dn[key(dn)]:
                order_line = order_line_map.get((key(row.get("dnd_so")), int(row.get("dnd_so_line") or 0))); material = materials.get(key(row.get("dnd_part"))); uom = units.get(key(row.get("dnd_um"))); location = locations.get(key(row.get("dnd_loc")) or key(header.get("dn_loc"))) or material.default_location
                if not order_line or not material or not uom or not location: raise CommandError(f"送货明细依赖缺失: {dn}/{row.get('dnd_line')}")
                cm = CustomerMaterial.objects.filter(customer=customer, material=material, customer_code=clean(next((x.get("sod_cust_part") for x in source["order_lines"] if key(x.get("sod_nbr")) == key(row.get("dnd_so")) and int(x.get("sod_line") or 0) == int(row.get("dnd_so_line") or 0)), ""))).first()
                DeliveryOrderLine.objects.update_or_create(delivery=delivery, line_number=int(row.get("dnd_line") or 0), defaults={"sales_order_line": order_line, "material": material, "customer_material": cm, "uom": uom, "actual_quantity": row.get("dnd_qty_ship") or 0, "ordered_spare_quantity": row.get("dnd_qty_spare") or 0, "actual_spare_quantity": row.get("dnd_qty_spare_ship") or 0, "source_location": location, "batch_number": clean(row.get("dnd_lot")), "notes": clean(row.get("dnd_rmks")), "created_by": clean(row.get("dnd_crt_by")), "source_snapshot": {"ordered_quantity": str(row.get("dnd_qty_ord") or 0), "delivered_quantity": str(row.get("dnd_qty_shipped") or 0), "delivered_spare_quantity": str(row.get("dnd_qty_spared") or 0)}, "srm_customer_po": order_line.order.customer_po, "srm_material_code": cm.customer_code if cm else material.code, "srm_material_name": material.name, "srm_quantity": row.get("dnd_qty_ship") or 0})
            imported += 1
        return imported

    def verify(self, source):
        numbers = [clean(row.get("dn_dn")) for row in source.get("headers", [])]
        deliveries = list(DeliveryOrder.objects.filter(number__in=numbers).prefetch_related("lines"))
        errors = []
        for delivery in deliveries:
            for line in delivery.lines.all():
                if line.sales_order_line.order.customer_id != delivery.customer_id:
                    errors.append(f"{delivery.number}/{line.line_number}: 客户与订单不一致")
                if line.material_id != line.sales_order_line.material_id or line.uom_id != line.sales_order_line.uom_id:
                    errors.append(f"{delivery.number}/{line.line_number}: 物料或单位与订单不一致")
                if line.customer_material_id and (line.customer_material.customer_id != delivery.customer_id or line.customer_material.material_id != line.material_id):
                    errors.append(f"{delivery.number}/{line.line_number}: 客户物料关联不一致")
                if line.material.batch_control and delivery.delivery_mode == SalesOrder.DeliveryMode.DIRECT and not line.batch_number:
                    errors.append(f"{delivery.number}/{line.line_number}: 批号控制物料缺少批号")
        return {"deliveries": len(deliveries), "lines": sum(d.lines.count() for d in deliveries), "errors": errors}

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 5000: raise CommandError("--limit 必须在 1 到 5000 之间")
        source = self.read_source(options["limit"], options.get("source_file"))
        sites = defaultdict(set)
        for row in source.get("locations", []):
            sites[key(row.get("loc_loc"))].add(key(row.get("loc_site")))
        if any(len(values) > 1 for values in sites.values()):
            raise CommandError("源库存在跨工厂同码库位，当前单工厂模型不可合并导入")
        if options["bootstrap_dependencies"] and not options["commit"]: raise CommandError("--bootstrap-dependencies 必须与 --commit 一起使用")
        if options["commit"]:
            with transaction.atomic():
                if options["bootstrap_dependencies"]: self.bootstrap(source)
                count = self.import_rows(source)
                result = self.verify(source)
                if result["errors"]:
                    raise CommandError("导入后关联校验失败：" + "；".join(result["errors"][:8]))
            self.stdout.write(self.style.SUCCESS(f"已导入 {count} 张送货单、{result['lines']} 行明细及其关联数据；关联校验通过，历史已过账记录未重复扣库存。"))
        else:
            self.stdout.write(f"源送货单 {len(source.get('headers', []))} 张，明细 {len(source.get('lines', []))} 行；只读预检未写入本地。")
            self.stdout.write("连接恢复后使用 --commit --bootstrap-dependencies 提交。")
