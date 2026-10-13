"""Local test ledger, with an immutable source baseline and transactional report rows.

Report rows are a read projection: only StockBalance.adjust updates live quantities.
The baseline's production/purchasing contributions remain explicitly dated; local
sales and warehouse reservations are calculated on each query.
"""
from copy import deepcopy
from decimal import Decimal
import hashlib

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone

from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportRow, InventoryReportLookup


def live_batch():
    return InventoryReportBatch.objects.filter(source='local', active=True).first()


def material_code(material, batch):
    return batch.manifest.get('material_codes', {}).get(str(material.pk), material.code)


def inventory_row(batch, material, location, lot):
    return InventoryReportRow.objects.filter(batch=batch, kind='inventory',
        site=location.source_site, material_code=material_code(material, batch),
        location_code=location.code, batch_number=lot).first()


def opening_balance(material, location, uom, lot):
    """Called under the location lock, before first movement of a baseline key."""
    from backend.domain.inventory import StockBalance, StockTransaction
    batch = live_batch()
    if batch and str(material.pk) in batch.manifest.get('blocked_materials', {}):
        raise ValidationError('该物料期初单位与本地资料不一致，请先核对单位，库存未变动')
    opening = inventory_row(batch, material, location, lot) if batch else None
    quantity = Decimal(opening.payload['quantity']) if opening else Decimal(0)
    if (opening and opening.payload.get('uom_code') not in (None, '', uom.code)
            and opening.payload.get('uom_name') != uom.name):
        raise ValidationError('本地期初与物料库存单位不同，请先核对单位')
    balance, created = StockBalance.objects.get_or_create(material=material, location=location,
        batch_number=lot, defaults={'uom': uom, 'quantity': quantity})
    if created and opening:
        StockTransaction.objects.create(material=material, location=location, uom=uom,
            batch_number=lot, quantity=quantity, balance_after=quantity, movement_type='opening',
            source_model='backend.inventoryreportbatch', source_id=str(batch.pk),
            source_line_id=str(opening.pk), actor='local-ledger-opening',
            effective_date=batch.manifest.get('opening_date') or timezone.localdate())
    return balance


def project_movement(balance, movement):
    """Executed inside the same transaction as the balance and business document."""
    batch = live_batch()
    if not batch:
        return
    material, location = balance.material, balance.location
    code = material_code(material, batch)
    row = inventory_row(batch, material, location, balance.batch_number)
    payload = dict(row.payload) if row else {}
    payload.update(site=location.source_site, material_code=code, material_name=material.name,
        specification=material.specification, location_code=location.code, location_name=location.name,
        location_type=payload.get('location_type') or location.location_type.upper(),
        location_type_name=location.get_location_type_display(), batch_number=balance.batch_number,
        uom_code=balance.uom.code, uom_name=balance.uom.name, quantity=str(balance.quantity),
        category_code=material.category.code, category_name=material.category.name,
        inventory_amount=None, sales_amount=None)
    fields = {key: payload.get(key, '') for key in ('site', 'material_code', 'material_name',
        'specification', 'location_code', 'location_type', 'batch_number', 'category_code')}
    if row:
        row.payload = payload
        for key, value in fields.items():
            setattr(row, key, value)
        row.save(update_fields=['payload', *fields])
    else:
        key = hashlib.sha256(f'{location.pk}:{material.pk}:{balance.batch_number}'.encode()).hexdigest()
        InventoryReportRow.objects.create(batch=batch, kind='inventory', source_table='stock_balance',
            source_key=key, payload=payload, **fields)
    for kind, lookup_code, name, site in (
        ('material', code, material.name, ''), ('location', location.code, location.name, location.source_site),
        ('lot', balance.batch_number, balance.batch_number, location.source_site),
        ('category', material.category.code, material.category.name, ''),
    ):
        InventoryReportLookup.objects.get_or_create(batch=batch, kind=kind, code=lookup_code, site=site,
            defaults={'name': name, 'source_order': 0})
    if movement.movement_type == 'opening':
        return
    document = line = order = order_line = None
    try:
        model = apps.get_model(movement.source_model)
        document = model.objects.get(pk=movement.source_id)
        if hasattr(document, 'lines'):
            line = document.lines.filter(pk=movement.source_line_id.split(':')[0]).first()
        order_line = getattr(line, 'sales_order_line', None) or getattr(line, 'purchase_order_line', None)
        order = order_line.order if order_line else None
    except (LookupError, ValueError, ObjectDoesNotExist):
        pass
    partner = getattr(document, 'customer', None) or getattr(document, 'supplier', None)
    number = getattr(document, 'number', movement.source_id)
    names = {'260': '成品出库-销售送货', '261': '销售退货', '250': '转仓出库', '150': '转仓入库'}
    event = {**payload, 'quantity': str(movement.quantity), 'movement_type': movement.movement_type,
        'movement_name': names.get(movement.movement_type, movement.movement_type),
        'receipt_quantity': str(max(movement.quantity, 0)), 'issue_quantity': str(max(-movement.quantity, 0)),
        'document_date': str(movement.effective_date), 'posted_at': movement.posted_at.isoformat(),
        'document_number': number, 'display_document_number': number,
        'document_line': getattr(line, 'line_number', movement.source_line_id),
        'order_number': getattr(order, 'number', ''), 'order_line': getattr(order_line, 'line_number', ''),
        'partner_code': getattr(partner, 'code', ''), 'partner_name': getattr(partner, 'name', ''),
        'partner_kind': getattr(partner, 'kind', ''), 'unit_cost': None, 'movement_amount': None,
        'transaction_price': str(order_line.unit_price) if order_line else None,
        'currency': order.currency.code if order and order.currency_id else '',
        'notes': getattr(line, 'notes', ''), 'source_model': movement.source_model,
        'source_id': movement.source_id, 'source_line_id': movement.source_line_id,
        'source_table': 'stock_transaction', 'source_key': str(movement.pk)}
    InventoryReportRow.objects.create(batch=batch, kind='movement', source_table='stock_transaction',
        source_key=str(movement.pk), payload=event, **fields,
        movement_type=movement.movement_type, document_date=movement.effective_date,
        posted_at=movement.posted_at, document_number=number, order_number=event['order_number'],
        partner_code=event['partner_code'], partner_kind=event['partner_kind'])


