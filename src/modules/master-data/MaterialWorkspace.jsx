import { useEffect, useRef, useState } from 'react'
import { Check, CheckCheck, ChevronFirst, ChevronLast, ChevronLeft, ChevronRight, Download, Plus, Printer, RefreshCw, RotateCcw, Save, Search, Trash2, Undo2 } from 'lucide-react'
import { api, download } from '../../api/client'
import { can } from '../../auth/session'
import { SearchableLookup } from '../../components/Field'
import { masterDataConfigs } from './configs'
import '../purchase/supplier-workspace.css'
import './material-workspace.css'

const states = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
const tabs = [
  ['basic', '基本属性'],
  ['engineering', '工程属性'],
  ['inventory', '库存属性'],
  ['mrp', 'MRP 属性']
]
const groups = {
  basic: new Set(['name', 'english_name', 'category', 'uom', 'old_code', 'customs_code', 'customs_name', 'barcode', 'tax_master', 'tax_name', 'invoice_name', 'purpose']),
  engineering: new Set(['join_date', 'part_type', 'product_group', 'active', 'engineering_reviewer', 'specification', 'carton_mark', 'gross_weight_g', 'net_weight_g', 'length', 'width', 'height', 'volume', 'version', 'drawing_number', 'scrap_rate', 'products_per_carton']),
  inventory: new Set(['default_location', 'default_storage_position', 'batch_control', 'batch_rule', 'abc_class', 'count_cycle_days', 'shelf_life_days', 'warehouse_manager']),
  mrp: new Set(['safety_stock_qty', 'max_stock_qty', 'stock_warning_qty', 'production_lead_days', 'purchase_lead_days', 'quality_control', 'quality_lead_days', 'supply_method', 'phantom', 'roll', 'min_purchase_qty', 'min_pack_qty', 'min_issue_qty', 'receipt_consume_mode', 'outsource_receipt_consume_mode', 'buyer', 'planner', 'default_supplier', 'production_line', 'order_strategy', 'order_qty', 'order_period_days', 'over_receipt_ratio', 'default_operation', 'scheduling_class', 'low_level_code', 'plan_order', 'non_production', 'purchase_quote_unrestricted', 'sales_quote_unrestricted', 'issue_qty_unrestricted', 'outsource_surplus_excluded_from_mrp'])
}

const blank = () => ({ name: '', english_name: '', category: null, uom: null, old_code: '', customs_code: '', customs_name: '', barcode: '', tax_master: null, tax_code: '', tax_name: '', invoice_name: '', purpose: '', default_location: null, default_storage_position: '', batch_control: false, batch_rule: '', quality_control: 'required', supply_method: 'purchase', plan_order: true, min_issue_qty: 1, active: true })
const text = (value) => value == null ? '' : String(value)
const dateTime = (value) => value ? String(value).replace('T', ' ').slice(0, 19) : ''

function Tool({ icon: Icon, children, onClick, disabled }) {
  return <button type="button" title={children} disabled={disabled} onClick={onClick}><Icon size={17} /><span>{children}</span></button>
}

function Lookup({ field, value, options, disabled, onChange, onSearch, tax = false }) {
  const optionCode = (row) => row.code || row.number || ''
  const optionText = (row) => tax ? [row.code, row.name, row.invoice_name].filter(Boolean).join(' ') : [row.code, row.name, row.description].filter(Boolean).join(' ')
  return <SearchableLookup label={field.label} value={value} options={options} onSearch={onSearch} onChange={onChange} disabled={disabled} required={field.required} clearOnFocus allowClear portal hideLabel optionCode={optionCode} optionText={optionText} className="sw-lookup" />
}

function Audit({ doc }) {
  return <aside className="sw-audit"><strong className={doc.status || 'draft'}>{states[doc.status] || '草稿'}</strong>{[['录入人', doc.created_by], ['录入时间', dateTime(doc.created_at)], ['审核人', doc.approved_by], ['审核时间', dateTime(doc.approved_at)], ['最后修改', dateTime(doc.updated_at)]].map(([label, value]) => <div key={label}><span>{label}</span><output>{value || ''}</output></div>)}</aside>
}

