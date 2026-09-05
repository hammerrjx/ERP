from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
import xlrd

from backend.models import (
    ApprovalStatus, Currency, CurrencyRate, CustomerMaterial, Location, Material,
    MaterialCompany, MaterialUomConversion, Partner, PartnerBankAccount,
    PartnerCompany, PartnerContact, ProductCategory, SupplierQuote,
    SupplierQuoteLine, Uom, UomCategory,
)


FILE_PREFIXES = {
    "currency": "2.1 -- 货币",
    "location": "2.2 -- 库位",
    "category": "2.3 -- 产品类",
    "uom": "2.4 -- 计量单位",
    "material": "2.5 -- 物料信息",
    "customer": "3.1 -- 客户资料",
    "supplier": "6.1 -- 供应商资料",
}
CODE_PATTERN = re.compile(r"^[A-Za-z0-9\u4e00-\u9fff][A-Za-z0-9\u4e00-\u9fff._/+()#&-]*$")
TEST_CODE_PATTERN = re.compile(r"^(?:TEST|DEMO|SAMPLE)(?:[-_0-9].*)?$", re.IGNORECASE)
TEST_NAMES = {"测试", "测试数据", "测试产品类", "测试供应商", "测试客户", "样例", "示例"}
MOJIBAKE_PATTERN = re.compile(r"[\u0400-\u052f\ufffd]|[\u00a0-\u00bf\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff]")


