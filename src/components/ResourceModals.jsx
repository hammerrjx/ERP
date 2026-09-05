import { useEffect, useState } from 'react'
import { ArrowUpRight, CalendarCheck, Check, CheckCircle2, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, CircleHelp, Coins, Download, Eye, FileCheck, Plus, Printer, RotateCcw, Save, Search, Settings, Trash2, Wrench, X } from 'lucide-react'
import { api, listPayload } from '../api/client'
import { formatDateTime, labelFor, relatedLabel, today } from '../shared/presentation'

const field = (key, label, options = {}) => ({ key, label, ...options })
const auditFields = [
  field('created_by', '录入人'),
  field('created_at', '录入时间'),
  field('updated_by', '修改人'),
  field('updated_at', '修改时间'),
]

export function DetailModal({ config: cfg, row, lookups, onClose }) {
  const configuredFields = cfg.resource === 'material' ? [field('code', '物料编码', { kind: 'readonly' }), ...cfg.fields] : cfg.fields
  const detailFields = [...new Map((cfg.audited ? [...configuredFields, ...auditFields] : configuredFields).map(item => [item.key, item])).values()]
  return <div className="modal-backdrop"><div className="modal detail-modal"><div className="modal-head"><div><h2>{cfg.title}详情</h2><p>{labelFor(row)}</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div><div className="detail-grid">{detailFields.filter(item => item.kind !== 'hidden').map(item => <div key={item.key}><span>{item.label}</span><strong>{item.key.endsWith('_at') ? formatDateTime(row[item.key]) : relatedLabel(row[item.key], item, lookups)}</strong></div>)}</div></div></div>
}

export function RecordModal({ config: cfg, lookups, record, onClose, onSave }) {
  const defaults = Object.fromEntries(cfg.fields.filter(item => item.defaultValue !== undefined).map(item => [item.key, item.defaultValue]))
  const [values, setValues] = useState({ ...defaults, ...(record || {}) })
  const [contacts, setContacts] = useState(() => Array.from({ length: 4 }, (_, index) => ({ name: '', position: '', phone: '', fax: '', email: '', is_primary: index === 0, ...(record?.contacts?.[index] || {}) })))
  const [tab, setTab] = useState(cfg.formTabs?.[0]?.id || '')
  const activeTab = cfg.formTabs?.find(item => item.id === tab)
  const visibleFields = cfg.formTabs ? cfg.fields.filter(item => activeTab?.keys.has(item.key)) : cfg.fields.filter(item => item.kind !== 'hidden')
  const save = event => { event.preventDefault(); onSave(activeTab?.id === 'contacts' || cfg.formTabs?.some(item => item.id === 'contacts') ? { ...values, contacts: contacts.filter(contact => contact.name.trim()) } : values) }
  return <div className="modal-backdrop"><form className={`modal ${cfg.formTabs ? 'partner-modal' : ''}`} onSubmit={save}><div className="modal-head"><div><h2>{record ? '编辑' : '新增'}{cfg.title}</h2><p>{cfg.audited ? '先保存草稿，再从列表提交审核' : '保存后立即写入业务明细'}</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div>{cfg.formTabs ? <div className="material-tabs partner-tabs" role="tablist" aria-label={`${cfg.title}属性`}>{cfg.formTabs.map(item => <button key={item.id} type="button" role="tab" aria-selected={tab === item.id} className={tab === item.id ? 'active' : ''} onClick={() => setTab(item.id)}>{item.label}</button>)}</div> : null}{activeTab?.id === 'contacts' ? <ContactFields contacts={contacts} onChange={(index, key, value) => setContacts(current => current.map((contact, contactIndex) => contactIndex === index ? { ...contact, [key]: value } : contact))} /> : <div className="form-grid">{visibleFields.map(item => { const options = item.key === 'address_code' ? (lookups.customerAddresses || []).filter(address => address.customer === Number(values.customer)) : item.lookup ? lookups[item.lookup] || [] : item.options || []; return <Field key={item.key} field={item} value={values[item.key] ?? ''} options={options} onChange={value => setValues(current => { const address = item.key === 'address_code' ? options.find(option => option.id === Number(value)) : null; return { ...current, [item.key]: value, ...(address ? { delivery_address: address.address } : {}) } })} /> })}</div>}{cfg.fields.filter(item => item.kind === 'hidden').map(item => <input key={item.key} type="hidden" value={values[item.key] ?? ''} readOnly />)}<div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary"><Check size={16} />保存</button></div></form></div>
}

export function SalesOrderModal({ token, lookups, record, onClose, onSave, onDelete, onAction, readOnly = false }) {
  if (readOnly) return <SalesOrderDetailModal lookups={lookups} record={record} onClose={onClose} />
  return <SalesOrderEditor token={token} lookups={lookups} record={record} onClose={onClose} onSave={onSave} onDelete={onDelete} onAction={onAction} />
}

