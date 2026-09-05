from unittest.mock import patch

import xlwt
from django.contrib.auth import get_user_model


def write_departments(path, rows):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("部门")
    headers = ["部门代码", "部门名称", "负责人", "备注", "上级部门", "录入人", "录入时间"]
    for column, header in enumerate(headers):
        sheet.write(0, column, header)
    for row_number, row in enumerate(rows, 1):
        for column, header in enumerate(headers):
            sheet.write(row_number, column, row.get(header, ""))
    workbook.save(str(path))


class SourceDatabaseIsolatedMixin:
    """Keep ordinary tests deterministic and leave live source checks explicit."""

    @classmethod
    def setUpClass(cls):
        cls._source_codes_patcher = patch("backend.material_codes._source_codes", return_value=None)
        cls._source_codes_patcher.start()
        try:
            super().setUpClass()
        except Exception:
            cls._source_codes_patcher.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            super().tearDownClass()
        finally:
            cls._source_codes_patcher.stop()


class CoreFlowSupport(SourceDatabaseIsolatedMixin):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("flow-admin", password="pass")
        self.client.force_authenticate(self.user)

    def post(self, resource, payload):
        response = self.client.post(f"/api/{resource}/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def approve(self, resource, record_id):
        submitted = self.client.post(f"/api/{resource}/{record_id}/submit/", {}, format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        approved = self.client.post(f"/api/{resource}/{record_id}/approve/", {}, format="json")
        self.assertEqual(approved.status_code, 200, approved.data)
        return approved.data

    def base_context(self):
        category = self.post("uom-category", {"code": "COUNT", "name": "数量"})
        uom = self.post("uom", {"code": "JIAN", "name": "件", "category": category["id"]})
        location = self.post("location", {"code": "FG01", "name": "成品仓", "location_type": "fg"})
        product_category = self.post("product-category", {"code": "FG", "name": "成品"})
        currency = self.post("currency", {"code": "CNY", "name": "人民币", "symbol": "¥"})
        material = self.post("material", {
            "code": "FG-001", "name": "交付产品", "category": product_category["id"],
            "uom": uom["id"], "default_location": location["id"], "tax_code": "1001",
        })
        customer = self.post("partner", {
            "code": "C001", "name": "客户一", "short_name": "客户一", "kind": "customer",
            "currency": currency["id"],
        })
        self.approve("material", material["id"])
        self.approve("partner", customer["id"])
        return {"uom": uom, "location": location, "currency": currency, "material": material, "customer": customer}
