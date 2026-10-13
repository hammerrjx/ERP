import { useEffect, useRef, useState } from 'react'
import { ArrowRight, ChevronLeft, ChevronRight, Download, RotateCcw, Search, WrapText, X } from 'lucide-react'
import { api, download } from '../../api/client'
import './warehouse.css'

const dateText = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
function defaults(movement) {
  const now = new Date()
  return { source: 'local', site: '1000', include_wip: '0', exclude_cost: '1', exclude_line: '1', sort: 'document_date',
    ...(movement ? { document_from: dateText(new Date(now.getFullYear(), now.getMonth(), 1)), document_to: dateText(new Date(now.getFullYear(), now.getMonth() + 1, 0)) } : {}) }
}
const lookupNames = { material: '物料', category: '产品类', location: '库位', lot: '批号', group: '产品组', part_type: '零件类型', keeper: '仓管员', movement_type: '进出类型', supplier: '供应商', customer: '客户', department: '部门' }

function LookupDialog({ selection, resource, token, filters, batchId, onSelect, onClose }) {
  const dialog = useRef(null)
  const sequence = useRef(0)
  const [field, setField] = useState('code')
  const [match, setMatch] = useState('contains')
  const [q, setQ] = useState('')
  const [applied, setApplied] = useState({ field: 'code', match: 'contains', q: '' })
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ count: 0, results: [] })
  const [chosen, setChosen] = useState(null)
  const [busy, setBusy] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => { dialog.current.showModal() }, [])
  useEffect(() => {
    const id = ++sequence.current
    setBusy(true); setError(''); setChosen(null)
    const params = new URLSearchParams({ ...filters, ...applied, kind: selection.kind, page, ...(batchId ? { batch_id: batchId } : {}) })
    api(`/${resource}/lookup/?${params}`, { token }).then((result) => {
      if (id === sequence.current) setData(result)
    }).catch((e) => { if (id === sequence.current) { setError(e.message); setData({ count: 0, results: [] }) } })
      .finally(() => { if (id === sequence.current) setBusy(false) })
    return () => { sequence.current++ }
  }, [applied, page, selection.kind, resource, token, batchId, filters])
  const pick = (row) => { if (row) onSelect(row.code) }
  return <dialog ref={dialog} className="ir-dialog" onCancel={(e) => { e.preventDefault(); onClose() }} aria-labelledby="ir-lookup-title">
    <header><h2 id="ir-lookup-title">{lookupNames[selection.kind]}检索</h2><button type="button" title="关闭检索" aria-label="关闭检索" onClick={onClose}><X size={18}/></button></header>
    <form className="ir-lookup-search" onSubmit={(e) => { e.preventDefault(); setPage(1); setApplied({ field, match, q }) }}>
      <select aria-label="检索字段" value={field} onChange={(e) => setField(e.target.value)}><option value="code">编码</option><option value="name">名称</option>{selection.kind === 'material' && <option value="specification">规格</option>}</select>
      <select aria-label="匹配方式" value={match} onChange={(e) => setMatch(e.target.value)}><option value="contains">包含</option><option value="equals">等于</option></select>
      <input autoFocus aria-label="检索内容" value={q} onChange={(e) => setQ(e.target.value)}/><button type="submit" disabled={busy}><Search size={15}/>查询</button>
    </form>
    {error && <div className="wh-error" role="alert">{error}</div>}
    <div className="ir-lookup-results" aria-busy={busy}><table><thead><tr><th>编码</th><th>名称</th>{selection.kind === 'material' && <th>规格</th>}</tr></thead><tbody>{!busy && data.results.map((row) => <tr key={`${row.site}:${row.code}`} className={chosen === row ? 'selected' : ''} onClick={() => setChosen(row)} onDoubleClick={() => pick(row)}>
      <td><button type="button" aria-pressed={chosen === row} onClick={() => setChosen(row)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); pick(row) } }}>{row.code || '（空）'}</button></td><td>{row.name}</td>{selection.kind === 'material' && <td>{row.specification}</td>}
    </tr>)}</tbody></table>{(busy || !data.results.length) && <p className="wh-empty">{busy ? '加载中' : '无匹配选项'}</p>}</div>
    <footer><span>共 {data.count.toLocaleString()} 条</span><button title="上一页" aria-label="检索上一页" disabled={busy || page === 1} onClick={() => setPage(page - 1)}><ChevronLeft size={16}/></button><span>{page} / {Math.max(1, Math.ceil(data.count / 50))}</span><button title="下一页" aria-label="检索下一页" disabled={busy || page * 50 >= data.count} onClick={() => setPage(page + 1)}><ChevronRight size={16}/></button><button disabled={!chosen || busy} onClick={() => pick(chosen)}>确定</button><button onClick={onClose}>取消</button></footer>
  </dialog>
}

