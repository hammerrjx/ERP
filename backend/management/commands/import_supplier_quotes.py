"""Read-only staged import for dgyzx1 supplier quotations."""

from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from backend.models import (
    ApprovalStatus, Currency, Location, Material, Partner, ProductCategory,
    RoutingOperation, SupplierQuote, SupplierQuoteLine, Uom, UomCategory,
)


def clean(value):
    return str(value or "").strip()


def key(value):
    return clean(value).upper()


def source_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def source_expiry(value):
    value = source_date(value)
    return None if value and value.year >= 2069 else value


def aware(value):
    if not value or not isinstance(value, datetime) or timezone.is_aware(value):
        return value
    return timezone.make_aware(value, timezone.get_current_timezone())


def source_status(row, prefix):
    """Preserve the legacy posted/check/approved workflow without guessing."""
    posted = bool(row.get(f"{prefix}_pst"))
    checked = bool(row.get(f"{prefix}_chk"))
    approved = bool(row.get(f"{prefix}_allow"))
    return {
        "status": ApprovalStatus.APPROVED if checked or approved else (ApprovalStatus.PENDING if posted else ApprovalStatus.DRAFT),
        "is_confirmed": posted,
        "confirmed_by": clean(row.get(f"{prefix}_pst_by")),
        "confirmed_at": aware(row.get(f"{prefix}_pst_date")),
        "approved_by": clean(row.get(f"{prefix}_chk_by") or row.get(f"{prefix}_allow_by")),
        "approved_at": aware(row.get(f"{prefix}_chk_date") or row.get(f"{prefix}_allow_date")),
    }


