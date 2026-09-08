import { useState } from 'react'
import { Check, X } from 'lucide-react'
import { field } from '../../app/config'
import { Field } from '../../components/Field'

const materialTabs = [
  {
    id: 'basic',
    label: '基本属性',
    keys: new Set([
      'name',
      'english_name',
      'category',
      'uom',
      'old_code',
      'customs_code',
      'customs_name',
      'barcode',
      'tax_master',
      'tax_name',
      'invoice_name',
      'purpose',
    ]),
  },
  {
    id: 'engineering',
    label: '工程属性',
    keys: new Set([
      'join_date',
      'part_type',
      'product_group',
      'engineering_reviewer',
      'specification',
      'carton_mark',
      'gross_weight_g',
      'net_weight_g',
      'length',
      'width',
      'height',
      'volume',
      'version',
      'drawing_number',
      'scrap_rate',
      'products_per_carton',
    ]),
  },
  {
    id: 'inventory',
    label: '库存属性',
    keys: new Set([
      'default_location',
      'default_storage_position',
      'batch_control',
      'batch_rule',
      'abc_class',
      'count_cycle_days',
      'shelf_life_days',
      'warehouse_manager',
    ]),
  },
  {
    id: 'mrp',
    label: 'MRP属性',
    keys: new Set([
      'safety_stock_qty',
      'max_stock_qty',
      'stock_warning_qty',
      'production_lead_days',
      'purchase_lead_days',
      'quality_control',
      'quality_lead_days',
      'supply_method',
      'phantom',
      'roll',
      'min_purchase_qty',
      'min_pack_qty',
      'min_issue_qty',
      'receipt_consume_mode',
      'outsource_receipt_consume_mode',
      'buyer',
      'planner',
      'default_supplier',
      'production_line',
      'order_strategy',
      'order_qty',
      'order_period_days',
      'over_receipt_ratio',
      'default_operation',
      'scheduling_class',
      'low_level_code',
      'plan_order',
      'non_production',
      'purchase_quote_unrestricted',
      'sales_quote_unrestricted',
      'issue_qty_unrestricted',
      'outsource_surplus_excluded_from_mrp',
    ]),
  },
]

export function MaterialRecordModal({ config: cfg, lookups, record, onClose, onSave }) {
  const defaults = Object.fromEntries(
    cfg.fields.filter((item) => item.defaultValue !== undefined).map((item) => [item.key, item.defaultValue])
  )
  const [values, setValues] = useState({ ...defaults, ...(record || {}) })
  const [tab, setTab] = useState('basic')
  const activeTab = materialTabs.find((item) => item.id === tab)
  const visibleFields = cfg.fields.filter((item) => activeTab.keys.has(item.key))
  if (tab === 'basic') visibleFields.unshift(field('code', '物料编码', { kind: 'readonly' }))
  const updateField = (key, value) => {
    if (key === 'tax_master') {
      const selected = (lookups.taxCodes || []).find((item) => item.id === Number(value))
      setValues((current) => ({
        ...current,
        tax_master: value,
        tax_code: selected?.code || '',
        tax_name: selected?.name || '',
        invoice_name: selected?.invoice_name || '',
      }))
      return
    }
    setValues((current) => ({ ...current, [key]: value }))
  }
  return (
    <div className="modal-backdrop">
      <form
        className="modal material-modal"
        onSubmit={(event) => {
          event.preventDefault()
          onSave(values)
        }}
      >
        <div className="modal-head">
          <div>
            <h2>
              {record ? '编辑' : '新增'}
              {cfg.title}
            </h2>
            <p>先保存草稿，再从列表提交审核</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <div className="material-tabs" role="tablist" aria-label="物料信息属性">
          {materialTabs.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={tab === item.id}
              className={tab === item.id ? 'active' : ''}
              onClick={() => setTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="material-form-head">
          <strong>{values.name || '新物料'}</strong>
          <span>{values.category ? '产品类已选择' : '请先填写基本属性'}</span>
        </div>
        <div className="form-grid material-form-grid">
          {visibleFields.map((item) => (
            <Field
              key={item.key}
              field={item}
              value={values[item.key] ?? ''}
              options={item.lookup ? lookups[item.lookup] || [] : item.options || []}
              onChange={(value) => updateField(item.key, value)}
            />
          ))}
        </div>
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary">
            <Check size={16} />
            保存物料
          </button>
        </div>
      </form>
    </div>
  )
}