export function InventoryDetailReport({ resource, title, session, onClose }) {
  const movement = resource === 'material-movement-detail'
  const [filters, setFilters] = useState(() => defaults(movement))
  const [executed, setExecuted] = useState(() => defaults(movement))
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ results: [], columns: [], count: 0, batch: null })
  const [busy, setBusy] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState('')
  const [exportError, setExportError] = useState('')
  const [selection, setSelection] = useState(null)
  const [wrap, setWrap] = useState(false)
  const [widths, setWidths] = useState({})
  const resizing = useRef(null)
  const sequence = useRef(0)
  const batchId = useRef(null)
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const id = ++sequence.current
    setBusy(true); setError('')
    const params = new URLSearchParams({ ...executed, page, page_size: 100, ...(batchId.current ? { batch_id: batchId.current } : {}) })
    api(`/${resource}/?${params}`, { token: session.token }).then((result) => {
      if (id === sequence.current) { setData(result); batchId.current = result.batch?.id ?? null }
    }).catch((e) => { if (id === sequence.current) { setError(e.message); setData((old) => ({ ...old, results: [], count: 0 })) } })
      .finally(() => { if (id === sequence.current) setBusy(false) })
    return () => { sequence.current++ }
  }, [resource, session.token, executed, page, revision])
  const change = (key, value) => setFilters((old) => ({ ...old, [key]: value }))
  const input = (key, label, kind, type = 'text') => <div className="ir-code-input"><input type={type} aria-label={label} value={filters[key] || ''} onChange={(e) => change(key, e.target.value)}/>{kind && <button type="button" title={`检索${label}`} aria-label={`检索${label}`} onClick={() => setSelection({ key, kind })}><Search size={14}/></button>}</div>
  const range = (key, label, type = 'text') => <div className="ir-field"><span>{label}</span><div className="ir-range">{input(`${key}_from`, `${label}起始`, type === 'date' ? null : key, type)}<ArrowRight size={14}/>{input(`${key}_to`, `${label}结束`, type === 'date' ? null : key, type)}</div></div>
  const single = (key, label, kind) => <div className="ir-field"><span>{label}</span>{input(key, label, kind)}</div>
  const toggle = (key, label) => <label className="ir-toggle"><input type="checkbox" checked={filters[key] === '1'} onChange={(e) => change(key, e.target.checked ? '1' : '0')}/>{label}</label>
  const query = (e) => { e?.preventDefault(); batchId.current = null; setPage(1); setExecuted({ ...filters }); setRevision((v) => v + 1); setExportError('') }
  const reset = () => { setFilters(defaults(movement)) }
  const toggleNonzero = () => {
    const nonzero_quantity = executed.nonzero_quantity === '1' ? '0' : '1'
    setFilters(old => ({ ...old, nonzero_quantity }))
    setExecuted(old => ({ ...old, nonzero_quantity }))
    setPage(1)
    setExportError('')
  }
  const exportRows = async () => {
    setExporting(true); setExportError('')
    try {
      const result = await download(`/${resource}/export/`, { token: session.token, body: { filters: { ...executed, batch_id: data.batch.id } } })
      const url = URL.createObjectURL(result.blob)
      const a = document.createElement('a'); a.href = url; a.download = result.filename; a.click()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (e) { setExportError(e.message) } finally { setExporting(false) }
  }
  const dirty = JSON.stringify(filters) !== JSON.stringify(executed)
  const columnWidth = (key) => widths[key] || (['material_name', 'specification', 'notes', 'customer_material_code', 'price_status'].includes(key) ? 220 : 130)
  const resizeColumn = (key, width) => setWidths((old) => ({ ...old, [key]: Math.max(80, Math.min(600, width)) }))
  return <section className="wh-workspace ir-workspace">
    <div className="wh-tabs"><h1>{title}</h1></div>
    <div className="ir-toolbar"><button disabled={busy} onClick={query}><Search size={16}/>查询</button><button disabled={busy || exporting || !data.batch || !!error} onClick={exportRows}><Download size={16}/>{exporting ? '导出中' : '导出'}</button><button onClick={reset}><RotateCcw size={16}/>恢复初始查询条件</button><button onClick={() => { setWrap(false); setWidths({}) }} title="恢复默认栏位设置"><RotateCcw size={16}/>恢复默认栏位设置</button><label><input type="checkbox" checked={wrap} onChange={(e) => setWrap(e.target.checked)}/><WrapText size={16}/>文字自动换行</label>{onClose && <button onClick={onClose}><X size={16}/>关闭</button>}</div>
    <form className="ir-filters" onSubmit={query}>
      <label className="ir-field"><span>数据口径</span><select value={filters.source} onChange={e => change('source', e.target.value)}><option value="local">本地业务账</option><option value="dgyzx1">dgyzx1 历史快照</option></select></label>
      <div className="ir-ranges">{range('material', '物料编码')}{movement && range('document', '单据日期', 'date')}{movement && range('posted', '审核日期', 'date')}{range('category', '产品类')}{movement ? <>{range('group', '产品组')}{range('part_type', '零件类型')}</> : <>{range('location', '库位')}{range('lot', '批号')}{single('description', '名称或规格类似')}{toggle('include_wip', '包括生产线库位')}</>}</div>
      {movement && <div className="ir-singles">{single('movement_type', '进出类型', 'movement_type')}{single('location', '库位', 'location')}{single('document_number', '单据编号')}{single('keeper', '仓管员', 'keeper')}{single('lot', '批号', 'lot')}{single('order_number', '订单号')}
        <div className="ir-field"><span>供应商/客户/部门</span><div className="ir-partner"><select aria-label="往来对象类型" value={filters.partner_kind || ''} onChange={(e) => setFilters((old) => ({ ...old, partner_kind: e.target.value, partner: '' }))}><option value="">全部</option><option value="supplier">供应商</option><option value="customer">客户</option><option value="department">部门</option></select>{input('partner', '往来对象编号', filters.partner_kind || null)}</div></div>
        <label className="ir-field"><span>排序方式</span><select value={filters.sort} onChange={(e) => change('sort', e.target.value)}><option value="document_date">0.按单据日期</option><option value="posted_at">1.按审核日期</option><option value="order_number">2.按订单号</option></select></label>{toggle('exclude_cost', '不查成本调整明细')}{toggle('exclude_line', '不查生产线出入库')}</div>}
      <button type="submit" hidden>查询</button>
    </form>
    <div className="ir-status"><span>站点 {filters.site}</span><span>{data.batch ? data.batch.source === 'local' ? '本地业务账 · 库存实时更新' : `dgyzx1 · 同步时间 ${data.batch.finished_at?.replace('T', ' ').slice(0, 19) || String(data.batch.created_at).slice(0, 19)}` : 'dgyzx1 · 尚未同步报表数据'}</span>{movement && data.batch && data.batch.source !== 'local' && <span>流水范围 {data.batch.date_from} 至 {data.batch.date_to}</span>}{dirty && <strong>条件已修改，待查询</strong>}</div>
    {(error || exportError) && <div className="wh-error" role="alert">{error || exportError}</div>}
    <div className={`wh-grid ir-grid ${wrap ? 'ir-wrap' : ''}`} aria-busy={busy}><table style={{ width: data.columns.reduce((sum, [key]) => sum + columnWidth(key), 0) }}><colgroup>{data.columns.map(([key]) => <col key={key} style={{ width: columnWidth(key) }}/>)}</colgroup><thead><tr>{data.columns.map(([key, label]) => <th key={key} title={label}>{!movement && key === 'quantity' ? <button type="button" className="ir-quantity-filter" disabled={busy} aria-pressed={executed.nonzero_quantity === '1'} title={executed.nonzero_quantity === '1' ? '点击显示全部库存' : '点击仅显示非零库存'} onClick={toggleNonzero}>{label}{executed.nonzero_quantity === '1' ? ' ≠ 0' : ''}</button> : label}<span className="ir-column-resize" role="separator" tabIndex={0} aria-label={`${label}列宽`} aria-orientation="vertical" aria-valuenow={columnWidth(key)} aria-valuemin={80} aria-valuemax={600}
      onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); resizing.current = { x: e.clientX, width: columnWidth(key) } }}
      onPointerMove={(e) => { if (resizing.current && e.currentTarget.hasPointerCapture(e.pointerId)) resizeColumn(key, resizing.current.width + e.clientX - resizing.current.x) }}
      onPointerUp={(e) => { e.currentTarget.releasePointerCapture(e.pointerId); resizing.current = null }}
      onKeyDown={(e) => { if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); resizeColumn(key, columnWidth(key) + (e.key === 'ArrowLeft' ? -10 : 10)) } }}/></th>)}</tr></thead><tbody>{!busy && !error && data.results.map((row) => <tr key={row.id}>{data.columns.map(([key]) => <td key={key} title={String(row[key] ?? '未同步')}>{row[key] == null ? '未同步' : String(row[key])}</td>)}</tr>)}</tbody></table>{(busy || !data.results.length) && <p className="wh-empty">{busy ? '加载中' : error ? '查询失败' : !data.batch ? '尚未同步报表数据' : '无匹配记录'}</p>}</div>
    <footer className="wh-footer ir-footer"><span>记录数 {data.count.toLocaleString()}</span><span>每页100条</span><button title="上一页" aria-label="上一页" disabled={busy || page === 1} onClick={() => setPage(page - 1)}><ChevronLeft size={16}/></button><span>{page} / {Math.max(1, Math.ceil(data.count / 100))}</span><button title="下一页" aria-label="下一页" disabled={busy || page * 100 >= data.count} onClick={() => setPage(page + 1)}><ChevronRight size={16}/></button></footer>
    {selection && <LookupDialog selection={selection} resource={resource} token={session.token} filters={filters} batchId={data.batch?.id} onClose={() => setSelection(null)} onSelect={(code) => { change(selection.key, code); setSelection(null) }}/>}</section>
}
