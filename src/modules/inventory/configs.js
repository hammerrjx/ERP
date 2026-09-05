import { AlertTriangle, ClipboardCheck, ListTree, Truck, Warehouse } from 'lucide-react'
import { config, field, numberColumn, statusColumn } from '../../app/config'
import { today } from '../../shared/presentation'

export const inventoryConfigs = {
  balances: config('库存余额', 'stock-balance', Warehouse, 'stock_balance', [['material', '物料'], ['location', '库位'], ['batch_number', '批号'], ['quantity', '现存量'], ['reserved_quantity', '预留量']], []),
  transactions: config('库存流水', 'stock-transaction', ListTree, 'stock_transaction', [['movement_type', '业务类型'], ['material', '物料'], ['location', '库位'], ['quantity', '数量'], ['balance_after', '结存'], ['posted_at', '记账时间']], []),
  transfers: config('库存调拨', 'stock-transfer', Truck, 'stock_transfer', [numberColumn, ['transfer_date', '调拨日期'], ['from_location', '调出库位'], ['to_location', '调入库位'], statusColumn], [field('transfer_date', '调拨日期', { kind: 'date', defaultValue: today() }), field('from_location', '调出库位', { lookup: 'locations', required: true }), field('to_location', '调入库位', { lookup: 'locations', required: true }), field('notes', '备注')], { audited: true }),
  transferLines: config('调拨明细', 'stock-transfer-line', Truck, 'stock_transfer', [['transfer', '调拨单'], ['line_number', '行号'], ['material', '物料'], ['quantity', '数量']], [field('transfer', '调拨单', { lookup: 'transfers', required: true }), field('line_number', '行号', { kind: 'number', required: true }), field('material', '物料', { lookup: 'materials', required: true }), field('uom', '单位', { lookup: 'uoms', required: true }), field('quantity', '数量', { kind: 'number', required: true }), field('batch_number', '批号')]),
  counts: config('库存盘点', 'stock-count', ClipboardCheck, 'stock_count', [numberColumn, ['count_date', '盘点日期'], ['location', '库位'], statusColumn], [field('count_date', '盘点日期', { kind: 'date', defaultValue: today() }), field('location', '盘点库位', { lookup: 'locations', required: true }), field('notes', '备注')], { audited: true }),
  countLines: config('盘点明细', 'stock-count-line', ClipboardCheck, 'stock_count', [['stock_count', '盘点单'], ['material', '物料'], ['system_quantity', '账面数'], ['counted_quantity', '实盘数'], ['variance_quantity', '差异']], [field('stock_count', '盘点单', { lookup: 'counts', required: true }), field('material', '物料', { lookup: 'materials', required: true }), field('uom', '单位', { lookup: 'uoms', required: true }), field('counted_quantity', '实盘数量', { kind: 'number', required: true }), field('batch_number', '批号')]),
  alerts: config('缺料预警', 'inventory-alert', AlertTriangle, 'inventory_alert', [['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '库位'], ['quantity', '现存量'], ['warning_quantity', '警戒量'], ['shortage_quantity', '缺口']], []),
}

