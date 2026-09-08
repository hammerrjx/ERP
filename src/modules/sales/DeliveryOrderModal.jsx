import { useEffect, useRef, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, Copy, Plus, RotateCcw, Save, Search, Trash2, Wrench, X } from 'lucide-react'
import { api } from '../../api/client'
import { today } from '../../shared/presentation'

function CodeLookup({ id, label, value, options, onChange, disabled, required }) {
  const selected = options.find(option => option.id === Number(value))
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const visible = options.filter(option => [option.code, option.name].filter(Boolean).join(' ').toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  const displayValue = query || selected?.code || ''
  return <div className="lookup-field delivery-code-lookup"><input id={id} required={required} value={displayValue} placeholder="输入代码或名称检索" onFocus={() => setOpen(true)} onChange={event => { setOpen(true); setQuery(event.target.value); onChange('') }} onBlur={() => setTimeout(() => setOpen(false), 150)} disabled={disabled} />{open && !disabled ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.id); setQuery(''); setOpen(false) }}><strong>{option.code}</strong><span>{option.name}</span></button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}</div> : null}<small className="field-related-name">{selected?.name || ''}</small></div>
}

function AddressLookup({ value, options, onChange, disabled, required }) {
  const selected = options.find(option => option.code === value)
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const visible = options.filter(option => [option.code, option.address].filter(Boolean).join(' ').toLowerCase().includes(query.trim().toLowerCase())).slice(0, 30)
  return <div className="lookup-field delivery-code-lookup"><input required={required} value={query || selected?.code || value || ''} placeholder="输入代码或名称检索，也可手工填写" onFocus={() => setOpen(true)} onChange={event => { setOpen(true); setQuery(event.target.value); onChange(event.target.value) }} onBlur={() => setTimeout(() => setOpen(false), 150)} disabled={disabled} />{open && !disabled ? <div className="lookup-menu">{visible.map(option => <button type="button" key={option.id} onMouseDown={event => event.preventDefault()} onClick={() => { onChange(option.code); setQuery(''); setOpen(false) }}><strong>{option.code}</strong><span>{option.address}</span></button>)}{visible.length === 0 ? <div className="lookup-empty">无匹配项，可直接使用当前输入</div> : null}</div> : null}<small className="field-related-name">{selected?.address || ''}</small></div>
}


const FILTERS = [
  ['customer_po', '客户 PO'], ['material_code', '内部物料编码'],
  ['customer_material_code', '客户物料编码'], ['terminal_material_code', '客户终端物料编码'],
  ['order_number', '客户订单'],
]
const DISPLAY_COLUMNS = [
  ['physical_quantity', '含备品本次数量'],
  ['material_name', '物料名称'], ['material_specification', '物料规格'],
  ['customer_material_code', '客户物料编码'], ['terminal_material_code', '客户终端物料编码'],
  ['customer_po', '客户 PO'], ['uom_code', '销售单位'], ['unit_price', '销售单价'],
  ['delivery_amount', '送货金额'], ['currency_code', '币种'], ['tax_rate', '税率'], ['ordered_quantity', '订购数量'],
  ['spare_quantity', '备品数量'], ['delivered_quantity', '净已送数量'],
  ['delivered_spare_quantity', '净已送备品'], ['uom_rate_m', '换算分子'],
  ['uom_rate_d', '换算分母'], ['inventory_uom_code', '库存单位'], ['order_notes', '订单备注'],
]
const quantity = value => Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 8 })