function SalesOrderEditor({ token, lookups, record, onClose, onSave, onDelete, onAction }) {
  const [values, setValues] = useState({ order_type: '1', tax_included: true, order_date: today(), delivery_mode: 'direct', exchange_rate: '1', version: 'A', ...(record || {}) })
  const [lines, setLines] = useState(record?.lines || [{ material: '', customer_material: '', quantity: '', spare_quantity: 0, promised_date: values.promised_date || today(), copper_origin: '', copper_currency: '', copper_price: 0 }])
  const customers = lookups.customers || []
  const materials = lookups.materials || []
  const customerMaterials = lookups.customerMaterials || []
  const addressOptions = customerAddressesFor(values.customer, lookups.customerAddresses)
  const priceTypes = [['1', '期货价'], ['2', '期目价'], ['3', '即日价'], ['4', '议价']]
  const update = (key, value) => {
    if (key === 'customer') {
      const selected = customers.find(item => item.id === Number(value))
      const paymentMethod = (lookups.paymentMethods || []).find(item => item.id === Number(selected?.payment_method_master)) || (lookups.paymentMethods || []).find(item => item.code === selected?.payment_method)
      setValues(current => ({ ...current, customer: value, customer_name: selected?.name || '', currency: selected?.currency || '', payment_method: paymentMethod?.id || '', tax_rate: selected?.tax_rate ?? 0, exchange_rate: selected?.exchange_rate || '1', address_code: '', delivery_address: '' }))
      setLines(current => current.map(line => ({ ...line, customer_material: '', source_quote_line: '', quote_number: '', unit_price: '', discounted_unit_price: '', untaxed_unit_price: '' })))
      return
    }
    if (key === 'address_code') {
      const address = addressOptions.find(item => item.id === Number(value))
      setValues(current => ({ ...current, address_code: value, delivery_address: address?.address || '' }))
      return
    }
    setValues(current => ({ ...current, [key]: value }))
  }
  const fetchQuote = async (index, line) => {
    if (!values.customer || !line.material) return
    const params = new URLSearchParams({ customer: values.customer, material: line.material, customer_material: line.customer_material || '', currency: values.currency || '', date: values.order_date || today() })
    try {
      const quote = await api(`/sales-quote/previous/?${params}`, { token })
      setLines(current => current.map((row, rowIndex) => rowIndex === index && row.material === line.material && row.customer_material === line.customer_material ? { ...row, source_quote_line: quote.quote_line_id || '', quote_number: quote.quote_number || '', price_type: quote.price_type || '', unit_price: quote.unit_price || '', discount_rate: quote.discount_rate ?? 100, discounted_unit_price: quote.discounted_unit_price || '', untaxed_unit_price: quote.untaxed_unit_price || '', requested_date: quote.effective_date || row.requested_date, expected_delivery_date: quote.promised_date || row.expected_delivery_date } : row))
    } catch { /* quote lookup is optional for legacy orders */ }
  }
  const updateLine = (index, key, value) => {
    const current = lines[index] || {}
    let next = { ...current, [key]: value }
    if (key === 'material') {
      const matches = customerMaterials.filter(item => item.customer === Number(values.customer) && item.material === Number(value) && item.enabled)
      next = { ...next, customer_material: matches.length === 1 ? matches[0].id : '', source_quote_line: '', quote_number: '', unit_price: '', price_type: '', discount_rate: 100, discounted_unit_price: '', untaxed_unit_price: '', material_name: materials.find(item => item.id === Number(value))?.name || '', material_specification: materials.find(item => item.id === Number(value))?.specification || '' }
    }
    if (key === 'customer_material') {
      const selected = customerMaterials.find(item => item.id === Number(value))
      next = { ...next, material: selected?.material || current.material, source_quote_line: '', quote_number: '', unit_price: '', price_type: '', discount_rate: 100, discounted_unit_price: '', untaxed_unit_price: '' }
    }
    setLines(currentLines => currentLines.map((line, lineIndex) => lineIndex === index ? next : line))
    if (key === 'material' || key === 'customer_material') fetchQuote(index, next)
  }
  const lineValue = (line, key) => {
    if (key === 'line_number') return line.line_number || ''
    if (key === 'material_code') return materials.find(item => item.id === Number(line.material))?.code || ''
    if (key === 'customer_material_code') return customerMaterials.find(item => item.id === Number(line.customer_material))?.customer_code || ''
    if (key === 'material_name') return line.material_name || materials.find(item => item.id === Number(line.material))?.name || ''
    if (key === 'material_specification') return line.material_specification || materials.find(item => item.id === Number(line.material))?.specification || ''
    if (key === 'customer_material_name') return customerMaterials.find(item => item.id === Number(line.customer_material))?.customer_name || ''
    if (key === 'customer_material_specification') return customerMaterials.find(item => item.id === Number(line.customer_material))?.customer_specification || ''
    if (key === 'terminal_customer_code' || key === 'terminal_customer_name') return customerMaterials.find(item => item.id === Number(line.customer_material))?.[key] || ''
    if (key === 'sales_uom') {
      const customerMaterial = customerMaterials.find(item => item.id === Number(line.customer_material))
      return (lookups.uoms || []).find(item => item.id === Number(line.uom || customerMaterial?.customer_uom))?.code || ''
    }
    if (key === 'inventory_uom') return (lookups.uoms || []).find(item => item.id === Number(line.inventory_uom))?.code || materials.find(item => item.id === Number(line.material))?.uom_code || ''
    if (key === 'tax_code' || key === 'tax_name' || key === 'invoice_name') return line[key] || materials.find(item => item.id === Number(line.material))?.[key] || ''
    if (key === 'discounted_unit_price') return line.discounted_unit_price || ''
    if (key === 'untaxed_unit_price') return line.untaxed_unit_price || ''
    if (key === 'tax_included_amount') return ((Number(line.quantity) || 0) * (Number(line.discounted_unit_price) || 0)).toFixed(2)
    if (key === 'untaxed_amount') return ((Number(line.quantity) || 0) * (Number(line.untaxed_unit_price) || 0)).toFixed(2)
    if (key === 'spare_ratio') return ((Number(line.quantity) ? Number(line.spare_quantity || 0) / Number(line.quantity) * 100 : 0)).toFixed(2)
    if (key === 'cartons') return (Number(line.products_per_carton) ? Number(line.quantity || 0) / Number(line.products_per_carton) : 0).toFixed(2)
    return line[key] ?? ''
  }
  const save = event => { event.preventDefault(); onSave({ ...values, lines: lines.filter(line => line.material).map((line, index) => ({ ...line, line_number: line.line_number || (index + 1) * 10, promised_date: line.promised_date || values.promised_date })) }) }
  const deleteLine = () => setLines(current => current.length > 1 ? current.slice(0, -1) : [{ material: '', customer_material: '', quantity: '', spare_quantity: 0, promised_date: values.promised_date || today(), copper_origin: '', copper_currency: '', copper_price: 0 }])
  const orderFields = [
    field('number', '客户订单', { kind: 'readonly' }), field('customer', '客户代码', { lookup: 'customers', required: true }), field('customer_name', '客户名称', { kind: 'readonly' }), field('order_type', '单别', { kind: 'select', required: true, options: [['1', '正式订单'], ['2', '样品订单']] }),
    field('order_date', '下单日期', { kind: 'date', required: true }), field('customer_po', '客户 PO', { required: true }), field('delivery_address', '送货地址', { required: true }), field('address_code', '地址代码', { lookup: 'customerAddresses' }), field('customer_buyer', '客户采购员'), field('sales_person', '业务员', { lookup: 'employees' }), field('business_group', '业务组别', { lookup: 'businessGroups' }), field('srm_number', 'SRM 单号'),
    field('payment_method', '支付方式', { lookup: 'paymentMethods', kind: 'readonly' }), field('currency', '币种', { lookup: 'currencies', required: true, kind: 'readonly' }), field('exchange_rate', '汇率', { kind: 'readonly' }), field('tax_included', '含税', { kind: 'checkbox' }), field('tax_rate', '增值税率(%)', { kind: 'readonly' }), field('delivery_mode', '送货模式', { kind: 'select', options: [['direct', '直送'], ['supplier', '供应商代送']] }), field('source_quote', '销售报价', { lookup: 'salesQuotes', kind: 'readonly' }), field('version', '版本号'), field('consumption_forecast', '消耗预测', { kind: 'checkbox' }), field('forecast_number', '预测单号'), field('consignment', '寄售', { kind: 'checkbox' }), field('promised_date', '承诺交期', { kind: 'date', required: true }), field('notes', '备注'),
    field('po_change_requested', '客户 PO 变更', { kind: 'readonly' }), field('po_change_by', '变更人', { kind: 'readonly' }), field('po_change_at', '变更时间', { kind: 'readonly' }), field('po_change_confirmed', 'PO 变更确认', { kind: 'readonly' }), field('po_change_confirmed_by', '确认人', { kind: 'readonly' }), field('po_change_confirmed_at', '确认时间', { kind: 'readonly' }), field('po_change_notes', '变更内容', { kind: 'readonly' }), field('delivery_approved', '交期审核', { kind: 'readonly' }), field('delivery_approved_by', '交期审核人', { kind: 'readonly' }), field('delivery_approved_at', '交期审核时间', { kind: 'readonly' }), field('print_count', '打印次数', { kind: 'readonly' }),
  ]
  const fieldByKey = Object.fromEntries(orderFields.map(item => [item.key, item]))
  const orderGroups = [
    { label: '订单基本信息', keys: ['number', 'customer', 'customer_name', 'order_type', 'order_date', 'customer_po', 'address_code', 'delivery_address', 'srm_number'] },
    { label: '客户与结算', keys: ['customer_buyer', 'sales_person', 'business_group', 'payment_method', 'currency', 'exchange_rate', 'tax_included', 'tax_rate', 'delivery_mode', 'source_quote'] },
    { label: '业务控制', keys: ['version', 'consumption_forecast', 'forecast_number', 'consignment', 'promised_date', 'notes'] },
    { label: 'PO 变更与审核', keys: ['po_change_requested', 'po_change_by', 'po_change_at', 'po_change_confirmed', 'po_change_confirmed_by', 'po_change_confirmed_at', 'po_change_notes', 'delivery_approved', 'delivery_approved_by', 'delivery_approved_at', 'print_count'] },
  ]
  const renderOrderField = key => {
    const item = fieldByKey[key]
    if (!item) return null
    const options = item.key === 'address_code' ? addressOptions : lookups[item.lookup] || item.options || []
    return <Field key={item.key} field={item} value={values[item.key] ?? ''} options={options} onChange={value => update(item.key, value)} />
  }
  const columns = [
    ['line_number', '行号', 'readonly'], ['material_code', '物料编码', 'editable'], ['customer_material_code', '客户物料编码', 'editable'], ['material_name', '物料名称', 'readonly'], ['material_specification', '规格', 'readonly'], ['customer_material_name', '客户物料名称', 'readonly'], ['customer_material_specification', '客户物料规格', 'readonly'], ['after_sales_method', '售后服务方式', 'readonly'], ['after_sales_method_name', '售后服务方式名称', 'readonly'], ['copper_origin', '铜产地', 'editable'], ['copper_currency', '铜币种', 'editable'], ['copper_price', '铜价', 'editable'], ['unit_price', '订单单价', 'readonly'], ['price_type', '单价类型', 'readonly'], ['quantity', '订购数量', 'editable'], ['spare_quantity', '备品数量', 'editable'], ['spare_ratio', '备品比例%', 'readonly'], ['sales_uom', '销售单位', 'readonly'], ['discounted_unit_price', '含税单价', 'readonly'], ['discount_rate', '折扣率%', 'readonly'], ['untaxed_unit_price', '未税单价', 'readonly'], ['tax_included_amount', '含税金额', 'readonly'], ['untaxed_amount', '未税金额', 'readonly'], ['special_cost', '特殊要求增加单位成本', 'readonly'], ['total_cost', '合计单位成本', 'readonly'], ['requested_date', '需求日期', 'readonly'], ['expected_delivery_date', '预计交货日期', 'readonly'], ['promised_date', '承诺交货日期', 'editable'], ['notes', '备注', 'readonly'], ['line_status', '状态', 'readonly'], ['closed_by', '关闭人', 'readonly'], ['closed_at', '关闭时间', 'readonly'], ['fixed_price', '固定价格', 'readonly'], ['income_account', '主营业务收入科目', 'readonly'], ['income_account_name', '科目名称', 'readonly'], ['replenishment_return', '补退货', 'readonly'], ['uom_rate_m', '单位转换率(分子)', 'readonly'], ['uom_rate_d', '单位转换率(分母)', 'readonly'], ['inventory_uom', '库存单位', 'readonly'], ['delivered_quantity', '送货数量', 'readonly'], ['returned_quantity', '退货数量', 'readonly'], ['delivered_spare_quantity', '送备品数量', 'readonly'], ['returned_spare_quantity', '退备品数量', 'readonly'], ['products_per_carton', '每箱产品数', 'readonly'], ['cartons', '箱数', 'readonly'], ['special_configuration_requirement', '特殊配置要求', 'readonly'], ['configuration_approved', '配置审核', 'readonly'], ['configuration_approved_by', '配置审核人', 'readonly'], ['configuration_approved_at', '配置审核时间', 'readonly'], ['created_by', '录入人', 'readonly'], ['created_at', '录入时间', 'readonly'], ['modification_count', '修改次数', 'readonly'], ['updated_by', '最后修改人', 'readonly'], ['updated_at', '最后修改时间', 'readonly'], ['tax_code', '税务编码', 'readonly'], ['tax_name', '税务名称', 'readonly'], ['invoice_name', '开票名称', 'readonly'], ['terminal_customer_code', '终端客户料号', 'readonly'], ['terminal_customer_name', '终端客户物料名称', 'readonly'],
  ]
  const total = lines.reduce((sum, line) => sum + Number(lineValue(line, 'tax_included_amount') || 0), 0)
  const renderCell = (line, index, [key, label, kind]) => {
    if (key === 'material_code') return <td key={key}><LineLookup label={label} value={line.material} options={materials.filter(item => item.active !== false)} onChange={value => updateLine(index, 'material', value)} /></td>
    if (key === 'customer_material_code') {
      const options = customerMaterials.filter(item => item.enabled !== false && item.customer === Number(values.customer) && (!line.material || item.material === Number(line.material)))
      return <td key={key}><LineLookup label={label} value={line.customer_material} options={options} customerMaterial onChange={value => updateLine(index, 'customer_material', value)} /></td>
    }
    if (key === 'quantity' || key === 'spare_quantity') return <td key={key}><input type="number" min={key === 'quantity' ? '0.000001' : '0'} step="any" required={key === 'quantity'} value={line[key] ?? ''} onChange={event => updateLine(index, key, event.target.value)} /></td>
    if (key === 'copper_origin' || key === 'copper_currency' || key === 'copper_price') return <td key={key}><input type={key === 'copper_price' ? 'number' : 'text'} min="0" step="any" value={line[key] ?? ''} onChange={event => updateLine(index, key, event.target.value)} /></td>
    if (key === 'promised_date') return <td key={key}><input type="date" required value={line[key] || values.promised_date || today()} onChange={event => updateLine(index, key, event.target.value)} /></td>
    if (key === 'price_type') return <td key={key}><input className="line-readonly" readOnly value={priceTypes.find(([value]) => value === String(line[key]))?.[1] || ''} /></td>
    return <td key={key}><input className="line-readonly" readOnly value={lineValue(line, key) || (key === 'line_number' ? (index + 1) * 10 : '')} /></td>
  }
  return <div className="modal-backdrop"><form className="modal sales-order-modal" onSubmit={save}>
    <div className="modal-head order-modal-head"><div><div className="order-kicker">销售管理 / 客户订单</div><h2>{record ? '编辑客户订单' : '新增客户订单'}</h2></div><div className="order-head-meta"><span className={`status ${record?.status === 'approved' ? 'green' : 'orange'}`}><i />{record?.status === 'approved' ? '已审核' : '草稿'}</span><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div></div>
    <OrderToolbar record={record} onAction={onAction} onDelete={onDelete} onDeleteLine={deleteLine} onClose={onClose} />
    <div className="order-summary"><div><span>客户</span><strong>{values.customer ? labelFor(customers.find(item => item.id === Number(values.customer)) || {}) : '待选择'}</strong></div><div><span>明细行</span><strong>{lines.filter(line => line.material).length} 行</strong></div><div><span>订单含税金额</span><strong>¥ {total.toFixed(2)}</strong></div><div><span>数据状态</span><strong className="summary-ok">可保存</strong></div></div>
    <section className="order-section order-header-section"><div className="section-title"><h3>订单表头</h3><span>按客户端 ERP 分组显示客户、结算、审核和变更信息</span></div><div className="order-header-groups">{orderGroups.map(group => <div className="order-field-group" key={group.label}><h4>{group.label}</h4><div className="form-grid order-form-grid">{group.keys.map(renderOrderField)}</div></div>)}</div></section>
    <section className="order-section order-lines-section"><div className="order-section-head"><div className="section-title"><h3>订单明细</h3><span>选定物料后可向右拖动滚动条查看其余明细字段，承诺交期由业务员填写</span></div><button type="button" className="secondary" onClick={() => setLines(current => [...current, { material: '', customer_material: '', quantity: '', spare_quantity: 0, promised_date: values.promised_date || today(), copper_origin: '', copper_currency: '', copper_price: 0 }])}><span>＋</span>新增明细</button></div><div className="order-lines-wrap"><table className="order-lines"><thead><tr>{columns.map(([key, label]) => <th key={key}>{label}</th>)}<th>操作</th></tr></thead><tbody>{lines.map((line, index) => <tr key={index}>{columns.map(column => renderCell(line, index, column))}<td><button type="button" title="删除明细" aria-label="删除明细" onClick={() => setLines(current => current.length > 1 ? current.filter((_, lineIndex) => lineIndex !== index) : current)}><X size={15} /></button></td></tr>)}</tbody></table></div></section>
    <div className="modal-foot"><span className="order-foot-note">保存后可从列表提交审核</span><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary"><Check size={16} />保存草稿</button></div>
  </form></div>
}

