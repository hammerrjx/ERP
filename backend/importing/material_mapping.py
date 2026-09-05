"""Legacy ``pt_mstr`` spreadsheet normalization for material imports."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


HEADER_ALIASES = {
    "物料编码": "pt_part", "物料名称": "pt_desc1", "英文名称": "pt_desc2",
    "单位": "pt_um", "产品类": "pt_prod_line", "默认库位": "pt_loc",
    "供应商": "pt_vend", "税务编码": "pt_char1", "税务名称": "pt_char2",
    "用途": "pt_char3", "开票名称": "pt_char5", "是否使用中": "pt_status",
    "是否批号控制": "pt_lot_serial", "批号规则": "pt_lot_grp",
}

COMPANY_PREFIX = "coerp"
REQUIRED_COLUMNS = {"pt_desc1", "pt_um", "pt_prod_line", "pt_loc"}


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def json_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def as_bool(value, default=False):
    text = clean_text(value).lower()
    if not text:
        return default
    return text in {"1", "true", "yes", "y", "是", "启用", "使用", "已审核"}


def as_decimal(value, default=Decimal("0")):
    text = clean_text(value)
    if not text:
        return default
    try:
        return Decimal(text)
    except InvalidOperation:
        return default


def as_int(value, default=0):
    try:
        return int(as_decimal(value, Decimal(default)))
    except (ValueError, OverflowError):
        return default


def normalized_headers(headers):
    values = []
    for header in headers:
        name = clean_text(header)
        values.append(HEADER_ALIASES.get(name, name))
    return values


def normalize_row(row):
    """Return the fields owned by the web material model plus conversion data."""
    value = lambda key: clean_text(row.get(key))
    supply_code = value("pt_pm_code").upper()
    return {
        "source_code": value("pt_part"),
        "name": value("pt_desc1"),
        "english_name": value("pt_desc2"),
        "category_code": value("pt_prod_line"),
        "uom_code": value("pt_um"),
        "location_code": value("pt_loc"),
        "supplier_code": value("pt_vend"),
        "tax_code": value("pt_char1"),
        "tax_name": value("pt_char2"),
        "purpose": value("pt_char3"),
        "invoice_name": value("pt_char5"),
        "active": as_bool(row.get("pt_status"), True),
        "supply_method": {"P": "purchase", "M": "manufacture", "S": "outsource"}.get(supply_code, "purchase"),
        "part_type": value("pt_part_type"),
        "product_group": value("pt_group"),
        "drawing_number": value("pt_draw"),
        "specification": value("pt_spec"),
        "default_storage_position": value("pt_loc_pos"),
        "version": value("pt_rev"),
        "customs_code": value("pt_custom_code"),
        "customs_name": value("pt_custom_name"),
        "barcode": value("pt_barcode"),
        "gross_weight_g": str(as_decimal(row.get("pt_gross_weight"))),
        "net_weight_g": str(as_decimal(row.get("pt_net_weight"))),
        "products_per_carton": str(as_decimal(row.get("pt_case_qty"))),
        "scrap_rate": str(as_decimal(row.get("pt_scrp_pct"))),
        "carton_mark": value("pt_ship_mark"),
        "length": str(as_decimal(row.get("pt_carton_l"))),
        "width": str(as_decimal(row.get("pt_carton_w"))),
        "height": str(as_decimal(row.get("pt_carton_h"))),
        "volume": str(as_decimal(row.get("pt_total"))),
        "batch_control": as_bool(row.get("pt_lot_serial")),
        "batch_rule": value("pt_lot_grp"),
        "abc_class": value("pt_abc"),
        "count_cycle_days": as_int(row.get("pt_cyc_int")),
        "warehouse_manager": value("pt_keeper"),
        "shelf_life_days": as_int(row.get("pt_shelf_life")),
        "production_line": value("pt_wo_line"),
        "plan_order": as_bool(row.get("pt_plan_ord"), True),
        "order_strategy": value("pt_ord_pol"),
        "order_qty": str(as_decimal(row.get("pt_ord_qty"))),
        "order_period_days": as_int(row.get("pt_ord_per")),
        "safety_stock_qty": str(as_decimal(row.get("pt_sfty_stk"))),
        "stock_warning_qty": str(as_decimal(row.get("pt_rop"))),
        "buyer": value("pt_buyer"), "planner": value("pt_planner"),
        "non_production": as_bool(row.get("pt_memo_item")),
        "max_stock_qty": str(as_decimal(row.get("pt_max_qty"))),
        "production_lead_days": as_int(row.get("pt_mfg_lt")),
        "purchase_lead_days": as_int(row.get("pt_pur_lt")),
        "quality_control": "required" if as_bool(row.get("pt_insp_rqd")) else "exempt",
        "quality_lead_days": as_int(row.get("pt_gr_lt")),
        "phantom": as_bool(row.get("pt_phantom")),
        "min_purchase_qty": str(as_decimal(row.get("pt_ord_min"))),
        "min_pack_qty": str(as_decimal(row.get("pt_ord_mult"))),
        "min_issue_qty": str(as_decimal(row.get("pt_iss_batch"), Decimal("1"))),
        "roll": as_bool(row.get("pt_roll_iss")),
        "over_receipt_ratio": str(as_decimal(row.get("pt_fgov_per"))),
        "issue_qty_unrestricted": as_bool(row.get("pt_iss_unlimit")),
        "purchase_quote_unrestricted": as_bool(row.get("pt_expu_perm")),
        "sales_quote_unrestricted": as_bool(row.get("pt_exsl_perm")),
        "engineering_reviewer": value("pt_eng"),
        "company_columns": {key.lower(): as_bool(raw) for key, raw in row.items() if key.lower().startswith(COMPANY_PREFIX)},
        "conversions": [
            {"usage": usage, "uom_code": value(column), "business_qty": str(as_decimal(row.get(f"{column}_m"))), "stock_qty": str(as_decimal(row.get(f"{column}_d")))}
            for usage, column in (("engineering", "pt_um_eng"), ("purchase", "pt_um_pur"), ("sales", "pt_um_sl"), ("production", "pt_um_isu"))
            if value(column)
        ],
    }
