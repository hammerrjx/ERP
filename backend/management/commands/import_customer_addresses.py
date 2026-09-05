"""Import customer addresses from the read-only dgyzx1 source."""
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import CustomerAddress, Partner


def clean(value):
    return str(value or "").strip()


class Command(BaseCommand):
    help = "导入 dgyzx1 客户地址；默认只读预检，--commit 才写入本地"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--source-file", help="离线 JSON，格式为 ca_mstr 行数组或 {addresses: [...]} ")

    def read_source(self, source_file=None):
        if source_file:
            payload = json.loads(open(source_file, encoding="utf-8").read())
            return payload.get("addresses", payload) if isinstance(payload, (dict, list)) else []
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
        load_dotenv(ENV_FILE)
        try:
            with pyodbc.connect(connection_string(), readonly=True) as connection:
                cursor = connection.cursor()
                result = cursor.execute("SELECT ca_cust, ca_addr, ca_txt, ca_rmks, ca_crt_by, ca_crt_date FROM dbo.ca_mstr ORDER BY ca_cust, ca_addr")
                columns = [item[0] for item in result.description]
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as exc:
            raise CommandError(f"无法连接 dgyzx1 源库（源库只读预检未执行）：{exc}") from exc

    def handle(self, *args, **options):
        rows = self.read_source(options.get("source_file"))
        existing = {(row.customer.code.upper(), row.code): row for row in CustomerAddress.objects.select_related("customer")}
        missing_customers = set()
        invalid = []
        for row in rows:
            customer_code, address_code, address = clean(row.get("ca_cust")), clean(row.get("ca_addr")), clean(row.get("ca_txt"))
            if not customer_code or not address_code or not address:
                invalid.append((customer_code, address_code))
            elif not Partner.objects.filter(code__iexact=customer_code, kind__in=("customer", "both")).exists():
                missing_customers.add(customer_code)
        self.stdout.write(f"源客户地址：{len(rows)}；本地已存在：{len(existing)}；待更新/新增：{len(rows) - len(existing)}")
        self.stdout.write(f"缺少本地客户：{len(missing_customers)}；无效地址：{len(invalid)}")
        if not options["commit"]:
            self.stdout.write(self.style.WARNING("预检完成：未写入任何业务数据。"))
            return
        if missing_customers or invalid:
            raise CommandError("地址导入依赖未通过：请先补齐客户资料并修正地址数据。")
        imported = 0
        with transaction.atomic():
            for row in rows:
                customer = Partner.objects.get(code__iexact=clean(row["ca_cust"]), kind__in=("customer", "both"))
                code = clean(row["ca_addr"])
                address, _ = CustomerAddress.objects.update_or_create(
                    customer=customer, code=code,
                    defaults={
                        "address": clean(row["ca_txt"]), "notes": clean(row.get("ca_rmks")),
                        "enabled": True, "source_object": "ca_mstr",
                        "source_key": f"{customer.code}|{code}",
                        "created_by": clean(row.get("ca_crt_by")) or "dgyzx1-import",
                    },
                )
                imported += 1
        self.stdout.write(self.style.SUCCESS(f"已幂等导入 {imported} 条客户地址。"))
