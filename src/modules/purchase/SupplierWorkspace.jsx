import { useEffect, useMemo, useRef, useState } from 'react'
import { Check, CheckCheck, ChevronFirst, ChevronLast, ChevronLeft, ChevronRight, Download, Minus, Plus, Printer, RefreshCw, RotateCcw, Save, Search, Trash2, Undo2, X } from 'lucide-react'
import { api, listPayload } from '../../api/client'
import { can } from '../../auth/session'
import { SearchableLookup } from '../../components/Field'
import './supplier-workspace.css'
import { SupplierDetails as PartnerSheet } from './SupplierDetails'

const today = () => new Date().toLocaleDateString('en-CA')
const states = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
const number = (value) => value == null || value === '' ? '' : String(value)
const dateTime = (value) => value ? String(value).replace('T', ' ').slice(0, 19) : ''
const partnerBlank = () => ({ kind: 'supplier', code: '', name: '', short_name: '', address: '', website: '', opening_date: null, quote_tax_included: true, service_score: '0', backup_ratio: '0', over_receipt_ratio: '0', registered_capital: '0', annual_revenue: '0', employee_count: 0, material_price_factor: '0', buyer: '', currency: null, payment_method_master: null, payment_terms: '', tax_rate: '0', quote_method: '', invoice_type: '', tax_calculation_method: '', supplier_type: '', default_receipt_location: null, payment_bank: '', bank_account: '', legal_person: '', tax_number: '', notes: '', contacts: [], strategic_supplier: false, payment_hold: false, internal_company: false, quoted_settlement: false, three_certificates: false, business_license: false })
const quoteBlank = () => ({ supplier: null, material: null, business_group: null, quote_type: 'purchase', effective_date: today(), expiry_date: '', material_unit_price: '', processing_unit_price: '', min_purchase_qty: '', min_pack_qty: '', delivery_days: '', operation: null, notes: '', lines: [] })

function Tool({ icon: Icon, children, onClick, disabled }) {
  return <button type="button" title={children} disabled={disabled} onClick={onClick}><Icon size={17} /><span>{children}</span></button>
}

function CodeNameLookup({ label, value, options, onChange, onSearch, disabled = false, required = false, code = (row) => row.code || row.number || '', name = (row) => row.name || row.description || '' }) {
  const selected = options.find((row) => String(row.id) === String(value))
  return <div className="sw-code-name"><SearchableLookup label={label} value={value} options={options} onChange={onChange} onSearch={onSearch} disabled={disabled} required={required} clearOnFocus allowClear portal hideLabel optionCode={code} className="sw-lookup" /><output title={name(selected || {})}>{name(selected || {})}</output>{label === '物料编码' && selected && <output className="sw-full-code">{code(selected)}</output>}</div>
}

function Audit({ doc, quote = false }) {
  return <aside className="sw-audit"><strong className={doc.status || 'draft'}>{states[doc.status] || '草稿'}</strong>{[
    ['录入人', doc.created_by], ['录入时间', dateTime(doc.created_at)],
    ...(quote ? [['采购确认人', doc.confirmed_by], ['审核人', doc.approved_by], ['核准人', doc.ratified_by], ['销售确认人', doc.sales_confirmed_by]] : [['审核人', doc.approved_by], ['审核时间', dateTime(doc.approved_at)]])
  ].map(([label, value]) => <div key={label}><span>{label}</span><output>{value || ''}</output></div>)}</aside>
}

function CheckField({ label, value, onChange, disabled }) {
  return <label className="sw-check"><input type="checkbox" checked={Boolean(value)} disabled={disabled} onChange={(event) => onChange(event.target.checked)} />{label}</label>
}