def text(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def canonical(value):
    return text(value).upper()


def boolean(value, default=False):
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return text(value).lower() in {"1", "true", "yes", "y", "是"}


def decimal_value(value, default="0"):
    try:
        result = Decimal(text(value) or default)
        return result if result >= 0 else Decimal(default)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def integer(value, default=0):
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return default


def excel_date(value, datemode):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return xlrd.xldate_as_datetime(float(value), datemode).date()
    except (TypeError, ValueError, xlrd.XLDateError):
        return None


def is_valid_code(value, maximum):
    value = text(value)
    return bool(value and len(value) <= maximum and CODE_PATTERN.fullmatch(value))


def is_obvious_test(code, name):
    normalized_name = text(name).strip()
    return bool(
        TEST_CODE_PATTERN.match(text(code))
        or normalized_name.upper().startswith(("TEST", "DEMO", "SAMPLE"))
        or normalized_name in TEST_NAMES
    )


def has_mojibake(value):
    return bool(MOJIBAKE_PATTERN.search(text(value)))


def approval_values(row):
    if boolean(row.get("作废")):
        return {"status": ApprovalStatus.VOID}
    if boolean(row.get("审核"), default=True):
        return {
            "status": ApprovalStatus.APPROVED,
            "approved_by": text(row.get("审核人")) or "legacy-import",
            "approved_at": timezone.now(),
        }
    return {"status": ApprovalStatus.DRAFT}


class WorkbookRows:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        book = xlrd.open_workbook(self.path, on_demand=True)
        try:
            sheet = book.sheet_by_index(0)
            headers = [text(sheet.cell_value(0, column)) for column in range(sheet.ncols)]
            for row_number in range(1, sheet.nrows):
                yield dict(zip(headers, (sheet.cell_value(row_number, column) for column in range(sheet.ncols))), __row__=row_number + 1, __datemode__=book.datemode)
        finally:
            book.release_resources()


class LegacyImporter:
    def __init__(self, paths, per_category=3):
        self.paths = paths
        self.per_category = per_category
        self.imported = Counter()
        self.skipped = Counter()
        self.category_samples = Counter()
        self.category_source_rows = Counter()
        self.seen = defaultdict(set)

    def skip(self, resource, reason):
        self.skipped[f"{resource}:{reason}"] += 1

    def unique(self, resource, value):
        key = canonical(value)
        if key in self.seen[resource]:
            self.skip(resource, "重复编码")
            return False
        self.seen[resource].add(key)
        return True

    def find_uom(self, value):
        key = canonical(value)
        return self.uoms_by_code.get(key) or self.uoms_by_name.get(key)

    def import_all(self):
        self.import_currencies()
        self.import_uoms()
        self.import_locations()
        self.import_categories()
        self.import_partners("customer")
        self.import_partners("supplier")
        self.import_materials()
        return self

    def import_currencies(self):
        for row in WorkbookRows(self.paths["currency"]):
            code, name = canonical(row.get("货币")), text(row.get("名称"))
            if not re.fullmatch(r"[A-Z]{3}", code) or not name or len(name) > 40:
                self.skip("货币", "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique("currency", code):
                self.skip("货币", "测试数据") if is_obvious_test(code, name) else None
                continue
            Currency.objects.update_or_create(code=code, defaults={"name": name, "symbol": text(row.get("符号"))[:8], "status": ApprovalStatus.APPROVED, "created_by": text(row.get("录入人")) or "legacy-import"})
            self.imported["货币"] += 1
        self.currencies = {canonical(item.code): item for item in Currency.objects.all()}

    def uom_category_code(self, code, name):
        value = f"{canonical(code)} {text(name)}"
        if any(token in value for token in ("KG", "公斤", "千克", "克", "吨")):
            return "WEIGHT", "重量"
        if any(token in value for token in ("M2", "平方米", "平米")):
            return "AREA", "面积"
        if any(token in value for token in ("M3", "L", "公升", "毫升", "升", "加仑")):
            return "VOLUME", "体积"
        if any(token in value for token in ("MM", " M ", "毫米", "米")):
            return "LENGTH", "长度"
        return "COUNT", "数量"

    def import_uoms(self):
        names = set()
        for row in WorkbookRows(self.paths["uom"]):
            code, name = text(row.get("单位")), text(row.get("描述"))
            if not is_valid_code(code, 16) or not name or len(name) > 32 or name.isascii():
                self.skip("计量单位", "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique("uom", code):
                self.skip("计量单位", "测试数据") if is_obvious_test(code, name) else None
                continue
            if canonical(name) in names:
                self.skip("计量单位", "重复名称")
                continue
            names.add(canonical(name))
            category_code, category_name = self.uom_category_code(code, name)
            category, _ = UomCategory.objects.update_or_create(code=category_code, defaults={"name": category_name, "status": ApprovalStatus.APPROVED, "created_by": "legacy-import"})
            Uom.objects.update_or_create(code=code, defaults={"name": name, "description": name, "category": category, "factor": 1, "min_pack_qty": decimal_value(row.get("最小包装数量")), "min_ship_qty": decimal_value(row.get("最小发出数量")), "status": ApprovalStatus.APPROVED, "created_by": text(row.get("录入人")) or "legacy-import"})
            self.imported["计量单位"] += 1
        self.uoms_by_code = {canonical(item.code): item for item in Uom.objects.all()}
        self.uoms_by_name = {canonical(item.name): item for item in Uom.objects.all()}

    def import_locations(self):
        type_map = {"FG": "fg", "RAW": "rm", "RM": "rm", "WIP": "wip", "NG": "ng", "VIRTUAL": "virtual"}
        for row in WorkbookRows(self.paths["location"]):
            code, name = text(row.get("库位")), text(row.get("名称"))
            if not is_valid_code(code, 32) or not name or len(name) > 120:
                self.skip("库位", "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique("location", code):
                self.skip("库位", "测试数据") if is_obvious_test(code, name) else None
                continue
            Location.objects.update_or_create(code=code, defaults={
                "name": name, "location_type": type_map.get(canonical(row.get("类型")), "warehouse"),
                "manager": text(row.get("仓管员"))[:64], "participate_mrp": boolean(row.get("参与MRP"), True),
                "usable": boolean(row.get("可以使用"), True), "allow_negative": boolean(row.get("可以负数")),
                "quarantine_return": boolean(row.get("检验不良退货暂存仓")), "disabled_for_inventory": boolean(row.get("禁用库位")),
                "approval_permissions": text(row.get("审核权限"))[:240], "storage_account": text(row.get("存货会计科目"))[:32],
                "sales_income_account": text(row.get("主营业务收入科目"))[:32], "shipped_goods_account": text(row.get("发出商品成本科目"))[:32],
                "sales_cost_account": text(row.get("主营业务成本科目"))[:32],
                "material_account": text(row.get("生产成本/直接材料科目"))[:32], "outsource_material_account": text(row.get("委托加工物资科目"))[:32],
                "status": ApprovalStatus.APPROVED, "created_by": text(row.get("录入人")) or "legacy-import",
            })
            self.imported["库位"] += 1
        self.locations = {canonical(item.code): item for item in Location.objects.all()}
        self.unassigned_location = None

    def import_categories(self):
        supply_map = {"P": "purchase", "M": "production", "S": "outsource"}
        for row in WorkbookRows(self.paths["category"]):
            code, name = text(row.get("产品类")), text(row.get("描述"))
            if not is_valid_code(code, 32) or not name or len(name) > 80 or has_mojibake(name):
                self.skip("产品类", "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique("category", code):
                self.skip("产品类", "测试数据") if is_obvious_test(code, name) else None
                continue
            default_uom = self.find_uom(row.get("默认单位"))
            default_location = self.locations.get(canonical(row.get("默认库位")))
            ProductCategory.objects.update_or_create(code=code, defaults={
                "name": name, "description": name, "default_uom": default_uom, "default_location": default_location,
                "code_prefix": code[:16], "supply_method": supply_map.get(canonical(row.get("采制代码")), "purchase"),
                "part_type": text(row.get("零件类型"))[:80], "product_group": text(row.get("产品组"))[:80], "buyer": text(row.get("采购员"))[:64],
                "quality_control": "required" if boolean(row.get("质检")) else "exempt", "phantom": boolean(row.get("虚项")),
                "main_production_plan": boolean(row.get("主生产计划")), "issue_material": boolean(row.get("发料")), "roll": boolean(row.get("卷发")),
                "key_material": boolean(row.get("关键物料")), "non_stock_material": boolean(row.get("非库存物料")),
                "batch_control": boolean(row.get("批号控制")), "batch_rule": text(row.get("批号规则"))[:80],
                "material_view_permissions": text(row.get("物料查看权限"))[:240] or "*", "material_edit_permissions": text(row.get("物料编辑权限"))[:240] or "*",
                "material_delete_permissions": text(row.get("物料删除权限"))[:240] or "*", "material_approval_permissions": text(row.get("物料审核/反审核权限"))[:240] or "*",
                "inventory_account": text(row.get("存货会计科目"))[:32], "business_income_account": text(row.get("主营业务收入科目"))[:32],
                "outsource_material_account": text(row.get("委托加工物资科目"))[:32], "production_cost_account": text(row.get("生产成本/直接材料科目"))[:32],
                "business_cost_account": text(row.get("主营业务成本科目"))[:32], "material_code_rule": text(row.get("物料编码规则"))[:80],
                "print_permission": text(row.get("可使用权限"))[:80],
                "status": ApprovalStatus.APPROVED, "created_by": text(row.get("录入人")) or "legacy-import",
            })
            self.imported["产品类"] += 1
        self.categories = {canonical(item.code): item for item in ProductCategory.objects.all()}

    def import_partners(self, kind):
        resource = "客户" if kind == "customer" else "供应商"
        code_field, name_field, short_field = (("客户代码", "客户全称", "客户简称") if kind == "customer" else ("供应商代码", "全称", "简称"))
        for row in WorkbookRows(self.paths[kind]):
            code, name, short_name = text(row.get(code_field)), text(row.get(name_field)), text(row.get(short_field))
            if not is_valid_code(code, 40) or len(name) < 2 or len(name) > 200 or not short_name or len(short_name) > 80 or has_mojibake(name) or has_mojibake(short_name):
                self.skip(resource, "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique(kind, code):
                self.skip(resource, "测试数据") if is_obvious_test(code, name) else None
                continue
            currency = self.currencies.get(canonical(row.get("常用币种")))
            values = {
                "name": name, "short_name": short_name, "kind": kind, "currency": currency,
                "address": text(row.get("地址"))[:240], "invoice_address": text(row.get("发票地址"))[:240],
                "delivery_address": text(row.get("送货地址"))[:240], "operating_address": text(row.get("经营地址"))[:240],
                "notes": text(row.get("备注") or row.get("客户备注") or row.get("供应商备注"))[:255],
                "website": text(row.get("网址") or row.get("公司网址"))[:200] if text(row.get("网址") or row.get("公司网址")).startswith(("http://", "https://")) else "",
                "currency": currency, "payment_method": text(row.get("支付方式"))[:80], "payment_terms": text(row.get("支付方式名称") or row.get("付款条件"))[:80],
                "quote_method": text(row.get("报价方式"))[:40], "tax_calculation_method": text(row.get("课税类别"))[:80],
                "invoice_type": text(row.get("发票类型"))[:40], "tax_rate": decimal_value(row.get("增值税率%")),
                "discount_rate": decimal_value(row.get("折扣率%"), "100"), "tax_number": text(row.get("税号"))[:32],
                "legal_person": text(row.get("法人"))[:80], "registered_capital": decimal_value(row.get("注册资金(万元)")),
                "annual_revenue": decimal_value(row.get("营业额(万元)") or row.get("年营业额(万元)")), "employee_count": integer(row.get("员工人数")),
                "opening_date": excel_date(row.get("开业日期"), row["__datemode__"]), "category": text(row.get("类别"))[:40],
                "region": text(row.get("地区"))[:80], "parent_company": text(row.get("客户总公司"))[:160], "sales_person": text(row.get("业务员名称"))[:64],
                "copper_origin": text(row.get("铜产地"))[:80], "copper_currency": text(row.get("铜币种"))[:40],
                "payment_bank": text(row.get("付款银行"))[:120], "bank_account": text(row.get("银行帐号"))[:80],
                "monthly_close_day": min(integer(row.get("月结日")), 31), "credit_enabled": not boolean(row.get("信用冻结")),
                "credit_limit_1": decimal_value(row.get("一级额度")), "credit_limit_2": decimal_value(row.get("二级额度")),
                "overdue_days_1": integer(row.get("超期天数1")), "overdue_days_2": integer(row.get("超期天数2")),
                "service_score": decimal_value(row.get("服务评分")), "buyer": text(row.get("采购员"))[:64] if kind == "supplier" else "",
                "internal_company": boolean(row.get("是否内部公司")), "supplier_type": text(row.get("类型"))[:32] if kind == "supplier" else "", "payment_hold": boolean(row.get("暂停付款")),
                "round_order_quantity_for_tier_price": boolean(row.get("按订单按合计数量考虑数量级单价") or row.get("按订单合计数量考虑数量级单价")),
                "three_certificates": boolean(row.get("三证合一")), "business_license": boolean(row.get("开户许可证")),
                "is_confirmed": boolean(row.get("确认")), "created_by": text(row.get("录入人")) or "legacy-import", **approval_values(row),
            }
            partner, _ = Partner.objects.update_or_create(code=code, defaults=values)
            contacts = 4 if kind == "customer" else 2
            for number in range(1, contacts + 1):
                contact_name = text(row.get(f"联系人{number}"))
                if contact_name and len(contact_name) <= 80:
                    PartnerContact.objects.update_or_create(partner=partner, name=contact_name, defaults={
                        "position": text(row.get(f"职位{number}"))[:80], "phone": text(row.get(f"联系电话{number}"))[:40],
                        "fax": text(row.get(f"传真{number}"))[:40], "email": text(row.get(f"电子邮箱{number}"))[:254], "is_primary": number == 1,
                    })
            if partner.bank_account:
                PartnerBankAccount.objects.update_or_create(partner=partner, account_number=partner.bank_account, defaults={"bank_name": partner.payment_bank, "account_name": partner.name, "is_default": True})
            self.imported[resource] += 1
        self.partners = {canonical(item.code): item for item in Partner.objects.all()}

    def import_materials(self):
        supply_map = {"P": "purchase", "M": "production", "S": "outsource"}
        usage_fields = {
            "engineering": ("工程单位", "工程单位转换率(分子)", "工程单位转换率(分母)"),
            "purchase": ("采购单位", "采购单位转换率(分子)", "采购单位转换率(分母)"),
            "sales": ("销售单位", "销售单位转换率(分子)", "销售单位转换率(分母)"),
            "production": ("生产领用单位", "生产领用单位转换率(分子)", "生产领用单位转换率(分母)"),
        }
        for row in WorkbookRows(self.paths["material"]):
            category_key = canonical(row.get("产品类"))
            category = self.categories.get(category_key)
            if not category:
                self.skip("物料", "产品类缺失")
                continue
            self.category_source_rows[category_key] += 1
            if self.category_samples[category_key] >= self.per_category:
                self.skip("物料", "超过每类样本上限")
                continue
            code, name = text(row.get("物料编码")), text(row.get("物料名称"))
            if not is_valid_code(code, 40) or not name or len(name) > 160 or has_mojibake(name):
                self.skip("物料", "格式不匹配")
                continue
            if is_obvious_test(code, name) or not self.unique("material", code):
                self.skip("物料", "测试数据") if is_obvious_test(code, name) else None
                continue
            uom = self.find_uom(row.get("单位"))
            source_location = canonical(row.get("默认库位"))
            location = self.locations.get(source_location) or category.default_location
            if not location and not source_location:
                if self.unassigned_location is None:
                    self.unassigned_location, _ = Location.objects.get_or_create(
                        code="LEGACY-UNASSIGNED",
                        defaults={
                            "name": "原ERP待分配库位", "location_type": "virtual",
                            "participate_mrp": False, "usable": False,
                            "status": ApprovalStatus.APPROVED, "created_by": "legacy-import",
                        },
                    )
                location = self.unassigned_location
            if not uom or not location:
                self.skip("物料", "单位或库位缺失")
                continue
            supplier = self.partners.get(canonical(row.get("供应商")))
            if supplier and supplier.kind not in {"supplier", "both"}:
                supplier = None
            values = {
                "name": name, "english_name": text(row.get("英文名称"))[:160], "category": category, "uom": uom,
                "customs_code": text(row.get("海关物料编码"))[:40], "customs_name": text(row.get("海关物料名称"))[:160],
                "barcode": text(row.get("条码"))[:80], "tax_code": "", "specification": text(row.get("规格型号")),
                "join_date": excel_date(row.get("加入日期"), row["__datemode__"]), "part_type": text(row.get("零件类型"))[:80],
                "product_group": text(row.get("产品组"))[:80], "drawing_number": text(row.get("绘图号"))[:80], "version": text(row.get("版本号"))[:40],
                "active": boolean(row.get("使用中"), True), "gross_weight_g": decimal_value(row.get("毛重(克)")), "net_weight_g": decimal_value(row.get("净重(克)")),
                "products_per_carton": decimal_value(row.get("每箱产品数")), "scrap_rate": decimal_value(row.get("损耗率")), "carton_mark": text(row.get("箱唛")),
                "length": decimal_value(row.get("长")), "width": decimal_value(row.get("宽")), "height": decimal_value(row.get("高")), "volume": decimal_value(row.get("体积")),
                "default_location": location, "default_storage_position": text(row.get("默认储存位置"))[:80], "abc_class": text(row.get("ABC分类"))[:8],
                "count_cycle_days": integer(row.get("盘点周期(天)")), "batch_control": boolean(row.get("批号控制")), "batch_rule": text(row.get("批号规则"))[:80],
                "warehouse_manager": text(row.get("仓管员"))[:64], "shelf_life_days": integer(row.get("保质期")), "plan_order": boolean(row.get("计划订单"), True),
                "order_strategy": text(row.get("订购策略"))[:40], "order_qty": decimal_value(row.get("订购数量")), "order_period_days": integer(row.get("订购期间")),
                "safety_stock_qty": decimal_value(row.get("安全库存数量")), "stock_warning_qty": decimal_value(row.get("库存警戒数量")),
                "buyer": text(row.get("采购员"))[:64], "planner": text(row.get("计划员"))[:64], "non_production": boolean(row.get("非生产物料")),
                "max_stock_qty": decimal_value(row.get("最大库存数量")), "default_supplier": supplier, "supply_method": supply_map.get(canonical(row.get("采制代码")), "purchase"),
                "production_lead_days": integer(row.get("生产提前期(天)")), "purchase_lead_days": integer(row.get("采购提前期(天)")),
                "quality_control": "required" if boolean(row.get("质检")) else "exempt", "quality_lead_days": integer(row.get("质检提前期(天)")),
                "phantom": boolean(row.get("虚项")), "min_purchase_qty": decimal_value(row.get("最小订购数量")), "min_pack_qty": decimal_value(row.get("最小包装数量")),
                "min_issue_qty": decimal_value(row.get("最小发出数量"), "1"), "roll": boolean(row.get("卷发")), "over_receipt_ratio": decimal_value(row.get("超入库比例%")),
                "issue_qty_unrestricted": boolean(row.get("不限制领料数量")), "purchase_quote_unrestricted": boolean(row.get("不受采购报价权限限制")),
                "sales_quote_unrestricted": boolean(row.get("不受销售报价权限限制")), "outsource_surplus_excluded_from_mrp": boolean(row.get("外协余料仓库存不参与MRP")),
                "default_operation": integer(row.get("默认工序")), "scheduling_class": text(row.get("排程分类"))[:80], "low_level_code": integer(row.get("低层代码")),
                "engineering_reviewer": text(row.get("审核工程师"))[:64], "receipt_consume_mode": text(row.get("生产入库扣料模式"))[:40],
                "outsource_receipt_consume_mode": text(row.get("外协收货扣料模式"))[:40], "production_line": text(row.get("生产线"))[:80],
                "created_by": text(row.get("录入人")) or "legacy-import", **approval_values(row),
            }
            material, _ = Material.objects.update_or_create(code=code, defaults=values)
            for usage, (unit_field, numerator_field, denominator_field) in usage_fields.items():
                business_uom = self.find_uom(row.get(unit_field))
                numerator = decimal_value(row.get(numerator_field))
                denominator = decimal_value(row.get(denominator_field))
                if business_uom and business_uom.category_id == uom.category_id and numerator > 0 and denominator > 0:
                    MaterialUomConversion.objects.update_or_create(material=material, usage=usage, defaults={"business_uom": business_uom, "business_qty": numerator, "stock_qty": denominator})
            self.category_samples[category_key] += 1
            self.imported["物料"] += 1

    def report(self):
        lines = ["# 原 ERP 基础资料导入报告", "", "## 导入数量", ""]
        for key, value in sorted(self.imported.items()):
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## 跳过数量", ""])
        for key, value in sorted(self.skipped.items()):
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## 产品类物料覆盖", "", "| 产品类 | 原始物料行数 | 导入样本数 |", "| --- | ---: | ---: |"])
        for category in ProductCategory.objects.order_by("code"):
            lines.append(f"| {category.code} {category.name} | {self.category_source_rows[canonical(category.code)]} | {Material.objects.filter(category=category).count()} |")
        return "\n".join(lines) + "\n"


class Command(BaseCommand):
    help = "从原 ERP 导出的 Excel 文件导入关联基础资料"

    def add_arguments(self, parser):
        parser.add_argument("--source-dir", required=True, type=Path)
        parser.add_argument("--per-category", type=int, default=3)
        parser.add_argument("--report", type=Path, default=Path("docs/legacy-import-report.md"))
        parser.add_argument("--replace", action="store_true", help="清空现有基础资料后重新导入")

    def handle(self, *args, **options):
        source_dir = options["source_dir"]
        paths = {}
        for resource, prefix in FILE_PREFIXES.items():
            matches = list(source_dir.glob(f"{prefix}*.xls"))
            if len(matches) != 1:
                raise CommandError(f"{prefix}: 应找到 1 个文件，实际 {len(matches)} 个")
            paths[resource] = matches[0]
        if options["per_category"] < 1:
            raise CommandError("--per-category 必须大于 0")
        with transaction.atomic():
            if options["replace"]:
                for model in (
                    SupplierQuoteLine, SupplierQuote, CustomerMaterial,
                    MaterialUomConversion, MaterialCompany, Material,
                    PartnerBankAccount, PartnerContact, PartnerCompany, Partner,
                    ProductCategory, Location, Uom, UomCategory, CurrencyRate, Currency,
                ):
                    model.objects.all().delete()
            importer = LegacyImporter(paths, options["per_category"]).import_all()
        report_path = options["report"]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(importer.report(), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"导入完成：{dict(importer.imported)}"))
        self.stdout.write(f"跳过：{dict(importer.skipped)}")
        self.stdout.write(f"报告：{report_path.resolve()}")
