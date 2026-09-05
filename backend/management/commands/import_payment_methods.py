"""Synchronize payment terms and customer/supplier links from dgyzx1."""
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import ApprovalStatus, Partner, PaymentMethod


def connection_string():
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value_text = line.split("=", 1)
                os.environ.setdefault(key.strip(), value_text.strip().strip("'\""))
    return (
        "DRIVER={SQL Server};SERVER=%s,%s;DATABASE=%s;UID=%s;PWD=%s;"
        % tuple(os.environ[name] for name in (
            "ERP_SOURCE_DB_HOST", "ERP_SOURCE_DB_PORT", "ERP_SOURCE_DB_NAME",
            "ERP_SOURCE_DB_USER", "ERP_SOURCE_DB_PASSWORD",
        ))
    )


def value(row, columns, *names, default=None):
    for name in names:
        if name in columns:
            return row[columns[name]]
    return default


def calc_method(raw):
    text = str(raw or "1").strip()
    return text if text in {"1", "2", "3"} else "1"


class Command(BaseCommand):
    help = "从 dgyzx1.ct_mstr 同步全部支付方式，并关联客户/供应商付款条件"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true", help="确认写入本地数据库")

    def handle(self, *args, **options):
        try:
            import pyodbc
            connection = pyodbc.connect(connection_string(), readonly=True, timeout=20)
        except Exception as exc:
            raise CommandError(f"无法连接 dgyzx1 源库（支付方式只读预检未执行）：{exc}") from exc

        try:
            with connection:
                cursor = connection.cursor()
                catalog = os.getenv("ERP_SOURCE_DB_CATALOG", "").strip()
                # Customer payment terms live in the business database; use the catalog only as a fallback.
                terms_queries = ["dbo.ct_mstr", f"[{catalog}].[dbo].[ct_mstr]"] if catalog else ["dbo.ct_mstr"]
                for table in terms_queries:
                    try:
                        cursor.execute(f"SELECT * FROM {table}")
                        break
                    except pyodbc.Error:
                        if table == terms_queries[-1]:
                            raise
                names = [item[0].lower() for item in cursor.description]
                columns = {name: index for index, name in enumerate(names)}
                rows = cursor.fetchall()
                cursor.execute("SELECT cm_addr, cm_cr_terms FROM dbo.cm_mstr")
                customers = cursor.fetchall()
                customer_columns = {item[0].lower(): index for index, item in enumerate(cursor.description)}
                cursor.execute("SELECT vd_addr, vd_cr_terms FROM dbo.vd_mstr")
                suppliers = cursor.fetchall()
                supplier_columns = {item[0].lower(): index for index, item in enumerate(cursor.description)}
        finally:
            connection.close()

        self.stdout.write(f"源库支付方式 {len(rows)} 条，客户关联 {len(customers)} 条，供应商关联 {len(suppliers)} 条")
        if not options["commit"]:
            self.stdout.write("预检完成；添加 --commit 才会写入本地数据库")
            return

        with transaction.atomic():
            by_code = {}
            for row in rows:
                code = str(value(row, columns, "ct_code", "ct_terms", default="") or "").strip()
                if not code:
                    continue
                method, _ = PaymentMethod.objects.update_or_create(code=code, defaults={
                    "description": str(value(row, columns, "ct_desc", "ct_description", default="") or "")[:255],
                    "discount_date_method": calc_method(value(row, columns, "ct_disc_date", "ct_disc_method", default="1")),
                    "discount_percent": value(row, columns, "ct_disc_pct", "ct_discount_pct", default=0) or 0,
                    "discount_days": value(row, columns, "ct_disc_days", default=0) or 0,
                    "discount_start_day": value(row, columns, "ct_disc_start", "ct_disc_date_day", default=0) or 0,
                    "due_date_method": calc_method(value(row, columns, "ct_due_date", "ct_due_method", default="1")),
                    "due_days": value(row, columns, "ct_due_days", default=0) or 0,
                    "due_start_day": value(row, columns, "ct_due_start", "ct_due_date_day", default=0) or 0,
                    "notes": str(value(row, columns, "ct_rmks", "ct_notes", default="") or "")[:255],
                    "status": ApprovalStatus.APPROVED,
                    "created_by": "dgyzx1-import",
                })
                by_code[code] = method

            for row in customers:
                partner = Partner.objects.filter(code=str(row[customer_columns["cm_addr"]]).strip()).first()
                term = str(row[customer_columns["cm_cr_terms"]] or "").strip()
                method = by_code.get(term)
                if term and method is None:
                    # Some legacy customers store a human-readable term that has no ct_mstr code.
                    method, _ = PaymentMethod.objects.update_or_create(
                        code=term,
                        defaults={"description": term, "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"},
                    )
                    by_code[term] = method
                if partner and method:
                    Partner.objects.filter(pk=partner.pk).update(payment_method_master=method, payment_method=method.code)
            for row in suppliers:
                partner = Partner.objects.filter(code=str(row[supplier_columns["vd_addr"]]).strip()).first()
                term = str(row[supplier_columns["vd_cr_terms"]] or "").strip()
                method = by_code.get(term)
                if term and method is None:
                    method, _ = PaymentMethod.objects.update_or_create(
                        code=term,
                        defaults={"description": term, "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"},
                    )
                    by_code[term] = method
                if partner and method:
                    Partner.objects.filter(pk=partner.pk).update(payment_method_master=method, payment_method=method.code)
            # Reconcile locally imported customers whose source record was not part of the address-filtered import.
            for partner in Partner.objects.exclude(payment_method="").filter(payment_method_master__isnull=True):
                term = str(partner.payment_method).strip()
                if not term:
                    continue
                method, _ = PaymentMethod.objects.get_or_create(
                    code=term,
                    defaults={"description": term, "status": ApprovalStatus.APPROVED, "created_by": "dgyzx1-import"},
                )
                Partner.objects.filter(pk=partner.pk).update(payment_method_master=method)
        self.stdout.write(self.style.SUCCESS(f"已同步 {len(by_code)} 条支付方式并更新客户/供应商关联"))