function SalesOrderDetailModal({ lookups, record, onClose }) {
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
    const option = options.find(item => item.id === Number(value) || item.code === value)
    return option ? labelFor(option) : value || ''
  }
  const customer = customers.find(item => item.id === Number(values.customer))
  const orderType = { '1': '正式订单', '2': '样品订单' }[String(values.order_type)] || values.order_type || ''
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
    if (key === 'tax_included' || key === 'consumption_forecast' || key === 'consignment' || key === 'po_change_requested' || key === 'po_change_confirmed' || key === 'delivery_approved') return value ? '是' : '否'
    return value ?? ''
  }
  const headerGroups = [
    { label: '订单基本信息', keys: [['number', '客户订单'], ['customer', '客户代码'], ['customer_name', '客户名称'], ['order_type', '单别'], ['order_date', '下单日期'], ['customer_po', '客户 PO'], ['address_code', '地址代码'], ['delivery_address', '送货地址'], ['srm_number', 'SRM 单号']] },
    { label: '客户与结算', keys: [['customer_buyer', '客户采购员'], ['sales_person', '业务员'], ['business_group', '业务组别'], ['payment_method', '支付方式'], ['currency', '币种'], ['exchange_rate', '汇率'], ['tax_included', '含税'], ['tax_rate', '增值税率(%)'], ['delivery_mode', '送货模式'], ['source_quote', '销售报价']] },
    { label: '业务控制', keys: [['version', '版本号'], ['consumption_forecast', '消耗预测'], ['forecast_number', '预测单号'], ['consignment', '寄售'], ['promised_date', '承诺交期'], ['notes', '备注']] },
    { label: 'PO 变更与审核', keys: [['po_change_requested', '客户 PO 变更'], ['po_change_by', '变更人'], ['po_change_at', '变更时间'], ['po_change_confirmed', 'PO 变更确认'], ['po_change_confirmed_by', '确认人'], ['po_change_confirmed_at', '确认时间'], ['po_change_notes', '变更内容'], ['delivery_approved', '交期审核'], ['delivery_approved_by', '交期审核人'], ['delivery_approved_at', '交期审核时间'], ['print_count', '打印次数']] },
  ]
  const columns = [
    ['line_number', '行号'], ['material_code', '物料编码'], ['customer_material_code', '客户物料编码'], ['material_name', '物料名称'], ['material_specification', '规格'], ['customer_material_name', '客户物料名称'], ['customer_material_specification', '客户物料规格'], ['after_sales_method', '售后服务方式'], ['after_sales_method_name', '售后服务方式名称'], ['copper_origin', '铜产地'], ['copper_currency', '铜币种'], ['copper_price', '铜价'], ['unit_price', '订单单价'], ['price_type', '单价类型'], ['quantity', '订购数量'], ['spare_quantity', '备品数量'], ['spare_ratio', '备品比例%'], ['sales_uom', '销售单位'], ['discounted_unit_price', '含税单价'], ['discount_rate', '折扣率%'], ['untaxed_unit_price', '未税单价'], ['tax_included_amount', '含税金额'], ['untaxed_amount', '未税金额'], ['special_cost', '特殊要求增加单位成本'], ['total_cost', '合计单位成本'], ['requested_date', '需求日期'], ['expected_delivery_date', '预计交货日期'], ['promised_date', '承诺交货日期'], ['notes', '备注'], ['line_status', '状态'], ['closed_by', '关闭人'], ['closed_at', '关闭时间'], ['fixed_price', '固定价格'], ['income_account', '主营业务收入科目'], ['income_account_name', '科目名称'], ['replenishment_return', '补退货'], ['uom_rate_m', '单位转换率(分子)'], ['uom_rate_d', '单位转换率(分母)'], ['inventory_uom', '库存单位'], ['delivered_quantity', '送货数量'], ['returned_quantity', '退货数量'], ['delivered_spare_quantity', '送备品数量'], ['returned_spare_quantity', '退备品数量'], ['products_per_carton', '每箱产品数'], ['cartons', '箱数'], ['special_configuration_requirement', '特殊配置要求'], ['configuration_approved', '配置审核'], ['configuration_approved_by', '配置审核人'], ['configuration_approved_at', '配置审核时间'], ['created_by', '录入人'], ['created_at', '录入时间'], ['modification_count', '修改次数'], ['updated_by', '最后修改人'], ['updated_at', '最后修改时间'], ['tax_code', '税务编码'], ['tax_name', '税务名称'], ['invoice_name', '开票名称'], ['terminal_customer_code', '终端客户料号'], ['terminal_customer_name', '终端客户物料名称'],
  ]
  const lineValue = (line, key) => {
    const material = materials.find(item => item.id === Number(line.material))
    const customerMaterial = customerMaterials.find(item => item.id === Number(line.customer_material))
    if (key === 'material_code') return material?.code || line.material_code || ''
    if (key === 'customer_material_code') return customerMaterial?.customer_code || line.customer_material_code || ''
    if (key === 'material_name') return line.material_name || material?.name || ''
    if (key === 'material_specification') return line.material_specification || material?.specification || ''
    if (key === 'customer_material_name') return line.customer_material_name || customerMaterial?.customer_name || ''
    if (key === 'customer_material_specification') return line.customer_material_specification || customerMaterial?.customer_specification || ''
    if (key === 'terminal_customer_code' || key === 'terminal_customer_name') return line[key] || customerMaterial?.[key] || ''
    if (key === 'sales_uom' || key === 'inventory_uom') return line[`${key === 'sales_uom' ? 'uom' : 'inventory_uom'}_code`] || line[key] || ''
    if (key === 'tax_included_amount' || key === 'untaxed_amount') return line[key] ?? ''
    if (key === 'spare_ratio' && line[key] == null) return Number(line.quantity) ? ((Number(line.spare_quantity || 0) / Number(line.quantity)) * 100).toFixed(2) : ''
    if (key === 'cartons' && line[key] == null) return Number(line.products_per_carton) ? (Number(line.quantity || 0) / Number(line.products_per_carton)).toFixed(2) : ''
    return line[key] ?? ''
  }
  const total = lines.reduce((sum, line) => sum + Number(line.tax_included_amount || 0), 0)
  const readOnlyField = (key, label) => <label className="readonly-field"><span>{label}</span><input readOnly value={formatValue(key, values[key])} /></label>
  return <div className="modal-backdrop"><div className="modal sales-order-modal sales-order-detail-modal">
    <div className="modal-head order-modal-head"><div><div className="order-kicker">销售管理 / 客户订单</div><h2>客户订单详情</h2><p>{values.number || `订单 #${values.id || ''}`}</p></div><div className="order-head-meta"><span className={`status ${values.status === 'approved' ? 'green' : values.status === 'pending' ? 'orange' : ''}`}><i />{({ approved: '已审核', pending: '待审核', rejected: '已驳回', draft: '草稿', void: '已作废' })[values.status] || values.status || '草稿'}</span><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div></div>
    <div className="order-command-bar"><button type="button" className="order-command" disabled><Search size={14} /><span>查询</span></button><button type="button" className="order-command" disabled><Plus size={14} /><span>新增</span></button><button type="button" className="order-command" disabled><Save size={14} /><span>保存</span></button><button type="button" className="order-command" disabled><Trash2 size={14} /><span>删除</span></button><button type="button" className="order-command" disabled><FileCheck size={14} /><span>审核</span></button><button type="button" className="order-command" disabled><RotateCcw size={14} /><span>反审核</span></button><button type="button" className="order-command" onClick={() => window.print()}><Eye size={14} /><span>预览</span></button><button type="button" className="order-command" onClick={() => window.print()}><Printer size={14} /><span>打印</span></button><button type="button" className="order-command" onClick={onClose}><X size={14} /><span>关闭</span></button></div>
    <div className="order-summary"><div><span>客户</span><strong>{customer ? labelFor(customer) : formatValue('customer', values.customer)}</strong></div><div><span>明细行</span><strong>{lines.length} 行</strong></div><div><span>订单含税金额</span><strong>¥ {total.toFixed(2)}</strong></div><div><span>数据状态</span><strong className={values.status === 'approved' ? 'summary-ok' : ''}>{({ approved: '已审核', pending: '待审核', rejected: '已驳回', draft: '草稿', void: '已作废' })[values.status] || '草稿'}</strong></div></div>
    <section className="order-section order-header-section"><div className="section-title"><h3>订单表头</h3><span>客户、结算、业务控制及审核信息</span></div><div className="order-header-groups">{headerGroups.map(group => <div className="order-field-group" key={group.label}><h4>{group.label}</h4><div className="form-grid order-form-grid">{group.keys.map(([key, label]) => readOnlyField(key, label))}</div></div>)}</div></section>
    <section className="order-section order-lines-section"><div className="order-section-head"><div className="section-title"><h3>订单明细</h3><span>向右拖动滚动条查看完整明细字段</span></div></div><div className="order-lines-wrap"><table className="order-lines"><thead><tr>{columns.map(([, label]) => <th key={label}>{label}</th>)}</tr></thead><tbody>{lines.map((line, index) => <tr key={line.id || index}>{columns.map(([key, label]) => <td key={key}><input className="line-readonly" readOnly aria-label={label} value={key.endsWith('_at') ? formatDateTime(line[key]) : lineValue(line, key)} /></td>)}</tr>)}</tbody></table></div></section>
    <div className="modal-foot"><span className="order-foot-note">已审核资料不可直接修改，如需变更请先执行反审核</span><button className="secondary" type="button" onClick={onClose}>关闭</button></div>
  </div></div>
}

