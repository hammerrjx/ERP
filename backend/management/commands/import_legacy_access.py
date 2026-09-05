import hashlib
import json
from collections import defaultdict
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from backend.models import ApprovalStatus, Department, Role, UserRole


PROGRAM_RESOURCES = {
    "AMDPMTA1": ("department",), "AMURMTA1": ("user_account",),
    "AMIQ0003": ("role", "user_role"), "AMLOMTA1": ("location", "warehouse"),
    "AMCUMTA1": ("currency",), "AMPLMTA1": ("product_category",),
    "AMUNMTA1": ("uom", "uom_category"), "AMPTMTA1": ("material",),
    "SLCMMTA1": ("partner",), "PUVDMTA1": ("partner",),
    "PSPSMTA1": ("bom",), "RWROMTA1": ("routing",),
    "SLPRMTA1": ("sales_quote",), "SLSOMTA1": ("sales_order",),
    "SLDNMTA1": ("delivery_order",), "SLCRMTA1": ("sales_return",),
    "PUVQMTA1": ("supplier_quote", "rfq"),
    "MRWPMTA1": ("purchase_requisition",), "PUPRMTA1": ("purchase_requisition",),
    "PUPRMTA3": ("purchase_requisition",), "PUPRMTA2": ("purchase_order",),
    "PUPRMTA4": ("purchase_order",), "PUPOMTA1": ("purchase_order",),
    "PUPOMTA2": ("purchase_order",), "PUGRMTA1": ("goods_receipt",),
    "PUGRMTA2": ("goods_receipt",), "PURTMTA1": ("purchase_return",),
    "PURTMTA2": ("purchase_return",), "ICPCMTA3": ("stock_transfer",),
    "ICAJMTA1": ("stock_count",), "ICAJMTA2": ("stock_count",),
    "ICIQ0009": ("stock_balance", "stock_transaction"),
    "ICIQ0020": ("stock_balance", "stock_transaction"),
    "ICIQ0029": ("stock_balance", "stock_transaction"),
    "SLIQ0022": ("inventory_alert",), "WOIQ0008": ("inventory_alert",),
}

ACTION_FIELDS = {
    "run": "view", "insert": "create", "modify": "change", "delete": "delete",
    "print": "print", "export": "export", "wf_submit": "submit",
    "chk": "approve", "pst": "approve", "view_cost": "view_cost",
}


def permissions_from(rows):
    values = set()
    for row in rows:
        resources = PROGRAM_RESOURCES.get(str(row.get("program", "")).upper(), ())
        for field, action in ACTION_FIELDS.items():
            if row.get(field):
                values.update(f"{resource}.{action}" for resource in resources)
    return sorted(values)


def source_role_code(department, group, username=""):
    value = f"SRC-{department}-{group}" + (f"-{username}" if username else "")
    if len(value) <= 40:
        return value
    return f"SRC-{department}-{hashlib.sha1(value.encode()).hexdigest()[:12]}"


