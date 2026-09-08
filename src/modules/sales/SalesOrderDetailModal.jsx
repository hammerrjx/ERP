import { Eye, FileCheck, Plus, Printer, RotateCcw, Save, Search, Trash2, X } from 'lucide-react'
import { formatDateTime, labelFor } from '../../shared/presentation'
import { orderLineColumns, orderFieldByKey, orderGroups } from './salesOrderFields'

export function SalesOrderDetailModal({ lookups, record, onClose }) {
  const values = record || {}
  const customers = lookups.customers || []
  const materials = lookups.materials || []
  const customerMaterials = lookups.customerMaterials || []
  const paymentMethods = lookups.paymentMethods || []
  const currencies = lookups.currencies || []
  const businessGroups = lookups.businessGroups || []
  const employees = lookups.employees || []
  const addresses = lookups.customerAddresses || []
  const quotes = lookups.salesQuotes || []
  const lines = values.lines || []
  const optionLabel = (options, value) => {
    const option = options.find((item) => item.id === Number(value) || item.code === value)
    return option ? labelFor(option) : value || ''
  }
  const customer = customers.find((item) => item.id === Number(values.customer))
  const orderType = { 1: '正式订单', 2: '样品订单' }[String(values.order_type)] || values.order_type || ''
  const deliveryMode = { direct: '直送', supplier: '供应商代送' }[values.delivery_mode] || values.delivery_mode || ''
  const formatValue = (key, value) => {
    if (key.endsWith('_at')) return value ? formatDateTime(value) : ''
    if (key === 'customer') return optionLabel(customers, value)
    if (key === 'customer_name') return customer?.name || value || ''
    if (key === 'order_type') return orderType
    if (key === 'payment_method') return optionLabel(paymentMethods, value)
    if (key === 'currency') return optionLabel(currencies, value)
    if (key === 'business_group') return optionLabel(businessGroups, value)
    if (key === 'sales_person') return optionLabel(employees, value)
    if (key === 'address_code') return optionLabel(addresses, value)
    if (key === 'source_quote') return optionLabel(quotes, value)
    if (key === 'delivery_mode') return deliveryMode
    if (
      key === 'tax_included' ||
      key === 'consumption_forecast' ||
      key === 'consignment' ||
      key === 'po_change_requested' ||
      key === 'po_change_confirmed' ||
      key === 'delivery_approved'
    )
      return value ? '是' : '否'
    return value ?? ''
  }
  const columns = [...orderLineColumns]
  columns.splice(
    columns.findIndex(([key]) => key === 'spare_quantity') + 1,
    0,
    ['execution_formal_net', '正式净累计'],
    ['execution_spare_net', '备品净累计'],
    ['execution_formal_remaining', '正式剩余'],
    ['execution_spare_remaining', '备品剩余'],
    ['execution_total_net', '含备品净已送'],
    ['execution_has_history_gap', '历史明细差额']
  )
  const lineValue = (line, key) => {
    if (key === 'execution_has_history_gap') return line.execution_summary?.has_history_gap ? '待核对' : '无差额'
    if (key.startsWith('execution_')) return line.execution_summary?.[key.slice(10)] ?? ''
    if (key === 'spare_ratio' && !Number(line.quantity)) return '不适用'
    const material = materials.find((item) => item.id === Number(line.material))
    const customerMaterial = customerMaterials.find((item) => item.id === Number(line.customer_material))
    if (key === 'material_code') return material?.code || line.material_code || ''
    if (key === 'customer_material_code') return customerMaterial?.customer_code || line.customer_material_code || ''
    if (key === 'material_name') return line.material_name || material?.name || ''
    if (key === 'material_specification') return line.material_specification || material?.specification || ''
    if (key === 'customer_material_name') return line.customer_material_name || customerMaterial?.customer_name || ''
    if (key === 'customer_material_specification')
      return line.customer_material_specification || customerMaterial?.customer_specification || ''
    if (key === 'terminal_customer_code' || key === 'terminal_customer_name')
      return line[key] || customerMaterial?.[key] || ''
    if (key === 'sales_uom' || key === 'inventory_uom')
      return line[`${key === 'sales_uom' ? 'uom' : 'inventory_uom'}_code`] || line[key] || ''
    if (key === 'tax_included_amount' || key === 'untaxed_amount') return line[key] ?? ''
    if (key === 'spare_ratio' && line[key] == null)
      return Number(line.quantity) ? ((Number(line.spare_quantity || 0) / Number(line.quantity)) * 100).toFixed(2) : ''
    if (key === 'cartons' && line[key] == null)
      return Number(line.products_per_carton)
        ? (Number(line.quantity || 0) / Number(line.products_per_carton)).toFixed(2)
        : ''
    return line[key] ?? ''
  }
  const total = lines.reduce((sum, line) => sum + Number(line.tax_included_amount || 0), 0)
  const readOnlyField = (key, label) => (
    <label className="readonly-field">
      <span>{label}</span>
      <input readOnly value={formatValue(key, values[key])} />
    </label>
  )
  return (
    <div className="modal-backdrop">
      <div className="modal sales-order-modal sales-order-detail-modal">
        <div className="modal-head order-modal-head">
          <div>
            <div className="order-kicker">销售管理 / 客户订单</div>
            <h2>客户订单详情</h2>
            <p>{values.number || `订单 #${values.id || ''}`}</p>
          </div>
          <div className="order-head-meta">
            <span
              className={`status ${values.status === 'approved' ? 'green' : values.status === 'pending' ? 'orange' : ''}`}
            >
              <i />
              {{ approved: '已审核', pending: '待审核', rejected: '已驳回', draft: '草稿', void: '已作废' }[
                values.status
              ] ||
                values.status ||
                '草稿'}
            </span>
            <button type="button" aria-label="关闭" onClick={onClose}>
              <X size={19} />
            </button>
          </div>
        </div>
        <div className="order-command-bar">
          <button type="button" className="order-command" disabled>
            <Search size={14} />
            <span>查询</span>
          </button>
          <button type="button" className="order-command" disabled>
            <Plus size={14} />
            <span>新增</span>
          </button>
          <button type="button" className="order-command" disabled>
            <Save size={14} />
            <span>保存</span>
          </button>
          <button type="button" className="order-command" disabled>
            <Trash2 size={14} />
            <span>删除</span>
          </button>
          <button type="button" className="order-command" disabled>
            <FileCheck size={14} />
            <span>审核</span>
          </button>
          <button type="button" className="order-command" disabled>
            <RotateCcw size={14} />
            <span>反审核</span>
          </button>
          <button type="button" className="order-command" onClick={() => window.print()}>
            <Eye size={14} />
            <span>预览</span>
          </button>
          <button type="button" className="order-command" onClick={() => window.print()}>
            <Printer size={14} />
            <span>打印</span>
          </button>
          <button type="button" className="order-command" onClick={onClose}>
            <X size={14} />
            <span>关闭</span>
          </button>
        </div>
        <div className="order-summary">
          <div>
            <span>客户</span>
            <strong>{customer ? labelFor(customer) : formatValue('customer', values.customer)}</strong>
          </div>
          <div>
            <span>明细行</span>
            <strong>{lines.length} 行</strong>
          </div>
          <div>
            <span>订单含税金额</span>
            <strong>¥ {total.toFixed(2)}</strong>
          </div>
          <div>
            <span>数据状态</span>
            <strong className={values.status === 'approved' ? 'summary-ok' : ''}>
              {{ approved: '已审核', pending: '待审核', rejected: '已驳回', draft: '草稿', void: '已作废' }[
                values.status
              ] || '草稿'}
            </strong>
          </div>
        </div>
        <section className="order-section order-header-section">
          <div className="section-title">
            <h3>订单表头</h3>
            <span>客户、结算、业务控制及审核信息</span>
          </div>
          <div className="order-header-groups">
            {orderGroups.map((group) => (
              <div className="order-field-group" key={group.label}>
                <h4>{group.label}</h4>
                <div className="form-grid order-form-grid">
                  {group.keys.map((key) => readOnlyField(key, orderFieldByKey[key].label))}
                </div>
              </div>
            ))}
          </div>
        </section>
        <section className="order-section order-lines-section">
          <div className="order-section-head">
            <div className="section-title">
              <h3>订单明细</h3>
              <span>向右拖动滚动条查看完整明细字段</span>
            </div>
          </div>
          <div className="order-lines-wrap">
            <table className="order-lines">
              <thead>
                <tr>
                  {columns.map(([, label]) => (
                    <th key={label}>{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {lines.map((line, index) => (
                  <tr key={line.id || index}>
                    {columns.map(([key, label]) => (
                      <td key={key}>
                        <input
                          className="line-readonly"
                          readOnly
                          aria-label={label}
                          value={key.endsWith('_at') ? formatDateTime(line[key]) : lineValue(line, key)}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        <div className="modal-foot">
          <span className="order-foot-note">已审核资料不可直接修改，如需变更请先执行反审核</span>
          <button className="secondary" type="button" onClick={onClose}>
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}
