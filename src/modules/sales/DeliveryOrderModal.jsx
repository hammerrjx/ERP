import { useMemo, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Eye, FileCheck, Plus, Printer, RotateCcw, Save, Search, Settings, Trash2, Wrench, X } from 'lucide-react'
import { labelFor, today } from '../../shared/presentation'

const EMPTY_LINE = { sales_order_line: '', actual_quantity: '', actual_spare_quantity: '0', source_location: '', batch_number: '', notes: '' }

function optionLabel(options, value) {
  const item = options.find(option => option.id === Number(value))
  return item ? labelFor(item) : value || ''
}

function CodeLookup({ id, label, value, options, onChange, disabled, required }) {
  const selected = options.find(option => option.id === Number(value))
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const visible = options.filter(option => [option.code, option.name].filter(Boolean).join(' ').toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  const displayValue = query || selected?.code || ''
  return <div className="lookup-field delivery-code-lookup"><input id={id} required={required} value={displayValue} placeholder="输入代码或名称检索" onFocus={() => setOpen(true)} onChange={event => { setOpen(true); setQuery(event.target.value); onChange('') }} onBlur={() => setTimeout(() => setOpen(false), 150)} disabled={disabled} />{open && !disabled ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.id); setQuery(''); setOpen(false) }}><strong>{option.code}</strong><span>{option.name}</span></button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}</div> : null}<small className="field-related-name">{selected?.name || '输入代码或名称检索后选择'}</small></div>
}

function AddressLookup({ value, options, onChange, disabled, required }) {
  const selected = options.find(option => option.code === value)
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const visible = options.filter(option => [option.code, option.address].filter(Boolean).join(' ').toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  return <div className="lookup-field delivery-code-lookup"><input required={required} value={query || selected?.code || value || ''} placeholder="输入代码或名称检索，也可手工填写" onFocus={() => setOpen(true)} onChange={event => { setOpen(true); setQuery(event.target.value); onChange(event.target.value) }} onBlur={() => setTimeout(() => setOpen(false), 150)} disabled={disabled} />{open && !disabled ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.code); setQuery(''); setOpen(false) }}><strong>{option.code}</strong><span>{option.address}</span></button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项，可直接使用当前输入</div> : null}</div> : null}<small className="field-related-name">{selected?.address || '可检索维护地址，也可手工填写旧客户地址代码'}</small></div>
}

