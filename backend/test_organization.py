from pathlib import Path
from tempfile import TemporaryDirectory
import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase

from backend.test_support import SourceDatabaseIsolatedMixin, write_departments


class OrganizationApiTests(SourceDatabaseIsolatedMixin, APITestCase):
    def test_department_import_builds_hierarchy_and_operation_roles(self):
        user = get_user_model().objects.create_superuser("root", password="pass")
        self.client.force_authenticate(user)
        with TemporaryDirectory() as directory:
            source = Path(directory) / "1.4 -- 部门(AMDPMTA1).xls"
            write_departments(source, [
                {"部门代码": "PD", "部门名称": "生产部"},
                {"部门代码": "PD1", "部门名称": "生产部(载带)", "上级部门": "PD"},
                {"部门代码": "PO", "部门名称": "执行采购"},
                {"部门代码": "ST", "部门名称": "仓库"},
            ])
            call_command("import_departments", source_file=source)

        departments = self.client.get("/api/department/")
        self.assertEqual(departments.status_code, 200, departments.data)
        by_code = {row["code"]: row for row in departments.data}
        self.assertEqual(by_code["PD1"]["parent"], by_code["PD"]["id"])
        self.assertEqual(by_code["PO"]["status"], "approved")

        roles = self.client.get("/api/role/")
        self.assertEqual(roles.status_code, 200, roles.data)
        by_code = {row["code"]: row for row in roles.data}
        self.assertIn("purchase_order.approve", by_code["PO-MANAGER"]["permissions"])
        self.assertIn("inventory_transfer.create", by_code["ST-OPERATOR"]["permissions"])
        self.assertNotIn("purchase_order.create", by_code["ST-OPERATOR"]["permissions"])

    def test_login_returns_assigned_departments_roles_and_permissions(self):
        admin = get_user_model().objects.create_superuser("root", password="pass")
        operator = get_user_model().objects.create_user("buyer", password="pass")
        self.client.force_authenticate(admin)
        department = self.client.post("/api/department/", {
            "code": "PO", "name": "执行采购", "status": "approved",
        }, format="json").data
        role = self.client.post("/api/role/", {
            "code": "PO-OPERATOR", "name": "执行采购-操作员",
            "department": department["id"],
            "permissions": ["purchase_order.view", "purchase_order.create"],
            "status": "approved",
        }, format="json").data
        assignment = self.client.post("/api/user-role/", {
            "user": operator.id, "role": role["id"], "department": department["id"],
            "is_primary": True,
        }, format="json")
        self.assertEqual(assignment.status_code, 201, assignment.data)

        self.client.force_authenticate(user=None)
        login = self.client.post("/api/auth/login/", {
            "username": "buyer", "password": "pass",
        }, format="json")
        self.assertEqual(login.status_code, 200, login.data)
        self.assertEqual(login.data["departments"], [{"code": "PO", "name": "执行采购"}])
        self.assertEqual(login.data["roles"], ["PO-OPERATOR"])
        self.assertIn("purchase_order.create", login.data["permissions"])

    def test_api_enforces_assigned_role_permissions(self):
        admin = get_user_model().objects.create_superuser("root", password="pass")
        operator = get_user_model().objects.create_user("viewer", password="pass")
        self.client.force_authenticate(admin)
        department = self.client.post("/api/department/", {
            "code": "ST", "name": "仓库", "status": "approved",
        }, format="json").data
        role = self.client.post("/api/role/", {
            "code": "ST-VIEWER", "name": "仓库-查看",
            "department": department["id"], "permissions": ["department.view"],
            "status": "approved",
        }, format="json").data
        self.client.post("/api/user-role/", {
            "user": operator.id, "role": role["id"], "department": department["id"],
            "is_primary": True,
        }, format="json")

        self.client.force_authenticate(operator)
        self.assertEqual(self.client.get("/api/department/").status_code, 200)
        denied = self.client.post("/api/department/", {
            "code": "ST2", "name": "二号仓库",
        }, format="json")
        self.assertEqual(denied.status_code, 403, denied.data)

    def test_legacy_access_import_uses_group_program_permissions_without_passwords(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "legacy-access.json"
            source.write_text(json.dumps({
                "departments": [{"code": "ST", "name": "仓库"}],
                "groups": [{"code": "STOR", "name": "仓库-作业员"}],
                "group_permissions": [{
                    "group": "STOR", "program": "AMLOMTA1", "run": True,
                }],
                "users": [{
                    "username": "ST03", "name": "仓库用户", "group": "STOR",
                    "department": "ST", "locked": False, "left": False,
                }],
                "user_permissions": [],
            }, ensure_ascii=False), encoding="utf-8")
            call_command("import_legacy_access", source_file=source)

        user = get_user_model().objects.get(username="ST03")
        self.assertFalse(user.has_usable_password())
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get("/api/location/").status_code, 200)
        denied = self.client.post("/api/location/", {
            "code": "RM02", "name": "二号原料仓", "location_type": "rm",
        }, format="json")
        self.assertEqual(denied.status_code, 403, denied.data)

    def test_admin_can_create_user_and_department_approval_rule(self):
        admin = get_user_model().objects.create_superuser("root", password="pass")
        self.client.force_authenticate(admin)
        department = self.client.post("/api/department/", {
            "code": "PO", "name": "执行采购", "status": "approved",
        }, format="json").data
        role = self.client.post("/api/role/", {
            "code": "PO-MANAGER", "name": "执行采购-经理",
            "department": department["id"], "permissions": ["purchase_order.approve"],
            "status": "approved",
        }, format="json").data
        account = self.client.post("/api/user-account/", {
            "username": "po-manager", "email": "po@example.com", "password": "Strong-pass-1",
        }, format="json")
        self.assertEqual(account.status_code, 201, account.data)
        self.assertNotIn("password", account.data)
        rule = self.client.post("/api/approval-rule/", {
            "code": "PO-ORDER-01", "document_type": "purchase_order", "sequence": 1,
            "department": department["id"], "role": role["id"], "status": "approved",
        }, format="json")
        self.assertEqual(rule.status_code, 201, rule.data)
        self.assertEqual(rule.data["department"], department["id"])