function customerAddressesFor(customer, addresses = []) { return (addresses || []).filter(item => item.customer === Number(customer)) }

function OrderToolbar({ record, onAction, onDelete, onDeleteLine, onClose }) {
  const run = action => { if (record?.id && onAction) onAction(action) }
  const command = (label, icon, action, disabled = false) => <button type="button" className="order-command" title={label} disabled={disabled || !record?.id} onClick={() => run(action)}>{icon}<span>{label}</span></button>
  return <div className="order-command-bar">
    {command('查询', <Search size={14} />, 'query', true)}
    <button type="button" className="order-command" title="新增" onClick={() => onAction?.('new')}><Plus size={14} /><span>新增</span></button>
    <button type="submit" className="order-command"><Save size={14} /><span>保存</span></button>
    <button type="button" className="order-command" onClick={onClose}><RotateCcw size={14} /><span>取消</span></button>
    <button type="button" className="order-command" title="删除" disabled={!record?.id} onClick={onDelete}><Trash2 size={14} /><span>删除</span></button>
    <button type="button" className="order-command" title="删行" onClick={onDeleteLine}><Trash2 size={14} /><span>删行</span></button>
    {command('审核', <FileCheck size={14} />, 'approve')}
    {command('反审核', <RotateCcw size={14} />, 'unapprove')}
    {command('交期审核', <CalendarCheck size={14} />, 'delivery-approve')}
    {command('交期反审核', <RotateCcw size={14} />, 'delivery-unapprove')}
    {command('PO变更确认', <CheckCircle2 size={14} />, 'po-change-confirm')}
    {command('PO变更反确认', <RotateCcw size={14} />, 'po-change-unconfirm')}
    {command('第一笔', <ChevronsLeft size={14} />, 'first', true)}
    {command('上一笔', <ChevronLeft size={14} />, 'previous', true)}
    {command('下一笔', <ChevronRight size={14} />, 'next', true)}
    {command('末一笔', <ChevronsRight size={14} />, 'last', true)}
    <button type="button" className="order-command" title="预览" onClick={() => window.print()}><Eye size={14} /><span>预览</span></button>
    <button type="button" className="order-command" title="打印" onClick={() => { window.print(); run('print') }}><Printer size={14} /><span>打印</span></button>
    {command('页面设置', <Settings size={14} />, 'page-settings', true)}
    {command('导出', <Download size={14} />, 'export', true)}
    {command('工具', <Wrench size={14} />, 'tools', true)}
    {command('帮助', <CircleHelp size={14} />, 'help', true)}
    <button type="button" className="order-command" title="关闭" onClick={onClose}><X size={14} /><span>关闭</span></button>
  </div>
}