export function DeliveryOrderModal({ lookups, record, onClose, onSave, onClearError, error = '', showErrorInModal = false, readOnly = false, loading = false }) {
  const orders = lookups.salesOrders || []
  const orderLines = lookups.salesOrderLines || []
  const locations = lookups.locations || []
  const materials = lookups.materials || []
  const customers = lookups.customers || []
  const addresses = lookups.customerAddresses || []
  const [values, setValues] = useState({ delivery_date: today(), delivery_mode: 'direct', document_type: 'normal', ...(record || {}) })
  const [lines, setLines] = useState(() => (record?.lines?.length ? record.lines.map(line => ({
    ...line,
    actual_quantity: record.document_type === 'normal' ? line.actual_quantity : Math.abs(Number(line.actual_quantity || 0)),
    actual_spare_quantity: record.document_type === 'normal' ? line.actual_spare_quantity : Math.abs(Number(line.actual_spare_quantity || 0)),
  })) : [{ ...EMPTY_LINE }]))
  const locationOptions = useMemo(() => {
    if (!values.source_location || locations.some(location => location.id === Number(values.source_location))) return locations
    return [{ id: Number(values.source_location), code: record?.source_location_code || values.source_location, name: record?.source_location_name || '' }, ...locations]
  }, [locations, record?.source_location_code, record?.source_location_name, values.source_location])
  const availableLines = useMemo(() => orderLines.filter(line => {
    if (!values.customer) return true
    const order = orders.find(item => item.id === Number(line.order))
    if (order && Number(order.customer) !== Number(values.customer)) return false
    return values.document_type === 'return'
      ? Number(line.delivered_quantity || 0) > 0
      : Number(line.quantity || 0) > Number(line.delivered_quantity || 0)
  }).sort((left, right) => Number(right.order) - Number(left.order) || Number(left.line_number) - Number(right.line_number)), [orderLines, orders, values.customer, values.document_type])
  const lineOptions = useMemo(() => {
    const selectedIds = new Set(lines.map(line => Number(line.sales_order_line)).filter(Boolean))
    const availableIds = new Set(availableLines.map(line => line.id))
    return orderLines.filter(line => selectedIds.has(line.id) || availableIds.has(line.id))
      .sort((left, right) => Number(right.order) - Number(left.order) || Number(left.line_number) - Number(right.line_number))
  }, [availableLines, lines, orderLines])
  const addressOptions = useMemo(() => addresses.filter(address => !values.customer || Number(address.customer) === Number(values.customer)), [addresses, values.customer])
  const update = (key, value) => {
    setValues(current => {
      const next = { ...current, [key]: value }
      if (key === 'customer') {
        next.delivery_address = ''
        next.address_code = ''
        setLines(current => current.map(line => ({ ...line, sales_order_line: '' })))
      }
      if (key === 'address_code') {
        const address = addressOptions.find(item => item.code === value)
        next.delivery_address = address?.address || next.delivery_address || ''
      }
      if (key === 'source_location') {
        setLines(currentLines => currentLines.map(line => line.source_location === current.source_location || !line.source_location ? { ...line, source_location: value } : line))
      }
      return next
    })
  }
  const updateLine = (index, key, value) => setLines(current => current.map((line, lineIndex) => lineIndex === index ? { ...line, [key]: value } : line))
  const selectLine = (index, value) => {
    const source = lineOptions.find(line => line.id === Number(value))
    if (!source) return updateLine(index, 'sales_order_line', value)
    updateLine(index, 'sales_order_line', value)
    const quantity = values.document_type === 'return'
      ? Number(source.delivered_quantity || 0)
      : Math.max(Number(source.quantity || 0) - Number(source.delivered_quantity || 0), 0)
    setLines(current => current.map((line, lineIndex) => lineIndex === index ? { ...line, sales_order_line: value, actual_quantity: line.actual_quantity || String(quantity), source_location: line.source_location || values.source_location || materials.find(material => material.id === Number(source.material))?.default_location || '' } : line))
  }
  const submit = event => {
    event.preventDefault()
    const selected = lines.filter(line => line.sales_order_line && Number(line.actual_quantity || 0) !== 0).map((line, index) => ({ ...line, line_number: (index + 1) * 10 }))
    onSave({ ...values, document_type: values.document_type, lines: selected })
  }
  const readOnlyInput = (value, className = 'delivery-readonly') => <input className={className} readOnly value={value ?? ''} />
  return <div className="modal-backdrop"><form className="modal delivery-order-modal" onSubmit={submit}>
    <div className="modal-head delivery-modal-head"><div><div className="order-kicker">销售管理 / 送货单</div><h2>{record ? '送货单' : '新增送货单'}</h2></div><div className="order-head-meta"><span className={`status ${record?.status === 'approved' ? 'green' : 'orange'}`}><i />{record?.status === 'approved' ? '已审核' : '草稿'}</span><button type="button" aria-label="关闭" onClick={onClose}><X size={19} /></button></div></div>
    {showErrorInModal && error ? <div className="error-banner delivery-modal-error" role="alert">{error}<button type="button" aria-label="关闭错误" onClick={onClearError}><X size={15} /></button></div> : null}
    <div className="erp-toolbar" aria-label="送货单工具栏"><button type="button" title="查询"><Search size={15} />查询</button><button type="button" title="新增"><Plus size={15} />新增</button><button type="submit" title="保存" disabled={readOnly}><Save size={15} />保存</button><button type="button" title="取消" onClick={onClose}><RotateCcw size={15} />取消</button><button type="button" title="删除"><Trash2 size={15} />删除</button><button type="button" title="审核"><FileCheck size={15} />审核</button><button type="button" title="预览"><Eye size={15} />预览</button><button type="button" title="打印"><Printer size={15} />打印</button><button type="button" title="页面设置"><Settings size={15} />页面设置</button><button type="button" title="工具"><Wrench size={15} />工具</button><span className="erp-toolbar-spacer" /><button type="button" title="上一笔"><ChevronLeft size={15} /></button><button type="button" title="下一笔"><ChevronRight size={15} /></button><button type="button" title="第一笔"><ChevronsLeft size={15} /></button><button type="button" title="末一笔"><ChevronsRight size={15} /></button></div>
    <div className="delivery-summary"><div><span>客户</span><strong>{optionLabel(customers, values.customer) || '待选择'}</strong></div><div><span>明细行</span><strong>{lines.filter(line => line.sales_order_line).length} 行</strong></div><div><span>单据类型</span><strong>{({ normal: '正常送货', return: '正常退货', red_flush: '红冲单据' })[values.document_type] || '正常送货'}</strong></div><div><span>数据状态</span><strong className="summary-ok">可保存</strong></div></div>
    <section className="delivery-section"><div className="section-title"><h3>送货单表头</h3><span>按客户端 ERP 栏头维护送货日期、客户、地址及送货方式</span></div><div className="delivery-header-grid">
      <label><span>送货单号</span>{readOnlyInput(values.number || '保存后生成')}</label><label><span>日期<em>*</em></span><input required type="date" value={values.delivery_date || today()} onChange={event => update('delivery_date', event.target.value)} disabled={readOnly} /></label><label><span>客户代码<em>*</em></span><CodeLookup id="delivery-customer" label="客户代码" required value={values.customer} options={customers} onChange={value => update('customer', value)} disabled={readOnly} /></label><label><span>单据类型<em>*</em></span><select required value={values.document_type || 'normal'} onChange={event => update('document_type', event.target.value)} disabled={readOnly}><option value="normal">1. 正常送货</option><option value="return">2. 正常退货</option><option value="red_flush">3. 红冲单据</option></select></label>
      <label><span>送货模式<em>*</em></span><select required value={values.delivery_mode || 'direct'} onChange={event => update('delivery_mode', event.target.value)} disabled={readOnly}><option value="direct">直送</option><option value="supplier">供应商代送</option></select></label><label><span>客户地址代码<em>*</em></span><AddressLookup required value={values.address_code || ''} options={addressOptions} onChange={value => update('address_code', value)} disabled={readOnly} /></label><label className="field-wide"><span>详细地址<em>*</em></span><input required value={values.delivery_address || ''} onChange={event => update('delivery_address', event.target.value)} disabled={readOnly} /></label><label><span>出库库位<em>*</em></span><CodeLookup id="delivery-location" label="出库库位" required value={values.source_location} options={locationOptions} onChange={value => update('source_location', value)} disabled={readOnly} /></label><label><span>SRM 系统单号</span><input value={values.srm_number || ''} onChange={event => update('srm_number', event.target.value)} disabled={readOnly} /></label><label className="field-wide"><span>备注</span><textarea value={values.notes || ''} onChange={event => update('notes', event.target.value)} disabled={readOnly} /></label>
    </div></section>
    <section className="delivery-section delivery-lines-section"><div className="order-section-head"><div className="section-title"><h3>送货明细</h3><span>{loading ? '正在加载订单与物料资料…' : '订单、物料、客户 PO 等字段自动带入；数量、库位、批号和备注可编辑'}</span></div><button type="button" className="secondary" onClick={() => setLines(current => [...current, { ...EMPTY_LINE, source_location: values.source_location || '' }])} disabled={readOnly || loading}><Plus size={15} />新增明细</button></div><div className="delivery-lines-wrap"><table className="delivery-lines"><thead><tr>{['行号', '客户订单', '订单行号', '物料编码', '物料名称', '物料规格', '客户物料编码', '客户物料名称', '客户物料规格', '客户物料备注', '终端客户代码', '终端客户名称', '客户 PO', '退货类型', '出库库位', '库位名称', '批号', '送货数量', '送备品数', '销售单位', '销售单价', '送货金额', '币种', '税率', '备注', '订购数量', '备品数量', '已送数量', '已送备品数', '单位转换率(分子)', '单位转换率(分母)', '库存单位', '客户订单备注', '录入人', '录入时间', '修改次数', '最后修改人', '最后修改时间', '操作'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{lines.map((line, index) => { const source = orderLines.find(item => item.id === Number(line.sales_order_line)) || line; const material = materials.find(item => item.id === Number(source?.material)); const customerMaterial = (lookups.customerMaterials || []).find(item => item.id === Number(source?.customer_material)); const order = orders.find(item => item.id === Number(source?.order)); const location = locations.find(item => item.id === Number(line.source_location || values.source_location)) || { code: line.source_location_code, name: line.source_location_name }; const amount = Number(line.actual_quantity || 0) * Number(source?.unit_price || 0); const options = readOnly ? [source] : lineOptions; return <tr key={line.id || index}><td>{readOnlyInput(line.line_number || (index + 1) * 10)}</td><td><select required value={line.sales_order_line || ''} onChange={event => selectLine(index, event.target.value)} disabled={readOnly || loading}><option value="">请选择</option>{options.map(item => <option key={item.id || item.sales_order_line} value={item.sales_order_line || item.id}>{item.order_number || optionLabel(orders, item.order)} / 行{item.order_line_number || item.line_number} / {item.material_code || `物料#${item.material}`} / 已送{item.delivered_quantity || 0}</option>)}</select></td><td>{readOnlyInput(source?.order_line_number || source?.line_number)}</td><td>{readOnlyInput(material?.code || source?.material_code)}</td><td>{readOnlyInput(material?.name || source?.material_name)}</td><td>{readOnlyInput(material?.specification || source?.material_specification)}</td><td>{readOnlyInput(customerMaterial?.customer_code || source?.customer_material_code)}</td><td>{readOnlyInput(source?.customer_material_name || customerMaterial?.customer_name)}</td><td>{readOnlyInput(source?.customer_material_specification || customerMaterial?.customer_specification)}</td><td>{readOnlyInput(source?.customer_material_notes || customerMaterial?.notes)}</td><td>{readOnlyInput(source?.terminal_customer_code || customerMaterial?.terminal_customer_code)}</td><td>{readOnlyInput(source?.terminal_customer_name || customerMaterial?.terminal_customer_name)}</td><td>{readOnlyInput(order?.customer_po || source?.customer_po)}</td><td>{readOnlyInput(({ normal: '正常送货', return: '正常退货', red_flush: '红冲单据' })[values.document_type] || '正常送货')}</td><td><select required value={line.source_location || values.source_location || ''} onChange={event => updateLine(index, 'source_location', event.target.value)} disabled={readOnly || loading}><option value="">请选择</option>{(readOnly && location ? [{ id: line.source_location || values.source_location, code: location.code }] : locations).map(item => <option key={item.id} value={item.id}>{item.code}</option>)}</select></td><td>{readOnlyInput(location?.name)}</td><td><input value={line.batch_number || ''} onChange={event => updateLine(index, 'batch_number', event.target.value)} disabled={readOnly} /></td><td><input required type="number" step="any" value={line.actual_quantity || ''} onChange={event => updateLine(index, 'actual_quantity', event.target.value)} disabled={readOnly} /></td><td><input type="number" min="0" step="any" value={line.actual_spare_quantity ?? 0} onChange={event => updateLine(index, 'actual_spare_quantity', event.target.value)} disabled={readOnly} /></td><td>{readOnlyInput(source?.uom_code)}</td><td>{readOnlyInput(source?.unit_price ?? 0)}</td><td>{readOnlyInput(amount.toFixed(2))}</td><td>{readOnlyInput(source?.currency_code)}</td><td>{readOnlyInput(source?.tax_rate ?? 0)}</td><td><input value={line.notes || ''} onChange={event => updateLine(index, 'notes', event.target.value)} disabled={readOnly} /></td><td>{readOnlyInput(source?.ordered_quantity || source?.quantity)}</td><td>{readOnlyInput(source?.spare_quantity ?? 0)}</td><td>{readOnlyInput(source?.delivered_quantity ?? 0)}</td><td>{readOnlyInput(source?.delivered_spare_quantity ?? 0)}</td><td>{readOnlyInput(source?.uom_rate_m ?? 1)}</td><td>{readOnlyInput(source?.uom_rate_d ?? 1)}</td><td>{readOnlyInput(source?.inventory_uom_code)}</td><td>{readOnlyInput(source?.order_notes || order?.notes)}</td><td>{readOnlyInput(source?.line_created_by || source?.created_by)}</td><td>{readOnlyInput(source?.line_created_at || source?.created_at)}</td><td>{readOnlyInput(source?.line_modification_count ?? source?.modification_count ?? 0)}</td><td>{readOnlyInput(source?.line_updated_by || source?.updated_by)}</td><td>{readOnlyInput(source?.line_updated_at || source?.updated_at)}</td><td><button type="button" title="删除明细" aria-label="删除明细" onClick={() => setLines(current => current.length > 1 ? current.filter((_, lineIndex) => lineIndex !== index) : [{ ...EMPTY_LINE }])} disabled={readOnly || loading}><Trash2 size={15} /></button></td></tr> })}</tbody></table></div></section>
    <div className="modal-foot"><span className="order-foot-note">保存后可从列表提交审核；当前阶段不写入库存</span><button className="secondary" type="button" onClick={onClose}>取消</button><button className="primary" type="submit" disabled={readOnly}><Check size={16} />保存草稿</button></div>
  </form></div>
}
