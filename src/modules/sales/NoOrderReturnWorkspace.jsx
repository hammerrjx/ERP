import { useEffect, useState } from 'react'
import { Plus, Save, Search, Trash2, Check, RotateCcw, Printer, Download } from 'lucide-react'
import { api, listPayload, download } from '../../api/client'
import { can } from '../../auth/session'
import { SearchableLookup } from '../../components/Field'
import './no-order-return.css'

const blank = () => ({ return_date: new Date().toLocaleDateString('en-CA'), site: '1000', lines: [], tax_rate: '0' })
const states = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
const heads = ['customer', 'return_date', 'site', 'currency', 'tax_rate', 'customer_po', 'business_group', 'delivery_address', 'reason']
const lineKeys = ['id', 'material', 'customer_material', 'quantity', 'spare_quantity', 'unit_price', 'return_location', 'batch_number', 'notes']
const columns = [
  ['line_number', '行号'], ['material_code', '物料编码'], ['customer_material_code', '客户物料编码'],
  ['material_name', '物料名称'], ['material_specification', '物料规格'], ['quantity', '退货数量', 'number'],
  ['spare_quantity', '退备品数', 'number'], ['uom_name', '销售单位'], ['unit_price', '单价', 'number'],
  ['amount', '金额'], ['return_location', '退入库位', 'location'], ['location_name', '库位名称'],
  ['batch_number', '批号', 'text'], ['notes', '备注', 'text'], ['uom_rate_m', '单位换算率(分子)'],
  ['uom_rate_d', '单位换算率(分母)'], ['inventory_uom_name', '库存单位'], ['created_by', '录入人'],
  ['created_at', '录入时间'], ['modification_count', '修改次数'], ['updated_by', '修改人'], ['updated_at', '修改时间'],
  ['created_name', '录入姓名'], ['updated_name', '修改姓名'], ['terminal_customer_code', '客户终端物料编码'], ['terminal_customer_name', '客户终端物料名称'],
]
// Exact eight-place decimal arithmetic; the saved result is verified by the server.
function units(value) {
  const match = String(value ?? '0').match(/^(-?)(\d*)(?:\.(\d{0,8}))?$/)
  if (!match) return 0n
  return BigInt((match[2] || '0') + (match[3] || '').padEnd(8, '0')) * (match[1] ? -1n : 1n)
}
function fixed(value, places) {
  const scale = 10n ** BigInt(places), negative = value < 0n, abs = negative ? -value : value
  return `${negative ? '-' : ''}${abs / scale}.${String(abs % scale).padStart(places, '0')}`
}
const cents = (line) => (units(line.quantity) * units(line.unit_price) + 50000000000000n) / 100000000000000n
const pick = (data, keys) => Object.fromEntries(keys.filter(k => data[k] !== undefined).map(k => [k, data[k]]))