function LineLookup({ label, value, options, customerMaterial = false, onChange }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find(option => option.id === Number(value))
  const code = option => customerMaterial ? option.customer_code || option.code || option.material_code : option.code || option.material_code
  const text = option => [code(option), option.name, option.customer_name, option.material_name, option.specification, option.material_specification].filter(Boolean).join(' ')
  const visible = options.filter(option => text(option).toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  return <label className={`lookup-field line-lookup ${customerMaterial ? 'customer-material-lookup' : ''}`}>
    <span>{label}</span>
    <input value={query || (selected ? code(selected) : '')} placeholder="输入代码或名称检索" onFocus={() => setOpen(true)} onChange={event => { setQuery(event.target.value); setOpen(true) }} onBlur={() => setTimeout(() => { setQuery(''); setOpen(false) }, 150)} />
    {open ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.id); setQuery(''); setOpen(false) }}><strong>{code(option)}</strong><span>{[option.name || option.customer_name || option.material_name, option.material_code].filter(Boolean).join(' · ')}</span></button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}</div> : null}
  </label>
}

function ContactFields({ contacts, onChange }) {
  return <div className="contact-list">{contacts.map((contact, index) => <section className="contact-card" key={index}><strong>联系人 {index + 1}</strong><div className="form-grid"><label><span>姓名</span><input value={contact.name} onChange={event => onChange(index, 'name', event.target.value)} /></label><label><span>职位</span><input value={contact.position} onChange={event => onChange(index, 'position', event.target.value)} /></label><label><span>联系电话</span><input value={contact.phone} onChange={event => onChange(index, 'phone', event.target.value)} /></label><label><span>传真</span><input value={contact.fax} onChange={event => onChange(index, 'fax', event.target.value)} /></label><label className="field-wide"><span>电子邮箱</span><input type="email" value={contact.email} onChange={event => onChange(index, 'email', event.target.value)} /></label></div></section>)}</div>
}

const customerMaterialFields = [
  field('customer', '客户代码', { lookup: 'customers', required: true }),
  field('material', '物料编码', { lookup: 'materials', required: true }),
  field('material_name', '物料名称', { kind: 'readonly' }),
  field('material_specification', '规格型号', { kind: 'readonly' }),
  field('customer_code', '客户物料编码', { required: true }),
  field('customer_name', '客户物料名称'), field('customer_specification', '客户规格'),
  field('customer_uom', '客户单位', { lookup: 'uoms' }),
  field('customer_uom_rate_m', '客户单位换算分子', { kind: 'number' }),
  field('customer_uom_rate_d', '客户单位换算分母', { kind: 'number' }),
  field('customer_barcode', '客户条码'), field('terminal_customer_code', '终端客户编码'),
  field('terminal_customer_name', '终端客户名称'), field('enabled', '启用', { kind: 'checkbox' }),
  field('notes', '备注'), field('created_by', '录入人', { kind: 'readonly' }), field('created_at', '录入时间', { kind: 'readonly' }),
]

