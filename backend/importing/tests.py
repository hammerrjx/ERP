from io import BytesIO
from unittest.mock import patch

import xlwt
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from backend.models import Company, Location, ProductCategory, TaxCode, Uom, UomCategory
from backend.importing.models import ErpImportProfile
from backend.test_support import SourceDatabaseIsolatedMixin


HEADERS = ["pt_part", "pt_desc1", "pt_um", "pt_prod_line", "pt_loc", "pt_char1"]
TITLES = ["物料编码", "物料名称", "单位", "产品类", "默认库位", "税务编码"]


def workbook(rows):
    book = xlwt.Workbook()
    sheet = book.add_sheet("pt_mstr")
    for column, value in enumerate(HEADERS): sheet.write(0, column, value)
    for column, value in enumerate(TITLES): sheet.write(1, column, value)
    for row_number, row in enumerate(rows, 2):
        for column, value in enumerate(row): sheet.write(row_number, column, value)
    output = BytesIO(); book.save(output)
    return SimpleUploadedFile("materials.xls", output.getvalue(), "application/vnd.ms-excel")


class MaterialImportTests(SourceDatabaseIsolatedMixin, APITestCase):
    def setUp(self):
        category = UomCategory.objects.create(code="COUNT", name="数量")
        self.uom = Uom.objects.create(code="EA", name="个", category=category)
        self.category = ProductCategory.objects.create(code="PML", name="产品类", code_prefix="PML", default_uom=self.uom)
        self.location = Location.objects.create(code="FG01", name="成品库")
        TaxCode.objects.create(code="TAX", name="税码")
        self.company = Company.objects.create(code="DGYZX1", name="单主体公司")
        ErpImportProfile.objects.create(name="coerp_dgyzx1 导入", company=self.company)
        self.user = get_user_model().objects.create_superuser("importer", password="pass")
        self.client.force_authenticate(self.user)

    @patch("backend.material_codes._source_codes", return_value=["PML-000406"])
    def test_preview_skips_template_titles_and_allocates_codes(self, _source_codes):
        response = self.client.post("/api/material-import/preview/", {"file": workbook([
            ["", "物料一", "EA", "PML", "FG01", "TAX"],
            ["", "物料二", "EA", "PML", "FG01", "TAX"],
        ])}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["total_rows"], 2)
        self.assertEqual([row["allocated_code"] for row in response.data["rows"]], ["PML-000407", "PML-000408"])

    @patch("backend.material_codes._source_codes", return_value=[])
    def test_confirm_creates_materials_only_after_successful_preview(self, _source_codes):
        response = self.client.post("/api/material-import/preview/", {"file": workbook([
            ["", "物料一", "EA", "PML", "FG01", "TAX"],
        ])}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["valid_rows"], 1)
        response = self.client.post(f"/api/material-import/{response.data['id']}/confirm/", {}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["imported_rows"], 1)
        from backend.models import Material, MaterialCompany
        material = Material.objects.get()
        self.assertEqual(MaterialCompany.objects.filter(material=material, company=self.company).count(), 1)

    def test_non_default_company_column_is_rejected(self):
        headers = HEADERS + ["coerp_other"]
        original = (HEADERS[:], TITLES[:])
        try:
            HEADERS[:] = headers
            TITLES[:] = TITLES + ["其他主体"]
            response = self.client.post("/api/material-import/preview/", {"file": workbook([["", "物料一", "EA", "PML", "FG01", "TAX", "Y"]])}, format="multipart")
            self.assertEqual(response.data["error_rows"], 1)
            self.assertIn("首期仅支持主体列", response.data["rows"][0]["errors"][0])
        finally:
            HEADERS[:], TITLES[:] = original

    def test_single_company_creates_default_import_binding(self):
        ErpImportProfile.objects.all().delete()
        response = self.client.post("/api/material-import/preview/", {"file": workbook([["", "物料一", "EA", "PML", "FG01", "TAX"]])}, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["import_profile"]["company_code"], self.company.code)

    def test_multiple_companies_require_an_explicit_default_import_binding(self):
        ErpImportProfile.objects.all().delete()
        Company.objects.create(code="DGYZX2", name="第二主体")
        response = self.client.post(
            "/api/material-import/preview/",
            {"file": workbook([["", "物料一", "EA", "PML", "FG01", "TAX"]])},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertIn("唯一的启用默认导入主体", response.data["detail"])
