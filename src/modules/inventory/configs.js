import { AlertTriangle, ClipboardCheck, ListTree, Truck, Warehouse } from 'lucide-react'
import { config, field, numberColumn, statusColumn } from '../../app/config'
import { today } from '../../shared/presentation'

export const inventoryConfigs = {
  materialInventoryBatch: config('物料库存批量查询', 'material-inventory-batch', ListTree, 'material_inventory_batch', [], [], { inventoryAnalysis: 'bulk' }),
  materialMonthlyInventory: config('物料进销存明细查询', 'material-monthly-inventory', ListTree, 'material_monthly_inventory', [], [], { inventoryAnalysis: 'monthly' }),
  inventoryOpening: config('期初库存录入', 'inventory-document', Warehouse, 'inventory_document', [], [], { warehouseKind: 'receipt', initialCount: true }),
  inventoryReport: config('收发存报表', 'inventory-report', ListTree, 'inventory_report', [], [], { inventoryLedger: true }),
  inventoryHistory: config('源库历史查询', 'legacy-inventory-record', ListTree, 'legacy_inventory_record', [], [], { inventoryLedger: true }),
  materialInventoryDetail: config('物料库存明细查询', 'material-inventory-detail', ListTree, 'material_inventory_detail', [], [], { inventoryLedger: true, reportKind: 'material-inventory' }),
  materialMovementDetail: config('物料进出明细查询', 'material-movement-detail', ListTree, 'material_movement_detail', [], [], { inventoryLedger: true, reportKind: 'material-movement' }),
  transferDetail: config('转仓明细查询', 'transfer-detail', ListTree, 'transfer_detail', [], [], { inventoryLedger: true, reportKind: 'transfer' }),
  countResult: config('盘点结果查询', 'count-result', ClipboardCheck, 'count_result', [], [], { inventoryLedger: true, reportKind: 'count' }),
  unplannedReceiptDetail: config('计划外入库查询', 'unplanned-receipt-detail', ListTree, 'unplanned_receipt_detail', [], [], { inventoryLedger: true, reportKind: 'receipt' }),
  unplannedIssueDetail: config('计划外出库查询', 'unplanned-issue-detail', ListTree, 'unplanned_issue_detail', [], [], { inventoryLedger: true, reportKind: 'issue' }),
  scrapDetail: config('报废明细查询', 'scrap-detail', ListTree, 'scrap_detail', [], [], { inventoryLedger: true, reportKind: 'scrap' }),
  ...Object.fromEntries([['Transfer', 'transfer', '转仓单'], ['Receipt', 'receipt', '计划外入库单'], ['Issue', 'issue', '计划外出库单'], ['Count', 'count', '盘点单'], ['Scrap', 'scrap', '报废单']].map(([key, kind, title]) => [
    `warehouse${key}`, config(title, 'inventory-document', Warehouse, 'inventory_document', [], [], { warehouseKind: kind }),
  ])),
  balances: config('库存余额', 'stock-balance', Warehouse, 'stock_balance', [['material', '物料'], ['location', '库位'], ['batch_number', '批号'], ['quantity', '现存量'], ['reserved_quantity', '预留量']], []),
  transactions: config('库存流水', 'stock-transaction', ListTree, 'stock_transaction', [['movement_type', '业务类型'], ['material', '物料'], ['location', '库位'], ['quantity', '数量'], ['balance_after', '结存'], ['posted_at', '记账时间']], []),
  transfers: config('库存调拨', 'stock-transfer', Truck, 'stock_transfer', [numberColumn, ['transfer_date', '调拨日期'], ['from_location', '调出库位'], ['to_location', '调入库位'], statusColumn], [field('transfer_date', '调拨日期', { kind: 'date', defaultValue: today() }), field('from_location', '调出库位', { lookup: 'locations', required: true }), field('to_location', '调入库位', { lookup: 'locations', required: true }), field('notes', '备注')], { audited: true }),
  transferLines: config('调拨明细', 'stock-transfer-line', Truck, 'stock_transfer', [['transfer', '调拨单'], ['line_number', '行号'], ['material', '物料'], ['quantity', '数量']], [field('transfer', '调拨单', { lookup: 'transfers', required: true }), field('line_number', '行号', { kind: 'number', required: true }), field('material', '物料', { lookup: 'materials', required: true }), field('uom', '单位', { lookup: 'uoms', required: true }), field('quantity', '数量', { kind: 'number', required: true }), field('batch_number', '批号')]),
  counts: config('库存盘点', 'stock-count', ClipboardCheck, 'stock_count', [numberColumn, ['count_date', '盘点日期'], ['location', '库位'], statusColumn], [field('count_date', '盘点日期', { kind: 'date', defaultValue: today() }), field('location', '盘点库位', { lookup: 'locations', required: true }), field('notes', '备注')], { audited: true }),
  countLines: config('盘点明细', 'stock-count-line', ClipboardCheck, 'stock_count', [['stock_count', '盘点单'], ['material', '物料'], ['system_quantity', '账面数'], ['counted_quantity', '实盘数'], ['variance_quantity', '差异']], [field('stock_count', '盘点单', { lookup: 'counts', required: true }), field('material', '物料', { lookup: 'materials', required: true }), field('uom', '单位', { lookup: 'uoms', required: true }), field('counted_quantity', '实盘数量', { kind: 'number', required: true }), field('batch_number', '批号')]),
  alerts: config('缺料预警', 'inventory-alert', AlertTriangle, 'inventory_alert', [['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '库位'], ['quantity', '现存量'], ['warning_quantity', '警戒量'], ['shortage_quantity', '缺口']], []),
}

