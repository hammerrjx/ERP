from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase
import xlwt

from backend.models import Currency, Location, Material, Partner, ProductCategory, Uom


FILES = {
    "货币": "2.1 -- 货币(AMCUMTA1).xls",
    "库位": "2.2 -- 库位(AMLOMTA1).xls",
    "产品类": "2.3 -- 产品类(AMPLMTA1).xls",
    "计量单位": "2.4 -- 计量单位(AMUNMTA1).xls",
    "物料信息": "2.5 -- 物料信息(AMPTMTA1).xls",
    "客户资料": "3.1 -- 客户资料(SLCMMTA1).xls",
    "供应商资料": "6.1 -- 供应商资料(PUVDMTA1).xls",
}


def write_xls(path, headers, rows):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("导入")
    for column, value in enumerate(headers):
        sheet.write(0, column, value)
    for row_number, row in enumerate(rows, 1):
        for column, header in enumerate(headers):
            sheet.write(row_number, column, row.get(header, ""))
    workbook.save(str(path))


class LegacyMasterDataImportTests(APITestCase):
    def test_command_filters_bad_data_samples_each_category_and_keeps_relations(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)
            write_xls(source / FILES["货币"], ["货币", "名称", "符号"], [
                {"货币": "RMB", "名称": "人民币", "符号": "￥"},
                {"货币": "RIUI", "名称": "错误日元"},
            ])
            write_xls(source / FILES["库位"], ["库位", "名称", "类型", "参与MRP", "可以使用"], [
                {"库位": "FG01", "名称": "成品仓", "类型": "FG", "参与MRP": True, "可以使用": True},
                {"库位": "TEST", "名称": "测试库", "类型": "RAW"},
            ])
            write_xls(source / FILES["计量单位"], ["单位", "描述", "最小包装数量", "最小发出数量"], [
                {"单位": "个", "描述": "个", "最小包装数量": 1, "最小发出数量": 1},
                {"单位": "DR", "描述": "DR"},
            ])
            write_xls(source / FILES["产品类"], ["产品类", "描述", "默认库位", "默认单位", "采制代码"], [
                {"产品类": "A", "描述": "成品", "默认库位": "FG01", "默认单位": "个", "采制代码": "P"},
                {"产品类": "B", "描述": "包装", "默认库位": "FG01", "默认单位": "个", "采制代码": "M"},
                {"产品类": "C", "描述": "无样本类别", "默认库位": "FG01", "默认单位": "个"},
                {"产品类": "E", "描述": "缺省库位类别", "默认单位": "个"},
                {"产品类": "D", "描述": "Ì¼¸Ö½Å±­", "默认库位": "FG01", "默认单位": "个"},
                {"产品类": "TEST", "描述": "测试产品类", "默认库位": "FG01", "默认单位": "个"},
            ])
            write_xls(source / FILES["客户资料"], ["客户代码", "客户简称", "客户全称", "常用币种", "联系人1", "联系电话1"], [
                {"客户代码": "C001", "客户简称": "客户一", "客户全称": "客户一有限公司", "常用币种": "RMB"},
                {"客户代码": "C001", "客户简称": "重复", "客户全称": "重复客户有限公司", "常用币种": "RMB"},
            ])
            write_xls(source / FILES["供应商资料"], ["供应商代码", "全称", "简称", "常用币种", "支付方式", "联系人1", "联系电话1"], [
                {"供应商代码": "S001", "全称": "供应商一有限公司", "简称": "供应商一", "常用币种": "RMB", "支付方式": "月结30天"},
                {"供应商代码": "TEST", "全称": "TEST供应商", "简称": "测试", "支付方式": "现金"},
            ])
            material_headers = ["物料编码", "物料名称", "单位", "产品类", "默认库位", "供应商", "使用中", "审核"]
            material_rows = [
                {"物料编码": f"A-{number}", "物料名称": f"成品{number}", "单位": "个", "产品类": "A", "默认库位": "FG01", "供应商": "S001", "使用中": True, "审核": True}
                for number in range(1, 5)
            ] + [
                {"物料编码": "B-1", "物料名称": "包装一", "单位": "个", "产品类": "B", "默认库位": "FG01", "使用中": True},
                {"物料编码": "E-1", "物料名称": "待分配物料", "单位": "个", "产品类": "E", "默认库位": "", "使用中": True},
                {"物料编码": "TEST-1", "物料名称": "TEST物料", "单位": "个", "产品类": "A", "默认库位": "FG01"},
                {"物料编码": "BAD\nCODE", "物料名称": "格式错误", "单位": "个", "产品类": "B", "默认库位": "FG01"},
            ]
            write_xls(source / FILES["物料信息"], material_headers, material_rows)

            Currency.objects.create(code="OLD", name="旧币种")
            output = StringIO()
            call_command("import_legacy_master_data", source_dir=source, replace=True, stdout=output)
            call_command("import_legacy_master_data", source_dir=source, stdout=StringIO())

        self.assertEqual(set(ProductCategory.objects.values_list("code", flat=True)), {"A", "B", "C", "E"})
        self.assertEqual(Material.objects.filter(category__code="A").count(), 3)
        self.assertEqual(Material.objects.filter(category__code="B").count(), 1)
        self.assertEqual(Material.objects.filter(category__code="C").count(), 0)
        self.assertEqual(Material.objects.get(code="E-1").default_location.code, "LEGACY-UNASSIGNED")
        self.assertEqual(Currency.objects.values_list("code", flat=True).get(), "RMB")
        self.assertEqual(Uom.objects.values_list("name", flat=True).get(), "个")
        self.assertEqual(set(Location.objects.values_list("code", flat=True)), {"FG01", "LEGACY-UNASSIGNED"})
        self.assertEqual(Partner.objects.filter(kind="customer").count(), 1)
        self.assertEqual(Partner.objects.filter(kind="supplier").count(), 1)
        sample = Material.objects.get(code="A-1")
        self.assertEqual(sample.category.code, "A")
        self.assertEqual(sample.uom.name, "个")
        self.assertEqual(sample.default_location.code, "FG01")
        self.assertEqual(sample.default_supplier.code, "S001")

        user = get_user_model().objects.create_superuser("import-check", password="pass")
        self.client.force_authenticate(user)
        response = self.client.get("/api/material/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