export function SupplierWorkspace({ mode, session }) {
  const isQuote = mode === 'quote'
  const title = isQuote ? '供应商报价' : '供应商资料'
  const resource = isQuote ? 'supplier-quote' : 'partner'
  const [doc, setDoc] = useState(() => isQuote ? quoteBlank() : partnerBlank())
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [tab, setTab] = useState(isQuote ? 'list' : 'edit')
  const [query, setQuery] = useState('')
  const [appliedQuery, setAppliedQuery] = useState('')
  const [page, setPage] = useState(1)
  const [count, setCount] = useState(0)
  const [selected, setSelected] = useState(null)
  const [dirty, setDirty] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const savedDoc = useRef(null)
  const lookupSequence = useRef({})
  const blank = () => isQuote ? quoteBlank() : partnerBlank()
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const permitted = (action) => can(session, isQuote ? 'supplier_quote' : 'partner', action)
  const editable = !doc.status || ['draft', 'rejected'].includes(doc.status)
  const locked = busy || !editable || !permitted(doc.id ? 'change' : 'create')
  const run = async (fn) => { setBusy(true); setError(''); setNotice(''); try { await fn() } catch (err) { setError(err.message) } finally { setBusy(false) } }
  const reload = async (search = appliedQuery, targetPage = page) => {
    const params = isQuote ? `?${new URLSearchParams({ page: targetPage, page_size: 50, q: search })}` : ''
    const result = await request(`/${resource}/${params}`)
    const records = listPayload(result)
    setRows(isQuote ? records : records.filter((row) => ['supplier', 'both'].includes(row.kind)))
    if (isQuote) setCount(result.count ?? records.length)
    return records
  }
  const ensureQuoteLookups = async () => {
    if (!isQuote || lookups.currency) return
    const entries = await Promise.all(['currency', 'uom', 'routing-operation', 'business-group']
      .map(async (item) => [item, listPayload(await request(`/${item}/`))]))
    setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
  }
  const searchLookup = async (kind, query = '', selected = doc[kind === 'partner' ? 'supplier' : 'material']) => {
    const sequence = (lookupSequence.current[kind] || 0) + 1
    lookupSequence.current[kind] = sequence
    const path = kind === 'material' ? `/material/sales-candidates/?${new URLSearchParams({ q: query, usage: 'purchase' })}`
      : `/material/candidates/?${new URLSearchParams({ kind: 'suppliers', q: query, selected: selected || '' })}`
    const rows = listPayload(await request(path))
    if (selected && !rows.some(row => String(row.id) === String(selected))) rows.push(await request(`/${kind}/${selected}/`))
    if (lookupSequence.current[kind] === sequence) setLookups(previous => ({ ...previous, [kind]: rows }))
  }
  useEffect(() => {
    let live = true
    if (isQuote) run(() => reload('', 1))
    else run(async () => {
      const resources = ['currency', 'payment-method', 'location', 'employee', 'accounting-account']
      const entries = await Promise.all(resources.map(async (item) => [item, listPayload(await request(`/${item}/`))]))
      if (live) { setLookups(Object.fromEntries(entries)); await reload() }
    })
    return () => { live = false }
  }, [mode, session.token])
  useEffect(() => {
    if (isQuote && tab === 'edit') run(async () => {
      await Promise.all([ensureQuoteLookups(), searchLookup('partner'), searchLookup('material')])
    })
  }, [isQuote, tab, doc.id])
  const set = (key, value) => { setDoc((previous) => ({ ...previous, [key]: value, ...(isQuote && key === 'supplier' ? { currency: (lookups.partner || []).find(row => row.id === Number(value))?.currency || null } : {}) })); setDirty(true) }
  const load = (row) => { savedDoc.current = row; setDoc({ ...row, contacts: row.contacts || [], bank_accounts: row.bank_accounts || [], lines: row.lines || [] }); setDirty(false); setSelected(null); setTab('edit'); setError('') }
  const select = (row) => { if (!dirty || window.confirm('放弃未保存的修改？')) load(row) }
  const options = (name, value) => (lookups[name] || []).filter((row) => String(row.id) === String(value) || (row.active !== false && row.status !== 'void' && !row.disabled))
  const supplierRows = options('partner', doc.supplier).filter((row) => ['supplier', 'both'].includes(row.kind) && (String(row.id) === String(doc.supplier) || row.status === 'approved'))
  const materialRows = options('material', doc.material).filter((row) => String(row.id) === String(doc.material) || (row.active && row.status === 'approved'))
  const supplier = supplierRows.find((row) => String(row.id) === String(doc.supplier))
  const material = materialRows.find((row) => String(row.id) === String(doc.material))
  const currency = (lookups.currency || []).find((row) => row.id === Number(doc.currency || supplier?.currency))
  const purchaseUom = (lookups.uom || []).find((row) => row.id === Number(doc.purchase_uom || material?.uom))
  const isOutsource = doc.quote_type === 'outsource'
  const priceKey = isOutsource ? 'processing_unit_price' : 'material_unit_price'
  const priceLabel = isOutsource ? '加工单价' : '材料单价'
  const taxRate = Number(supplier?.tax_rate ?? doc.tax_rate ?? 0)
  const price = Number(doc[priceKey] || 0)
  const transition = (action) => run(async () => { load(await request(`/${resource}/${doc.id}/${action}/`, { method: 'POST' })); await reload(); setNotice('操作完成') })
  const save = () => run(async () => {
    const body = isQuote ? {
      supplier: doc.supplier, material: doc.material, business_group: doc.business_group, quote_type: doc.quote_type,
      effective_date: doc.effective_date, expiry_date: doc.expiry_date || null,
      material_unit_price: isOutsource ? '0' : doc.material_unit_price || '0', processing_unit_price: isOutsource ? doc.processing_unit_price || '0' : '0',
      min_purchase_qty: doc.min_purchase_qty || '0', min_pack_qty: doc.min_pack_qty || '0', delivery_days: doc.delivery_days || '0', operation: isOutsource ? doc.operation : null, notes: doc.notes || '',
      lines: (doc.lines || []).map((line, index) => ({ line_number: line.line_number || index + 1, min_qty: line.min_qty || '0', material_unit_price: isOutsource ? null : line.material_unit_price || '0', processing_unit_price: isOutsource ? line.processing_unit_price || '0' : null, notes: line.notes || '' }))
    } : { ...doc, kind: doc.kind || 'supplier', contacts: (doc.contacts || []).filter((contact) => contact.name) }
    const saved = await request(doc.id ? `/${resource}/${doc.id}/` : `/${resource}/`, { method: doc.id ? 'PATCH' : 'POST', body })
    load(saved); await reload(); setNotice('已保存')
  })
  const remove = () => run(async () => { if (!window.confirm(`确认删除${title}？`)) return; await request(`/${resource}/${doc.id}/`, { method: 'DELETE' }); load(blank()); await reload(); setNotice('已删除') })
  const exportCsv = async () => {
    let exportRows = rows
    if (isQuote) {
      exportRows = []
      for (let current = 1; current <= Math.ceil(count / 100); current++) {
        const result = await request(`/${resource}/?${new URLSearchParams({ page: current, page_size: 100, q: appliedQuery })}`)
        exportRows.push(...listPayload(result))
      }
    }
    const cols = isQuote ? ['报价单号', '供应商代码', '供应商名称', '物料编码', '物料名称', '报价类型', '含税单价', '生效日期', '失效日期', '状态'] : ['供应商代码', '供应商名称', '简称', '币种', '采购员', '状态']
    const values = exportRows.map((row) => isQuote ? [row.number, row.supplier_code, row.supplier_name, row.material_code, row.material_name, row.quote_type === 'outsource' ? '外协报价' : '采购报价', row.unit_price, row.effective_date, row.expiry_date, states[row.status]] : [row.code, row.name, row.short_name, (lookups.currency || []).find((item) => item.id === row.currency)?.code, row.buyer, states[row.status]])
    const quote = (value) => `"${String(value ?? '').replace(/^[=+@-]/, "'$&").replaceAll('"', '""')}"`
    const url = URL.createObjectURL(new Blob(['\ufeff' + [cols, ...values].map((row) => row.map(quote).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' }))
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${title}.csv`; anchor.click(); URL.revokeObjectURL(url)
  }
  const index = rows.findIndex((row) => row.id === doc.id)
  const filtered = useMemo(() => isQuote ? rows : rows.filter((row) => Object.values(row).join(' ').toLowerCase().includes(query.toLowerCase())), [rows, query, isQuote])
  const startNew = () => run(async () => { await ensureQuoteLookups(); select(blank()) })
  const navigate = destination => run(async () => {
    if (dirty && !window.confirm('放弃未保存的修改？')) return
    let targetPage = page, targetIndex = destination
    if (isQuote) {
      if (destination === 'first') { targetPage = 1; targetIndex = 0 }
      else if (destination === 'last') { targetPage = Math.max(1, Math.ceil(count / 50)); targetIndex = -1 }
      else if (destination < 0) { targetPage = page - 1; targetIndex = -1 }
      else if (destination >= rows.length) { targetPage = page + 1; targetIndex = 0 }
    } else targetIndex = destination === 'first' ? 0 : destination === 'last' ? -1 : destination
    const records = targetPage === page ? rows : await reload(appliedQuery, targetPage)
    setPage(targetPage)
    if (records.at(targetIndex)) load(records.at(targetIndex))
  })
  const head = (label, node) => <label className="sw-field"><span>{label}</span>{node}</label>
  const input = (label, key, type = 'text', readOnly = false) => head(label, <input aria-label={label} type={type} value={number(doc[key])} readOnly={readOnly} disabled={locked && !readOnly} onChange={(event) => set(key, type === 'date' && !event.target.value ? null : event.target.value)} />)
  const lineKey = isQuote ? 'lines' : 'bank_accounts'
  const lineRows = doc[lineKey] || []
  const addLine = () => { const line = isQuote ? { line_number: Math.max(0, ...lineRows.map(row => row.line_number || 0)) + 1, min_qty: '', material_unit_price: '', processing_unit_price: '', notes: '' } : { line_number: Math.max(0, ...lineRows.map(row => row.line_number || 0)) + 10, account_type: 'company', bank_name: '', account_name: '', account_number: '', other_info: '', notes: '', bank_code: '' }; set(lineKey, [...lineRows, line]); setSelected(lineRows.length) }
  const updateLine = (index, key, value) => set(lineKey, lineRows.map((line, lineIndex) => lineIndex === index ? { ...line, [key]: value } : line))
  return <section className="sw-workspace" aria-label={title}>
    <div className="sw-toolbar"><Tool icon={Search} onClick={() => setTab('list')}>查询</Tool><Tool icon={Plus} disabled={!permitted('create') || busy} onClick={startNew}>新增</Tool><Tool icon={Save} disabled={locked || !dirty} onClick={save}>保存</Tool><Tool icon={Undo2} disabled={!dirty || busy} onClick={() => select(savedDoc.current || blank())}>取消</Tool><Tool icon={Trash2} disabled={!doc.id || locked || !permitted('delete')} onClick={remove}>删除</Tool><Tool icon={Plus} disabled={locked} onClick={addLine}>增行</Tool><Tool icon={Minus} disabled={locked || selected == null} onClick={() => { set(lineKey, lineRows.filter((_, index) => index !== selected)); setSelected(null) }}>删行</Tool>
      {isQuote ? <><Tool icon={Check} disabled={!doc.id || dirty || !['draft', 'rejected'].includes(doc.status) || !permitted('confirm')} onClick={() => transition('confirm')}>采购确认</Tool><Tool icon={X} disabled={!doc.id || dirty || doc.status !== 'pending' || !permitted('confirm')} onClick={() => transition('unconfirm')}>采购反确认</Tool><Tool icon={CheckCheck} disabled={!doc.id || dirty || doc.status !== 'pending' || !permitted('approve')} onClick={() => transition('approve')}>审核</Tool><Tool icon={RotateCcw} disabled={!doc.id || doc.status !== 'approved' || !permitted('approve')} onClick={() => transition('unapprove')}>反审核</Tool><Tool icon={CheckCheck} disabled={!doc.id || doc.status !== 'approved' || doc.is_ratified || !permitted('ratify')} onClick={() => transition('ratify')}>核准</Tool><Tool icon={RotateCcw} disabled={!doc.id || !doc.is_ratified || !permitted('ratify')} onClick={() => transition('unratify')}>反核准</Tool><Tool icon={Check} disabled={!doc.id || !doc.is_ratified || doc.is_sales_confirmed || !permitted('approve')} onClick={() => transition('sales-confirm')}>销售确认</Tool><Tool icon={X} disabled={!doc.id || !doc.is_sales_confirmed || !permitted('approve')} onClick={() => transition('sales-unconfirm')}>销售反确认</Tool></> : <><Tool icon={CheckCheck} disabled={!doc.id || doc.status !== 'draft' || !permitted('submit')} onClick={() => transition('submit')}>提交</Tool><Tool icon={Check} disabled={!doc.id || doc.status !== 'pending' || !permitted('approve')} onClick={() => transition('approve')}>审核</Tool><Tool icon={RotateCcw} disabled={!doc.id || doc.status !== 'approved' || !permitted('approve')} onClick={() => transition('unapprove')}>反审核</Tool></>}
      {!isQuote && <><Tool icon={Check} disabled={busy || dirty || doc.status !== 'approved' || doc.is_confirmed || !permitted('approve')} onClick={() => transition('confirm')}>确认</Tool><Tool icon={X} disabled={busy || dirty || !doc.is_confirmed || !permitted('approve')} onClick={() => transition('unconfirm')}>反确认</Tool><Tool icon={X} disabled={busy || dirty || !doc.id || doc.status === 'void' || !permitted('delete')} onClick={() => { if (window.confirm('确认作废此供应商？')) transition('void') }}>作废</Tool><Tool icon={RotateCcw} disabled={busy || doc.status !== 'void' || !permitted('change')} onClick={() => transition('restore')}>反作废</Tool></>}
      <i /><Tool icon={ChevronFirst} disabled={busy || !rows.length} onClick={() => navigate("first")}>第一笔</Tool><Tool icon={ChevronLeft} disabled={busy || index < 0 || (index === 0 && (!isQuote || page === 1))} onClick={() => navigate(index - 1)}>上一笔</Tool><Tool icon={ChevronRight} disabled={busy || index < 0 || (index >= rows.length - 1 && (!isQuote || page * 50 >= count))} onClick={() => navigate(index + 1)}>下一笔</Tool><Tool icon={ChevronLast} disabled={busy || !rows.length} onClick={() => navigate("last")}>末一笔</Tool><Tool icon={Printer} disabled={!doc.id} onClick={() => window.print()}>打印</Tool><Tool icon={Download} disabled={busy || !rows.length} onClick={() => run(exportCsv)}>导出</Tool><Tool icon={RefreshCw} disabled={busy} onClick={() => run(reload)}>刷新</Tool></div>
    <div className="sw-tabs"><button className={tab === 'edit' ? 'active' : ''} onClick={() => setTab('edit')}>资料维护</button><button className={tab === 'list' ? 'active' : ''} onClick={() => setTab('list')}>资料浏览</button><h1>{title}</h1></div>
    {error && <div className="sw-error">{error}</div>}{notice && <div className="sw-notice">{notice}</div>}
    {tab === 'list' ? <>
      <form className="sw-filter" onSubmit={event => { event.preventDefault(); if (isQuote) { setAppliedQuery(query); setPage(1); run(() => reload(query, 1)) } }}>
        <Search size={16}/><input aria-label={`查询${title}`} placeholder="输入代码、名称、单号或日期" value={query} onChange={event => setQuery(event.target.value)} />
        {isQuote && <button disabled={busy}>查询</button>}
      </form>
      <div className="sw-grid"><table><thead><tr>{(isQuote ? ['报价单号', '供应商代码', '供应商名称', '物料编码', '物料名称', '类型', '含税单价', '生效日期', '状态'] : ['供应商代码', '供应商全称', '简称', '采购员', '币种', '状态']).map(label => <th key={label}>{label}</th>)}</tr></thead>
        <tbody>{filtered.map(row => <tr key={row.id} onDoubleClick={() => select(row)}><td><button className="sw-link" onClick={() => select(row)}>{isQuote ? row.number : row.code}</button></td>{isQuote ? <><td>{row.supplier_code}</td><td>{row.supplier_name}</td><td className="sw-code-cell" title={row.material_code}>{row.material_code}</td><td>{row.material_name}</td><td>{row.quote_type === 'outsource' ? '外协报价' : '采购报价'}</td><td>{row.unit_price}</td><td>{row.effective_date}</td></> : <><td>{row.name}</td><td>{row.short_name}</td><td>{row.buyer}</td><td>{(lookups.currency || []).find(item => item.id === row.currency)?.code}</td></>}<td>{states[row.status]}</td></tr>)}</tbody>
      </table>{!filtered.length && <p className="sw-empty">暂无记录</p>}</div>
      {isQuote && <footer className="sw-pagination">共 {count} 条<button disabled={busy || page <= 1} onClick={() => { const next = page - 1; setPage(next); run(() => reload(appliedQuery, next)) }}>上一页</button>{page} / {Math.max(1, Math.ceil(count / 50))}<button disabled={busy || page * 50 >= count} onClick={() => { const next = page + 1; setPage(next); run(() => reload(appliedQuery, next)) }}>下一页</button></footer>}
    </> : isQuote ? <QuoteSheet {...{ doc, set, head, input, locked, supplierRows, materialRows, lookups, supplier, material, currency, purchaseUom, isOutsource, priceKey, priceLabel, taxRate, price, lineRows, selected, setSelected, updateLine, searchLookup, setError }} /> : <PartnerSheet {...{ doc, set, head, input, locked, lookups, options, lineRows, selected, setSelected, updateLine }} />}
    <footer className="sw-footer"><span>记录数 {tab === 'list' ? (isQuote ? count : filtered.length) : lineRows.length}</span><span>{busy ? '处理中' : dirty ? '未保存' : states[doc.status] || '草稿'}</span><span>{doc.number || doc.code}</span></footer>
  </section>
}

function QuoteSheet({ doc, set, head, input, locked, supplierRows, materialRows, lookups, supplier, material, currency, purchaseUom, isOutsource, priceKey, priceLabel, taxRate, price, lineRows, selected, setSelected, updateLine, searchLookup, setError }) {
  const operations = (lookups['routing-operation'] || []).filter((row) => row.active !== false)
  const untaxed = price / (1 + taxRate / 100)
  const chooseType = (value) => !locked && set('quote_type', value)
  return <><div className="sw-head"><div className="sw-fields sw-quote-fields">{head('报价单号', <input value={doc.number || ''} readOnly placeholder="保存后生成" />)}{head('供应商', <CodeNameLookup label="供应商" value={doc.supplier} options={supplierRows} onSearch={q => searchLookup("partner", q).catch(error => setError(error.message))} onChange={(value) => set('supplier', value)} disabled={locked} required />)}{head('业务类型', <CodeNameLookup label="业务类型" value={doc.business_group} options={(lookups['business-group'] || []).filter((row) => row.active || row.id === doc.business_group)} onChange={(value) => set('business_group', value)} disabled={locked} required />)}{head('物料编码', <CodeNameLookup label="物料编码" value={doc.material} options={materialRows} onSearch={q => searchLookup("material", q).catch(error => setError(error.message))} onChange={(value) => set('material', value)} disabled={locked} required />)}{head('物料名称', <input value={material?.name || doc.material_name || ''} readOnly />)}{head('物料规格', <input value={material?.specification || doc.material_specification || ''} readOnly />)}{head('币种', <input value={currency?.code || doc.currency_code || ''} readOnly />)}{head('采购单位', <input value={purchaseUom?.code || doc.purchase_uom_code || ''} readOnly />)}{head('报价类型', <div className="sw-segment"><button type="button" className={!isOutsource ? 'active' : ''} disabled={locked} onClick={() => chooseType('purchase')}>采购报价</button><button type="button" className={isOutsource ? 'active' : ''} disabled={locked} onClick={() => chooseType('outsource')}>外协报价</button></div>)}{head('外协工序', isOutsource ? <CodeNameLookup label="外协工序" value={doc.operation} options={operations} onChange={(value) => set('operation', value)} disabled={locked} required code={(row) => row.sequence} name={(row) => row.name} /> : <input value="不适用" readOnly />)}{head('含税方式', <input value={(supplier?.quote_tax_included ?? doc.tax_included) ? '含税' : '未税'} readOnly />)}{head('税率(%)', <input value={taxRate} readOnly />)}{input('生效日期', 'effective_date', 'date')}{input('失效日期', 'expiry_date', 'date')}{input(priceLabel, priceKey, 'number')}{head('含税单价', <input value={price.toFixed(8)} readOnly />)}{head('未税单价', <input value={untaxed.toFixed(8)} readOnly />)}{input('最小采购数量', 'min_purchase_qty', 'number')}{input('最小包装数量', 'min_pack_qty', 'number')}{input('交货天数', 'delivery_days', 'number')}{head('价格说明', <textarea aria-label="价格说明" disabled={locked} value={doc.notes || ''} onChange={(event) => set('notes', event.target.value)} />)}</div><Audit doc={doc} quote /></div><div className="sw-detail-title">数量阶梯价</div><div className="sw-grid"><table className="sw-lines"><thead><tr>{['行号', '数量大于等于', priceLabel, '含税单价', '未税单价', '价格说明'].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{lineRows.map((line, index) => { const tier = Number(line[priceKey] || 0); return <tr key={index} className={selected === index ? 'selected' : ''} onClick={() => setSelected(index)}><td className="sw-derived">{line.line_number || index + 1}</td><td><input type="number" min="0" step="0.00000001" disabled={locked} value={line.min_qty || ''} onChange={(event) => updateLine(index, 'min_qty', event.target.value)} /></td><td><input type="number" min="0" step="0.00000001" disabled={locked} value={line[priceKey] || ''} onChange={(event) => updateLine(index, priceKey, event.target.value)} /></td><td className="sw-derived">{tier.toFixed(8)}</td><td className="sw-derived">{(tier / (1 + taxRate / 100)).toFixed(8)}</td><td><input disabled={locked} value={line.notes || ''} onChange={(event) => updateLine(index, 'notes', event.target.value)} /></td></tr> })}</tbody></table>{!lineRows.length && <p className="sw-empty">未设置阶梯时，采购订单使用主报价单价</p>}</div></>
}
