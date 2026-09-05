"""Preflight and staged import for legacy dgyzx1 sales quotations."""

from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import (
    ApprovalStatus, Currency, CustomerMaterial, Location, Material, Partner,
    ProductCategory, SalesQuote, SalesQuoteLine, SalesQuoteTier, Uom, UomCategory,
)


def clean(value):
    return str(value or "").strip()


def key(value):
    return clean(value).upper()


def aware(value):
    if not value or not isinstance(value, datetime) or timezone.is_aware(value):
        return value
    return timezone.make_aware(value, timezone.get_current_timezone())


def expiry(value):
    return None if value and value.year >= 2069 else (value.date() if isinstance(value, datetime) else value)


def pick(row, *names, default=None):
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return default


class Command(BaseCommand):
    help = "只读预检 dgyzx1 销售报价；显式添加 --commit 才写入本地 ERP"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=500)
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--bootstrap-dependencies", action="store_true", help="提交前导入本批报价所引用且本地缺失的源主数据")
        parser.add_argument("--source-file", type=Path, help="使用预先导出的 JSON 数据进行离线验证")

    def read_source(self, limit, source_file=None):
        if source_file:
            source = json.loads(source_file.read_text(encoding="utf-8"))
            date_fields = ("sc_start", "sc_expire", "sc_crt_date", "sc_mod_date", "sc_pst_date", "sc_chk_date", "sc_appro_date")
            for row in source.get("headers", []):
                for name in date_fields:
                    if row.get(name):
                        row[name] = datetime.fromisoformat(row[name])
            return source

        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv

        load_dotenv(ENV_FILE)
        with pyodbc.connect(connection_string(), readonly=True) as connection:
            cursor = connection.cursor()

            def rows(sql, parameters=()):
                result = cursor.execute(sql, parameters)
                columns = [item[0] for item in result.description]
                return [dict(zip(columns, item)) for item in result.fetchall()]

            headers = rows(f"""
                SELECT TOP {limit}
                    sc_nbr, sc_cust, sc_curr, sc_part, sc_cust_part, sc_um,
                    sc_um_rate_m, sc_um_rate_d, sc_start, sc_expire, sc_vat,
                    sc_vat_rate, sc_disc, sc_price, sc_rmks, sc_crt_by,
                    sc_crt_date, sc_wf_status, sc_mod_times, sc_mod_by,
                    sc_mod_date, sc_pst, sc_pst_by, sc_pst_date, sc_ast_code,
                    sc_spare_pct, sc_qtype, sc_chk, sc_chk_by, sc_chk_date,
                    sc_appro, sc_appro_by, sc_appro_date
                FROM dbo.sc_mstr
                ORDER BY sc_mod_date DESC, sc_nbr DESC
            """)
            numbers = [row["sc_nbr"] for row in headers]
            tiers = []
            for offset in range(0, len(numbers), 200):
                batch = numbers[offset:offset + 200]
                placeholders = ",".join("?" for _ in batch)
                tiers.extend(rows(f"SELECT * FROM dbo.scd_det WHERE scd_nbr IN ({placeholders})", batch))
            customer_codes = sorted({clean(row.get("sc_cust")) for row in headers if clean(row.get("sc_cust"))})
            material_codes = sorted({clean(row.get("sc_part")) for row in headers if clean(row.get("sc_part"))})
            placeholders = ",".join("?" for _ in customer_codes) or "?"
            customers = rows(f"SELECT * FROM dbo.cm_mstr WHERE cm_addr IN ({placeholders})", customer_codes or [""])
            placeholders = ",".join("?" for _ in material_codes) or "?"
            materials = rows(f"SELECT * FROM dbo.pt_mstr WHERE pt_part IN ({placeholders})", material_codes or [""])
            customer_material_keys = []
            for customer_code in customer_codes:
                placeholders = ",".join("?" for _ in material_codes) or "?"
                customer_material_keys.extend(rows(f"SELECT * FROM dbo.cp_mstr WHERE cp_cust = ? AND cp_part IN ({placeholders})", [customer_code, *(material_codes or [""])]))
            uom_codes = sorted({clean(value) for row in headers + materials + customer_material_keys for value in (row.get("sc_um"), row.get("pt_um"), row.get("pt_um_sl"), row.get("cp_um")) if clean(value)})
            product_line_codes = sorted({clean(row.get("pt_prod_line")) for row in materials if clean(row.get("pt_prod_line"))})
            location_codes = sorted({clean(row.get("pt_loc")) for row in materials if clean(row.get("pt_loc"))})
            placeholders = ",".join("?" for _ in product_line_codes) or "?"
            prod_lines = rows(f"SELECT pl_prod_line, pl_desc, pl_um, pl_loc FROM dbo.pl_mstr WHERE pl_prod_line IN ({placeholders})", product_line_codes or [""])
            location_codes.extend(clean(row.get("pl_loc")) for row in prod_lines if clean(row.get("pl_loc")))
            placeholders = ",".join("?" for _ in sorted(set(location_codes))) or "?"
            locations = rows(f"SELECT loc_loc, loc_desc, loc_type, loc_avail, loc_nettable, loc_disabled FROM dbo.loc_mstr WHERE loc_loc IN ({placeholders})", sorted(set(location_codes)) or [""])
            placeholders = ",".join("?" for _ in uom_codes) or "?"
            source_units = rows(f"SELECT * FROM dbo.um_mstr WHERE um_um IN ({placeholders})", uom_codes or [""])
        return {"headers": headers, "tiers": tiers, "customer_material_keys": customer_material_keys,
                "customers": customers, "materials": materials, "source_units": source_units,
                "prod_lines": prod_lines, "locations": locations}

    def bootstrap_dependencies(self, source):
        """Import only master rows referenced by the selected quote batch."""
        currencies = {key(row.code): row for row in Currency.objects.all()}
        for row in source.get("customers", []):
            code = clean(row.get("cm_addr"))
            if not code:
                continue
            currency = currencies.get(key(row.get("cm_curr")))
            if not currency:
                currency = Currency.objects.create(code=key(row.get("cm_curr")) or "RMB", name=key(row.get("cm_curr")) or "人民币", status=ApprovalStatus.APPROVED, created_by="legacy-import")
                currencies[key(currency.code)] = currency
            Partner.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("cm_name")) or code, "short_name": clean(row.get("cm_sort")) or clean(row.get("cm_name")) or code,
                "kind": "customer", "currency": currency, "address": clean(row.get("cm_txt_run")),
                "invoice_address": clean(row.get("cm_txt_inv")), "delivery_address": clean(row.get("cm_txt_ship")),
                "business_owner": clean(row.get("cm_slspsn")), "payment_terms": clean(row.get("cm_cr_terms")),
                "tax_rate": row.get("cm_vat") or Decimal("0"), "discount_rate": row.get("cm_disc") or Decimal("100"),
                "backup_ratio": row.get("cm_spare_pct") or Decimal("0"), "quote_tax_included": clean(row.get("cm_price_vat")) != "0",
                "payment_bank": clean(row.get("cm_bank")), "bank_account": clean(row.get("cm_bank_acct")),
                "notes": clean(row.get("cm_cmmt")), "status": ApprovalStatus.APPROVED,
                "is_confirmed": bool(row.get("cm_pst") or row.get("cm_chk")), "created_by": clean(row.get("cm_crt_by")) or "legacy-import",
            })
        uom_categories = {key(row.code): row for row in UomCategory.objects.all()}
        uoms = {key(row.code): row for row in Uom.objects.all()}
        for row in source.get("source_units", []):
            code, name = clean(row.get("um_um")), clean(row.get("um_desc"))
            if not code or not name or key(code) in uoms:
                continue
            category = uom_categories.get("COUNT") or UomCategory.objects.create(code="COUNT", name="数量", status=ApprovalStatus.APPROVED, created_by="legacy-import")
            uoms[key(code)] = Uom.objects.create(code=code, name=name, description=name, category=category, status=ApprovalStatus.APPROVED, created_by="legacy-import")
        locations = {key(row.code): row for row in Location.objects.all()}
        for row in source.get("locations", []):
            code = clean(row.get("loc_loc"))
            if not code or key(code) in locations:
                continue
            locations[key(code)] = Location.objects.create(code=code, name=clean(row.get("loc_desc")) or code, location_type="fg" if key(row.get("loc_type")) == "FG" else "warehouse", usable=bool(row.get("loc_avail")), participate_mrp=bool(row.get("loc_nettable")), disabled_for_inventory=bool(row.get("loc_disabled")), status=ApprovalStatus.APPROVED, created_by="legacy-import")
        categories = {key(row.code): row for row in ProductCategory.objects.all()}
        for row in source.get("prod_lines", []):
            code = clean(row.get("pl_prod_line"))
            if not code or key(code) in categories:
                continue
            default_uom = uoms.get(key(row.get("pl_um"))) or next(iter(uoms.values()), None)
            default_location = locations.get(key(row.get("pl_loc"))) or next(iter(locations.values()), None)
            if not default_uom or not default_location:
                continue
            categories[key(code)] = ProductCategory.objects.create(code=code, name=clean(row.get("pl_desc")) or code, default_uom=default_uom, default_location=default_location, code_prefix=code, status=ApprovalStatus.APPROVED, created_by="legacy-import")
        for row in source.get("materials", []):
            code = clean(row.get("pt_part"))
            if not code or Material.objects.filter(code=code).exists():
                continue
            category = categories.get(key(row.get("pt_prod_line")))
            uom = uoms.get(key(row.get("pt_um"))) or (category.default_uom if category else None)
            location = locations.get(key(row.get("pt_loc"))) or (category.default_location if category else None)
            if not category or not uom or not location:
                continue
            Material.objects.create(code=code, name=clean(row.get("pt_desc1")) or code, specification=clean(row.get("pt_spec")), category=category, uom=uom, default_location=location, active=bool(row.get("pt_status")), tax_code="", status=ApprovalStatus.APPROVED, created_by=clean(row.get("pt_crt_by")) or "legacy-import")
        customer_map = {key(row.code): row for row in Partner.objects.filter(kind__in=("customer", "both"))}
        material_map = {key(row.code): row for row in Material.objects.all()}
        for row in source.get("customer_material_keys", []):
            customer = customer_map.get(key(row.get("cp_cust")))
            material = material_map.get(key(row.get("cp_part")))
            code = clean(row.get("cp_cust_part"))
            if not customer or not material or not code:
                continue
            CustomerMaterial.objects.update_or_create(customer=customer, material=material, customer_code=code, defaults={
                "customer_name": clean(row.get("cp_cust_desc")), "customer_uom": uoms.get(key(row.get("cp_um"))),
                "customer_uom_rate_m": row.get("cp_um_rate_m") or Decimal("1"), "customer_uom_rate_d": row.get("cp_um_rate_d") or Decimal("1"),
                "enabled": True, "created_by": clean(row.get("cp_crt_by")) or "legacy-import",
            })

    def analyze(self, source):
        headers = source.get("headers", [])
        local = {
            "customers": {key(row.code): row for row in Partner.objects.filter(kind__in=("customer", "both"))},
            "materials": {key(row.code): row for row in Material.objects.all()},
            "currencies": {key(row.code): row for row in Currency.objects.all()},
            "uoms": {key(row.code): row for row in Uom.objects.all()},
        }
        local_customer_materials = {
            (key(row.customer.code), key(row.material.code), key(row.customer_code)): row
            for row in CustomerMaterial.objects.select_related("customer", "material")
        }
        source_customer_materials = {
            (key(row.get("cp_cust")), key(row.get("cp_part")), key(row.get("cp_cust_part")))
            for row in source.get("customer_material_keys", [])
        }
        missing = defaultdict(set)
        historical_customer_materials = set()
        sentinel_expiry = 0
        status_combinations = Counter()
        eligible = []
        for row in headers:
            customer_code, material_code = key(row.get("sc_cust")), key(row.get("sc_part"))
            currency_code, uom_code = key(row.get("sc_curr")), key(row.get("sc_um"))
            customer_material_key = (customer_code, material_code, key(row.get("sc_cust_part")))
            current_customer_material_missing = False
            for name, code in (("customers", customer_code), ("materials", material_code), ("currencies", currency_code), ("uoms", uom_code)):
                if code not in local[name]:
                    missing[name].add(code or "<空值>")
            if customer_material_key not in local_customer_materials:
                if customer_material_key in source_customer_materials:
                    missing["customer_materials"].add(" / ".join(customer_material_key))
                    current_customer_material_missing = True
                else:
                    historical_customer_materials.add(customer_material_key)
            if row.get("sc_expire") and row["sc_expire"].year >= 2069:
                sentinel_expiry += 1
            status_combinations[(clean(row.get("sc_wf_status")), bool(row.get("sc_pst")), bool(row.get("sc_chk")), bool(row.get("sc_appro")))] += 1
            if all(code in local[name] for name, code in (("customers", customer_code), ("materials", material_code), ("currencies", currency_code), ("uoms", uom_code))) and not current_customer_material_missing:
                eligible.append(row)
        high_water = max(headers, key=lambda row: (row.get("sc_mod_date") or datetime.min, clean(row.get("sc_nbr"))), default=None)
        return {
            "headers": headers, "tiers": source.get("tiers", []), "local": local,
            "local_customer_materials": local_customer_materials, "missing": missing,
            "historical_customer_materials": historical_customer_materials,
            "sentinel_expiry": sentinel_expiry, "status_combinations": status_combinations,
            "eligible": eligible, "high_water": high_water,
        }

    def print_report(self, report, commit):
        mode = "提交" if commit else "只读预检"
        self.stdout.write(f"销售报价导入模式：{mode}")
        self.stdout.write(f"源报价：{len(report['headers'])}；源阶梯价：{len(report['tiers'])}；可导入：{len(report['eligible'])}")
        self.stdout.write(f"2069 长期有效日期规范化为空：{report['sentinel_expiry']}")
        self.stdout.write(f"源库已删除客户物料关系（允许保留快照导入）：{len(report['historical_customer_materials'])}")
        for name, label in (("customers", "客户"), ("materials", "物料"), ("currencies", "币种"), ("uoms", "单位"), ("customer_materials", "当前有效客户物料")):
            values = sorted(report["missing"][name])
            self.stdout.write(f"缺少{label}：{len(values)}" + (f"；示例：{', '.join(values[:8])}" if values else ""))
        self.stdout.write("状态组合（wf/pst/chk/appro）：" + "; ".join(f"{combo}={count}" for combo, count in report["status_combinations"].most_common()))
        if report["high_water"]:
            self.stdout.write(f"本批高水位：sc_mod_date={report['high_water'].get('sc_mod_date')}；sc_nbr={report['high_water'].get('sc_nbr')}")

    @staticmethod
    def workflow(row):
        confirmed = bool(row.get("sc_pst") or row.get("sc_chk") or row.get("sc_appro"))
        approved = bool(row.get("sc_chk") or row.get("sc_appro"))
        ratified = bool(row.get("sc_appro"))
        return {
            "status": ApprovalStatus.APPROVED if approved else ApprovalStatus.PENDING if confirmed else ApprovalStatus.DRAFT,
            "is_confirmed": confirmed,
            "confirmed_by": clean(row.get("sc_pst_by") or row.get("sc_chk_by") or row.get("sc_appro_by")),
            "confirmed_at": aware(row.get("sc_pst_date") or row.get("sc_chk_date") or row.get("sc_appro_date")),
            "approved_by": clean(row.get("sc_chk_by") or row.get("sc_appro_by")) if approved else "",
            "approved_at": aware(row.get("sc_chk_date") or row.get("sc_appro_date")) if approved else None,
            "is_ratified": ratified,
            "ratified_by": clean(row.get("sc_appro_by")) if ratified else "",
            "ratified_at": aware(row.get("sc_appro_date")) if ratified else None,
        }

    def import_rows(self, report):
        tiers_by_quote = defaultdict(list)
        for tier in report["tiers"]:
            tiers_by_quote[key(tier.get("scd_nbr"))].append(tier)
        imported = 0
        with transaction.atomic():
            for row in report["eligible"]:
                customer = report["local"]["customers"][key(row.get("sc_cust"))]
                material = report["local"]["materials"][key(row.get("sc_part"))]
                currency = report["local"]["currencies"][key(row.get("sc_curr"))]
                uom = report["local"]["uoms"][key(row.get("sc_um"))]
                relationship_key = (key(row.get("sc_cust")), key(row.get("sc_part")), key(row.get("sc_cust_part")))
                customer_material = report["local_customer_materials"].get(relationship_key)
                quote, _ = SalesQuote.objects.update_or_create(number=clean(row.get("sc_nbr")), defaults={
                    "customer": customer, "currency": currency,
                    "effective_date": row["sc_start"].date() if isinstance(row.get("sc_start"), datetime) else row.get("sc_start"),
                    "expiry_date": expiry(row.get("sc_expire")), "tax_included": bool(row.get("sc_vat")),
                    "tax_rate": row.get("sc_vat_rate") or Decimal("0"), "discount_rate": row.get("sc_disc") or Decimal("100"),
                    "backup_ratio": row.get("sc_spare_pct") or Decimal("0"),
                    "usage": clean(row.get("sc_qtype")), "notes": clean(row.get("sc_rmks")),
                    "modification_count": row.get("sc_mod_times") or 0, "created_by": clean(row.get("sc_crt_by")),
                    "updated_by": clean(row.get("sc_mod_by")), "source_object": "sc_mstr", **self.workflow(row),
                })
                SalesQuote.objects.filter(pk=quote.pk).update(created_at=aware(row.get("sc_crt_date")), updated_at=aware(row.get("sc_mod_date")))
                line, _ = SalesQuoteLine.objects.update_or_create(quote=quote, line_number=10, defaults={
                    "material": material, "customer_material": customer_material, "uom": uom, "quantity": Decimal("1"),
                    "unit_price": row.get("sc_price") or Decimal("0"), "tax_rate": row.get("sc_vat_rate") or Decimal("0"),
                    "uom_rate_m": row.get("sc_um_rate_m") or Decimal("1"), "uom_rate_d": row.get("sc_um_rate_d") or Decimal("1"),
                    "customer_material_code": clean(row.get("sc_cust_part")),
                    "customer_material_name": customer_material.customer_name if customer_material else "",
                    "terminal_customer_code": customer_material.terminal_customer_code if customer_material else "",
                    "terminal_customer_name": customer_material.terminal_customer_name if customer_material else "",
                    "material_name": material.name, "material_specification": material.specification,
                })
                tier_lines = []
                for index, tier in enumerate(tiers_by_quote[key(row.get("sc_nbr"))], 1):
                    quantity = pick(tier, "scd_qty", "scd_min_qty", "scd_qty_from")
                    price = pick(tier, "scd_price", "scd_unit_price")
                    if quantity is None or price is None:
                        continue
                    line_number = int(pick(tier, "scd_line", default=index * 10))
                    tier_lines.append(line_number)
                    SalesQuoteTier.objects.update_or_create(quote_line=line, line_number=line_number, defaults={
                        "min_quantity": quantity, "unit_price": price,
                        "backup_ratio": pick(tier, "scd_spare_pct", "scd_backup_ratio", default=Decimal("0")),
                        "notes": clean(pick(tier, "scd_rmks", "scd_notes", default="")),
                        "created_by": clean(pick(tier, "scd_crt_by", default=row.get("sc_crt_by"))),
                        "updated_by": clean(pick(tier, "scd_mod_by", default=row.get("sc_mod_by"))), "source_object": "scd_det",
                    })
                line.tiers.filter(source_object="scd_det").exclude(line_number__in=tier_lines).delete()
                imported += 1
        return imported

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 5000:
            raise CommandError("--limit 必须在 1 到 5000 之间")
        source = self.read_source(limit, options.get("source_file"))
        if options["bootstrap_dependencies"] and not options["commit"]:
            raise CommandError("--bootstrap-dependencies 必须与 --commit 一起使用")
        if options["bootstrap_dependencies"]:
            with transaction.atomic():
                self.bootstrap_dependencies(source)
        report = self.analyze(source)
        self.print_report(report, options["commit"])
        if not options["commit"]:
            self.stdout.write(self.style.WARNING("预检完成：未写入任何业务数据；通过后使用 --commit 明确提交本批数据。"))
            return
        blocking = sum(len(report["missing"][name]) for name in ("customers", "materials", "currencies", "uoms", "customer_materials"))
        if blocking:
            raise CommandError("主数据依赖尚未通过，已取消整批写入。请先导入并核对缺失的主数据。")
        imported = self.import_rows(report)
        self.stdout.write(self.style.SUCCESS(f"已幂等导入 {imported} 张销售报价；源报价单号保持不变。"))
