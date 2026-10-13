"""Import legacy quotation data into a separate cutoff test ledger.

This command deliberately reads SQL Server only.  It is intended for the
2026-08-31 replay database and preserves the original quotation numbers.
"""

from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.management.commands.import_supplier_quotes import Command as SupplierCommand
from backend.management.commands.import_sales_quotes import Command as SalesCommand


CUTOFF = date(2026, 8, 31)
NEXT_DAY = date(2026, 9, 1)


class Command(BaseCommand):
    help = "Read-only import of dgyzx1 quotations created through 2026-08-31 into a cutoff ledger"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true", help="write to the configured local database")
        parser.add_argument("--report", type=Path, required=True, help="JSON result report path")

    @staticmethod
    def _read_rows(cursor, sql, parameters=()):
        result = cursor.execute(sql, parameters)
        columns = [column[0] for column in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def _by_codes(self, cursor, table, column, codes):
        rows = []
        for offset in range(0, len(codes), 500):
            batch = codes[offset:offset + 500]
            marks = ",".join("?" for _ in batch)
            rows.extend(self._read_rows(cursor, f"SELECT * FROM dbo.{table} WHERE {column} IN ({marks})", batch))
        return rows

    def read_source(self):
        import pyodbc
        from tools.inspect_source_schema import connection_string

        with pyodbc.connect(connection_string("coerp_dgyzx1"), readonly=True, timeout=30) as connection:
            cursor = connection.cursor()
            supplier_headers = self._read_rows(cursor, "SELECT * FROM dbo.pc_mstr WHERE pc_crt_date < '20260901'")
            sales_headers = self._read_rows(cursor, "SELECT * FROM dbo.sc_mstr WHERE sc_crt_date < '20260901'")

            supplier_numbers = [row["pc_nbr"] for row in supplier_headers]
            sales_numbers = [row["sc_nbr"] for row in sales_headers]
            supplier_tiers, sales_tiers = [], []
            for offset in range(0, len(supplier_numbers), 500):
                batch = supplier_numbers[offset:offset + 500]
                marks = ",".join("?" for _ in batch)
                supplier_tiers.extend(self._read_rows(cursor, f"SELECT * FROM dbo.pcd_det WHERE pcd_nbr IN ({marks}) AND (pcd_crt_date IS NULL OR pcd_crt_date < '20260901')", batch))
            for offset in range(0, len(sales_numbers), 500):
                batch = sales_numbers[offset:offset + 500]
                marks = ",".join("?" for _ in batch)
                sales_tiers.extend(self._read_rows(cursor, f"SELECT * FROM dbo.scd_det WHERE scd_nbr IN ({marks}) AND (scd_crt_date IS NULL OR scd_crt_date < '20260901')", batch))

            clean = lambda value: str(value or "").strip()
            supplier_codes = sorted({clean(row.get("pc_vend")) for row in supplier_headers if clean(row.get("pc_vend"))})
            customer_codes = sorted({clean(row.get("sc_cust")) for row in sales_headers if clean(row.get("sc_cust"))})
            material_codes = sorted({clean(row.get("pc_part")) for row in supplier_headers if clean(row.get("pc_part"))} | {clean(row.get("sc_part")) for row in sales_headers if clean(row.get("sc_part"))})
            suppliers = self._by_codes(cursor, "vd_mstr", "vd_addr", supplier_codes)
            customers = self._by_codes(cursor, "cm_mstr", "cm_addr", customer_codes)
            materials = self._by_codes(cursor, "pt_mstr", "pt_part", material_codes)
            customer_materials = [row for row in self._by_codes(cursor, "cp_mstr", "cp_part", material_codes) if clean(row.get("cp_cust")) in customer_codes]
            currency_codes = sorted({clean(row.get("pc_curr")) for row in supplier_headers if clean(row.get("pc_curr"))} | {clean(row.get("sc_curr")) for row in sales_headers if clean(row.get("sc_curr"))})
            currencies = self._by_codes(cursor, "ex_mstr", "ex_curr", currency_codes)
            unit_codes = sorted({clean(value) for row in supplier_headers + sales_headers + materials + customer_materials for value in (row.get("pc_um"), row.get("sc_um"), row.get("pt_um"), row.get("pt_um_pur"), row.get("pt_um_sl"), row.get("cp_um")) if clean(value)})
            units = self._by_codes(cursor, "um_mstr", "um_um", unit_codes)
            category_codes = sorted({clean(row.get("pt_prod_line")) for row in materials if clean(row.get("pt_prod_line"))})
            categories = self._by_codes(cursor, "pl_mstr", "pl_prod_line", category_codes)
            location_codes = sorted({clean(row.get("pt_loc")) for row in materials if clean(row.get("pt_loc"))} | {clean(row.get("pl_loc")) for row in categories if clean(row.get("pl_loc"))})
            locations = self._by_codes(cursor, "loc_mstr", "loc_loc", location_codes)
        return {
            "supplier": {"headers": supplier_headers, "tiers": supplier_tiers, "suppliers": suppliers, "materials": materials, "currencies": currencies, "units": units, "categories": categories, "locations": locations, "price_checks": []},
            "sales": {"headers": sales_headers, "tiers": sales_tiers, "customers": customers, "materials": materials, "customer_material_keys": customer_materials, "source_units": units, "prod_lines": categories, "locations": locations},
        }

    @staticmethod
    def _after_cutoff(value):
        return isinstance(value, datetime) and value.date() >= NEXT_DAY

    def _record_boundary_exceptions(self, source):
        exceptions = {"supplier_modified_after_cutoff": [], "sales_modified_after_cutoff": []}
        for name, rows, prefix in (("supplier_modified_after_cutoff", source["supplier"]["headers"], "pc"), ("sales_modified_after_cutoff", source["sales"]["headers"], "sc")):
            for row in rows:
                if self._after_cutoff(row.get(f"{prefix}_mod_date")):
                    exceptions[name].append(row.get(f"{prefix}_nbr"))
        return exceptions

    def handle(self, *args, **options):
        source = self.read_source()
        boundary = self._record_boundary_exceptions(source)
        supplier_command, sales_command = SupplierCommand(), SalesCommand()
        supplier_report = supplier_command.analyze(source["supplier"])
        if supplier_report["missing"]:
            raise CommandError("supplier quotation source has mandatory blank references")

        if options["commit"]:
            with transaction.atomic():
                supplier_lookups = supplier_command.sync_dependencies(source["supplier"])
                supplier_counts = supplier_command.import_quotes(source["supplier"], supplier_report, supplier_lookups)
                sales_command.bootstrap_dependencies(source["sales"])
                sales_report = sales_command.analyze(source["sales"])
                blocking = sum(len(sales_report["missing"][name]) for name in ("customers", "materials", "currencies", "uoms", "customer_materials"))
                if blocking:
                    raise CommandError(f"sales quotation dependencies missing: {blocking}")
                sales_count = sales_command.import_rows(sales_report)
        else:
            supplier_counts, sales_count = Counter(), 0
            sales_report = sales_command.analyze(source["sales"])

        report = {
            "cutoff": CUTOFF.isoformat(), "source_readonly": True, "committed": bool(options["commit"]),
            "supplier_quotes": len(source["supplier"]["headers"]), "supplier_quote_tiers": len(source["supplier"]["tiers"]),
            "sales_quotes": len(source["sales"]["headers"]), "sales_quote_tiers": len(source["sales"]["tiers"]),
            "imported_supplier": dict(supplier_counts), "imported_sales": sales_count,
            "sales_eligible": len(sales_report["eligible"]), "boundary_exceptions": boundary,
        }
        options["report"].write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        self.stdout.write(json.dumps(report, ensure_ascii=False, default=str))
