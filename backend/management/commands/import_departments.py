from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import xlrd

from backend.models import ApprovalStatus, Department, Role


DEPARTMENT_MODULES = {
    "FI": ("finance", "payable_voucher", "receivable"),
    "GM": ("*",),
    "HQ": ("production", "inventory_issue", "quality"),
    "HR": ("organization", "user", "role"),
    "PD": ("production", "inventory_issue", "quality"),
    "PMC": ("purchase_requisition", "mrp", "sales_order", "inventory_balance", "shortage_alert"),
    "PO": ("purchase_order", "purchase_requisition", "goods_receipt", "purchase_return", "payable_voucher"),
    "PU": ("material", "supplier", "supplier_quote", "rfq"),
    "QM": ("quality", "goods_receipt", "sales_return"),
    "RD": ("material", "bom", "routing"),
    "SD": ("sales_quote", "sales_order", "delivery_order", "sales_return"),
    "ST": ("inventory_balance", "goods_receipt", "stock_issue", "inventory_transfer", "stock_count"),
    "ZB": ("*",),
}


def modules_for(code):
    if code in DEPARTMENT_MODULES:
        return DEPARTMENT_MODULES[code]
    for prefix in ("PD", "SD"):
        if code.startswith(prefix):
            return DEPARTMENT_MODULES[prefix]
    return ("master_data",)


def role_permissions(code, manager=False):
    modules = modules_for(code)
    if modules == ("*",):
        return ["*"]
    actions = ("view", "create", "change", "submit")
    permissions = [f"{module}.{action}" for module in modules for action in actions]
    if "sales_quote" in modules:
        permissions.append("sales_quote.confirm")
    if manager:
        permissions.extend(f"{module}.approve" for module in modules)
        if "sales_quote" in modules:
            permissions.append("sales_quote.ratify")
    return permissions


class Command(BaseCommand):
    help = "导入 AMDPMTA1 部门表，并建立部门操作员/经理角色权限"

    def add_arguments(self, parser):
        parser.add_argument("--source-file", required=True, type=Path)
        parser.add_argument("--replace", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        path = options["source_file"]
        if not path.exists():
            raise CommandError(f"部门文件不存在：{path}")
        sheet = xlrd.open_workbook(str(path)).sheet_by_index(0)
        headers = [str(value).strip() for value in sheet.row_values(0)]
        rows = []
        for index in range(1, sheet.nrows):
            row = dict(zip(headers, sheet.row_values(index)))
            code = str(row.get("部门代码", "")).strip().upper()
            name = str(row.get("部门名称", "")).strip()
            if code and name and code not in {item["code"] for item in rows}:
                rows.append({
                    "code": code,
                    "name": name,
                    "manager": str(row.get("负责人", "")).strip(),
                    "notes": str(row.get("备注", "")).strip(),
                    "parent_code": str(row.get("上级部门", "")).strip().upper(),
                    "source_created_by": str(row.get("录入人", "")).strip(),
                    "source_created_at": self.parse_excel_date(row.get("录入时间"), sheet.book.datemode),
                })
        if options["replace"]:
            Role.objects.all().delete()
            Department.objects.all().delete()
        departments = {}
        for row in rows:
            department, _ = Department.objects.update_or_create(
                code=row["code"],
                defaults={
                    "name": row["name"],
                    "manager": row["manager"],
                    "notes": row["notes"],
                    "source_created_by": row["source_created_by"],
                    "source_created_at": row["source_created_at"],
                    "status": ApprovalStatus.APPROVED,
                    "approved_by": "legacy-import",
                    "approved_at": timezone.now(),
                },
            )
            departments[row["code"]] = department
        for row in rows:
            department = departments[row["code"]]
            parent = departments.get(row["parent_code"])
            if department.parent_id != getattr(parent, "id", None):
                department.parent = parent
                department.save(update_fields=["parent", "updated_at"])
            for suffix, title, manager in (("OPERATOR", "操作员", False), ("MANAGER", "经理", True)):
                Role.objects.update_or_create(
                    code=f"{department.code}-{suffix}",
                    defaults={
                        "name": f"{department.name}-{title}",
                        "department": department,
                        "permissions": role_permissions(department.code, manager),
                        "status": ApprovalStatus.APPROVED,
                        "approved_by": "legacy-import",
                        "approved_at": timezone.now(),
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"已导入 {len(departments)} 个部门和 {Role.objects.count()} 个角色"))

    @staticmethod
    def parse_excel_date(value, datemode):
        if not isinstance(value, (int, float)) or not value:
            return None
        parts = xlrd.xldate_as_datetime(value, datemode)
        return timezone.make_aware(parts) if timezone.is_naive(parts) else parts
