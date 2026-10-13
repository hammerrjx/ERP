import { useEffect, useState } from 'react'
import { Plus, Minus, Save, Trash2, Check, Undo2, Search, Printer, Download, ChevronFirst, ChevronLast, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { api, download } from '../../api/client'
import { can } from '../../auth/session'
import './requisition-workspace.css'

const today = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai' }).format(new Date())
const blank = () => ({ requisition_type: 'P', document_type: '', site: '1000', request_date: today(), requester: '', notes: '', lines: [], version: 0 })
const states = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
const time = value => value ? new Date(value).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }) : ''
const sourceColumns = [
  ['sequence', '行号'], ['source_number', '生产单号/客户订单号'], ['source_marker', '标志'], ['source_sequence', '序号'],
  ['reqd_wod_qty_req_std', '标准需求数量（领料单位）'], ['reqd_wod_qty_req_scr', '损耗需求数量（领料单位）'], ['reqd_wod_qty_req', '需求数量（领料单位）'],
  ['quantity', '来源数量（网页MRP为当前分配）'], ['suggested_qty', '原MRP建议量'], ['generated_qty', '原生成数量'], ['reqd_mrp_req_tot', 'MRP总需求'], ['reqd_mrp_ld_net', 'MRP可用库存'], ['reqd_mrp_ord', 'MRP订购中/在制'],
  ['reqd_mrp_pr', 'MRP请购中'], ['reqd_mrp_safe', 'MRP安全库存'], ['reqd_mrp_alloc', 'MRP分配数量'], ['reqd_mrp_left', 'MRP库存余量'], ['reqd_mrp_short', 'MRP短缺数量'],
  ['source_line', '生产线'], ['reqd_wod_part', '主件编码'], ['parent_name', '主件名称'], ['reqd_wo_qty_ord', '生产数量'], ['customer_order', '客户订单'], ['customer_po', '客户PO']
]
const extraColumns = [
  ['pt_desc2','英文名称','material'], ['pt_prod_line','产品类','material'], ['category_name','产品类名称','material'], ['pt_group','产品组','material'], ['group_name','产品组名称','material'],
  ['pt_part_type','零件类型','material'], ['part_type_name','零件类型名称','material'], ['req_src','来源','source'], ['req_wo_nbr','生产单号/订单号','source'], ['req_wo_lot','标志/行号','source'],
  ['req_mrp_req_self','本行需求','source'], ['req_mrp_req_tot','MRP总需求','source'], ['req_mrp_ld_net','MRP可用库存','source'], ['req_mrp_ld_unnet','非可用库存','source'],
  ['req_mrp_ord','MRP订购中/在制','source'], ['req_mrp_pr','MRP请购中','source'], ['req_mrp_safe','MRP安全库存','source'], ['req_mrp_alloc','MRP分配数量','source'],
  ['req_mrp_left','MRP库存余量','source'], ['req_mrp_short','MRP短缺数量','source'], ['req_mrp_qty_org','MRP原建议量','source'],
  ['created_by','录入人','audit'], ['created_at','录入时间','audit'], ['modification_count','修改次数','audit'], ['updated_by','修改人','audit'], ['updated_at','修改时间','audit']
]

function Lookup({ kind, request, onPick, onClose }) {
  const [q, setQ] = useState('')
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  useEffect(() => {
    let current = true
    const timer = setTimeout(() => request(`/purchase-requisition/lookups/?${new URLSearchParams({kind,q})}`).then(r => { if (current) setRows(r) }).catch(e => { if (current) setError(e.message) }), 180)
    return () => { current = false; clearTimeout(timer) }
  }, [kind,q])
  return <div className="rq-backdrop"><section className="rq-lookup" role="dialog" aria-modal="true" aria-label={kind === 'employee' ? '请购人检索' : '物料检索'}><header><h2>{kind === 'employee' ? '请购人检索' : '物料检索'}</h2><button onClick={onClose} aria-label="关闭检索"><X size={18}/></button></header><input autoFocus aria-label="检索编码或名称" placeholder="输入编码或名称" value={q} onChange={e => setQ(e.target.value)}/>{error && <p role="alert">{error}</p>}<p>最多显示50条，请输入条件缩小范围。</p><div className="rq-lookup-results">{rows.map(row => <button key={row.id} onClick={() => onPick(row)}>{row.code}　{row.name}</button>)}</div></section></div>
}