export function CustomerMaterialModal({ lookups, record, onClose, onSave }) {
  const [values, setValues] = useState({ customer_uom_rate_m: 1, customer_uom_rate_d: 1, enabled: true, ...(record || {}) })
  const update = (key, value) => {
    if (key === 'material') {
      const material = (lookups.materials || []).find(item => item.id === Number(value))
      setValues(current => ({ ...current, material: value, material_name: material?.name || '', material_specification: material?.specification || '' }))
      return
    }
    setValues(current => ({ ...current, [key]: value }))
  }
  return <div className="modal-backdrop"><form className="modal" onSubmit={event => { event.preventDefault(); const { material_name, material_specification, created_by, created_at, ...payload } = values; onSave(payload) }}><div className="modal-head"><div><h2>{record ? '编辑' : '新增'}客户物料</h2><p>客户和物料均关联本系统主数据，名称与规格由物料编码自动带出</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div><div className="form-grid">{customerMaterialFields.map(item => <Field key={item.key} field={item} value={values[item.key] ?? ''} options={item.lookup ? lookups[item.lookup] || [] : item.options || []} onChange={value => update(item.key, value)} />)}</div><div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary"><Check size={16} />保存</button></div></form></div>
}

const materialTabs = [
  { id: 'basic', label: '基本属性', keys: new Set(['name', 'english_name', 'category', 'uom', 'old_code', 'customs_code', 'customs_name', 'barcode', 'tax_master', 'tax_name', 'invoice_name', 'purpose']) },
  { id: 'engineering', label: '工程属性', keys: new Set(['join_date', 'part_type', 'product_group', 'engineering_reviewer', 'specification', 'carton_mark', 'gross_weight_g', 'net_weight_g', 'length', 'width', 'height', 'volume', 'version', 'drawing_number', 'scrap_rate', 'products_per_carton']) },
  { id: 'inventory', label: '库存属性', keys: new Set(['default_location', 'default_storage_position', 'batch_control', 'batch_rule', 'abc_class', 'count_cycle_days', 'shelf_life_days', 'warehouse_manager']) },
  { id: 'mrp', label: 'MRP属性', keys: new Set(['safety_stock_qty', 'max_stock_qty', 'stock_warning_qty', 'production_lead_days', 'purchase_lead_days', 'quality_control', 'quality_lead_days', 'supply_method', 'phantom', 'roll', 'min_purchase_qty', 'min_pack_qty', 'min_issue_qty', 'receipt_consume_mode', 'outsource_receipt_consume_mode', 'buyer', 'planner', 'default_supplier', 'production_line', 'order_strategy', 'order_qty', 'order_period_days', 'over_receipt_ratio', 'default_operation', 'scheduling_class', 'low_level_code', 'plan_order', 'non_production', 'purchase_quote_unrestricted', 'sales_quote_unrestricted', 'issue_qty_unrestricted', 'outsource_surplus_excluded_from_mrp']) },
]

export function MaterialRecordModal({ config: cfg, lookups, record, onClose, onSave }) {
  const defaults = Object.fromEntries(cfg.fields.filter(item => item.defaultValue !== undefined).map(item => [item.key, item.defaultValue]))
  const [values, setValues] = useState({ ...defaults, ...(record || {}) })
  const [tab, setTab] = useState('basic')
  const activeTab = materialTabs.find(item => item.id === tab)
  const visibleFields = cfg.fields.filter(item => activeTab.keys.has(item.key))
  if (tab === 'basic') visibleFields.unshift(field('code', '物料编码', { kind: 'readonly' }))
  const updateField = (key, value) => {
    if (key === 'tax_master') {
      const selected = (lookups.taxCodes || []).find(item => item.id === Number(value))
      setValues(current => ({ ...current, tax_master: value, tax_code: selected?.code || '', tax_name: selected?.name || '', invoice_name: selected?.invoice_name || '' }))
      return
    }
    setValues(current => ({ ...current, [key]: value }))
  }
  return <div className="modal-backdrop"><form className="modal material-modal" onSubmit={event => { event.preventDefault(); onSave(values) }}><div className="modal-head"><div><h2>{record ? '编辑' : '新增'}{cfg.title}</h2><p>先保存草稿，再从列表提交审核</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div><div className="material-tabs" role="tablist" aria-label="物料信息属性">{materialTabs.map(item => <button key={item.id} type="button" role="tab" aria-selected={tab === item.id} className={tab === item.id ? 'active' : ''} onClick={() => setTab(item.id)}>{item.label}</button>)}</div><div className="material-form-head"><strong>{values.name || '新物料'}</strong><span>{values.category ? '产品类已选择' : '请先填写基本属性'}</span></div><div className="form-grid material-form-grid">{visibleFields.map(item => <Field key={item.key} field={item} value={values[item.key] ?? ''} options={item.lookup ? lookups[item.lookup] || [] : item.options || []} onChange={value => updateField(item.key, value)} />)}</div><div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary"><Check size={16} />保存物料</button></div></form></div>
}