class Command(BaseCommand):
    help = "从原 ERP 只读导入用户、用户组及阶段 1/2 程序权限（不导入密码）"

    def add_arguments(self, parser):
        parser.add_argument("--source-file", type=Path)
        parser.add_argument("--replace", action="store_true")

    def read_source(self, path=None):
        if path:
            return json.loads(path.read_text(encoding="utf-8"))

        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv

        load_dotenv(ENV_FILE)
        with pyodbc.connect(connection_string(), readonly=True) as connection:
            cursor = connection.cursor()

            def rows(sql):
                result = cursor.execute(sql)
                columns = [item[0] for item in result.description]
                return [dict(zip(columns, item)) for item in result.fetchall()]

            permission_columns = ", ".join(
                f"grpd_{field} AS [{field}]" for field in ACTION_FIELDS
            )
            user_permission_columns = ", ".join(
                f"usrp_{field} AS [{field}]" for field in ACTION_FIELDS
            )
            return {
                "departments": rows("""
                    SELECT dp_code AS code, dp_name AS name, dp_manager AS manager,
                           dp_upper_dept AS parent
                    FROM dbo.dp_mstr
                """),
                "groups": rows("SELECT grp_code AS code, grp_desc AS name FROM dbo.grp_mstr"),
                "group_permissions": rows(f"""
                    SELECT grpd_code AS [group], grpd_prog AS program, {permission_columns}
                    FROM dbo.grpd_det
                """),
                "users": rows("""
                    SELECT usr_user AS username, usr_name AS name, usr_group AS [group],
                           usr_dept AS department, usr_lock AS locked, usr_out AS [left]
                    FROM dbo.usr_mstr
                """),
                "user_permissions": rows(f"""
                    SELECT usrp_user AS username, usrp_prog AS program, {user_permission_columns}
                    FROM dbo.usrp_det
                """),
            }

    @transaction.atomic
    def handle(self, *args, **options):
        source = self.read_source(options.get("source_file"))
        if options["replace"]:
            UserRole.objects.filter(role__code__startswith="SRC-").delete()
            Role.objects.filter(code__startswith="SRC-").delete()

        departments = {}
        department_rows = source.get("departments", [])
        for row in department_rows:
            code = str(row.get("code") or "").strip().upper()
            if not code:
                continue
            department, _ = Department.objects.update_or_create(code=code, defaults={
                "name": str(row.get("name") or code).strip(),
                "manager": str(row.get("manager") or "").strip(),
                "status": ApprovalStatus.APPROVED, "approved_by": "legacy-import",
                "approved_at": timezone.now(),
            })
            departments[code] = department
        for row in department_rows:
            code = str(row.get("code") or "").strip().upper()
            parent = departments.get(str(row.get("parent") or "").strip().upper())
            if code in departments and departments[code].parent_id != getattr(parent, "id", None):
                departments[code].parent = parent
                departments[code].save(update_fields=["parent", "updated_at"])

        groups = {str(row.get("code") or "").strip().upper(): str(row.get("name") or "").strip()
                  for row in source.get("groups", [])}
        group_rows = defaultdict(list)
        for row in source.get("group_permissions", []):
            group_rows[str(row.get("group") or "").strip().upper()].append(row)
        direct_rows = defaultdict(dict)
        for row in source.get("user_permissions", []):
            direct_rows[str(row.get("username") or "").strip()][str(row.get("program") or "").strip().upper()] = row

        user_model = get_user_model()
        imported = active = 0
        for row in source.get("users", []):
            username = str(row.get("username") or "").strip()
            if not username:
                continue
            department_code = str(row.get("department") or "SYS").strip().upper() or "SYS"
            department = departments.get(department_code)
            if department is None:
                department, _ = Department.objects.update_or_create(code=department_code, defaults={
                    "name": department_code, "status": ApprovalStatus.APPROVED,
                    "approved_by": "legacy-import", "approved_at": timezone.now(),
                })
                departments[department_code] = department
            group = str(row.get("group") or "").strip().upper()
            effective = {str(item.get("program") or "").strip().upper(): item for item in group_rows.get(group, [])}
            overrides = direct_rows.get(username, {})
            effective.update(overrides)
            permission_values = ["*"] if group == "ADM" else permissions_from(effective.values())
            role_code = source_role_code(department_code, group or "USER", username if overrides else "")
            role, _ = Role.objects.update_or_create(code=role_code, defaults={
                "name": groups.get(group) or group or "原 ERP 用户",
                "department": department, "permissions": permission_values,
                "active": True, "status": ApprovalStatus.APPROVED,
                "approved_by": "legacy-import", "approved_at": timezone.now(),
            })
            is_active = not bool(row.get("locked")) and not bool(row.get("left"))
            user, created = user_model.objects.update_or_create(username=username, defaults={
                "first_name": str(row.get("name") or "")[:150], "is_active": is_active,
            })
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
            UserRole.objects.update_or_create(user=user, role=role, department=department, defaults={
                "is_primary": True, "active": True,
            })
            imported += 1
            active += int(is_active)

        self.stdout.write(self.style.SUCCESS(
            f"已导入 {imported} 个用户（启用 {active}）、{len(departments)} 个部门和 {Role.objects.filter(code__startswith='SRC-').count()} 个源角色"
        ))