def local_contributions(batch, part=None):
    """Stable local IDs prevent a source document with the same number being replaced."""
    from backend.domain.sales import SalesOrderLine
    from backend.domain.delivery import DeliveryOrderLine
    from backend.domain.warehouse_documents import InventoryDocumentLine
    from backend.domain.purchase import PurchaseOrderLine
    result = {}
    from django.db.models import Q
    from backend.domain.master_data import Material
    mapped = batch.manifest.get('material_codes', {})
    parts = None if part is None else {part} if isinstance(part, str) else set(part)
    material_ids = None if parts is None else list(Material.objects.filter(
        Q(code__in=parts) | Q(pk__in=[int(k) for k, v in mapped.items() if v in parts])).values_list('pk', flat=True))
    def scoped(qs):
        return qs if material_ids is None else qs.filter(material_id__in=material_ids)

    def add(key, tab, line, quantity, kind, location=None):
        location = location or line.material.default_location
        if not location and not getattr(line, 'order', None):
            return
        result[key] = {'tab': tab, 'part': material_code(line.material, batch),
            'site': getattr(getattr(line, 'order', None), 'site', getattr(location, 'source_site', '')), 'quantity': str(quantity), 'kind': kind,
            'document': getattr(getattr(line, 'order', None) or getattr(line, 'delivery', None)
                                or getattr(line, 'document', None), 'number', ''),
            'line': str(line.line_number), 'location': getattr(location, 'code', ''), 'location_name': getattr(location, 'name', ''),
            'lot': getattr(line, 'batch_number', ''), 'nettable': bool(location and location.participate_mrp),
            'location_type': location.location_type.upper() if location else '', 'origin': 'local',
            'status': getattr(getattr(line, 'order', None), 'status', ''),
            'purchase_type': getattr(getattr(line, 'order', None), 'purchase_type', '')}

    orders = SalesOrderLine.objects.select_related('order__customer', 'material__default_location')
    for line in scoped(orders.filter(order__status='approved', line_status__in=['', 'normal'])):
        if line.material.no_stock_movement or (line.order.customer.consignment and not line.order.consignment):
            continue
        qty = (line.quantity + line.spare_quantity - line.delivered_quantity - line.delivered_spare_quantity)
        qty = qty * line.uom_rate_m / line.uom_rate_d
        add(f'order:{line.pk}', 'demand', line, qty, '本地客户订单')
    drafts = DeliveryOrderLine.objects.filter(delivery__posted=False,
        delivery__status__in=['draft', 'pending']).select_related('delivery__customer',
            'sales_order_line__order', 'source_location', 'material')
    for line in scoped(drafts):
        if line.material.no_stock_movement or not line.source_location.participate_mrp:
            continue
        if line.delivery.customer.consignment and not line.sales_order_line.order.consignment:
            continue
        source = line.sales_order_line
        qty = (line.actual_quantity + line.actual_spare_quantity) * source.uom_rate_m / source.uom_rate_d
        add(f'delivery:{line.pk}', 'allocation', line, qty, '本地未审核送货', line.source_location)
    for line in scoped(InventoryDocumentLine.objects.filter(document__status__in=['draft', 'confirmed'],
            document__kind__in=['issue', 'transfer', 'scrap']).select_related(
                'document__from_location', 'document__to_location', 'from_location', 'to_location', 'material')):
        origin = line.from_location or line.document.from_location
        destination = line.to_location or line.document.to_location
        if not origin or not origin.participate_mrp:
            continue
        if destination and destination.source_site == origin.source_site and destination.participate_mrp:
            continue
        add(f'warehouse:{line.pk}', 'allocation', line, line.quantity, '本地未审核出仓', origin)
    for line in scoped(PurchaseOrderLine.objects.exclude(order__status='void').exclude(order__purchase_type='non_production').exclude(line_status__in=['C','c','closed']).select_related(
            'order', 'material__default_location', 'material__uom', 'source_supplier_quote', 'uom')):
        if line.material.no_stock_movement: continue
        quantity = line.quantity-line.received_quantity+max(line.spare_quantity-line.received_spare_quantity,0)
        if line.allocation_managed:
            quantity = quantity * line.uom_rate_m / line.uom_rate_d
        elif line.uom_id != line.material.uom_id:
            quote = line.source_supplier_quote
            if not quote or quote.uom_rate_d <= 0:
                continue
            quantity = quantity * quote.uom_rate_m / quote.uom_rate_d
        add(f'purchase:{line.pk}', 'order', line, quantity, '本地采购中')
    return result