export function ConversionModal({ kind, row, session, onClose, onSave }) {
  const salesFields = [
    field('customer_po', '客户 PO', { required: true }),
    field('delivery_address', '送货地址', { required: true }),
    field('promised_date', '承诺交期', { kind: 'date', required: true }),
    field('delivery_mode', '送货模式', { kind: 'select', defaultValue: 'direct', options: [['direct', '直送'], ['supplier', '供应商代送']] }),
    field('srm_number', 'SRM 单号'), field('notes', '备注'),
  ]
  const defaults = Object.fromEntries(salesFields.filter(item => item.defaultValue !== undefined).map(item => [item.key, item.defaultValue]))
  const [values, setValues] = useState(defaults)
  const [choices, setChoices] = useState([])
  const [selected, setSelected] = useState(new Set())
  const [loading, setLoading] = useState(kind === 'purchase')
  const [loadError, setLoadError] = useState('')
  useEffect(() => {
    if (kind !== 'purchase') return
    Promise.all([
      api('/supplier-inquiry/', { token: session.token }), api('/rfq-line/', { token: session.token }), api('/rfq/', { token: session.token }),
    ]).then(([inquiries, rfqLines, rfqs]) => {
      const rfqIds = new Set(listPayload(rfqs).filter(rfq => rfq.requisition === row.id).map(rfq => rfq.id))
      const lineIds = new Set(listPayload(rfqLines).filter(line => rfqIds.has(line.rfq)).map(line => line.id))
      setChoices(listPayload(inquiries).filter(item => item.selected && lineIds.has(item.rfq_line)))
    }).catch(requestError => setLoadError(requestError.message)).finally(() => setLoading(false))
  }, [kind, row.id, session])
  const toggle = id => setSelected(current => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next })
  const submit = event => {
    event.preventDefault()
    onSave(kind === 'sales' ? values : { supplier_inquiry_ids: [...selected] })
  }
  const title = kind === 'sales' ? '转销售订单' : '转采购单'
  return <div className="modal-backdrop"><form className="modal" onSubmit={submit}><div className="modal-head"><div><h2>{title}</h2><p>来源 {row.number || `#${row.id}`}，生成后保留来源关系</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div>{kind === 'sales' ? <div className="form-grid">{salesFields.map(item => <Field key={item.key} field={item} value={values[item.key] ?? ''} options={item.options || []} onChange={value => setValues(current => ({ ...current, [item.key]: value }))} />)}</div> : <div className="source-list">{loading ? <div className="empty">正在加载</div> : loadError ? <div className="error-banner">{loadError}</div> : choices.length ? choices.map(choice => <label className="source-row" key={choice.id}><input type="checkbox" checked={selected.has(choice.id)} onChange={() => toggle(choice.id)} /><strong>响应</strong><span>询价行 #{choice.rfq_line}</span><span>供应商 #{choice.supplier}</span><span>{choice.unit_price}</span></label>) : <div className="empty">没有可转换的已选中供应商响应</div>}</div>}<div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary" disabled={kind === 'purchase' && !selected.size}><ArrowUpRight size={16} />{title}</button></div></form></div>
}

export function PayableGenerateModal({ session, onClose, onSave }) {
  const [sources, setSources] = useState([])
  const [selected, setSelected] = useState(new Set())
  const [voucherDate, setVoucherDate] = useState(today())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    Promise.all([
      api('/goods-receipt-line/', { token: session.token }), api('/goods-receipt/', { token: session.token }),
      api('/purchase-return-line/', { token: session.token }), api('/purchase-return/', { token: session.token }),
      api('/payable-voucher-line/', { token: session.token }),
    ]).then(([receiptLines, receipts, returnLines, returns, usedLines]) => {
      const approvedReceipts = new Set(listPayload(receipts).filter(row => row.status === 'approved').map(row => row.id))
      const approvedReturns = new Set(listPayload(returns).filter(row => row.status === 'approved').map(row => row.id))
      const usedReceipts = new Set(listPayload(usedLines).map(row => row.source_receipt_line).filter(Boolean))
      const usedReturns = new Set(listPayload(usedLines).map(row => row.source_purchase_return_line).filter(Boolean))
      setSources([
        ...listPayload(receiptLines).filter(row => approvedReceipts.has(row.receipt) && !usedReceipts.has(row.id)).map(row => ({ key: `receipt-${row.id}`, type: '收货', id: row.id, material: row.material, quantity: row.quantity })),
        ...listPayload(returnLines).filter(row => approvedReturns.has(row.purchase_return) && !usedReturns.has(row.id)).map(row => ({ key: `return-${row.id}`, type: '退货', id: row.id, material: row.material, quantity: row.quantity })),
      ])
    }).catch(requestError => setError(requestError.message)).finally(() => setLoading(false))
  }, [session])
  const toggle = key => setSelected(current => { const next = new Set(current); next.has(key) ? next.delete(key) : next.add(key); return next })
  const submit = event => {
    event.preventDefault()
    const chosen = sources.filter(source => selected.has(source.key))
    onSave({
      voucher_date: voucherDate,
      receipt_line_ids: chosen.filter(source => source.type === '收货').map(source => source.id),
      purchase_return_line_ids: chosen.filter(source => source.type === '退货').map(source => source.id),
    })
  }
  return <div className="modal-backdrop"><form className="modal payable-modal" onSubmit={submit}><div className="modal-head"><div><h2>自动生成应付凭单</h2><p>按供应商、币种、支付方式和税率自动拆分</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div><label><span>凭单日期<em>*</em></span><input required type="date" value={voucherDate} onChange={event => setVoucherDate(event.target.value)} /></label><div className="source-list">{loading ? <div className="empty">正在加载</div> : error ? <div className="error-banner">{error}</div> : sources.length ? sources.map(source => <label className="source-row" key={source.key}><input type="checkbox" checked={selected.has(source.key)} onChange={() => toggle(source.key)} /><strong>{source.type}</strong><span>来源行 #{source.id}</span><span>物料 #{source.material}</span><span>{source.quantity}</span></label>) : <div className="empty">没有待生成的已审核来源</div>}</div><div className="modal-foot"><span>已选择 {selected.size} 条</span><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary" disabled={!selected.size}><Coins size={16} />生成凭单</button></div></form></div>
}

export function DocumentEvidenceModal({ row, evidenceType, onClose, onSave }) {
  const [file, setFile] = useState(null)
  const [notes, setNotes] = useState('')
  return <div className="modal-backdrop"><form className="modal" onSubmit={event => { event.preventDefault(); onSave({ file, notes }) }}><div className="modal-head"><div><h2>上传签收凭证并确认</h2><p>{row.number || `单据 #${row.id}`}，确认后保留凭证和确认人记录</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div><div className="form-grid"><label className="field-wide"><span>签收/退货凭证<em>*</em></span><input required type="file" accept=".pdf,image/*" onChange={event => setFile(event.target.files?.[0] || null)} /></label><label className="field-wide"><span>备注</span><textarea value={notes} onChange={event => setNotes(event.target.value)} /></label></div><div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary" disabled={!file}><Check size={16} />上传并确认</button></div></form></div>
}

export function SalesOrderWorkflowModal({ workflow, row, session, onClose, onSave }) {
  const isMrp = workflow === 'mrp'
  const isReceipt = workflow === 'receipt'
  const [departments, setDepartments] = useState([])
  const [sourceLines, setSourceLines] = useState([])
  const [locations, setLocations] = useState([])
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [values, setValues] = useState(() => isMrp ? {
    department: '', needed_date: row.promised_date || today(), notes: '',
  } : isReceipt ? {
    receipt_date: today(), supplier_delivery_number: '', notes: '',
  } : {
    delivery_date: today(), delivery_address: row.delivery_address || '',
    srm_number: row.srm_number || '', customer_po: row.customer_po || '',
    delivery_mode: row.delivery_mode || 'direct', notes: '',
  })
  useEffect(() => {
    const requests = isMrp
      ? [api('/department/', { token: session.token })]
      : [
          api(isReceipt ? '/purchase-order-line/' : '/sales-order-line/', { token: session.token }),
          api('/location/', { token: session.token }), api('/material/', { token: session.token }),
        ]
    Promise.all(requests)
      .then(result => {
        if (isMrp) {
          setDepartments(listPayload(result[0]))
          return
        }
        const candidates = listPayload(result[0]).filter(line => {
          if (isReceipt) return line.order === row.id && Number(line.quantity) > Number(line.received_quantity)
          return line.order === row.id && Number(line.quantity) > Number(line.delivered_quantity)
        })
        const locs = listPayload(result[1]); const mats = listPayload(result[2])
        setLocations(locs); setMaterials(mats)
        setSourceLines(candidates.map(line => ({
          ...line, selected: true,
          quantity: isReceipt ? String(Number(line.quantity) - Number(line.received_quantity)) : undefined,
          actual_quantity: isReceipt ? undefined : String(Number(line.quantity) - Number(line.delivered_quantity)),
          actual_spare_quantity: '0',
          location: isReceipt ? undefined : line.material_default_location,
          source_location: isReceipt ? undefined : line.material_default_location,
          batch_number: '',
        })))
      }).catch(requestError => setLoadError(requestError.message)).finally(() => setLoading(false))
  }, [isMrp, isReceipt, row.id, session.token])
  const update = (key, value) => setValues(current => ({ ...current, [key]: value }))
  const updateLine = (id, key, value) => setSourceLines(current => current.map(line => line.id === id ? { ...line, [key]: value } : line))
  const submit = event => {
    event.preventDefault()
    const selected = sourceLines.filter(line => line.selected)
    onSave(isMrp ? values : {
      ...values,
      lines: selected.map(line => isReceipt ? ({ purchase_order_line: line.id, quantity: line.quantity, location: line.location, batch_number: line.batch_number }) : ({ sales_order_line: line.id, actual_quantity: line.actual_quantity, actual_spare_quantity: line.actual_spare_quantity, source_location: line.source_location, batch_number: line.batch_number })),
    })
  }
  const title = isMrp ? 'MRP 请购分析' : isReceipt ? '按采购单生成收货草稿' : '按订单生成送货草稿'
  const source = isReceipt ? '采购单' : '销售订单'
  const materialName = id => materials.find(item => item.id === id)?.name || `物料 #${id}`
  const lineEditor = !isMrp ? <div className="source-list">{sourceLines.length ? sourceLines.map(line => <div className="source-row workflow-source" key={line.id}><input type="checkbox" checked={line.selected} onChange={event => updateLine(line.id, 'selected', event.target.checked)} /><strong>{materialName(line.material)}</strong><span>订单行 {line.line_number}</span><label><span>{isReceipt ? '本次收货' : '本次送货'}</span><input required={line.selected} disabled={!line.selected} type="number" min="0.000001" step="any" value={isReceipt ? line.quantity : line.actual_quantity} onChange={event => updateLine(line.id, isReceipt ? 'quantity' : 'actual_quantity', event.target.value)} /></label>{!isReceipt ? <label><span>送备品数</span><input disabled={!line.selected} type="number" min="0" step="any" value={line.actual_spare_quantity} onChange={event => updateLine(line.id, 'actual_spare_quantity', event.target.value)} /></label> : null}<label><span>{isReceipt ? '入库库位' : '出库库位'}</span><select required={line.selected} disabled={!line.selected} value={isReceipt ? line.location || '' : line.source_location || ''} onChange={event => updateLine(line.id, isReceipt ? 'location' : 'source_location', Number(event.target.value))}><option value="">请选择</option>{locations.map(location => <option key={location.id} value={location.id}>{location.code} {location.name}</option>)}</select></label><label><span>批号</span><input disabled={!line.selected} value={line.batch_number} onChange={event => updateLine(line.id, 'batch_number', event.target.value)} /></label></div>) : <div className="empty">没有可生成的待处理来源行</div>}</div> : null
  return <div className="modal-backdrop"><form className="modal workflow-modal" onSubmit={submit}><div className="modal-head"><div><h2>{title}</h2><p>{row.number || `${source} #${row.id}`}，勾选来源行并确认数量、库位后生成草稿</p></div><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div>{loadError ? <div className="error-banner">{loadError}</div> : <><div className="form-grid">{isMrp ? <><label><span>请购部门<em>*</em></span><select required value={values.department} onChange={event => update('department', event.target.value === '' ? '' : Number(event.target.value))} disabled={loading}><option value="">请选择</option>{departments.map(department => <option key={department.id} value={department.id}>{department.code} {department.name}</option>)}</select></label><label><span>需求日期<em>*</em></span><input required type="date" value={values.needed_date} onChange={event => update('needed_date', event.target.value)} /></label><label className="field-wide"><span>分析备注</span><textarea value={values.notes} onChange={event => update('notes', event.target.value)} /></label></> : isReceipt ? <><label><span>收货日期<em>*</em></span><input required type="date" value={values.receipt_date} onChange={event => update('receipt_date', event.target.value)} /></label><label><span>供应商送货单号<em>*</em></span><input required value={values.supplier_delivery_number} onChange={event => update('supplier_delivery_number', event.target.value)} /></label><label className="field-wide"><span>单头备注</span><textarea value={values.notes} onChange={event => update('notes', event.target.value)} /></label></> : <><label><span>送货日期<em>*</em></span><input required type="date" value={values.delivery_date} onChange={event => update('delivery_date', event.target.value)} /></label><label><span>送货模式<em>*</em></span><select required value={values.delivery_mode} onChange={event => update('delivery_mode', event.target.value)}><option value="direct">直送</option><option value="supplier">供应商代送</option></select></label><label><span>送货地址<em>*</em></span><input required value={values.delivery_address} onChange={event => update('delivery_address', event.target.value)} /></label><label><span>SRM 系统单号<em>*</em></span><input required value={values.srm_number} onChange={event => update('srm_number', event.target.value)} /></label><label><span>客户 PO<em>*</em></span><input required value={values.customer_po} onChange={event => update('customer_po', event.target.value)} /></label><label className="field-wide"><span>单头备注</span><textarea value={values.notes} onChange={event => update('notes', event.target.value)} /></label></>}</div>{lineEditor}</>}<div className="modal-foot"><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary" disabled={loading || Boolean(loadError) || (!isMrp && !sourceLines.some(line => line.selected))}>{isMrp ? '生成请购草稿' : isReceipt ? '生成收货草稿' : '生成送货草稿'}</button></div></form></div>
}

function Field({ field: item, value, options, onChange }) {
  if (item.kind === 'checkbox') return <label className="check-field"><input type="checkbox" checked={Boolean(value)} onChange={event => onChange(event.target.checked)} /><span>{item.label}</span></label>
  if (item.kind === 'readonly') {
    const related = item.lookup ? options.find(option => option.id === Number(value) || option.code === value) : null
    const display = item.key.endsWith('_at') ? formatDateTime(value) : related ? labelFor(related) : (value || '')
    return <label className="readonly-field"><span>{item.label}</span><input value={display} readOnly /></label>
  }
  if (item.kind === 'permissions') return <label className="field-wide"><span>{item.label}{item.required ? <em>*</em> : null}</span><textarea required={item.required} value={Array.isArray(value) ? value.join(', ') : value} onChange={event => onChange(event.target.value.split(',').map(entry => entry.trim()).filter(Boolean))} placeholder="例如 purchase_order.view, purchase_order.create" /></label>
  if (item.lookup || item.key === 'address_code') return <SearchableLookup field={item} value={value} options={options} onChange={onChange} />
  if (item.kind === 'select') {
    const selectOptions = item.lookup ? options.map(option => ({ value: option.id, label: labelFor(option) })) : options.map(([optionValue, label]) => ({ value: optionValue, label }))
    return <label><span>{item.label}{item.required ? <em>*</em> : null}</span><select required={item.required} value={value} onChange={event => onChange(event.target.value === '' ? '' : item.lookup ? Number(event.target.value) : event.target.value)}><option value="">请选择</option>{selectOptions.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
  }
  return <label><span>{item.label}{item.required ? <em>*</em> : null}</span><input required={item.required} type={item.kind || 'text'} step={item.kind === 'number' ? 'any' : undefined} value={value} onChange={event => onChange(event.target.value)} /></label>
}

function SearchableLookup({ field: item, value, options, onChange }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find(option => option.id === Number(value))
  const customerMaterial = item.lookup === 'customerMaterials'
  const optionCode = option => customerMaterial ? option.customer_code || option.code || option.material_code : option.code || option.number || option.username || option.name || option.material_code
  const optionText = option => [optionCode(option), option.name, option.customer_name, option.material_name, option.specification, option.material_specification].filter(Boolean).join(' ')
  const selectedLabel = selected ? optionCode(selected) : ''
  const visible = options.filter(option => optionText(option).toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  return <label className={`lookup-field ${customerMaterial ? 'customer-material-lookup' : ''}`}><span>{item.label}{item.required ? <em>*</em> : null}</span><input required={item.required} value={query || (selected ? selectedLabel : '')} placeholder="输入代码或名称检索" onFocus={() => setOpen(true)} onChange={event => { setOpen(true); setQuery(event.target.value) }} onBlur={() => setTimeout(() => setOpen(false), 150)} />{open ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.id); setQuery(''); setOpen(false) }}><strong>{optionCode(option)}</strong>{option.name || option.customer_name || option.material_name ? <span>{option.name || option.customer_name || option.material_name}</span> : null}</button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}</div> : null}</label>
}