export function RequisitionWorkspace({ session, convertMode = false, initialId = null }) {
  const [doc, setDoc] = useState(blank)
  const [saved, setSaved] = useState(null)
  const [selected, setSelected] = useState(0)
  const [dirty, setDirty] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [lookup, setLookup] = useState(null)
  const [browse, setBrowse] = useState(true)
  const [preview, setPreview] = useState(false)
  const [filters, setFilters] = useState({ q: '', status: '', requisition_type: '' })
  const [applied, setApplied] = useState(filters)
  const [page, setPage] = useState(1)
  const [list, setList] = useState({ count: 0, results: [] })
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const run = async fn => { setBusy(true); setError(''); setNotice(''); try { await fn() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const loadList = async (values = applied, p = page) => setList(await request(`/purchase-requisition/?${new URLSearchParams({ ...values, workspace: '1', page: p })}`))
  useEffect(() => { run(() => loadList()) }, [page, applied, session.token])
  const adopt = value => { setDoc(value); setSaved(value); setDirty(false); setSelected(0); setBrowse(false) }
  useEffect(() => {
    if (initialId) run(async () => adopt(await request(`/purchase-requisition/${initialId}/`)))
  }, [initialId, session.token])
  const select = row => { if (!dirty || window.confirm('放弃未保存的修改？')) run(async () => adopt(await request(`/purchase-requisition/${row.id}/`))) }
  const set = (key, value) => { setDoc(old => ({ ...old, [key]: value })); setDirty(true) }
  const setLine = (index, key, value) => { setDoc(old => ({ ...old, lines: old.lines.map((r,i) => i === index ? { ...r, [key]: value } : r) })); setDirty(true) }
  const downstream = doc.lines.some(r => Number(r.converted_qty) > 0)
  const editable = doc.requisition_type === 'P' && (!doc.status || ['draft','rejected'].includes(doc.status)) && !downstream
  const locked = busy || !editable || !can(session, 'purchase_requisition', doc.id ? 'change' : 'create')
  const field = (key, label, type = 'text') => <label>{label}<input aria-label={label} type={type} value={doc[key] || ''} disabled={locked} onChange={e => set(key,e.target.value)}/></label>
  const save = () => run(async () => {
    const body = { request_date:doc.request_date, requester:doc.requester || session.user?.username || session.username || '', requisition_type:doc.requisition_type,
      document_type:doc.document_type, site:doc.site, notes:doc.notes, version:doc.version,
      lines:doc.lines.map(r => ({ ...(r.id ? { id:r.id } : {}), line_number:r.line_number, material:r.material, uom:r.uom, needed_date:r.needed_date, requested_qty:r.requested_qty, notes:r.notes || '' })) }
    if (!body.requester) delete body.requester
    adopt(await request(`/purchase-requisition/${doc.id ? doc.id+'/' : ''}`, { method:doc.id ? 'PUT' : 'POST', body }))
    await loadList(); setNotice('已保存')
  })
  const action = verb => run(async () => {
    if (verb === 'approve' && ['draft','rejected'].includes(doc.status)) await request(`/purchase-requisition/${doc.id}/submit/`, { method:'POST' })
    adopt(await request(`/purchase-requisition/${doc.id}/${verb}/`, { method:'POST' })); await loadList()
  })
  const add = row => {
    const line_number = Math.max(0,...doc.lines.map(r => r.line_number),...(saved?.lines || []).map(r => r.line_number)) + 10
    set('lines',[...doc.lines,{ line_number,material:row.material,uom:row.uom,material_snapshot:row.snapshot,source_snapshot:{},sources:[],needed_date:doc.request_date,requested_qty:'1',converted_qty:'0',notes:'',line_status:'' }])
    setSelected(doc.lines.length);setLookup(null)
  }
  const exportFile = () => run(async () => {
    const result = await download(`/purchase-requisition/${doc.id}/export/`, { token:session.token })
    const url = URL.createObjectURL(result.blob); const a=document.createElement('a'); a.href=url;a.download=result.filename;a.click();setTimeout(() => URL.revokeObjectURL(url),1000)
  })
  const print = () => run(async () => { adopt(await request(`/purchase-requisition/${doc.id}/print/`, { method:'POST' })); setPreview(true); setTimeout(() => window.print(),100) })
  const remove = () => { if (window.confirm(`删除请购单 ${doc.number}？`)) run(async () => { await request(`/purchase-requisition/${doc.id}/`,{method:'DELETE'});setDoc(blank());setSaved(null);setDirty(false);setBrowse(true);await loadList() }) }
  const line = doc.lines[selected]
  if (convertMode) return <ConversionWorkspace session={session} request={request} />
  const navigate = direction => { if (!dirty || window.confirm('放弃未保存的修改？')) run(async () => adopt(await request(`/purchase-requisition/navigate/?${new URLSearchParams({...applied,direction,current:doc.id || ''})}`))) }
  const tool = (Icon,label,fn,disabled=false) => <button type="button" onClick={fn} disabled={busy || disabled} title={label}><Icon size={16}/>{label}</button>
  return <section className={`rq-workspace ${preview ? 'rq-preview' : ''}`}>
    <h1>请购单</h1>
    <div className="rq-toolbar">
      {tool(Search,'查询',() => setBrowse(true))}{tool(Plus,'新增',() => { if (!dirty || window.confirm('放弃未保存的修改？')) { setDoc(blank());setSaved(null);setSelected(0);setDirty(false);setBrowse(false) } },!can(session,'purchase_requisition','create'))}
      {tool(Save,'保存',save,locked || !dirty)}{tool(Undo2,'取消',() => { if (saved) adopt(saved);else {setDoc(blank());setDirty(false)} },!dirty)}
      {tool(Trash2,'删除',remove,locked || !doc.id || !can(session,'purchase_requisition','delete'))}{tool(Minus,'删行',() => {set('lines',doc.lines.filter((_,i) => i !== selected));setSelected(0)},locked || !line)}
      {tool(Check,'审核',() => action('approve'),dirty || !doc.id || !['draft','pending','rejected'].includes(doc.status) || doc.requisition_type !== 'P' || !can(session,'purchase_requisition','approve'))}
      {tool(Undo2,'反审核',() => action('unapprove'),dirty || doc.status !== 'approved' || downstream || doc.requisition_type !== 'P' || !can(session,'purchase_requisition','approve'))}
      {tool(ChevronFirst,'首笔',() => navigate('first'),!list.count)}{tool(ChevronLeft,'前笔',() => navigate('previous'),!doc.id)}
      {tool(ChevronRight,'后笔',() => navigate('next'),!doc.id)}{tool(ChevronLast,'末笔',() => navigate('last'),!list.count)}
      {tool(Search,preview ? '关闭预览' : '预览',() => setPreview(!preview),!doc.id)}{tool(Printer,'打印',print,!doc.id || dirty)}{tool(Download,'导出',exportFile,!doc.id || dirty)}
    </div>
    {error && <p className="rq-error" role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}
    <nav className="rq-tabs"><button onClick={() => setBrowse(false)} aria-selected={!browse}>资料维护</button><button onClick={() => setBrowse(true)} aria-selected={browse}>资料浏览</button></nav>
    {browse ? <>
      <form className="rq-query" onSubmit={e => {e.preventDefault();setPage(1);setApplied({...filters})}}><input aria-label="查询条件" placeholder="单号、物料、请购人、来源单号" value={filters.q} onChange={e => setFilters({...filters,q:e.target.value})}/><select aria-label="查询类型" value={filters.requisition_type} onChange={e => setFilters({...filters,requisition_type:e.target.value})}><option value="">全部类型</option><option value="P">P.采购</option><option value="S">S.外协</option><option value="M">M.其他历史类型</option></select><select aria-label="查询状态" value={filters.status} onChange={e => setFilters({...filters,status:e.target.value})}><option value="">全部状态</option>{Object.entries(states).map(([key,label]) => <option key={key} value={key}>{label}</option>)}</select><button disabled={busy}>查询</button></form>
      <div className="rq-grid"><table><thead><tr>{['请购单号','日期','类型','单别','请购人','状态'].map(c => <th key={c}>{c}</th>)}</tr></thead><tbody>{list.results.map(row => <tr key={row.id}><td><button className="rq-link" onClick={() => select(row)}>{row.number}</button></td><td>{row.request_date}</td><td>{row.requisition_type}</td><td>{row.document_type}</td><td>{row.requester}</td><td>{states[row.status]}</td></tr>)}</tbody></table></div>
      <footer>共 {list.count} 张<button disabled={busy || page === 1} onClick={() => setPage(page-1)}>上一页</button>{page} / {Math.max(1,Math.ceil(list.count/50))}<button disabled={busy || page*50>=list.count} onClick={() => setPage(page+1)}>下一页</button></footer>
    </> : <>
      <div className="rq-header"><label>请购单号<output>{doc.number || '〈自动编号〉'}</output></label>{field('request_date','日期','date')}<label>类型<select aria-label="类型" value={doc.requisition_type} disabled={locked} onChange={e => set('requisition_type',e.target.value)}><option value="P">P.采购</option><option value="S" disabled>S.外协（本期只读）</option>{doc.requisition_type === 'M' && <option value="M">M.其他历史类型</option>}</select></label>
      <label>请购人<div className="rq-input-search"><input aria-label="请购人" value={doc.requester || ''} disabled={locked} onChange={e => set('requester',e.target.value)} placeholder="默认当前关联员工"/><button aria-label="检索请购人" disabled={locked} onClick={() => setLookup('employee')}><Search size={14}/></button></div></label>
      <label>单别<select aria-label="单别" value={doc.document_type} disabled><option value="">普通</option>{doc.document_type && <option value={doc.document_type}>{doc.document_type}.历史单别</option>}</select></label>{field('notes','备注')}
      <label>录入人<output>{doc.created_by || ''}</output></label><label>录入时间<output>{time(doc.created_at)}</output></label><label>审核人<output>{doc.approved_by || ''}</output></label><label>审核时间<output>{time(doc.approved_at)}</output></label><label>打印次数<output>{doc.print_count || 0}</output></label><label>状态<output>{states[doc.status] || '草稿'}{dirty ? ' · 未保存' : ''}</output></label></div>
      {doc.requisition_type !== 'P' && <p className="rq-info">当前为历史{doc.requisition_type}类型，仅供查看、打印和导出；外协业务尚未开放维护。</p>}
      <div className="rq-line-actions">{tool(Plus,'增行',() => setLookup('material'),locked)}{tool(Check,'关闭行',() => { const reason=window.prompt('请输入关闭原因');if (reason) run(async () => adopt(await request(`/purchase-requisition/${doc.id}/close_line/`,{method:'POST',body:{line_id:line.id,reason}}))) },dirty || !line?.id || line.line_status === 'C' || doc.status !== 'approved' || doc.requisition_type !== 'P' || !can(session,'purchase_requisition','approve'))}<span>数量单位：物料库存单位</span></div>
      <div className="rq-grid rq-lines"><table><thead><tr>{['行号','物料编码','物料名称','规格','最小采购数量','最小包装数量','需求日期','请购数量','已采购数','库存单位','状态','备注',...extraColumns.map(c => c[1])].map((c,i) => <th key={i}>{c}</th>)}</tr></thead><tbody>{doc.lines.map((row,i) => <tr key={row.id || row.line_number} className={selected === i ? 'selected' : ''} onClick={() => setSelected(i)}><td><button className="rq-link" onClick={() => setSelected(i)}>{row.line_number}</button></td>{['pt_part','pt_desc1','pt_spec','pt_ord_min','pt_ord_mult'].map(key => <td key={key}>{row.material_snapshot?.[key] || ''}</td>)}<td><input aria-label={`需求日期${row.line_number}`} type="date" value={row.needed_date || ''} disabled={locked} onChange={e => setLine(i,'needed_date',e.target.value)}/></td><td><input aria-label={`请购数量${row.line_number}`} type="number" step="0.00000001" value={row.requested_qty} disabled={locked} onChange={e => setLine(i,'requested_qty',e.target.value)}/></td><td>{row.converted_qty}</td><td>{row.material_snapshot?.pt_um}</td><td>{row.line_status === 'C' ? '关闭' : row.line_status || '正常'}</td><td><input aria-label={`备注${row.line_number}`} value={row.notes || ''} disabled={locked} onChange={e => setLine(i,'notes',e.target.value)}/></td>{extraColumns.map(([key,,kind]) => <td key={key}>{(kind === 'material' ? row.material_snapshot : kind === 'audit' ? row : row.source_snapshot)?.[key] ?? ''}</td>)}</tr>)}</tbody></table>{!doc.lines.length && <p>点击“增行”选择请购物料。</p>}</div>
      <h2>合并请购明细 {line ? `· 请购行 ${line.line_number}` : ''}</h2><div className="rq-grid rq-sources"><table><thead><tr>{sourceColumns.map(([key,label]) => <th key={key}>{label}</th>)}</tr></thead><tbody>{(line?.sources || []).map(row => <tr key={row.id || row.sequence}>{sourceColumns.map(([key]) => <td key={key}>{row[key] ?? row.snapshot?.[key] ?? ''}</td>)}</tr>)}</tbody></table>{!line?.sources?.length && <p>当前物料行无合并来源明细。</p>}</div>
      <footer>站点 {doc.site} · {doc.lines.length} 条物料明细 · {(line?.sources || []).length} 条当前行来源</footer>
    </>}
    {lookup && <Lookup kind={lookup} request={request} onClose={() => setLookup(null)} onPick={row => { if (lookup === 'employee') {set('requester',row.code);setLookup(null)} else add(row) }}/>}</section>
}

function ConversionWorkspace({ session, request }) {
  const [number, setNumber] = useState('')
  const [doc, setDoc] = useState(null)
  const [supplier, setSupplier] = useState(null)
  const [suppliers, setSuppliers] = useState([])
  const [department, setDepartment] = useState('')
  const [selected, setSelected] = useState({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const load = async () => { setError(''); try { const rows = await request(`/purchase-requisition/?workspace=1&q=${encodeURIComponent(number)}&requisition_type=P`); if (!rows.results?.length) throw new Error('未找到P采购请购单'); setDoc(await request(`/purchase-requisition/${rows.results[0].id}/`)) } catch (e) { setError(e.message) } }
  const findSuppliers = async value => { setSupplier(null); setSuppliers(await request(`/purchase-requisition/lookups/?kind=supplier&q=${encodeURIComponent(value)}`)) }
  const submit = async () => { if (!doc || !supplier) return setError('请购单和供应商不能为空'); setBusy(true);setError(''); try { const lines = doc.lines.filter(row => selected[row.id]).map(row => ({ line_id:row.id, quantity:selected[row.id].quantity || row.requested_qty - row.converted_qty, ...(selected[row.id].unit_price ? {unit_price:selected[row.id].unit_price} : {}) })); if (!lines.length) throw new Error('至少选择一条可转采购明细'); if (!window.confirm('确认继续生成采购单吗？')) return; const order = await request(`/purchase-requisition/${doc.id}/convert-purchase/`, {method:'POST', body:{supplier_id:supplier.id,department_id:department || doc.department,lines}}); window.alert(`采购单 ${order.number} 已生成`); setDoc(await request(`/purchase-requisition/${doc.id}/`)); setSelected({}) } catch (e) { setError(e.message) } finally { setBusy(false) } }
  return <section className="rq-workspace"><h1>请购单转采购单</h1><div className="rq-toolbar"><button onClick={load} disabled={busy}>查询</button><button onClick={submit} disabled={busy || !doc}>提交</button></div>{error && <p className="rq-error">{error}</p>}<div className="rq-header"><label>请购单号<input value={number} onChange={e => setNumber(e.target.value)} placeholder="输入请购单号" /></label><label>供应商<input value={supplier?.name || ''} onChange={e => findSuppliers(e.target.value)} placeholder="确认或手动输入供应商" /></label><label>采购部门<input value={department} onChange={e => setDepartment(e.target.value)} placeholder="部门ID" /></label></div>{suppliers.length > 0 && <div className="rq-lookup-results">{suppliers.map(row => <button key={row.id} onClick={() => {setSupplier(row);setSuppliers([])}}>{row.code}　{row.name}　{row.currency_code}</button>)}</div>}{doc && <><p>单号：{doc.number}　状态：{states[doc.status]}　类型：{doc.requisition_type}</p><div className="rq-grid rq-lines"><table><thead><tr><th>选择</th><th>行号</th><th>物料编码</th><th>物料名称</th><th>剩余可采购</th><th>本次采购数量</th><th>单价</th><th>需求日期</th></tr></thead><tbody>{doc.lines.map(row => { const remaining = Number(row.requested_qty || 0) - Number(row.converted_qty || 0); const value = selected[row.id] || {}; return <tr key={row.id}><td><input type="checkbox" disabled={remaining <= 0 || row.line_status === 'C' || !row.material} checked={!!selected[row.id]} onChange={e => setSelected(old => e.target.checked ? {...old,[row.id]:{quantity:String(remaining),unit_price:'0'}} : Object.fromEntries(Object.entries(old).filter(([key]) => key !== String(row.id))))}/></td><td>{row.line_number}</td><td>{row.material_snapshot?.pt_part}</td><td>{row.material_snapshot?.pt_desc1}</td><td>{remaining}</td><td><input type="number" step="0.00000001" disabled={!selected[row.id]} value={value.quantity || ''} onChange={e => setSelected(old => ({...old,[row.id]:{...old[row.id],quantity:e.target.value}}))}/></td><td><input type="number" step="0.00000001" disabled={!selected[row.id]} value={value.unit_price || ''} onChange={e => setSelected(old => ({...old,[row.id]:{...old[row.id],unit_price:e.target.value}}))}/></td><td>{row.needed_date}</td></tr> })}</tbody></table></div></>}</section>
}