def bulk_payload(snapshot, batch, part=None):
    from backend.domain.master_data import Location
    from backend.domain.purchase import PurchaseOrder
    from backend.inventory_analysis import BULK_NUMBERS, reconcile_bulk
    parts = None if part is None else {part} if isinstance(part, str) else set(part)
    payload = deepcopy(snapshot.payload) if parts is None else {
        'rows': [dict(r) for r in snapshot.payload.get('rows', []) if r['tmp_part'] in parts],
        'details': [dict(r) for r in snapshot.payload.get('details', []) if r['part'] in parts]}
    site = snapshot.site
    locations = {(loc.source_site, loc.code): loc for loc in Location.objects.all()}
    imported_requisitions = set(batch.manifest.get('requisition_import', {}).get('numbers', []))
    imported_orders = set(PurchaseOrder.objects.filter(source_object='dgyzx1.po_mstr',
        number__in={r['document'] for r in payload.get('details', []) if r['tab'] == 'order'}).values_list('number', flat=True))
    trade_sync = batch.manifest.get('trade_sync', {})
    synced_sales = set(trade_sync.get('source_sales_numbers', []))
    synced_parts = set(trade_sync.get('material_codes', []))
    details = [row for row in payload.get('details', []) if row['tab'] != 'stock'
        and not (row['tab'] == 'demand' and row['kind'] == '销售订单' and row['document'] in synced_sales and row['part'] in synced_parts)
        and not (row['tab'] == 'requisition' and row['document'] in imported_requisitions)
        and not (row['tab'] == 'order' and row['document'] in imported_orders)]
    from backend.requisitions import supply_contributions
    details.extend(supply_contributions(site, part=part))
    rows = {r['tmp_part']: r for r in payload.get('rows', [])}
    for detail in details:
        rows.setdefault(detail['part'], {'tmp_part': detail['part']})
    inventory = InventoryReportRow.objects.filter(batch=batch, kind='inventory', site=site)
    if part is not None:
        inventory = inventory.filter(material_code__in=parts)
    for record in inventory.iterator(chunk_size=1000):
        p = record.payload
        loc = locations.get((site, record.location_code))
        details.append({'tab': 'stock', 'part': record.material_code, 'kind': '本地库存',
            'document': record.location_code, 'line': '', 'location': record.location_code,
            'location_name': p.get('location_name', ''), 'lot': record.batch_number,
            'nettable': bool(loc and loc.participate_mrp), 'location_type': record.location_type,
            'quantity': p['quantity']})
        rows.setdefault(record.material_code, {'tmp_part': record.material_code,
            'pt_desc1': record.material_name, 'pt_spec': record.specification,
            'pt_um': p.get('uom_name', ''), 'tmp_sfty_stk': '0'})
    before = batch.manifest.get('local_contributions', {})
    current = local_contributions(batch, part=part)
    for key in before.keys() | current.keys():
        old, new = before.get(key), current.get(key)
        # Synced source contributions have been removed above: add the current
        # business row once, rather than applying a delta against the old opening.
        if trade_sync and (key.startswith('purchase:') or (key.startswith('order:') and
                ((new or old or {}).get('document') in synced_sales) and (new or old or {}).get('part') in synced_parts)):
            old = None
        # Keep site/material changes as two separate contributions rather than netting unlike keys.
        for value, sign in ((old, -1), (new, 1)):
            if value and value['site'] == site and (parts is None or value['part'] in parts):
                item = dict(value, quantity=str(Decimal(value['quantity']) * sign))
                if Decimal(item['quantity']):
                    details.append(item)
                    rows.setdefault(item['part'], {'tmp_part': item['part'], 'tmp_sfty_stk': '0'})
    payload['rows'], payload['details'] = list(rows.values()), details
    for row in payload['rows']:
        for field in BULK_NUMBERS:
            row.setdefault(field, '0')
    reconcile_bulk(payload['rows'], details)
    payload['source'] = 'local'
    return payload
