"""Trade/customer-order MRP snapshots and calculation service."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from datetime import date, timedelta
import hashlib
import json

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import connection, models, transaction
from django.db.models import Q
from django.utils import timezone

from .base import ApprovalStatus
from .inventory import StockBalance
from .inventory_reports import InventoryReportBatch, InventoryReportLookup
from .master_data import Material
from .purchase import PurchaseOrder, PurchaseOrderLine, PurchaseRequisition, PurchaseRequisitionLine, PurchaseRequisitionSource
from .sales import SalesOrderLine

ZERO = Decimal("0")


class TradeMrpSiteParameter(models.Model):
    """ptp2_det(site, part): null overrides fall back to the material master."""
    site = models.CharField(max_length=20)
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="trade_mrp_site_parameters")
    safety_stock_qty = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True)
    min_purchase_qty = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True)
    min_pack_qty = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True)
    source_profile = models.CharField(max_length=40, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("site", "material"), name="uniq_trade_mrp_site_parameter")]


class TradeMrpRun(models.Model):
    site = models.CharField(max_length=20, default="1000")
    mode = models.CharField(max_length=20, default="net")
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, default="preview")
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    source_fingerprint = models.CharField(max_length=64, blank=True)
    confirmation_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at", "-id")


class TradeMrpResult(models.Model):
    run = models.ForeignKey(TradeMrpRun, on_delete=models.CASCADE, related_name="results")
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="trade_mrp_results")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="trade_mrp_results")
    demand_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    available_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    on_order_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    approved_requisition_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    pending_requisition_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    safety_stock_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    shortage_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    suggested_qty = models.DecimalField(max_digits=19, decimal_places=8, default=ZERO)
    adjusted_qty = models.DecimalField(max_digits=19, decimal_places=8, null=True, blank=True)
    needed_date = models.DateField(null=True, blank=True)
    source_snapshot = models.JSONField(default=list, blank=True)
    calculation_snapshot = models.JSONField(default=dict, blank=True)
    requisition = models.ForeignKey(PurchaseRequisition, null=True, blank=True, on_delete=models.SET_NULL, related_name="trade_mrp_results")

    class Meta:
        ordering = ("material__code", "id")
        constraints = [models.UniqueConstraint(fields=("run", "material"), name="uniq_trade_mrp_run_material")]


def _ceil_to(value, unit):
    value, unit = Decimal(value), Decimal(unit or 0)
    if unit <= 0:
        return value
    return (value / unit).to_integral_value(rounding=ROUND_CEILING) * unit


def _remaining_source(line):
    # MRWPMT01 mode 2 clamps formal and spare balances independently.
    return max(line.quantity - line.delivered_quantity, ZERO) + max(line.spare_quantity - line.delivered_spare_quantity, ZERO)


def _unit_issue(row, material, label):
    m, d = getattr(row, "uom_rate_m", Decimal(1)), getattr(row, "uom_rate_d", Decimal(1))
    inventory = getattr(row, "inventory_uom_id", None)
    if m <= 0 or d <= 0 or m != d or (inventory and inventory != material.uom_id):
        return f"{label}：单位换算不是有效1:1，暂不能生成"
    if row.uom_id != material.uom_id and not hasattr(row, "uom_rate_m"):
        return f"{label}：数量单位与物料库存单位不一致，暂不能生成"
    return None


def _build_results(site, filters):
    # Filters select source rows, never trim the same-material demand pool.
    base = SalesOrderLine.objects.select_related("order__customer", "customer_material", "material__category", "uom", "material__uom").filter(
        order__site=site, order__status=ApprovalStatus.APPROVED, line_status="normal"
    ).filter(Q(order__customer__consignment=False) | Q(order__consignment=True))
    qs = base
    for key, field in (("order", "order__number"), ("line", "line_number"),
                       ("order_date", "order__order_date"), ("material", "material__code"),
                       ("category", "material__category__code")):
        for suffix, lookup in (("from", "gte"), ("to", "lte")):
            value = filters.get(f"{key}_{suffix}")
            if value not in (None, ""):
                qs = qs.filter(**{f"{field}__{lookup}": value})
    for key in ("planner", "buyer"):
        if filters.get(key):
            qs = qs.filter(**{f"material__{key}__iexact": filters[key]})
    if filters.get("order"):
        qs = qs.filter(order__number__icontains=filters["order"])
    if filters.get("material"):
        qs = qs.filter(Q(material__code__icontains=filters["material"]) | Q(material__name__icontains=filters["material"]))
    if filters.get("customer"):
        qs = qs.filter(Q(order__customer__code__icontains=filters["customer"]) | Q(order__customer__name__icontains=filters["customer"]))
    if filters.get("customer_po"):
        qs = qs.filter(order__customer_po__icontains=filters["customer_po"])
    if filters.get("customer_material_id"):
        # The chosen composite customer/material/external-code identity is an exact FK.
        qs = qs.filter(customer_material_id=filters["customer_material_id"])
    if filters.get("date_from"):
        qs = qs.filter(promised_date__gte=filters["date_from"])
    if filters.get("date_to"):
        qs = qs.filter(promised_date__lte=filters["date_to"])

    demand = defaultdict(list)
    for line in qs.order_by("promised_date", "order__number", "line_number"):
        qty = _remaining_source(line)
        if qty > 0:
            demand[line.material_id].append({"line": line, "qty": qty})
    global_rows, stocks, purchases, requisitions, pending_transfers = (defaultdict(list) for _ in range(5))
    for row in base.filter(material_id__in=demand).order_by("pk"):
        global_rows[row.material_id].append(row)
    for row in StockBalance.objects.select_related("location").filter(material_id__in=demand).filter(
        Q(location__source_site=site) | Q(location__source_site="")
    ).order_by("pk"):
        stocks[row.material_id].append(row)
    # The existing import/transfer path maps ordinary stock purchases to PRODUCTION.
    for row in PurchaseOrderLine.objects.select_related("order").filter(
        material_id__in=demand, order__site=site, order__status=ApprovalStatus.APPROVED,
        order__purchase_type=PurchaseOrder.PurchaseType.PRODUCTION, line_status=""
    ).order_by("pk"):
        purchases[row.material_id].append(row)
    for row in PurchaseOrderLine.objects.select_related("order").filter(
        material_id__in=demand, order__site=site, line_status="",
        order__status__in=[ApprovalStatus.DRAFT, ApprovalStatus.PENDING, ApprovalStatus.REJECTED]
    ).filter(Q(source_requisition_line__isnull=False) | Q(allocations__requisition_line__isnull=False)).distinct():
        pending_transfers[row.material_id].append(row)
    for row in PurchaseRequisitionLine.objects.select_related("requisition").filter(
        material_id__in=demand, requisition__site=site, requisition__requisition_type="P", line_status="",
        requisition__status__in=[ApprovalStatus.APPROVED, ApprovalStatus.DRAFT, ApprovalStatus.PENDING]
    ).filter(
        Q(requisition__status=ApprovalStatus.APPROVED) |
        Q(source_kind="trade_mrp", requisition__source_profile="trade_mrp")
    ).order_by("pk"):
        requisitions[row.material_id].append(row)

    output = []
    active_local_batch = InventoryReportBatch.objects.filter(active=True, source='local').first()
    sync_unit_conflicts = {r['local_id'] for r in (active_local_batch.manifest.get('trade_sync', {}).get('unit_conflicts', []) if active_local_batch else [])}
    sync_local_conflicts = set(active_local_batch.manifest.get('trade_sync', {}).get('conflict_material_ids', []) if active_local_batch else [])
    local_scope = active_local_batch.manifest.get('trade_mrp_local_test', {}) if active_local_batch else {}
    # Reuse the inventory module's gend_det dictionary; never borrow its stock balances.
    dictionary_batch = InventoryReportBatch.objects.filter(active=True).order_by('-created_at', '-pk').first()
    if dictionary_batch and dictionary_batch.source == 'local':
        dictionary_batch = InventoryReportBatch.objects.filter(
            pk=dictionary_batch.manifest.get('baseline_batch_id'), source='coerp_dgyzx1').first()
    if dictionary_batch and dictionary_batch.source != 'coerp_dgyzx1':
        dictionary_batch = None
    dictionary = {(entry.kind, entry.code): entry.name for entry in
        InventoryReportLookup.objects.filter(batch=dictionary_batch, kind__in=['group', 'part_type'], site='')} if dictionary_batch else {}
    site_parameters = {p.material_id: p for p in TradeMrpSiteParameter.objects.filter(site=site, material_id__in=demand)}
    for material_id, rows in sorted(demand.items()):
        material = rows[0]["line"].material
        parameter = site_parameters.get(material_id)
        parameters = {key: (getattr(parameter, key) if parameter is not None and getattr(parameter, key) is not None else getattr(material, key))
            for key in ("safety_stock_qty", "min_purchase_qty", "min_pack_qty")}
        minimum, package = parameters["min_purchase_qty"], parameters["min_pack_qty"]
        issues, supply, all_demand = [], [], []
        from backend.trade_mrp_readiness import material_scope_issues
        issues.extend(material_scope_issues(material, local_scope))
        if material_id in sync_unit_conflicts:
            issues.append('源物料与本地同编码的库存单位冲突，该物料未同步，暂不能生成')
        elif material_id in sync_local_conflicts:
            issues.append('该物料存在保留的本地修改与源数据差异，请先核对同步冲突，暂不能生成')
        if material.quality_control not in {"required", "exempt"} or (material.quality_control == "required") != material.inspection_required:
            issues.append("物料质检设置与收货需检标记不一致，请先核对源物料质检属性")
        if material.inspection_required:
            issues.append("物料需检，质量放行流程尚未验收，本期阻止生成")
        if not material.active or material.status != ApprovalStatus.APPROVED:
            issues.append("物料未审核或已停用")
        if material.no_stock_movement or material.non_production or material.supply_method != "purchase":
            issues.append("非普通库存采购物料，本期未开放制造或外协物料直接采购")
        if any(value is not None and value < 0 for value in parameters.values()):
            issues.append("安全库存、最小采购量及包装量不能为负数")
        for row in pending_transfers[material_id]:
            issues.append(f"采购{row.order.number}/{row.line_number}已占用请购但尚未审核，请先处理转采单据后重算")
        available = unavailable = on_order = approved = pending_qty = total_demand = ZERO
        for row in global_rows[material_id]:
            qty = row.quantity + row.spare_quantity - row.delivered_quantity - row.delivered_spare_quantity
            total_demand += qty
            all_demand.append({"id": row.pk, "order": row.order.number, "line": row.line_number,
                "quantity": str(qty), "source_quantity": str(_remaining_source(row)), "date": str(row.promised_date),
                "uom": row.uom_id, "rate_m": str(row.uom_rate_m), "rate_d": str(row.uom_rate_d)})
            issues.append(_unit_issue(row, material, f"订单{row.order.number}/{row.line_number}"))
        for row in stocks[material_id]:
            loc = row.location
            usable = loc.participate_mrp and loc.usable and not loc.disabled_for_inventory and loc.location_type != "ng"
            qty = row.quantity - row.reserved_quantity
            if usable and not loc.source_site and (row.quantity or row.reserved_quantity):
                issues.append(f"库位{loc.code}未指定站点，请先明确库存归属")
            if usable and loc.source_site == site:
                available += qty
                issues.append(_unit_issue(row, material, f"库存{loc.code}/{row.batch_number}"))
            else:
                unavailable += row.quantity
            supply.append({"kind": "stock", "id": row.pk, "location": loc.code, "site": loc.source_site,
                "quantity": str(row.quantity), "reserved": str(row.reserved_quantity), "usable": usable and loc.source_site == site,
                "batch": row.batch_number, "exclusion_reason": "" if usable and loc.source_site == site else "库位不可用、不参与MRP、不良或站点未明确", "uom": row.uom_id})
        for row in purchases[material_id]:
            qty = row.quantity - row.received_quantity + max(row.spare_quantity - row.received_spare_quantity, ZERO)
            on_order += qty
            issues.append(_unit_issue(row, material, f"采购{row.order.number}/{row.line_number}"))
            supply.append({"kind": "purchase", "id": row.pk, "number": row.order.number, "line": row.line_number,
                "quantity": str(qty), "uom": row.uom_id, "rate_m": str(row.uom_rate_m), "rate_d": str(row.uom_rate_d),
                "status": row.order.status, "date": str(row.promised_date)})
        for row in requisitions[material_id]:
            qty = max(row.requested_qty - row.converted_qty, ZERO)
            if row.requisition.status == ApprovalStatus.APPROVED:
                approved += qty
            else:
                pending_qty += qty
            issues.append(_unit_issue(row, material, f"请购{row.requisition.number}/{row.line_number}"))
            supply.append({"kind": "requisition", "id": row.pk, "number": row.requisition.number,
                "line": row.line_number, "quantity": str(qty), "status": row.requisition.status, "uom": row.uom_id})
        safety = parameters["safety_stock_qty"] or ZERO
        balance = available + on_order + approved + pending_qty - total_demand - safety
        shortage = max(-balance, ZERO)
        remaining = shortage
        snapshots = []
        for item in reversed(rows):
            row = item["line"]
            allocated = min(item["qty"], remaining)
            original_date = row.promised_date
            before_clamp = original_date - timedelta(days=material.quality_lead_days if material.inspection_required else 0)
            arrival_date = max(before_clamp, timezone.localdate())
            snapshots.append({"sales_order_line_id": row.pk, "sales_order": row.order.number,
                "line": row.line_number, "customer_po": row.order.customer_po, "quantity": str(item["qty"]),
                "allocated_qty": str(allocated), "supplement_qty": "0", "promised_date": str(row.promised_date),
                "material": material.code, "uom": material.uom.name,
                "customer": row.order.customer.code, "customer_name": row.order.customer.name,
                "customer_material_code": row.customer_material.customer_code if row.customer_material_id else "",
                "terminal_material_code": row.terminal_customer_code,
                "order_type": row.order.get_order_type_display(), "order_date": str(row.order.order_date),
                "order_notes": row.order.notes,
                "arrival_before_clamp": str(before_clamp), "arrival_date": str(arrival_date),
                "overdue": before_clamp < timezone.localdate()})
            remaining -= allocated
        if snapshots and remaining > 0 and filters.get("last_pr", True):
            snapshots[0]["allocated_qty"] = str(Decimal(snapshots[0]["allocated_qty"]) + remaining)
            snapshots[0]["supplement_qty"] = str(remaining)
        snapshots.reverse()
        # MRWPMT01_qry 1031-1083: chronological packaging, carry surplus forward.
        to_buy = sum((Decimal(s["allocated_qty"]) for s in snapshots), ZERO)
        surplus = ZERO
        for source in snapshots:
            raw = Decimal(source["allocated_qty"])
            qty = ZERO
            if raw > 0 and to_buy > 0:
                if surplus > raw:
                    surplus -= raw
                else:
                    qty = max(_ceil_to(raw - surplus, package), minimum)
                    if to_buy > qty:
                        to_buy -= qty
                    else:
                        qty = max(_ceil_to(to_buy, package), minimum) if filters.get("last_pr", True) else to_buy
                        to_buy = ZERO
                    surplus += qty - raw
            source["suggested_qty"] = str(qty)
            source["packaging_delta"] = str(qty - raw)
        snapshot = {"rule_version": "trade-net-v3", "issues": sorted(set(filter(None, issues))),
            "local_test_scope_version": local_scope.get('version', ''),
            "material_info": {"code": material.code, "name": material.name,
                "english_name": material.english_name, "specification": material.specification,
                "category": material.category.code, "category_name": material.category.name,
                "product_group": material.product_group, "part_type": material.part_type,
                "product_group_name": dictionary.get(('group', material.product_group), ''),
                "part_type_name": dictionary.get(('part_type', material.part_type), ''),
                "dictionary_batch_id": dictionary_batch.pk if dictionary_batch else None,
                "planner": material.planner, "buyer": material.buyer},
            "global_demand": all_demand, "supply": supply, "balance_qty": str(balance),
            "unavailable_qty": str(unavailable), "min_purchase_qty": str(minimum),
            "min_pack_qty": str(package), "inspection_required": material.inspection_required,
            "quality_lead_days": material.quality_lead_days,
            "quality_control": material.quality_control,
            "quality_note": "需检物料阻止生成；本期仅开放已核实的免检贸易库存",
            "parameter_scope": "站点覆盖，空值回退物料主档" if parameter else "物料主档（本站点无覆盖记录）"}
        output.append(dict(material_id=material.pk, uom_id=material.uom_id, demand_qty=total_demand,
            available_qty=available, on_order_qty=on_order, approved_requisition_qty=approved,
            pending_requisition_qty=pending_qty, safety_stock_qty=safety, shortage_qty=shortage,
            suggested_qty=sum((Decimal(s["suggested_qty"]) for s in snapshots), ZERO),
            needed_date=min(x["line"].promised_date for x in rows), source_snapshot=snapshots,
            calculation_snapshot=snapshot))
    sequence = 0
    for row in output:
        for source in row["source_snapshot"]:
            sequence += 1
            source["analysis_sequence"] = sequence
    return output


def _fingerprint(rows):
    return hashlib.sha256(json.dumps(rows, default=str, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@transaction.atomic
def calculate_trade_mrp(*, site="1000", mode="net", filters=None, actor="system"):
    if mode != "net":
        raise ValidationError("本期只开放净需求模式；其他模式尚未验收")
    if not isinstance(site, str) or not site.strip() or len(site) > 20:
        raise ValidationError("请填写有效站点")
    filters = dict(filters or {})
    for key in ("date_from", "date_to", "order_date_from", "order_date_to"):
        if filters.get(key):
            try:
                date.fromisoformat(filters[key])
            except (ValueError, TypeError):
                raise ValidationError("交期必须为YYYY-MM-DD")
    if filters.get("date_from") and filters.get("date_to") and filters["date_from"] > filters["date_to"]:
        raise ValidationError("交期起不能晚于交期止")
    for key, label in (("order", "订单编号"), ("line", "行号"), ("order_date", "订单日期"),
                       ("material", "物料编码"), ("category", "产品类")):
        start, end = filters.get(f"{key}_from"), filters.get(f"{key}_to")
        if start not in (None, "") and end not in (None, "") and start > end:
            raise ValidationError(f"{label}起值不能大于止值")
    if not isinstance(filters.get("last_pr", True), bool):
        raise ValidationError("最后一笔补足必须为布尔值")
    rows = _build_results(site, filters)
    run = TradeMrpRun.objects.create(site=site, mode=mode, filters=filters, created_by=actor, source_fingerprint=_fingerprint(rows))
    TradeMrpResult.objects.bulk_create([TradeMrpResult(run=run, **row) for row in rows])
    return run


def _quantity(value, label):
    try:
        qty = Decimal(str(value))
        if not qty.is_finite() or qty < 0 or qty >= Decimal("100000000000") or qty != qty.quantize(Decimal("0.00000001")):
            raise InvalidOperation
        return qty
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f"{label}：请购量必须为非负数，最多11位整数、8位小数")


def _generation_plan(run, *, source_quantities=None, quantities=None, selected_sources=None, adjustment_reason="", header=None):
    results = list(run.results.select_related("material", "uom"))
    if not results:
        raise ValidationError("没有可生成的贸易MRP结果")
    if any(r.calculation_snapshot.get("rule_version") != "trade-net-v3" for r in results):
        raise ValidationError("该批次使用旧运算规则，请重新计算")
    if not isinstance(adjustment_reason, str) or len(adjustment_reason) > 1000:
        raise ValidationError("调整原因最多1000字")
    all_sources = {s["sales_order_line_id"] for r in results for s in r.source_snapshot}
    if selected_sources is None:
        selected_sources = [s["sales_order_line_id"] for r in results for s in r.source_snapshot if Decimal(s["suggested_qty"]) > 0]
    if not isinstance(selected_sources, (list, set)) or any(type(i) is not int for i in selected_sources) or set(selected_sources) - all_sources:
        raise ValidationError("请选择本批次内的订单来源行")
    selected_sources = set(selected_sources)
    source_quantities = {} if source_quantities is None else source_quantities
    if not isinstance(source_quantities, dict) or set(map(str, source_quantities)) - {str(i) for i in selected_sources}:
        raise ValidationError("本次请购量必须绑定已选的订单来源行")
    values = {str(k): v for k, v in source_quantities.items()}
    # Compatibility for an old caller is unambiguous only with one selected source.
    if quantities is not None:
        if values or not isinstance(quantities, dict) or set(map(str, quantities)) - {str(r.pk) for r in results}:
            raise ValidationError("请购数量包含无效结果行")
        for r in results:
            key = str(r.pk)
            if key not in quantities and r.pk not in quantities:
                continue
            qty = _quantity(quantities.get(key, quantities.get(r.pk)), r.material.code)
            sources = [s for s in r.source_snapshot if s["sales_order_line_id"] in selected_sources]
            if qty and len(sources) != 1:
                raise ValidationError("汇总数量不能分配给多条来源，请在需求明细逐行调量")
            for s in sources:
                values[str(s["sales_order_line_id"])] = qty
    lines = []
    for result in results:
        for source in result.source_snapshot:
            sid = source["sales_order_line_id"]
            if sid not in selected_sources:
                continue
            suggested = Decimal(source["suggested_qty"])
            qty = _quantity(values.get(str(sid), suggested), f'{source["sales_order"]}/{source["line"]}')
            if qty != suggested and not adjustment_reason.strip():
                raise ValidationError("人工调整请购量时请填写调整原因")
            if qty == 0:
                continue
            if result.calculation_snapshot.get("issues"):
                raise ValidationError(result.calculation_snapshot["issues"])
            lines.append({"result_id": result.pk, "source_id": sid, "material_id": result.material_id,
                "material_code": result.material.code, "material_name": result.material.name,
                "uom_id": result.uom_id, "uom": result.uom.name, "source_number": source["sales_order"],
                "source_line": source["line"], "quantity": format(qty.normalize(), 'f'), "suggested_qty": str(suggested),
                "allocated_qty": source["allocated_qty"], "supplement_qty": source["supplement_qty"],
                "packaging_delta": source["packaging_delta"], "adjustment_delta": str(qty - suggested),
                "original_date": source["promised_date"], "needed_date": source["arrival_date"]})
    if not lines:
        raise ValidationError("请选择存在正请购数量的来源行")
    header = dict(header or {})
    return {"run_id": run.pk, "rule_version": "trade-net-v3", "site": run.site,
        "aggregation_mode": "none", "lines": lines, "header": header,
        "adjustment_reason": adjustment_reason.strip()}


def _check_generation_environment():
    from backend.trade_mrp_readiness import generation_readiness
    if not generation_readiness()['enabled']:
        raise ValidationError("贸易MRP生成尚未启用或本地测试账套身份不匹配")
    if connection.vendor != "sqlite" or connection.settings_dict.get("OPTIONS", {}).get("transaction_mode") != "IMMEDIATE":
        raise ValidationError("当前数据库尚未通过跨单据并发验收，本期只允许SQLite IMMEDIATE试点账套生成")


def _check_fresh(run):
    if not run.source_fingerprint or _fingerprint(_build_results(run.site, run.filters)) != run.source_fingerprint:
        raise ValidationError("供需、单位、日期或计划参数已变化，请重新计算后生成")


@transaction.atomic
def preview_trade_mrp_generation(run_id, **values):
    run = TradeMrpRun.objects.get(pk=run_id)
    if run.status != "preview":
        raise ValidationError("该批次已确认或取消，请查询历史结果")
    _check_fresh(run)
    return _generation_plan(run, **values)


@transaction.atomic
def confirm_trade_mrp(run_id, *, actor="system", **values):
    _check_generation_environment()
    run = TradeMrpRun.objects.select_for_update().get(pk=run_id)
    if run.site != "1000":
        raise ValidationError("本期生成范围仅为已规划的站点1000")
    if run.status not in {"preview", "confirmed"}:
        raise ValidationError("该批次已取消，不能生成")
    plan = _generation_plan(run, **values)
    request_fingerprint = _fingerprint(plan)
    if run.status == "confirmed":
        if run.confirmation_snapshot.get("request_fingerprint") != request_fingerprint:
            raise ValidationError("该批次已按其他数量或来源确认，请查询原请购")
        req = PurchaseRequisition.objects.filter(pk=run.confirmation_snapshot.get("requisition_id")).first()
        if not req:
            raise ValidationError("原请购已删除；本批次不会再次生成，请重新分析当前缺口")
        return req
    list(Material.objects.select_for_update().filter(pk__in=[x["material_id"] for x in plan["lines"]]).order_by("pk"))
    _check_fresh(run)
    header = plan["header"]
    req = PurchaseRequisition.objects.create(site=run.site, requisition_type="P", document_type="",
        source_profile="trade_mrp", aggregation_mode=PurchaseRequisition.AggregationMode.NONE,
        quantity_rule="mrp", only_positive=True,
        request_date=date.fromisoformat(header["request_date"]) if header.get("request_date") else timezone.localdate(),
        requester=header.get("requester") or actor, department_id=header.get("department_id"),
        created_by=actor, notes=header.get("notes", "") or f"贸易端MRP运行 #{run.pk}",
        needed_date=min(x["needed_date"] for x in plan["lines"]),
        source_snapshot={"trade_mrp_run": run.pk, "filters": run.filters, "generation_plan": plan})
    results = {r.pk: r for r in run.results.select_related("material", "uom")}
    totals = defaultdict(lambda: ZERO)
    from backend.requisitions import material_snapshot
    for index, entry in enumerate(plan["lines"], 1):
        result = results[entry["result_id"]]
        source = next(s for s in result.source_snapshot if s["sales_order_line_id"] == entry["source_id"])
        qty = Decimal(entry["quantity"])
        snapshot = {**result.calculation_snapshot, **entry, "trade_mrp_run": run.pk,
            "requested_qty": str(qty), "adjustment_reason": plan["adjustment_reason"], "actor": actor}
        line = PurchaseRequisitionLine(requisition=req, line_number=index * 10, material=result.material,
            uom=result.uom, needed_date=entry["needed_date"], source_kind="trade_mrp",
            source_sales_order_line_id=entry["source_id"], mrp_demand_qty=Decimal(source["quantity"]),
            on_order_qty=max(result.on_order_qty + result.approved_requisition_qty, ZERO),
            available_qty=max(result.available_qty, ZERO), safety_stock_qty=result.safety_stock_qty,
            requested_qty=qty, calculation_snapshot=snapshot, created_by=actor,
            material_snapshot=material_snapshot(result.material),
            source_snapshot={"req_src": "2", "req_wo_nbr": source["sales_order"], "req_wo_lot": str(source["line"]),
                "req_mrp_req_self": source["quantity"], "req_mrp_req_tot": str(result.demand_qty),
                "req_mrp_ld_net": str(result.available_qty), "req_mrp_ord": str(result.on_order_qty),
                "req_mrp_pr": str(result.approved_requisition_qty), "req_mrp_qty_org": source["allocated_qty"]})
        line.full_clean(); line.save()
        # dgyzx1 MYPR26090569: one reqd row per req line, source sequence starts at 10.
        PurchaseRequisitionSource.objects.create(line=line, sequence=10, source_number=source["sales_order"],
            source_marker=str(source["line"]), source_sequence=source["analysis_sequence"], quantity=qty,
            snapshot={**source, "generated_qty": str(qty), "reqd_wod_part": result.material.code,
                "reqd_wod_qty_req": source["quantity"], "reqd_mrp_req_tot": str(result.demand_qty),
                "reqd_mrp_ld_net": str(result.available_qty), "reqd_mrp_ord": str(result.on_order_qty),
                "reqd_mrp_pr": str(result.approved_requisition_qty), "reqd_mrp_safe": str(result.safety_stock_qty),
                "reqd_mrp_left": result.calculation_snapshot["balance_qty"], "reqd_mrp_short": str(result.shortage_qty),
                "customer_order": source["sales_order"]})
        totals[result.pk] += qty
    for result_id, qty in totals.items():
        TradeMrpResult.objects.filter(pk=result_id).update(adjusted_qty=qty, requisition=req)
    run.status = "confirmed"
    run.confirmed_by = actor
    run.confirmed_at = timezone.now()
    run.confirmation_snapshot = {"request_fingerprint": request_fingerprint, "requisition_id": req.pk,
        "requisition_number": req.number, "plan": plan}
    run.save(update_fields=["status", "confirmed_by", "confirmed_at", "confirmation_snapshot"])
    return req