export function NoOrderReturnWorkspace({ session }) {
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const [doc, setDoc] = useState(blank), [saved, setSaved] = useState(null), [dirty, setDirty] = useState(false)
  const [rows, setRows] = useState([]), [browse, setBrowse] = useState(false), [search, setSearch] = useState('')
  const [page, setPage] = useState(1), [count, setCount] = useState(0)
  const [lookups, setLookups] = useState({}), [defaults, setDefaults] = useState({})
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState('')
  const [selected, setSelected] = useState(null), [candidate, setCandidate] = useState(null), [materialSearch, setMaterialSearch] = useState('')
  const editable = !busy && !doc.posted && !doc.source_key && (!doc.status || ['draft', 'rejected'].includes(doc.status)) && can(session, 'sales_return', doc.id ? 'change' : 'create')
  const approveAllowed = can(session, 'sales_return', 'approve') && !busy && !dirty && doc.id && !doc.source_key
  const total = fixed(doc.lines.reduce((sum, line) => sum + cents(line), 0n), 2)
  const run = async (fn) => { setBusy(true); setError(''); setNotice(''); try { await fn() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const reload = async (p = page, query = search) => {
    const result = await request(`/no-order-return/?page=${p}&search=${encodeURIComponent(query)}`)
    setRows(result.results); setCount(result.count); setPage(p)
  }
  useEffect(() => { run(async () => {
    const entries = await Promise.all(['partner', 'currency', 'location'].map(async r => [r, listPayload(await request(`/${r}/`))]))
    setLookups(Object.fromEntries(entries)); setDefaults(await request('/no-order-return/defaults/')); await reload(1, '')
  }) }, [session.token])
  useEffect(() => { const warn = e => { if (dirty) { e.preventDefault(); e.returnValue = '' } }; window.addEventListener('beforeunload', warn); return () => window.removeEventListener('beforeunload', warn) }, [dirty])
  useEffect(() => {
    if (!dirty || doc.posted) return
    const rate = (defaults.rates || []).find(r => r.currency_id === Number(doc.currency) && r.effective_date <= doc.return_date && (!r.expiry_date || r.expiry_date >= doc.return_date))
    const currency = (lookups.currency || []).find(r => r.id === Number(doc.currency))
    setDoc(old => ({ ...old, exchange_rate: rate?.rate_to_company || (currency ? '1' : '') }))
  }, [doc.currency, doc.return_date, dirty, defaults.rates, lookups.currency])
  const accept = (value) => { setDoc(value); setSaved(value); setDirty(false); setSelected(null); setBrowse(false) }
  const discard = () => !dirty || window.confirm('放弃未保存的修改？')
  const load = (row) => { if (discard()) run(async () => accept(await request(`/no-order-return/${row.id}/`))) }
  const change = (key, value) => {
    if (!editable) return
    if (key === 'customer' && doc.lines.length && !window.confirm('更换客户将清空明细，是否继续？')) return
    setDoc(old => {
      const customer = (lookups.partner || []).find(r => String(r.id) === String(value))
      return { ...old, [key]: value, ...(key === 'customer' ? { lines: [], currency: customer?.currency, tax_rate: customer?.tax_rate || '0' } : {}) }
    }); setDirty(true)
  }
  const lineSet = (index, key, value) => { if (!editable) return; setDoc(old => ({ ...old, lines: old.lines.map((line, i) => i === index ? { ...line, [key]: value } : line) })); setDirty(true) }
  const save = () => run(async () => {
    const body = { ...pick(doc, heads), ...(doc.id ? { revision: doc.revision } : {}), lines: doc.lines.map(line => pick(line, lineKeys)) }
    accept(await request(doc.id ? `/no-order-return/${doc.id}/` : '/no-order-return/', { method: doc.id ? 'PATCH' : 'POST', body }))
    await reload(); setNotice('已保存')
  })
  const transition = action => run(async () => { accept(await request(`/no-order-return/${doc.id}/${action}/`, { method: 'POST', body: { revision: doc.revision } })); await reload(); setNotice('操作完成') })
  const add = () => { change('lines', [...doc.lines, { line_number: Math.max(0, ...doc.lines.map(l => l.line_number || 0)) + 10, quantity: '0', spare_quantity: '0', unit_price: '0', batch_number: '', notes: '' }]); setSelected(doc.lines.length) }
  const deleteLine = () => { if (selected !== null) { change('lines', doc.lines.filter((_, i) => i !== selected)); setSelected(null) } }
  const newDoc = () => { if (discard()) { accept(blank()); setSaved(null) } }
  const remove = () => { if (window.confirm(`删除退货单 ${doc.number}？`)) run(async () => { await request(`/no-order-return/${doc.id}/`, { method: 'DELETE' }); accept(blank()); await reload() }) }
  const queryMaterials = (index, query = '', p = 1) => run(async () => {
    if (!doc.customer) throw new Error('请先选择客户')
    const result = await request(`/no-order-return/candidates/?customer=${doc.customer}&search=${encodeURIComponent(query)}&page=${p}`)
    setCandidate({ index, ...result }); setMaterialSearch(query)
  })
  const applyMaterial = hit => {
    setDoc(old => ({ ...old, lines: old.lines.map((line, i) => i === candidate.index ? { ...line, ...pick(hit, [...columns.map(c => c[0]), 'material', 'customer_material']) } : line) })); setDirty(true); setCandidate(null)
  }
  const customers = (lookups.partner || []).filter(r => ['customer', 'both'].includes(r.kind))
  const locations = (lookups.location || []).filter(r => r.source_site === doc.site && !r.disabled_for_inventory)
  const lookup = (name, value, options, onChange) => <SearchableLookup label={name} value={value ?? ''} options={options} onChange={onChange} disabled={!editable} hideLabel portal />
  const input = (key, label, type = 'text', readOnly = false) => <label key={key}><span>{label}</span><input aria-label={label} type={type} step={type === 'number' ? 'any' : undefined} value={doc[key] ?? ''} onChange={e => change(key, e.target.value)} readOnly={readOnly} disabled={!readOnly && !editable} /></label>
  const exportDoc = () => run(async () => { const { blob, filename } = await download(`/no-order-return/${doc.id}/export/`, { token: session.token }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url) })
  const navigate = offset => {
    if (!discard()) return
    run(async () => {
      const index = rows.findIndex(r => r.id === doc.id)
      let nextPage = page, nextIndex = index + offset
      if (offset === 'first') { nextPage = 1; nextIndex = 0 }
      else if (offset === 'last') { nextPage = Math.max(1, Math.ceil(count / 50)); nextIndex = -1 }
      else if (nextIndex < 0 && page > 1) { nextPage--; nextIndex = -1 }
      else if (nextIndex >= rows.length && page * 50 < count) { nextPage++; nextIndex = 0 }
      let list = rows
      if (nextPage !== page) {
        const result = await request(`/no-order-return/?page=${nextPage}&search=${encodeURIComponent(search)}`)
        list = result.results; setRows(list); setPage(nextPage); setCount(result.count)
      }
      const row = nextIndex === -1 ? list[list.length - 1] : list[nextIndex]
      if (row) accept(await request(`/no-order-return/${row.id}/`))
    })
  }
  return <section className="return-workspace" aria-label="无订单退货">
    <h1>无订单退货</h1>
    <div className="return-toolbar">
      <button onClick={() => { setBrowse(true); run(() => reload()) }}><Search size={15} />查询</button>
      <button disabled={busy || !can(session, 'sales_return', 'create')} onClick={newDoc}><Plus size={15} />新增</button>
      <button disabled={!editable || !dirty || !doc.lines.length} onClick={save}><Save size={15} />保存</button>
      <button disabled={!dirty || busy} onClick={() => { if (discard()) accept(saved || blank()) }}>取消</button>
      <button disabled={!doc.id || doc.posting_version > 0 || doc.source_key || busy || !can(session, 'sales_return', 'delete')} onClick={remove}>删除</button>
      <button disabled={!editable || selected === null} onClick={deleteLine}><Trash2 size={14} />删行</button>
      <button disabled={!approveAllowed || doc.posted || !defaults.posting_enabled} onClick={() => transition('approve')}><Check size={15} />审核</button>
      <button disabled={!approveAllowed || !doc.posted} onClick={() => transition('unapprove')}><RotateCcw size={15} />反审核</button>
      <button disabled={!approveAllowed || !doc.posted || doc.is_confirmed} onClick={() => transition('confirm')}>回单确认</button>
      <button disabled={!approveAllowed || !doc.is_confirmed} onClick={() => transition('unconfirm')}>反回单确认</button>
      <button disabled={!approveAllowed || !doc.posted || doc.is_signed} onClick={() => transition('sign')}>回单签收</button>
      <button disabled={!approveAllowed || !doc.is_signed} onClick={() => transition('unsign')}>反回单签收</button>
      {[['first', '第一笔'], [-1, '上一笔'], [1, '下一笔'], ['last', '末一笔']].map(([offset, label]) => <button key={label} disabled={busy || !rows.length} onClick={() => navigate(offset)}>{label}</button>)}
      <button disabled={!doc.id || dirty} onClick={() => window.print()}><Printer size={15} />预览 / 打印 / 页面设置</button>
      <button disabled={!doc.id || dirty || busy} onClick={exportDoc}><Download size={15} />导出</button>
    </div>
    <div className="return-tabs"><button onClick={() => setBrowse(false)} aria-pressed={!browse}>资料维护</button><button onClick={() => setBrowse(true)} aria-pressed={browse}>资料浏览</button><span>{states[doc.status] || '草稿'}{dirty ? ' · 未保存' : ''}</span></div>
    {error && <div className="return-error" role="alert">{error}</div>}{notice && <div role="status">{notice}</div>}
    {!defaults.posting_enabled && <div className="return-notice">本账套尚未启用退货库存过账，可维护草稿；请先在完整测试账套完成验收。</div>}
    {browse ? <div className="return-browse"><form onSubmit={e => { e.preventDefault(); run(() => reload(1)) }}><input aria-label="查询退货单" value={search} onChange={e => setSearch(e.target.value)} placeholder="退货单号、客户代码、客户名称、客户PO" /><button>查询</button></form><table><thead><tr><th>退货单号</th><th>日期</th><th>客户代码</th><th>客户名称</th><th>客户PO</th><th>状态</th></tr></thead><tbody>{rows.map(row => <tr key={row.id}><td><button onClick={() => load(row)}>{row.number}</button></td><td>{row.return_date}</td><td>{row.customer_code}</td><td>{row.customer_name}</td><td>{row.customer_po}</td><td>{states[row.status]}</td></tr>)}</tbody></table><button disabled={page <= 1 || busy} onClick={() => run(() => reload(page - 1))}>上一页</button><span>第 {page} 页 · 共 {count} 笔</span><button disabled={page * 50 >= count || busy} onClick={() => run(() => reload(page + 1))}>下一页</button></div> : <>
    <div className="return-head">
      {input('number', '退货单号', 'text', true)}{input('return_date', '日期', 'date')}
      <label><span>退入库位</span><input readOnly value="" aria-label="表头退入库位" title="按明细退入库位记账" /></label>{input('site', '站点')}
      <label><span>客户代码</span>{lookup('客户代码', doc.customer, customers, value => change('customer', value))}</label>
      <label><span>客户名称</span><input readOnly value={customers.find(r => r.id === Number(doc.customer))?.name || doc.customer_name || ''} /></label>
      <label><span>币种</span>{lookup('币种', doc.currency, lookups.currency || [], value => change('currency', value))}</label>
      {input('exchange_rate', '兑换率', 'text', true)}{input('tax_rate', '增值税率%', 'number')}{input('customer_po', '客户PO')}
      <label><span>业务组别</span>{lookup('业务组别', doc.business_group, (defaults.groups || []).map(r => ({ ...r, id: r.code })), value => change('business_group', value))}</label>
      <label><span>送货地址</span>{lookup('送货地址', doc.delivery_address, (defaults.addresses || []).map(r => ({ ...r, id: r.name })), value => change('delivery_address', value))}</label>
      {input('reason', '备注')}
      <label><span>默认打印人</span><input readOnly value={doc.default_print_person || defaults.default_print_person || ''} /></label>
      <div className="audit-fields">{[['created_by','录入人'],['created_at','录入时间'],['updated_by','修改人'],['updated_at','修改时间'],['approved_by','审核人'],['approved_at','审核时间'],['confirmed_by','回单确认人'],['confirmed_at','确认时间'],['signed_by','回单签收人'],['signed_at','签收时间']].map(([key,label]) => input(key,label,'text',true))}<label><input type="checkbox" checked={Boolean(doc.is_confirmed)} readOnly />回单确认</label><label><input type="checkbox" checked={Boolean(doc.is_signed)} readOnly />回单签收</label></div>
    </div>
    <div className="return-table-wrap"><table className="return-table"><thead><tr>{columns.map(([key,label]) => <th key={key}>{label}</th>)}</tr></thead><tbody>{doc.lines.map((line,index) => <tr key={line.id || `new-${index}`} className={selected === index ? 'selected' : ''} onClick={() => setSelected(index)}>{columns.map(([key,label,type]) => {
      let value = line[key] ?? ''
      if (key === 'material_code') return <td key={key}><button disabled={!editable} className="material-search" onClick={() => queryMaterials(index)}><Search size={13} />{value || '检索物料'}</button></td>
      if (key === 'return_location') return <td key={key}>{lookup(`${label}第${line.line_number}行`, line.return_location, locations, value => lineSet(index,key,value))}</td>
      if (key === 'location_name') value = locations.find(r => r.id === Number(line.return_location))?.name || line.location_name || ''
      if (key === 'amount') value = fixed(cents(line), 2)
      return <td key={key} className={!type ? 'derived' : ''}>{type ? <input aria-label={`${label}第${line.line_number}行`} type={type} min={type === 'number' ? '0' : undefined} step="0.00000001" value={value} onChange={e => lineSet(index,key,e.target.value)} disabled={!editable} /> : <span title={String(value)}>{value}</span>}</td>
    })}</tr>)}</tbody><tfoot><tr>{columns.map(([key]) => <td key={key}>{key === 'line_number' ? '合计' : key === 'quantity' || key === 'spare_quantity' ? fixed(doc.lines.reduce((sum,line) => sum + units(line[key]),0n),8) : key === 'amount' ? total : ''}</td>)}</tr></tfoot></table></div>
    <button disabled={!editable} className="add-line" onClick={add}><Plus size={14} />增加明细</button>
    </>}
    {candidate && <div className="return-modal-backdrop"><section role="dialog" aria-modal="true" aria-label="物料检索" className="candidate-popover"><form onSubmit={e => { e.preventDefault(); queryMaterials(candidate.index,materialSearch) }}><input autoFocus aria-label="物料检索条件" value={materialSearch} onChange={e => setMaterialSearch(e.target.value)} placeholder="物料编码、名称或客户物料编码" /><button disabled={busy}>检索</button><button type="button" onClick={() => setCandidate(null)}>关闭</button></form><p>选择物料及其客户关联记录，灰色字段自动带入。</p><div className="candidate-results">{candidate.results.map(hit => <button disabled={busy} key={hit.id} onClick={() => applyMaterial(hit)}><strong>{hit.material_code}</strong><span>{hit.material_name}</span><span>客户物料：{hit.customer_material_code || '无'}</span><span>终端物料：{hit.terminal_customer_code} {hit.terminal_customer_name}</span></button>)}{!candidate.results.length && <p>未找到匹配物料</p>}</div><button disabled={candidate.page <= 1 || busy} onClick={() => queryMaterials(candidate.index,materialSearch,candidate.page-1)}>上一页</button><span>第 {candidate.page} 页 · 共 {candidate.count} 个物料</span><button disabled={candidate.page*40 >= candidate.count || busy} onClick={() => queryMaterials(candidate.index,materialSearch,candidate.page+1)}>下一页</button></section></div>}
    <footer className="return-footer">明细 {doc.lines.length} 行 <span>退货金额 {total}</span></footer>
  </section>
}