function OrderGenerator({ token, customer, delivery, documentType, existing, onClose, onGenerate }) {
  const [filters, setFilters] = useState({ match: 'contains' })
  const [result, setResult] = useState({ results: [], count: 0, page: 1 })
  const [selected, setSelected] = useState({})
  const [direction, setDirection] = useState(documentType === 'normal' ? 'ship' : 'return')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const requestId = useRef(0)
  const existingIds = new Set(existing.map(row => Number(row.sales_order_line)))
  const query = async (page = 1) => {
    const id = ++requestId.current
    setBusy(true); setError('')
    const params = new URLSearchParams({ ...filters, customer, page, ...(delivery ? { delivery } : {}) })
    try {
      const response = await api('/delivery-order/order-candidates/?' + params, { token })
      if (id === requestId.current) setResult(response)
    } catch (e) { if (id === requestId.current) setError(e.message) }
    finally { if (id === requestId.current) setBusy(false) }
  }
  useEffect(() => { query(); return () => { requestId.current++ } }, [])
  const toggle = (row, checked) => setSelected(current => {
    const next = { ...current }
    if (checked) {
      next[row.sales_order_line] = { ...row,
        actual_quantity: direction === 'return' ? String(-Number(row.returnable_quantity)) : row.available_quantity,
        actual_spare_quantity: direction === 'return' ? String(-Number(row.returnable_spare_quantity)) : row.available_spare_quantity,
        batch_number: '', notes: '' }
    } else delete next[row.sales_order_line]
    return next
  })
  const generate = () => {
    const rows = Object.values(selected)
    if (!rows.length) return setError('请勾选订单明细')
    for (const row of rows) {
      const amount = Number(row.actual_quantity), spare = Number(row.actual_spare_quantity)
      if (!Number.isFinite(amount) || !Number.isFinite(spare) || (!amount && !spare)) return setError('送货数量与备品数不能同时为0')
      const limit = amount < 0 ? row.returnable_quantity : row.available_quantity
      const spareLimit = spare < 0 ? row.returnable_spare_quantity : row.available_spare_quantity
      if (Math.abs(amount) > Number(limit) || Math.abs(spare) > Number(spareLimit)) return setError(row.order_number + ' / ' + row.order_line_number + '：数量超过当前可用额度')
    }
    onGenerate(rows)
  }
  const update = (id, key, value) => setSelected(current => ({ ...current, [id]: { ...current[id], [key]: value } }))
  return <div className="modal-backdrop delivery-overlay"><div role="dialog" aria-modal="true" aria-label="根据客户订单生成明细" className="modal delivery-generator">
    <div className="modal-head"><h2>根据客户订单生成明细</h2><button type="button" aria-label="关闭生成窗口" onClick={onClose}><X size={19} /></button></div>
    <form className="delivery-query" onSubmit={event => { event.preventDefault(); query() }}>
      <label><span>查询方式</span><select value={filters.match} onChange={event => setFilters(current => ({ ...current, match: event.target.value }))}><option value="contains">包含</option><option value="exact">精确</option><option value="range">区间</option></select></label>
      {FILTERS.map(([key, label]) => <label key={key}><span>{label}</span><div className="delivery-range"><input aria-label={label} value={filters[key] || ''} onChange={event => setFilters(current => ({ ...current, [key]: event.target.value }))} />{filters.match === 'range' && <input aria-label={label + '结束'} value={filters[key + '_to'] || ''} onChange={event => setFilters(current => ({ ...current, [key + '_to']: event.target.value }))} />}</div></label>)}
      {[['order_date', '下单日期'], ['promised_date', '预计交货日期']].map(([key, label]) => <label key={key}><span>{label}</span><div className="delivery-range"><input type="date" aria-label={label + '开始'} value={filters[key + '_from'] || ''} onChange={event => setFilters(current => ({ ...current, [key + '_from']: event.target.value }))} /><input type="date" aria-label={label + '结束'} value={filters[key + '_to'] || ''} onChange={event => setFilters(current => ({ ...current, [key + '_to']: event.target.value }))} /></div></label>)}
      <button className="primary" disabled={busy}><Search size={15} />查询</button>
    </form>
    <div className="delivery-selection-bar"><label>数量方向 <select value={direction} onChange={event => { setDirection(event.target.value); setSelected({}) }}><option value="ship">送出（正数）</option><option value="return">退回（负数）</option></select></label><button type="button" onClick={() => result.results.filter(row => !existingIds.has(row.sales_order_line)).forEach(row => toggle(row, true))} disabled={busy}>选中本页</button><button type="button" onClick={() => setSelected({})}>全不选</button><span>已选 {Object.keys(selected).length} 行</span></div>
    {error && <div className="error-banner" role="alert">{error}</div>}
    <div className="delivery-candidates-wrap"><table className="delivery-candidates"><thead><tr>{['选择', '客户订单', '订单行号', '内部物料编码', '客户物料编码', '终端物料编码', '客户 PO', '物料名称', '订购数量', '净已送数量', '未审核送货', '可送上限', '可退数量', '本次送货数量', '本次备品数', '可送备品', '可退备品', '库存参考'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>
      {result.results.map(row => { const picked = selected[row.sales_order_line]; return <tr key={row.sales_order_line} className={picked ? 'is-selected' : ''}>
        <td><input type="checkbox" aria-label={'选择' + row.order_number + '行' + row.order_line_number} checked={Boolean(picked)} disabled={existingIds.has(row.sales_order_line) || busy} onChange={event => toggle(row, event.target.checked)} /></td>
        <td>{row.order_number}</td><td>{row.order_line_number}</td><td>{row.material_code}</td><td>{row.customer_material_code}</td><td>{row.terminal_material_code}</td><td>{row.customer_po}</td><td>{row.material_name}</td>
        {[row.ordered_quantity, row.delivered_quantity, row.pending_quantity, row.available_quantity, row.returnable_quantity].map((value, index) => <td className="numeric" key={index}>{quantity(value)}</td>)}
        <td><input type="number" step="0.00000001" aria-label="本次送货数量" value={picked?.actual_quantity ?? ''} disabled={!picked || busy} onChange={event => update(row.sales_order_line, 'actual_quantity', event.target.value)} /></td>
        <td><input type="number" step="0.00000001" aria-label="本次备品数" value={picked?.actual_spare_quantity ?? ''} disabled={!picked || busy} onChange={event => update(row.sales_order_line, 'actual_spare_quantity', event.target.value)} /></td>
        <td className="numeric">{quantity(row.available_spare_quantity)}</td><td className="numeric">{quantity(row.returnable_spare_quantity)}</td><td>未同步</td>
      </tr> })}
      {!result.results.length && <tr><td colSpan={18} className="delivery-empty">{busy ? '查询中…' : '无符合条件的订单明细'}</td></tr>}
    </tbody></table></div>
    <div className="modal-foot"><span>共 {result.count} 行 · 第 {result.page} 页</span><button type="button" title="上一页" disabled={busy || result.page <= 1} onClick={() => query(result.page - 1)}><ChevronLeft size={16} /></button><button type="button" title="下一页" disabled={busy || result.page * 30 >= result.count} onClick={() => query(result.page + 1)}><ChevronRight size={16} /></button><button type="button" className="secondary" onClick={onClose}>关闭</button><button type="button" className="primary" disabled={busy || !Object.keys(selected).length} onClick={generate}><Check size={16} />生成</button></div>
  </div></div>
}

export function DeliveryOrderModal({ token, lookups, record, onClose, onSave, onClearError, error = '', readOnly = false, loading = false }) {
  const [values, setValues] = useState({ delivery_date: today(), delivery_mode: 'direct', document_type: 'normal', address_code: '0', ...(record || {}) })
  const [lines, setLines] = useState(record?.lines || [])
  const [toolsOpen, setToolsOpen] = useState(false)
  const [confirmNumber, setConfirmNumber] = useState(false)
  const [generator, setGenerator] = useState(false)
  const [generatedCount, setGeneratedCount] = useState(null)
  const [busy, setBusy] = useState(false)
  const [localError, setLocalError] = useState('')
  const requestId = useRef(crypto.randomUUID())
  const locations = lookups.locations || []
  const addresses = (lookups.customerAddresses || []).filter(row => row.customer === Number(values.customer))
  const locked = readOnly || record?.posted || record?.status === 'approved'
  const update = (key, value) => {
    setLocalError('')
    setValues(current => ({ ...current, [key]: value, ...(key === 'customer' ? { address_code: '0', address_snapshot: '', delivery_address: '' } : {}) }))
    if (key === 'customer') setLines([])
    if (key === 'address_code') {
      const address = addresses.find(row => row.code === value)
      setValues(current => ({ ...current, address_snapshot: address?.address || '' }))
    }
  }
  const openGenerator = () => {
    setToolsOpen(false)
    if (!values.customer) return setLocalError('请先选择客户')
    if (!values.delivery_date) return setLocalError('请填写送货日期')
    if (!values.delivery_address?.trim()) return setLocalError('请填写实际收货厂区')
    if (record?.id || values.reservation) setGenerator(true)
    else setConfirmNumber(true)
  }
  const reserveNumber = async () => {
    setBusy(true); setLocalError('')
    try {
      const reserved = await api('/delivery-order/reserve-number/', { token, method: 'POST', body: { request_id: requestId.current, delivery_date: values.delivery_date } })
      setValues(current => ({ ...current, ...reserved }))
      setConfirmNumber(false); setGenerator(true)
    } catch (e) { setLocalError(e.message); setConfirmNumber(false) }
    finally { setBusy(false) }
  }
  const submit = async event => {
    event.preventDefault()
    if (busy || locked) return
    if (!lines.length) return setLocalError('请先根据客户订单生成明细')
    if (!record?.id && !values.reservation) return setLocalError('请先取得正式单号')
    setBusy(true); setLocalError('')
    try { await onSave({ ...values, lines }) }
    catch (e) { setLocalError(e.message) }
    finally { setBusy(false) }
  }
  const editLine = (index, key, value) => setLines(current => current.map((row, i) => i === index ? { ...row, [key]: value } : row))
  const close = () => { if (!busy) onClose() }
  return <>
    <div className="modal-backdrop"><form className="modal delivery-order-modal delivery-sheet" onSubmit={submit} aria-label="送货单编辑">
      <div className="modal-head"><div><h2>{record ? '送货单' : '新增送货单'}</h2><span>{values.number || '未取号'}</span></div><div className="order-head-meta"><span className={'status ' + (locked ? 'green' : 'orange')}>{locked ? '已审核' : '草稿'}</span><button type="button" aria-label="关闭送货单" onClick={close} disabled={busy}><X size={19} /></button></div></div>
      <div className="erp-toolbar"><button type="submit" title="保存" disabled={locked || busy}><Save size={16} />保存</button><button type="button" title="取消" disabled={busy} onClick={close}><RotateCcw size={16} />取消</button><div className="delivery-tools"><button type="button" title="工具" disabled={locked || busy} aria-expanded={toolsOpen} onClick={() => setToolsOpen(!toolsOpen)}><Wrench size={16} />工具</button>{toolsOpen && <div className="delivery-tools-menu"><button type="button" onClick={openGenerator}>根据客户订单生成明细</button></div>}</div></div>
      {(localError || error) && <div className="error-banner" role="alert">{localError || error}<button type="button" aria-label="关闭错误" onClick={() => { setLocalError(''); onClearError?.() }}><X size={15} /></button></div>}
      <section className="delivery-header-grid">
        <label><span>送货单号</span><input readOnly value={values.number || ''} /></label>
        <label><span>送货日期 <em>*</em></span><input type="date" required value={values.delivery_date} disabled={locked || busy} onChange={event => update('delivery_date', event.target.value)} /></label>
        <label><span>客户代码 <em>*</em></span><CodeLookup id="delivery-customer" label="客户代码" required value={values.customer} options={lookups.customers || []} onChange={value => update('customer', value)} disabled={locked || busy || lines.length > 0} /></label>
        <label><span>客户地址代码</span><AddressLookup value={values.address_code || ''} options={addresses} onChange={value => update('address_code', value)} disabled={locked || busy} /></label>
        <label><span>送货模式</span><select value={values.delivery_mode} disabled={locked || busy} onChange={event => update('delivery_mode', event.target.value)}><option value="direct">1. 直送</option><option value="supplier">2. 供应商代送</option></select></label>
        <label><span>业务模式</span><select value={values.document_type} disabled={locked || busy} onChange={event => update('document_type', event.target.value)}><option value="normal">正常送货</option><option value="return">正常退货</option><option value="red_flush">红冲单据</option></select></label>
        <label><span>SRM 系统单号</span><input maxLength={80} value={values.srm_number || ''} disabled={locked || busy} onChange={event => update('srm_number', event.target.value)} /></label>
        <label><span>默认打印人</span><input maxLength={64} value={values.default_print_person || ''} disabled={locked || busy} onChange={event => update('default_print_person', event.target.value)} /></label>
        <label className="field-wide"><span>送货地址 / 实际收货厂区 <em>*</em></span><input required maxLength={240} value={values.delivery_address || ''} disabled={locked || busy} onChange={event => update('delivery_address', event.target.value)} /></label>
        <label className="field-wide"><span>客户资料详细地址</span><input readOnly value={values.address_snapshot || ''} /></label>
        <label className="field-wide"><span>单头备注</span><input maxLength={240} value={values.notes || ''} disabled={locked || busy} onChange={event => update('notes', event.target.value)} /></label>
      </section>
      <section className="delivery-sheet-details"><div className="order-section-head"><h3>送货明细 <small>{lines.length} 行</small></h3><button type="button" className="secondary" onClick={openGenerator} disabled={locked || busy}><Plus size={15} />根据客户订单生成</button></div>
      <div className="delivery-lines-wrap"><table className="delivery-lines"><thead><tr>{['行号', '客户订单', '订单行号', '物料编码', '本次送货数量', '本次备品数', '出库库位', '库位名称', '批号', '明细备注', ...DISPLAY_COLUMNS.map(column => column[1]), '操作'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{lines.map((line, index) => {
        const location = locations.find(row => row.id === Number(line.source_location))
        return <tr key={line.id || index}>
          <td>{line.line_number || (index + 1) * 10}</td><td>{line.order_number}</td><td>{line.order_line_number}</td><td>{line.material_code}</td>
          <td><input type="number" step="0.00000001" aria-label={'送货数量行' + (index + 1)} value={line.actual_quantity ?? ''} disabled={locked || busy} onChange={event => editLine(index, 'actual_quantity', event.target.value)} /></td>
          <td><input type="number" step="0.00000001" aria-label={'备品数行' + (index + 1)} value={line.actual_spare_quantity ?? '0'} disabled={locked || busy} onChange={event => editLine(index, 'actual_spare_quantity', event.target.value)} /></td>
          <td><select required aria-label={'出库库位行' + (index + 1)} value={line.source_location || ''} disabled={locked || busy || loading} onChange={event => editLine(index, 'source_location', event.target.value)}><option value="">请选择</option>{!location && line.source_location && <option value={line.source_location}>{line.source_location_code || line.source_location}</option>}{locations.filter(row => !row.disabled_for_inventory || row.id === Number(line.source_location)).map(row => <option key={row.id} value={row.id}>{row.code} {row.source_site || ''}</option>)}</select></td>
          <td>{location?.name || line.source_location_name}</td>
          <td><input aria-label={'批号行' + (index + 1)} value={line.batch_number || ''} maxLength={80} disabled={locked || busy} onChange={event => editLine(index, 'batch_number', event.target.value)} /></td>
          <td><input aria-label={'备注行' + (index + 1)} value={line.notes || ''} maxLength={240} disabled={locked || busy} onChange={event => editLine(index, 'notes', event.target.value)} /></td>
          {DISPLAY_COLUMNS.map(([key]) => <td key={key}>{key === 'delivery_amount' ? (Number(line.actual_quantity || 0) * Number(line.unit_price || 0)).toFixed(2) : key === 'physical_quantity' ? quantity(Number(line.actual_quantity || 0) + Number(line.actual_spare_quantity || 0)) : line[key] ?? ''}</td>)}
          <td><button type="button" title="拆分库位或批号" disabled={locked || busy} onClick={() => setLines(current => [...current, { ...line, id: undefined, line_number: undefined, actual_quantity: '0', actual_spare_quantity: '0', source_location: '', batch_number: '' }])}><Copy size={15} /></button><button type="button" title="删除明细" disabled={locked || busy} onClick={() => setLines(current => current.filter((_, i) => i !== index))}><Trash2 size={15} /></button></td>
        </tr>
      })}{!lines.length && <tr><td colSpan={29} className="delivery-empty">暂无明细</td></tr>}</tbody></table></div></section>
      <div className="modal-foot"><span>{values.created_by ? '录入人：' + values.created_by : ''}</span><button type="button" className="secondary" onClick={close} disabled={busy}>关闭</button><button type="submit" className="primary" disabled={locked || busy}><Save size={16} />{busy ? '保存中…' : '保存'}</button></div>
    </form></div>
    {confirmNumber && <div className="modal-backdrop delivery-overlay"><div className="modal delivery-confirm" role="dialog" aria-modal="true" aria-label="生成新单号"><div className="modal-head"><h2>是否自动生成新单号？</h2></div><div className="modal-foot"><button type="button" onClick={() => setConfirmNumber(false)} disabled={busy}>否</button><button type="button" className="primary" onClick={reserveNumber} disabled={busy}>是</button></div></div></div>}
    {generator && <OrderGenerator token={token} customer={values.customer} delivery={record?.id} documentType={values.document_type} existing={lines} onClose={() => setGenerator(false)} onGenerate={rows => { setLines(current => [...current, ...rows]); setGenerator(false); setGeneratedCount(rows.length) }} />}
    {generatedCount !== null && <div className="modal-backdrop delivery-overlay"><div className="modal delivery-confirm" role="dialog" aria-modal="true" aria-label="生成完成"><div className="modal-head"><h2>生成完成，共添加 {generatedCount} 行明细</h2></div><div className="modal-foot"><button type="button" className="primary" onClick={() => setGeneratedCount(null)}>确定</button></div></div></div>}
  </>
}
