"""Synchronize local tax master data from the read-only dgyzx1 material table."""

from collections import Counter, defaultdict
import os

import pyodbc
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import ApprovalStatus, Material, TaxCode


def _load_env():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    env_path = os.path.join(root, ".env")
    values = {}
    try:
        with open(env_path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip().strip('"').strip("'")
    except OSError as exc:
        raise CommandError(f"无法读取 .env：{exc}") from exc
    return values


def _source_connection():
    values = _load_env()
    required = [
        "ERP_SOURCE_DB_HOST",
        "ERP_SOURCE_DB_PORT",
        "ERP_SOURCE_DB_NAME",
        "ERP_SOURCE_DB_USER",
        "ERP_SOURCE_DB_PASSWORD",
    ]
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise CommandError(f".env 缺少配置项：{', '.join(missing)}")
    driver = os.getenv("ERP_SOURCE_DB_DRIVER", "ODBC Driver 18 for SQL Server")
    connection_string = (
        f"DRIVER={{{driver}}};SERVER={values['ERP_SOURCE_DB_HOST']},{values['ERP_SOURCE_DB_PORT']};"
        f"DATABASE={values['ERP_SOURCE_DB_NAME']};UID={values['ERP_SOURCE_DB_USER']};"
        f"PWD={values['ERP_SOURCE_DB_PASSWORD']};Encrypt=yes;TrustServerCertificate=yes;"
        "APP=ERP-TaxSync;Connection Timeout=15;"
    )
    try:
        return pyodbc.connect(connection_string, readonly=True, timeout=15)
    except pyodbc.Error as exc:
        raise CommandError(f"无法连接源库 {values['ERP_SOURCE_DB_NAME']}：{exc}") from exc


def _fetch_source_tax_codes(connection):
    query = """
        SELECT LTRIM(RTRIM(pt_char1)), LTRIM(RTRIM(pt_char2)), LTRIM(RTRIM(pt_char5))
        FROM dbo.pt_mstr
        WHERE pt_char1 IS NOT NULL AND LTRIM(RTRIM(pt_char1)) <> ''
    """
    grouped = defaultdict(Counter)
    for code, name, invoice_name in connection.cursor().execute(query).fetchall():
        code = str(code or "").strip()
        if not code:
            continue
        name = str(name or "").strip()[:160]
        invoice_name = str(invoice_name or "").strip()[:160]
        grouped[code][(name, invoice_name)] += 1
    result = {}
    for code, combinations in grouped.items():
        # Most frequently used values are the stable representative; ties are deterministic.
        (name, invoice_name), _ = sorted(
            combinations.items(), key=lambda item: (-item[1], item[0][0], item[0][1])
        )[0]
        result[code] = {"name": name or code, "invoice_name": invoice_name}
    return result


class Command(BaseCommand):
    help = "以只读方式从 dgyzx1.dbo.pt_mstr 同步税务编码、名称和开票名称"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="只读取并报告，不写入本地数据库")
        parser.add_argument(
            "--purge-unreferenced-stale",
            action="store_true",
            help="物理删除源库不存在且没有物料引用的旧税务编码",
        )

    def handle(self, *args, **options):
        with _source_connection() as connection:
            source = _fetch_source_tax_codes(connection)
        if not source:
            raise CommandError("源库未返回任何税务编码，已中止同步")

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"源库税务编码 {len(source)} 个；未写入本地数据库"))
            return

        with transaction.atomic():
            created = updated = 0
            for code, values in source.items():
                tax, was_created = TaxCode.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": values["name"],
                        "invoice_name": values["invoice_name"],
                        "active": True,
                        "status": ApprovalStatus.APPROVED,
                        "created_by": "dgyzx1-tax-sync",
                    },
                )
                if not was_created:
                    TaxCode.objects.filter(pk=tax.pk).update(
                        name=values["name"], invoice_name=values["invoice_name"],
                        active=True, status=ApprovalStatus.APPROVED,
                    )
                created += int(was_created)
                updated += int(not was_created)

            stale = TaxCode.objects.exclude(code__in=source).update(active=False)
            purged = 0
            if options["purge_unreferenced_stale"]:
                purged, _ = TaxCode.objects.filter(active=False, materials__isnull=True).delete()

            material_updates = 0
            for material in Material.objects.select_related("tax_master").iterator(chunk_size=500):
                code = (material.tax_code or "").strip()
                values = source.get(code)
                if not values:
                    continue
                tax = TaxCode.objects.get(code=code)
                changed = material.tax_master_id != tax.pk or material.tax_name != values["name"]
                material.tax_master = tax
                material.tax_name = values["name"]
                if not material.invoice_name:
                    material.invoice_name = values["invoice_name"]
                    changed = True
                if changed:
                    material.save(update_fields=["tax_master", "tax_name", "invoice_name", "updated_at"])
                    material_updates += 1

        self.stdout.write(self.style.SUCCESS(
            f"dgyzx1 税务同步完成：源库 {len(source)} 个，新增 {created} 个，更新 {updated} 个，"
            f"停用旧编码 {stale} 个，物理删除无引用旧编码 {purged} 个，"
            f"更新物料 {material_updates} 条；未向源库写入数据"
        ))
