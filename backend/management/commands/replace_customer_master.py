"""Replace legacy test customers, import the customer workbook, then sync source addresses."""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.management.commands.import_legacy_master_data import (
    LegacyImporter, WorkbookRows, canonical, is_obvious_test, text,
)
from backend.models import (
    ApprovalStatus, CustomerAddress, CustomerMaterial, DeliveryOrder, GoodsReceipt, Partner, PurchaseOrder, PurchaseReturn, PayableVoucher, SalesOrder, SalesQuote, SalesReturn,
    SupplierInquiry, SupplierQuote,
)


def source_customer_rows():
    import pyodbc
    from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
    load_dotenv(ENV_FILE)
    with pyodbc.connect(connection_string(), readonly=True) as connection:
        cursor = connection.cursor()
        rows = cursor.execute("""
            SELECT DISTINCT cm_addr, cm_name, cm_sort, cm_txt_inv, cm_txt_run, cm_txt_ship,
                cm_www, cm_cmmt, cm_slspsn, cm_curr, cm_disc, cm_vat, cm_cr_terms,
                cm_bank, cm_bank_acct, cm_ac_code_pre, cm_ac_code_ar, cm_ac_code_income,
                cm_ac_code_cost, cm_crt_by
            FROM dbo.cm_mstr
            WHERE cm_addr IN (SELECT DISTINCT ca_cust FROM dbo.ca_mstr)
        """).fetchall()
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