class Command(BaseCommand):
    help = "只读预检 dgyzx1 最新供应商报价；显式添加 --commit 才同步写入本地 ERP"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50, help="按 pc_mod_date 倒序读取的最新报价数，默认 50")
        parser.add_argument("--commit", action="store_true", help="确认同步写入本地 ERP")

    def read_source(self, limit):
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv

        load_dotenv(ENV_FILE)
        with pyodbc.connect(connection_string(), readonly=True, timeout=20) as connection:
            cursor = connection.cursor()

            def rows(sql, parameters=()):
                result = cursor.execute(sql, parameters)
                columns = [item[0] for item in result.description]
                return [dict(zip(columns, item)) for item in result.fetchall()]

            headers = rows(f"""
                SELECT TOP {limit}
                    pc_nbr, pc_vend, pc_curr, pc_part, pc_um, pc_um_rate_m, pc_um_rate_d,
                    pc_start, pc_expire, pc_vat_incl, pc_vat, pc_type, pc_price_mtl,
                    pc_price_sub, pc_price, pc_rmks, pc_wf_status, pc_crt_by, pc_crt_date,
                    pc_mod_times, pc_mod_by, pc_mod_date, pc_pst, pc_pst_by, pc_pst_date,
                    pc_ord_min, pc_ord_mult, pc_pur_lt, pc_allow, pc_allow_by, pc_allow_date,
                    pc_chk, pc_chk_by, pc_chk_date, pc_sale, pc_sale_by, pc_sale_date,
                    pc_op, pc_po_part
                FROM dbo.pc_mstr
                ORDER BY pc_mod_date DESC, pc_nbr DESC
            """)
            numbers = [row["pc_nbr"] for row in headers]
            tiers = []
            for offset in range(0, len(numbers), 200):
                batch = numbers[offset:offset + 200]
                placeholders = ",".join("?" for _ in batch)
                tiers.extend(rows(f"SELECT * FROM dbo.pcd_det WHERE pcd_nbr IN ({placeholders})", batch))

            vendor_codes = sorted({clean(row.get("pc_vend")) for row in headers if clean(row.get("pc_vend"))})
            material_codes = sorted({clean(row.get("pc_part")) for row in headers if clean(row.get("pc_part"))})
            currency_codes = sorted({clean(row.get("pc_curr")) for row in headers if clean(row.get("pc_curr"))})

            def lookup(table, column, codes):
                placeholders = ",".join("?" for _ in codes) or "?"
                return rows(f"SELECT * FROM dbo.{table} WHERE {column} IN ({placeholders})", codes or [""])

            suppliers = lookup("vd_mstr", "vd_addr", vendor_codes)
            materials = lookup("pt_mstr", "pt_part", material_codes)
            currencies = lookup("ex_mstr", "ex_curr", currency_codes)
            unit_codes = sorted({clean(value) for row in headers + materials for value in (
                row.get("pc_um"), row.get("pt_um"), row.get("pt_um_pur"),
            ) if clean(value)})
            units = lookup("um_mstr", "um_um", unit_codes)
            product_lines = sorted({clean(row.get("pt_prod_line")) for row in materials if clean(row.get("pt_prod_line"))})
            locations = sorted({clean(row.get("pt_loc")) for row in materials if clean(row.get("pt_loc"))})
            categories = lookup("pl_mstr", "pl_prod_line", product_lines)
            locations = lookup("loc_mstr", "loc_loc", locations)

            # These views are the legacy price authority.  They intentionally
            # have no quote number, so they validate prices rather than replace
            # pc_mstr/pcd_det as the import source.
            price_checks = []
            for row in headers:
                price_checks.extend(rows("""
                    SELECT 'master' AS source_name, pc_vend, pc_part, pc_curr, pc_start, pc_expire, pc_vat, pc_price
                    FROM dbo.v_pc_mstr_price
                    WHERE pc_vend = ? AND pc_part = ? AND pc_curr = ?
                    UNION ALL
                    SELECT 'all' AS source_name, pc_vend, pc_part, pc_curr, pc_start, pc_expire, pc_vat, pc_price
                    FROM dbo.v_pc_all_price
                    WHERE pc_vend = ? AND pc_part = ? AND pc_curr = ?
                """, (row["pc_vend"], row["pc_part"], row["pc_curr"], row["pc_vend"], row["pc_part"], row["pc_curr"])))
        return {
            "headers": headers, "tiers": tiers, "suppliers": suppliers, "materials": materials,
            "currencies": currencies, "units": units, "categories": categories, "locations": locations,
            "price_checks": price_checks,
        }

    @staticmethod
    def price_view_matches(row, source):
        target = (key(row.get("pc_vend")), key(row.get("pc_part")), key(row.get("pc_curr")), source_date(row.get("pc_start")), source_date(row.get("pc_expire")), row.get("pc_vat"), row.get("pc_price"))
        return any((key(item.get("pc_vend")), key(item.get("pc_part")), key(item.get("pc_curr")), source_date(item.get("pc_start")), source_date(item.get("pc_expire")), item.get("pc_vat"), item.get("pc_price")) == target for item in source["price_checks"] if item.get("source_name") == "master")

    def analyze(self, source):
        headers = source["headers"]
        tiers_by_quote = defaultdict(list)
        for row in source["tiers"]:
            tiers_by_quote[key(row.get("pcd_nbr"))].append(row)
        missing = defaultdict(set)
        view_mismatches = []
        for row in headers:
            for field, label in (("pc_vend", "供应商"), ("pc_part", "物料"), ("pc_curr", "币种"), ("pc_um", "单位")):
                if not clean(row.get(field)):
                    missing[label].add("<空值>")
            if not self.price_view_matches(row, source):
                view_mismatches.append(clean(row.get("pc_nbr")))
        return {
            "tiers_by_quote": tiers_by_quote,
            "missing": missing,
            "view_mismatches": view_mismatches,
            "type_counts": Counter(clean(row.get("pc_type")) for row in headers),
            "latest": headers[0] if headers else None,
            "oldest": headers[-1] if headers else None,
        }

    def print_report(self, source, report, commit):
        mode = "提交" if commit else "只读预检"
        self.stdout.write(f"供应商报价导入模式：{mode}")
        self.stdout.write(f"源报价：{len(source['headers'])}；源阶梯价：{len(source['tiers'])}；关联供应商：{len(source['suppliers'])}；关联物料：{len(source['materials'])}")
        self.stdout.write(f"报价类型：采购 P={report['type_counts']['P']}；外协 S={report['type_counts']['S']}")
        self.stdout.write(f"价格视图校验：v_pc_mstr_price 未匹配 {len(report['view_mismatches'])} 张" + (f"；示例：{', '.join(report['view_mismatches'][:8])}" if report["view_mismatches"] else ""))
        for label, values in report["missing"].items():
            self.stdout.write(f"源报价缺少{label}：{len(values)}")
        if report["latest"]:
            self.stdout.write(f"本批时间范围：{report['oldest']['pc_mod_date']} 至 {report['latest']['pc_mod_date']}")

    def sync_dependencies(self, source):
        imported = Counter()
        currencies = {key(item.code): item for item in Currency.objects.all()}
        for row in source["currencies"]:
            code = clean(row.get("ex_curr"))
            if not code:
                continue
            currencies[key(code)], _ = Currency.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("ex_desc")) or code, "symbol": clean(row.get("ex_symbol"))[:8],
                "status": ApprovalStatus.APPROVED, "created_by": clean(row.get("ex_crt_by")) or "dgyzx1-import",
            })
            imported["币种"] += 1
        category, _ = UomCategory.objects.get_or_create(code="COUNT", defaults={"name": "数量", "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"})
        units = {key(item.code): item for item in Uom.objects.all()}
        units_by_name = {key(item.name): item for item in Uom.objects.all()}
        for row in source["units"]:
            code, name = clean(row.get("um_um")), clean(row.get("um_desc")) or clean(row.get("um_um"))
            if not code:
                continue
            unit = units.get(key(code)) or units_by_name.get(key(name))
            if unit:
                # Local unit names are unique.  When legacy systems use a
                # different code for the same localized unit, keep the local
                # identity and map the source code to it.
                # Do not overwrite an established local unit's category or
                # approval state merely because it is reused by this batch.
                # The source unit code remains mapped in `units` below.
                pass
            else:
                unit = Uom.objects.create(
                    code=code, name=name, description=name, category=category,
                    status=ApprovalStatus.APPROVED, created_by=clean(row.get("um_crt_by")) or "dgyzx1-import",
                )
                units_by_name[key(name)] = unit
            units[key(code)] = unit
            imported["单位"] += 1
        locations = {key(item.code): item for item in Location.objects.all()}
        for row in source["locations"]:
            code = clean(row.get("loc_loc"))
            if not code:
                continue
            locations[key(code)], _ = Location.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("loc_desc")) or code, "location_type": "fg" if key(row.get("loc_type")) == "FG" else "warehouse",
                "usable": bool(row.get("loc_avail")), "participate_mrp": bool(row.get("loc_nettable")),
                "disabled_for_inventory": bool(row.get("loc_disabled")), "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import",
            })
            imported["库位"] += 1
        categories = {key(item.code): item for item in ProductCategory.objects.all()}
        for row in source["categories"]:
            code = clean(row.get("pl_prod_line"))
            if not code:
                continue
            default_uom = units.get(key(row.get("pl_um"))) or next(iter(units.values()), None)
            default_location = locations.get(key(row.get("pl_loc"))) or next(iter(locations.values()), None)
            if not default_uom or not default_location:
                continue
            categories[key(code)], _ = ProductCategory.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("pl_desc")) or code, "description": clean(row.get("pl_desc")),
                "default_uom": default_uom, "default_location": default_location, "code_prefix": code,
                "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import",
            })
            imported["产品类"] += 1
        suppliers = {key(item.code): item for item in Partner.objects.all()}
        for row in source["suppliers"]:
            code = clean(row.get("vd_addr"))
            currency = currencies.get(key(row.get("vd_curr")))
            if not code or not currency:
                continue
            suppliers[key(code)], _ = Partner.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("vd_name")) or code, "short_name": clean(row.get("vd_sort")) or clean(row.get("vd_name")) or code,
                "kind": Partner.PartnerKind.SUPPLIER, "currency": currency, "address": clean(row.get("vd_txt"))[:240],
                "buyer": clean(row.get("vd_buyer")), "payment_method": clean(row.get("vd_cr_terms")) or "原ERP未设置",
                "tax_rate": row.get("vd_vat") or Decimal("0"), "quote_method": clean(row.get("vd_quot_type")),
                "invoice_type": clean(row.get("vd_inv_type")), "tax_calculation_method": clean(row.get("vd_vat_method")),
                "payment_bank": clean(row.get("vd_bank")), "bank_account": clean(row.get("vd_bank_acct")),
                "notes": clean(row.get("vd_rmks")), "payment_hold": bool(row.get("vd_hold")),
                "internal_company": bool(row.get("vd_isinternal")), "status": ApprovalStatus.APPROVED,
                "created_by": clean(row.get("vd_crt_by")) or "dgyzx1-import",
            })
            imported["供应商"] += 1
        materials = {key(item.code): item for item in Material.objects.all()}
        for row in source["materials"]:
            code = clean(row.get("pt_part"))
            category = categories.get(key(row.get("pt_prod_line")))
            uom = units.get(key(row.get("pt_um")))
            location = locations.get(key(row.get("pt_loc"))) or getattr(category, "default_location", None)
            if not code or not category or not uom or not location:
                continue
            materials[key(code)], _ = Material.objects.update_or_create(code=code, defaults={
                "name": clean(row.get("pt_desc1")) or code, "english_name": clean(row.get("pt_desc2")),
                "specification": clean(row.get("pt_spec")), "category": category, "uom": uom, "default_location": location,
                "default_supplier": suppliers.get(key(row.get("pt_vend"))), "active": bool(row.get("pt_status")),
                "supply_method": "purchase", "min_purchase_qty": row.get("pt_ord_min") or Decimal("0"),
                "min_pack_qty": row.get("pt_ord_mult") or Decimal("0"), "purchase_lead_days": row.get("pt_pur_lt") or 0,
                "buyer": clean(row.get("pt_buyer")), "planner": clean(row.get("pt_planner")),
                "status": ApprovalStatus.APPROVED, "created_by": clean(row.get("pt_crt_by")) or "dgyzx1-import",
            })
            imported["物料"] += 1
        return imported, currencies, units, suppliers, materials

    def import_quotes(self, source, report, lookups):
        _, currencies, units, suppliers, materials = lookups
        tiers_by_quote = report["tiers_by_quote"]
        imported = Counter()
        for row in source["headers"]:
            supplier = suppliers.get(key(row.get("pc_vend")))
            material = materials.get(key(row.get("pc_part")))
            currency = currencies.get(key(row.get("pc_curr")))
            purchase_uom = units.get(key(row.get("pc_um")))
            if not supplier or not material or not currency or not purchase_uom:
                imported["报价跳过：关联缺失"] += 1
                continue
            quote_type = SupplierQuote.QuoteType.PURCHASE if key(row.get("pc_type")) == "P" else SupplierQuote.QuoteType.OUTSOURCE
            parent_material = materials.get(key(row.get("pc_po_part"))) if quote_type == SupplierQuote.QuoteType.OUTSOURCE else None
            operation = None
            if parent_material and row.get("pc_op"):
                operation = RoutingOperation.objects.filter(routing__material=parent_material, sequence=row["pc_op"]).first()
            quote, _ = SupplierQuote.objects.update_or_create(number=clean(row.get("pc_nbr")), defaults={
                "supplier": supplier, "material": material, "currency": currency, "purchase_uom": purchase_uom,
                "uom_rate_m": row.get("pc_um_rate_m") or Decimal("1"), "uom_rate_d": row.get("pc_um_rate_d") or Decimal("1"),
                "quote_type": quote_type, "tax_included": bool(row.get("pc_vat_incl")), "tax_rate": row.get("pc_vat") or Decimal("0"),
                "effective_date": source_date(row.get("pc_start")), "expiry_date": source_expiry(row.get("pc_expire")),
                "material_unit_price": row.get("pc_price_mtl") or Decimal("0") if quote_type == SupplierQuote.QuoteType.PURCHASE else Decimal("0"),
                "processing_unit_price": row.get("pc_price_sub") or Decimal("0") if quote_type == SupplierQuote.QuoteType.OUTSOURCE else Decimal("0"),
                "min_purchase_qty": row.get("pc_ord_min") or Decimal("0"), "min_pack_qty": row.get("pc_ord_mult") or Decimal("0"),
                "delivery_days": row.get("pc_pur_lt") or 0, "operation": operation, "parent_material": parent_material,
                "notes": clean(row.get("pc_rmks")), "workflow_status": clean(row.get("pc_wf_status")),
                "is_ratified": bool(row.get("pc_allow")), "ratified_by": clean(row.get("pc_allow_by")),
                "ratified_at": aware(row.get("pc_allow_date")), "is_sales_confirmed": bool(row.get("pc_sale")),
                "sales_confirmed_by": clean(row.get("pc_sale_by")), "sales_confirmed_at": aware(row.get("pc_sale_date")),
                "modification_count": row.get("pc_mod_times") or 0, "source_object": "pc_mstr",
                "created_by": clean(row.get("pc_crt_by")), "updated_by": clean(row.get("pc_mod_by")), **source_status(row, "pc"),
            })
            SupplierQuote.objects.filter(pk=quote.pk).update(created_at=aware(row.get("pc_crt_date")), updated_at=aware(row.get("pc_mod_date")))
            line_numbers = []
            for index, tier in enumerate(sorted(tiers_by_quote[key(row.get("pc_nbr"))], key=lambda item: (item.get("pcd_qty") or 0, item.get("pcd_line") or 0)), 1):
                min_qty = tier.get("pcd_qty")
                if min_qty is None:
                    continue
                line_number = int(tier.get("pcd_line") or index)
                line_numbers.append(line_number)
                SupplierQuoteLine.objects.update_or_create(quote=quote, line_number=line_number, defaults={
                    "min_qty": min_qty,
                    "material_unit_price": (tier.get("pcd_price_mtl") or Decimal("0")) if quote_type == SupplierQuote.QuoteType.PURCHASE else None,
                    "processing_unit_price": (tier.get("pcd_price_sub") or Decimal("0")) if quote_type == SupplierQuote.QuoteType.OUTSOURCE else None,
                    "notes": clean(tier.get("pcd_rmks")), "created_by": clean(tier.get("pcd_crt_by")),
                    "updated_by": clean(tier.get("pcd_mod_by")), "modification_count": tier.get("pcd_mod_times") or 0, "source_object": "pcd_det",
                })
                imported["报价阶梯"] += 1
            quote.lines.filter(source_object="pcd_det").exclude(line_number__in=line_numbers).delete()
            imported["报价"] += 1
        return imported

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 5000:
            raise CommandError("--limit 必须在 1 到 5000 之间")
        source = self.read_source(limit)
        report = self.analyze(source)
        self.print_report(source, report, options["commit"])
        if not options["commit"]:
            self.stdout.write(self.style.WARNING("预检完成：未写入任何数据；确认后使用 --limit 50 --commit。"))
            return
        if report["missing"]:
            raise CommandError("源报价存在必填关联空值，已取消整批同步。")
        with transaction.atomic():
            lookups = self.sync_dependencies(source)
            imported = self.import_quotes(source, report, lookups)
        self.stdout.write(self.style.SUCCESS(f"同步完成：{dict(imported)}；基础资料：{dict(lookups[0])}"))
