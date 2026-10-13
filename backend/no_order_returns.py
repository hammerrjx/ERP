"""SLCRMTA2 / SLCRMT02_pst: local no-order returns, never write the source ERP."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from backend.domain.base import ApprovalStatus
from backend.domain.delivery import InventoryPostingControl, SalesReturn, SalesReturnHistory
from backend.domain.inventory import StockBalance, StockTransaction
from backend.domain.master_data import Location
from backend.domain.sales import CustomerMaterial
from backend.inventory_codes import SALES_RETURN, TRANSFER_IN, TRANSFER_OUT


def derive_line(line):
    """Resolve a selected material association. Native rates here are m/d."""
    material = line.material
    if not material.active:
        raise ValidationError("物料已停用")
    choices = CustomerMaterial.objects.filter(customer=line.sales_return.customer, material=material, enabled=True)
    if line.customer_material_id:
        cp = choices.filter(pk=line.customer_material_id).first()
        if cp is None:
            raise ValidationError("所选客户物料关联不属于当前客户和物料，或已停用")
    else:
        candidates = list(choices[:2])
        if len(candidates) > 1:
            raise ValidationError("此物料有多个客户料号，请在物料检索中选择完整关联记录")
        cp = candidates[0] if candidates else None
    line.customer_material = cp
    line.customer_material_code = cp.customer_code if cp else ""
    line.terminal_customer_code = cp.terminal_customer_code if cp else ""
    line.terminal_customer_name = cp.terminal_customer_name if cp else ""
    line.material_name, line.material_specification = material.name, material.specification
    line.inventory_uom = material.uom
    conversion = material.uom_conversions.filter(usage="sales").first()
    line.uom = cp.customer_uom if cp and cp.customer_uom_id else conversion.business_uom if conversion else material.uom
    if cp and cp.customer_uom_id:
        line.uom_rate_m, line.uom_rate_d = cp.customer_uom_rate_m, cp.customer_uom_rate_d
    elif conversion:
        # Existing source importer stores pt_um_sl_m/d in business_qty/stock_qty.
        line.uom_rate_m, line.uom_rate_d = conversion.business_qty, conversion.stock_qty
    else:
        line.uom_rate_m = line.uom_rate_d = Decimal(1)


def amount(line):
    # SLIQ0005_qry rounds price * formal quantity to 2 places; spares are not billed.
    return (line.quantity * line.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def effective_control(doc):
    control = InventoryPostingControl.objects.select_for_update().filter(site=doc.site).first()
    if not control:
        raise ValidationError("尚未配置本账套库存有效期间，禁止审核或反审核")
    if not control.min_date <= doc.return_date <= control.max_date:
        raise ValidationError("单据日期超出系统有效日期范围")
    periods = [p for p in control.calendar if date.fromisoformat(p['start']) <= doc.return_date <= date.fromisoformat(p['end'])]
    if len(periods) != 1:
        raise ValidationError("库存月结日历缺失或日期重叠")
    period = periods[0]
    if period.get('frozen'):
        raise ValidationError("当前库存月份已冻结")
    if control.closed_year * 12 + control.closed_month >= int(period['year']) * 12 + int(period['month']):
        raise ValidationError("当前库存月份已关账")
    return control


def check_location(doc, location, actor, control, permission=True):
    if location.source_site != doc.site:
        raise ValidationError(f"库位 {location.code} 不属于站点 {doc.site}，请先补齐库位站点")
    if location.disabled_for_inventory:
        raise ValidationError(f"库位 {location.code} 已停用")
    permitted = control.location_permissions.get(location.code, [])
    if permission and actor != 'SYSTEM' and '*' not in permitted and actor not in permitted:
        raise ValidationError(f"用户 {actor} 无库位 {location.code} 的出入仓权限")


def stock_adjust(doc, line, actor, location, quantity, code, source_line, reversal=None):
    # Convert once using the native ratio, including non-unit ratios with the same UOM.
    # Generic StockBalance.adjust uses d/m; passing stock UOM avoids double conversion.
    StockBalance.adjust(material=line.material, location=location, uom=line.inventory_uom,
        quantity=quantity, movement_type=code, source_model=doc._meta.label_lower,
        source_id=doc.pk, source_line_id=source_line, actor=actor, batch_number=line.batch_number,
        effective_date=doc.return_date, reversal_of=reversal, forbid_negative=True)
    StockTransaction.objects.filter(source_model=doc._meta.label_lower, source_line_id=source_line,
        movement_type=code, location=location).update(business_uom=line.uom,
        business_quantity=quantity * line.uom_rate_d / line.uom_rate_m,
        uom_rate_m=line.uom_rate_m, uom_rate_d=line.uom_rate_d)


@transaction.atomic
def post_return(doc, actor):
    current = SalesReturn.objects.select_for_update().get(pk=doc.pk)
    if current.posted:
        doc.__dict__.update(current.__dict__)
        return
    if current.source_key:
        raise ValidationError("源系统历史退货只读，不允许重复记入本地库存")
    if current.status not in (ApprovalStatus.DRAFT, ApprovalStatus.PENDING, ApprovalStatus.REJECTED):
        raise ValidationError("当前状态不能审核")
    if not getattr(settings, 'ERP_NO_ORDER_RETURN_POST_STOCK', False):
        raise ValidationError("本账套无订单退货库存过账尚未启用，请在完整测试账套验收后启用")
    current.full_clean()
    if not current.customer_po or not current.business_group or not current.currency_id:
        raise ValidationError("客户PO、业务组别及币种不能为空")
    control = effective_control(current)
    lines = list(current.lines.select_related('material__uom', 'uom', 'inventory_uom', 'return_location'))
    if not lines:
        raise ValidationError("退货单至少需要一条明细")
    locations = {line.return_location_id for line in lines}
    consignment_location = None
    if current.customer.consignment:
        consignment_location = Location.objects.filter(code=current.customer.code, source_site=current.site).first()
        if consignment_location is None:
            raise ValidationError("寄售客户缺少同站点、以客户代码命名的库存库位")
        locations.add(consignment_location.pk)
    list(Location.objects.select_for_update().filter(pk__in=locations).order_by('pk'))
    version = current.posting_version + 1
    for line in lines:
        line.full_clean()
        if not line.inventory_uom_id or line.inventory_uom_id != line.material.uom_id:
            raise ValidationError("库存单位快照缺失或主数据已改变，请重新选择物料")
        check_location(current, line.return_location, actor, control)
        q = (line.quantity + line.spare_quantity) * line.uom_rate_m / line.uom_rate_d
        if q != q.quantize(Decimal('0.00000001')):
            raise ValidationError("单位换算后的库存数量超过8位小数")
        if consignment_location:
            check_location(current, consignment_location, actor, control, permission=False)
            if not line.material.no_stock_movement:
                stock_adjust(current, line, actor, consignment_location, -q, TRANSFER_OUT, f'{line.pk}:v{version}')
                stock_adjust(current, line, actor, line.return_location, q, TRANSFER_IN, f'{line.pk}:v{version}')
        else:
            if not line.material.no_stock_movement:
                stock_adjust(current, line, actor, line.return_location, q, SALES_RETURN, f'{line.pk}:v{version}')
            SalesReturnHistory.objects.create(line=line, version=version, quantity=-line.quantity,
                spare_quantity=-line.spare_quantity, snapshot={
                    'customer': current.customer.code, 'site': current.site, 'date': str(current.return_date),
                    'document': current.number, 'document_type': 'R', 'order_number': '', 'order_line': 0,
                    'customer_po': current.customer_po, 'material': line.material.code,
                    'unit_price': str(line.unit_price), 'amount': str(-amount(line)),
                    'currency': current.currency.code, 'exchange_rate': str(current.exchange_rate),
                    'tax_rate': str(current.tax_rate), 'uom': line.uom.code,
                    'rate_m': str(line.uom_rate_m), 'rate_d': str(line.uom_rate_d)})
    current.posting_version = version
    current.status = ApprovalStatus.APPROVED
    current.posted = current.stock_posted = True
    current.approved_by, current.approved_at = actor, timezone.now()
    current.revision += 1
    current.save()
    doc.__dict__.update(current.__dict__)


@transaction.atomic
def unpost_return(doc, actor):
    current = SalesReturn.objects.select_for_update().get(pk=doc.pk)
    if not current.posted or current.status != ApprovalStatus.APPROVED:
        raise ValidationError("只有已审核记录可以反审核")
    if current.source_key or not current.stock_posted:
        raise ValidationError("历史退货缺少本地库存过账依据，不能反审核")
    if current.downstream_references:
        raise ValidationError("退货已关联应收凭单或发票，不允许反审核")
    control = effective_control(current)
    lines = {str(line.pk): line for line in current.lines.select_related('material', 'inventory_uom', 'uom', 'return_location')}
    entries = list(StockTransaction.objects.filter(source_model=current._meta.label_lower, source_id=str(current.pk),
        source_line_id__endswith=f':v{current.posting_version}', reversal_of__isnull=True).select_related('location').order_by('id'))
    list(Location.objects.select_for_update().filter(pk__in=[t.location_id for t in entries]).order_by('pk'))
    for line in lines.values():
        check_location(current, line.return_location, actor, control)
    for entry in entries:
        line = lines[entry.source_line_id.split(':')[0]]
        # Reverse stored postings, never current customer consignment settings or ratios.
        StockBalance.adjust(material=entry.material, location=entry.location, uom=entry.uom,
            quantity=-entry.quantity, movement_type=entry.movement_type,
            source_model=current._meta.label_lower, source_id=current.pk,
            source_line_id=f'{line.pk}:v{current.posting_version}:undo', actor=actor,
            batch_number=entry.batch_number, effective_date=current.return_date, reversal_of=entry, forbid_negative=True)
        StockTransaction.objects.filter(reversal_of=entry).update(business_uom=entry.business_uom,
            business_quantity=-entry.business_quantity if entry.business_quantity is not None else None,
            uom_rate_m=entry.uom_rate_m, uom_rate_d=entry.uom_rate_d)
    SalesReturnHistory.objects.filter(line__sales_return=current, version=current.posting_version, active=True).update(active=False)
    current.posted = current.stock_posted = False
    current.status = ApprovalStatus.DRAFT
    current.approved_by, current.approved_at = '', None
    current.revision += 1
    current.save()
    doc.__dict__.update(current.__dict__)