class Command(BaseCommand):
    help = "清理 3.1.xls 测试客户，导入客户资料，并同步 dgyzx1 客户地址"

    def add_arguments(self, parser):
        parser.add_argument("--customer-file", type=Path, required=True)
        parser.add_argument("--commit", action="store_true")

    def read_workbook(self, path):
        rows = list(WorkbookRows(path))
        valid, test = [], []
        for row in rows:
            code, name, creator = text(row.get("客户代码")), text(row.get("客户全称")), text(row.get("录入人"))
            if is_obvious_test(code, name) or creator.upper().startswith("TEST"):
                test.append(row)
            else:
                valid.append(row)
        return rows, valid, test

    def dependency_counts(self, customers):
        return {
            "customer_materials": CustomerMaterial.objects.filter(customer__in=customers).count(),
            "addresses": CustomerAddress.objects.filter(customer__in=customers).count(),
            "quotes": SalesQuote.objects.filter(customer__in=customers).count(),
            "orders": SalesOrder.objects.filter(customer__in=customers).count(),
            "deliveries": DeliveryOrder.objects.filter(customer__in=customers).count(),
            "returns": SalesReturn.objects.filter(customer__in=customers).count(),
            "supplier_quotes": SupplierQuote.objects.filter(supplier__in=customers).count(),
            "purchase_orders": PurchaseOrder.objects.filter(supplier__in=customers).count(),
            "goods_receipts": GoodsReceipt.objects.filter(supplier__in=customers).count(),
            "payables": PayableVoucher.objects.filter(supplier__in=customers).count(),
            "purchase_returns": PurchaseReturn.objects.filter(supplier__in=customers).count(),
            "supplier_inquiries": SupplierInquiry.objects.filter(supplier__in=customers).count(),
        }

    def import_source_customers(self, rows):
        from backend.models import Currency
        currencies = {canonical(item.code): item for item in Currency.objects.all()}
        for row in rows:
            code = text(row.get("cm_addr"))
            currency = currencies.get(canonical(row.get("cm_curr")))
            if not code or not currency:
                raise CommandError(f"地址客户缺少本地币种：{code}/{row.get('cm_curr')}")
            Partner.objects.update_or_create(code=code, defaults={
                "name": text(row.get("cm_name")) or code,
                "short_name": text(row.get("cm_sort")) or code,
                "kind": "customer", "currency": currency,
                "invoice_address": text(row.get("cm_txt_inv"))[:240],
                "address": text(row.get("cm_txt_run"))[:240],
                "delivery_address": text(row.get("cm_txt_ship"))[:240],
                "website": text(row.get("cm_www"))[:200],
                "notes": text(row.get("cm_cmmt"))[:255],
                "sales_person": text(row.get("cm_slspsn"))[:64],
                "discount_rate": row.get("cm_disc") or 100,
                "tax_rate": row.get("cm_vat") or 0,
                "payment_terms": text(row.get("cm_cr_terms"))[:80],
                "payment_bank": text(row.get("cm_bank"))[:120],
                "bank_account": text(row.get("cm_bank_acct"))[:80],
                "deposit_account": text(row.get("cm_ac_code_pre"))[:32],
                "receivable_account": text(row.get("cm_ac_code_ar"))[:32],
                "income_account": text(row.get("cm_ac_code_income"))[:32],
                "cost_account": text(row.get("cm_ac_code_cost"))[:32],
                "status": ApprovalStatus.APPROVED,
                "created_by": text(row.get("cm_crt_by")) or "dgyzx1-import",
            })

    def import_excel_customers(self, path, rows):
        from backend.models import Currency
        importer = LegacyImporter({"customer": path})
        importer.currencies = {canonical(item.code): item for item in Currency.objects.all()}
        importer.seen["customer"] = set()
        original = WorkbookRows
        try:
            import backend.management.commands.import_legacy_master_data as module
            module.WorkbookRows = lambda _: rows
            importer.import_partners("customer")
        finally:
            module.WorkbookRows = original

    def sync_addresses(self, rows):
        customers = {canonical(item.code): item for item in Partner.objects.filter(kind__in=("customer", "both"))}
        imported = 0
        for row in rows:
            customer = customers.get(canonical(row.get("ca_cust")))
            code = text(row.get("ca_addr"))
            address = text(row.get("ca_txt"))
            if not customer or not code or not address:
                raise CommandError(f"客户地址依赖缺失：{row.get('ca_cust')}/{row.get('ca_addr')}")
            CustomerAddress.objects.update_or_create(customer=customer, code=code, defaults={
                "address": address[:240], "notes": text(row.get("ca_rmks"))[:240], "enabled": True,
                "source_object": "ca_mstr", "source_key": f"{customer.code}|{code}",
                "created_by": text(row.get("ca_crt_by")) or "dgyzx1-import",
            })
            imported += 1
        return imported

    def handle(self, *args, **options):
        path = options["customer_file"]
        if not path.is_file():
            raise CommandError(f"客户资料文件不存在：{path}")
        all_rows, valid_rows, test_rows = self.read_workbook(path)
        test_codes = {text(row.get("客户代码")) for row in test_rows if text(row.get("客户代码"))}
        test_customers = Partner.objects.filter(code__in=test_codes, kind__in=("customer", "both"))
        source_rows = source_customer_rows()
        address_rows = []
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
        load_dotenv(ENV_FILE)
        with pyodbc.connect(connection_string(), readonly=True) as connection:
            cursor = connection.cursor()
            result = cursor.execute("SELECT ca_cust,ca_addr,ca_txt,ca_rmks,ca_crt_by FROM dbo.ca_mstr ORDER BY ca_cust,ca_addr")
            columns = [item[0] for item in result.description]
            address_rows = [dict(zip(columns, row)) for row in result.fetchall()]
        counts = self.dependency_counts(test_customers)
        deletable_count = test_customers.count()
        self.stdout.write(f"Excel 总客户：{len(all_rows)}；有效客户：{len(valid_rows)}；测试客户：{len(test_rows)}")
        self.stdout.write(f"本地待清理测试客户：{test_customers.count()}；关联记录：{counts}")
        self.stdout.write(f"地址客户补齐：{len(source_rows)}；源客户地址：{len(address_rows)}")
        if not options["commit"]:
            self.stdout.write(self.style.WARNING("预检完成：未删除或写入任何本地数据。"))
            return
        protected = {key: value for key, value in counts.items() if value and key not in {"addresses"}}
        if protected:
            raise CommandError(f"测试客户存在受保护业务关联，已中止：{protected}")
        with transaction.atomic():
            # No protected references remain; cascaded contact/company/bank rows are safe to remove.
            test_customers.delete()
            self.import_source_customers(source_rows)
            self.import_excel_customers(path, valid_rows)
            imported_addresses = self.sync_addresses(address_rows)
        self.stdout.write(self.style.SUCCESS(f"已删除测试客户 {deletable_count} 条，导入有效客户 {len(valid_rows)} 条，导入客户地址 {imported_addresses} 条。"))