export function MaterialWorkspace({ session }) {
  const cfg = masterDataConfigs.materials
  const [doc, setDoc] = useState(blank)
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [tab, setTab] = useState('list')
  const [propertyTab, setPropertyTab] = useState('basic')
  const [query, setQuery] = useState({ code: '', q: '', category: '', exact: '0', page_size: 50 })
  const [applied, setApplied] = useState(null)
  const [page, setPage] = useState(1), [count, setCount] = useState(0)
  const savedDoc = useRef(blank())
  const searchSequence = useRef(0)
  const [dirty, setDirty] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const editable = ['draft', 'rejected', undefined, null, ''].includes(doc.status)
  const locked = busy || !editable || !can(session, 'material', doc.id ? 'change' : 'create')
  const loadRows = async (filters = applied, target = page) => {
    if (!filters) return
    const id = ++searchSequence.current
    setBusy(true); setError('')
    try {
      const result = await request(`/material/search/?${new URLSearchParams({ ...filters, page: target })}`)
      if (id === searchSequence.current) { setRows(result.results); setNotice(''); setCount(result.count); setPage(result.page); setApplied(filters) }
      return result
    } catch (err) { if (id === searchSequence.current) setError(err.message) }
    finally { if (id === searchSequence.current) setBusy(false) }
  }
  const candidateTimers = useRef({})
  const candidateSequences = useRef({})
  const fetchCandidates = async (key, q = '', selected = '') => {
    const id = (candidateSequences.current[key] || 0) + 1
    candidateSequences.current[key] = id
    try {
      const result = await request(`/material/candidates/?${new URLSearchParams({ kind: key, q, selected: selected || '' })}`)
      if (candidateSequences.current[key] === id) setLookups(old => ({ ...old, [key]: result }))
    } catch (err) { if (candidateSequences.current[key] === id) setError(err.message) }
  }
  const searchCandidates = (key, q, selected) => {
    clearTimeout(candidateTimers.current[key])
    candidateSequences.current[key] = (candidateSequences.current[key] || 0) + 1
    candidateTimers.current[key] = setTimeout(() => fetchCandidates(key, q, selected), 300)
  }
  useEffect(() => {
    if (tab !== 'edit') return
    for (const key of groups[propertyTab]) {
      const item = cfg.fields.find(f => f.key === key)
      if (item?.lookup) fetchCandidates(item.lookup, '', doc[key])
    }
    return () => {
      Object.values(candidateTimers.current).forEach(clearTimeout)
      for (const key of Object.keys(candidateSequences.current)) candidateSequences.current[key]++
    }
  }, [tab, propertyTab, doc.id, session.token])
  useEffect(() => () => { searchSequence.current++ }, [])
  const set = (key, value) => { setDoc((current) => ({ ...current, [key]: value })); setDirty(true) }
  const load = (row) => { savedDoc.current = { ...blank(), ...row }; setDoc({ ...blank(), ...row }); setDirty(false); setTab('edit'); setPropertyTab('basic'); setError('') }
  const select = async (row) => {
    if (dirty && !window.confirm('放弃未保存的修改？')) return
    setBusy(true); setError('')
    try { load(row.id ? await request(`/material/${row.id}/`) : row) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  const navigate = async (position) => {
    if (!applied || (dirty && !window.confirm('放弃未保存的修改？'))) return
    const size = Number(applied.page_size), target = Math.floor(position / size) + 1
    const result = target === page ? { results: rows } : await loadRows(applied, target)
    const row = result?.results[position % size]
    if (row) { setDirty(false); setBusy(true); try { load(await request(`/material/${row.id}/`)) } catch (err) { setError(err.message) } finally { setBusy(false) } }
  }
  const exportRows = async () => {
    setBusy(true); setError('')
    try { const file = await download('/material/search-export/', { token: session.token, body: { filters: applied } }); const url = URL.createObjectURL(file.blob); const a = document.createElement('a'); a.href = url; a.download = file.filename; a.click(); URL.revokeObjectURL(url) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  const activeOptions = (name, value) => (lookups[name] || []).filter((row) => String(row.id) === String(value) || (row.active !== false && row.status !== 'void' && !row.disabled))
  const category = (lookups.categories || []).find((row) => String(row.id) === String(doc.category))
  const tax = (lookups.taxCodes || []).find((row) => String(row.id) === String(doc.tax_master))
  const update = (key, value) => {
    if (key === 'tax_master') {
      const selected = (lookups.taxCodes || []).find((row) => String(row.id) === String(value))
      setDoc((current) => ({ ...current, tax_master: value, tax_code: selected?.code || '', tax_name: selected?.name || '', invoice_name: selected?.invoice_name || '' })); setDirty(true); return
    }
    if (key === 'category') {
      const selected = (lookups.categories || []).find((row) => String(row.id) === String(value))
      const defaults = [['uom', selected?.default_uom], ['default_location', selected?.default_location], ['supply_method', selected?.supply_method], ['part_type', selected?.part_type], ['product_group', selected?.product_group], ['buyer', selected?.buyer], ['quality_control', selected?.quality_control], ['phantom', selected?.phantom], ['roll', selected?.roll], ['batch_control', selected?.batch_control], ['batch_rule', selected?.batch_rule]]
      const changed = defaults.filter(([defaultKey, next]) => next != null && next !== '' && text(doc[defaultKey]) !== text(next))
      if (changed.length && !window.confirm('是否套用所选产品类的默认单位、库位及属性？')) { set('category', value); return }
      for (const [key, next] of defaults) { const item = cfg.fields.find(f => f.key === key); if (item?.lookup && next) fetchCandidates(item.lookup, '', next) }
      setDoc((current) => ({ ...current, category: value, ...Object.fromEntries(defaults.filter(([, next]) => next != null && next !== '').map(([key, next]) => [key, next])) })); setDirty(true); return
    }
    set(key, value)
  }
  const save = async () => {
    setBusy(true); setError(''); setNotice('')
    try {
      const payload = Object.fromEntries(Object.entries(doc).filter(([key, value]) => !['code', 'tax_code', 'tax_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'approved_by', 'approved_at', 'status'].includes(key) && (value !== '' || key === 'invoice_name') && value !== undefined))
      const saved = await request(doc.id ? `/material/${doc.id}/` : '/material/', { method: doc.id ? 'PATCH' : 'POST', body: payload })
      load(saved); await loadRows(); setNotice('已保存物料')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  const action = async (name) => { setBusy(true); setError(''); try { load(await request(`/material/${doc.id}/${name}/`, { method: 'POST' })); await loadRows(); setNotice('操作完成') } catch (err) { setError(err.message) } finally { setBusy(false) } }
  const remove = async () => { if (!window.confirm('确认删除物料？')) return; setBusy(true); try { await request(`/material/${doc.id}/`, { method: 'DELETE' }); load(blank()); await loadRows(); setNotice('已删除物料') } catch (err) { setError(err.message) } finally { setBusy(false) } }
  const filtered = rows
  const related = (name, value) => { const row = (lookups[name] || []).find((item) => String(item.id) === String(value)); return row ? [row.code, row.name].filter(Boolean).join(' ') : '' }
  const localIndex = rows.findIndex((row) => row.id === doc.id)
  const index = localIndex < 0 ? -1 : (page - 1) * Number(applied?.page_size || 50) + localIndex
  const fieldByKey = Object.fromEntries(cfg.fields.map((item) => [item.key, item]))
  const renderField = (key) => {
    const item = fieldByKey[key]; if (!item) return null
    const derived = ['tax_name'].includes(key) || ['code'].includes(key)
    const disabled = locked || derived
    let node
    if (item.lookup) node = <Lookup field={item} value={doc[key]} options={activeOptions(item.lookup, doc[key])} disabled={disabled} onChange={(value) => update(key, value)} onSearch={q => searchCandidates(item.lookup, q, doc[key])} tax={item.lookup === 'taxCodes'} />
    else if (item.kind === 'readonly' || derived) node = <input value={text(doc[key] || (key === 'tax_name' ? tax?.name : ''))} readOnly />
    else if (item.kind === 'checkbox') node = <input type="checkbox" checked={Boolean(doc[key])} disabled={disabled} onChange={(event) => update(key, event.target.checked)} />
    else if (item.kind === 'select') node = <select value={doc[key] ?? ''} disabled={disabled} onChange={(event) => update(key, event.target.value)}><option value="">请选择</option>{(item.options || []).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>
    else node = <input type={item.kind === 'number' ? 'number' : item.kind === 'date' ? 'date' : 'text'} step={item.kind === 'number' ? 'any' : undefined} value={text(doc[key])} disabled={disabled} onChange={(event) => update(key, event.target.value)} />
    if (key === 'active') return <div className="mt-use-state" key={key}>
      <label className="sw-field sw-check"><span>{item.label}</span><input type="checkbox" checked={Boolean(doc.active)} disabled={disabled} aria-describedby="material-use-help" onChange={(event) => update('active', event.target.checked)} /></label>
      <div id="material-use-help" className="mt-use-help" aria-live="polite">
        <strong>{doc.active ? '使用中' : '不在使用中'}{dirty ? '（有未保存修改）' : ''}</strong>
        <span>已审核且使用中的物料可用于新增请购、采购；其他业务条件仍需满足。</span>
        {!doc.active && <span>当前未勾选“使用中”，保存并审核后仍不可用于新增请购、采购。</span>}
        {doc.status === 'approved' && <span>请先反审核，修改并保存后重新提交、审核。反审核期间，该物料暂不可用于新增请购、采购。</span>}
      </div>
    </div>
    return <label className={`sw-field ${item.kind === 'checkbox' ? 'sw-check' : ''}`} key={key}><span>{item.label}{item.required ? <em>*</em> : null}</span>{node}</label>
  }
  return <section className="sw-workspace mt-workspace" aria-label="物料信息">
    <div className="sw-toolbar"><Tool icon={Search} disabled={busy} onClick={() => { if (!dirty || window.confirm('保留未保存的修改并查看列表？')) { setTab('list'); loadRows(query, 1) } }}>查询</Tool><Tool icon={Plus} disabled={!can(session, 'material', 'create') || busy} onClick={() => select(blank())}>新增</Tool><Tool icon={Save} disabled={locked || !dirty} onClick={save}>保存</Tool><Tool icon={Undo2} disabled={!dirty || busy} onClick={() => { if (window.confirm('放弃未保存的修改？')) { load(savedDoc.current) } }}>取消</Tool><Tool icon={Trash2} disabled={!doc.id || locked || !can(session, 'material', 'delete')} onClick={remove}/><Tool icon={CheckCheck} disabled={!doc.id || dirty || !['draft', 'rejected'].includes(doc.status) || !can(session, 'material', 'submit')} onClick={() => action('submit')}>提交</Tool><Tool icon={Check} disabled={!doc.id || dirty || doc.status !== 'pending' || !can(session, 'material', 'approve')} onClick={() => action('approve')}>审核</Tool><Tool icon={RotateCcw} disabled={!doc.id || doc.status !== 'approved' || !can(session, 'material', 'approve')} onClick={() => action('unapprove')}>反审核</Tool><i /><Tool icon={ChevronFirst} disabled={busy || !count} onClick={() => navigate(0)}>首笔</Tool><Tool icon={ChevronLeft} disabled={busy || index <= 0} onClick={() => navigate(index - 1)}>上笔</Tool><Tool icon={ChevronRight} disabled={busy || index < 0 || index >= count - 1} onClick={() => navigate(index + 1)}>下笔</Tool><Tool icon={ChevronLast} disabled={busy || !count} onClick={() => navigate(count - 1)}>末笔</Tool><Tool icon={Printer} disabled={!doc.id} onClick={() => window.print()}>打印</Tool><Tool icon={Download} disabled={busy || !applied || !count} onClick={exportRows}>导出</Tool><Tool icon={RefreshCw} disabled={busy} onClick={() => loadRows()}>刷新</Tool></div>
    <div className="sw-tabs"><button className={tab === 'edit' ? 'active' : ''} onClick={() => setTab('edit')}>资料维护</button><button className={tab === 'list' ? 'active' : ''} onClick={() => { if (!dirty || window.confirm('保留未保存的修改并查看列表？')) setTab('list') }}>资料浏览</button><h1>物料信息</h1></div>
    {error && <div className="sw-error">{error}</div>}{notice && <div className="sw-notice">{notice}</div>}
    {tab === 'list' ? <><form className="sw-filter mt-search" onSubmit={e => { e.preventDefault(); loadRows(query, 1) }}>
      {[['code', '物料编码'], ['q', '名称或规格'], ['category', '产品类编码或名称']].map(([key, label]) => <label key={key}>{label}<input aria-label={label} value={query[key]} onChange={e => setQuery(old => ({ ...old, [key]: e.target.value }))}/></label>)}
      <label><input type="checkbox" checked={query.exact === '1'} onChange={e => setQuery(old => ({ ...old, exact: e.target.checked ? '1' : '0' }))}/>编码精确匹配</label>
      <select aria-label="审核状态" value={query.status || ''} onChange={e => setQuery(old => ({ ...old, status: e.target.value }))}><option value="">全部审核状态</option>{Object.entries(states).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
      <select aria-label="使用状态" value={query.active || ''} onChange={e => setQuery(old => ({ ...old, active: e.target.value }))}><option value="">全部使用状态</option><option value="1">使用中</option><option value="0">不在使用中</option></select>
    </form><div className="sw-grid"><table><thead><tr>{['物料编码', '物料名称', '产品类', '单位', '默认库位', '供应方式', '状态', '使用状态'].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{filtered.map((row) => <tr key={row.id}><td className="sw-code-cell" title={row.code}><button className="sw-link" onClick={() => select(row)}>{row.code}</button></td><td>{row.name}</td><td>{row.category_code || category?.code}</td><td>{row.uom_code}</td><td>{row.default_location_code}</td><td>{row.supply_method}</td><td>{states[row.status]}</td><td>{row.active ? '使用中' : '不在使用中'}</td></tr>)}</tbody></table>{!filtered.length && <p className="sw-empty">{busy ? '正在检索…' : applied ? '无匹配物料' : '点击查询显示全部物料，输入条件后查询显示匹配物料'}</p>}</div></> : <><div className="sw-head mt-head"><div className="sw-fields"><label className="sw-field"><span>物料编码</span><input title={doc.code || ''} value={doc.code || ''} placeholder="保存时生成" readOnly /></label><label className="sw-field"><span>物料名称</span><input value={doc.name || '新物料'} readOnly /></label></div><Audit doc={doc}/></div><div className="material-property-tabs">{tabs.map(([id, label]) => <button key={id} className={propertyTab === id ? 'active' : ''} onClick={() => setPropertyTab(id)}>{label}</button>)}</div><div className="sw-fields mt-fields">{Array.from(groups[propertyTab]).map(renderField)}</div></>}
    <footer className="sw-footer">{tab === 'list' && <><button disabled={busy || page <= 1} onClick={() => loadRows(applied, page - 1)}>上一页</button><span>{page} / {Math.max(1, Math.ceil(count / Number(applied?.page_size || 50)))}</span><button disabled={busy || page * Number(applied?.page_size || 50) >= count} onClick={() => loadRows(applied, page + 1)}>下一页</button><select aria-label="每页条数" value={query.page_size} onChange={e => { const next = { ...query, page_size: Number(e.target.value) }; setQuery(next); if (applied) loadRows({ ...applied, page_size: next.page_size }, 1) }}><option value="50">50条/页</option><option value="100">100条/页</option></select></>}<span>记录数 {tab === 'list' ? count : doc.id ? 1 : 0}</span><span>{busy ? '处理中' : dirty ? '未保存' : states[doc.status] || '草稿'}</span><span>{doc.code || ''}</span>{doc.id && applied && localIndex < 0 && <span>当前物料不在本页查询结果中</span>}</footer>
  </section>
}
