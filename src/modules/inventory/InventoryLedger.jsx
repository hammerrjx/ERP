import { useEffect, useRef, useState } from 'react'
import { Search, Download, RefreshCw } from 'lucide-react'
import { api, listPayload } from '../../api/client'
import { SearchableLookup } from '../../components/Field'
import './warehouse.css'
import { InventoryDetailReport } from './InventoryDetailReport'

export function InventoryLedger(props) {
  if (['material-inventory-detail', 'material-movement-detail'].includes(props.resource)) return <InventoryDetailReport key={props.resource} {...props}/>
  return <GenericInventoryLedger {...props}/>
}

function GenericInventoryLedger({ resource, title, session }) {
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [q, setQ] = useState('')
  const [location, setLocation] = useState('')
  const [start, setStart] = useState(new Date().toLocaleDateString('en-CA').slice(0, 8) + '01')
  const [end, setEnd] = useState(new Date().toLocaleDateString('en-CA'))
  const [table, setTable] = useState('tr_hist')
  const [page, setPage] = useState(0)
  const serverPaged = ['stock-balance', 'stock-transaction'].includes(resource)
  const [count, setCount] = useState(0)
  const history = resource === 'legacy-inventory-record'
  const report = resource === 'inventory-report'
  const detailKind = {
    'material-inventory-detail': 'material-inventory',
    'material-movement-detail': 'material-movement',
    'transfer-detail': 'transfer',
    'count-result': 'count',
    'unplanned-receipt-detail': 'receipt',
    'unplanned-issue-detail': 'issue',
    'scrap-detail': 'scrap',
  }[resource]
  const detailReport = Boolean(detailKind)
  const dateFiltered = report || detailReport || resource === 'stock-transaction'
  const applied = useRef({ q, location, ...(dateFiltered ? { start, end } : {}) })
  const fetchRows = (targetPage, all = false, filters = applied.current) => {
    const params = new URLSearchParams({ ...filters, ...(serverPaged && !all ? { page: targetPage + 1, page_size: 100 } : {}) })
    return api(`/${resource}/?${params}`, { token: session.token })
  }
  const load = async (targetPage = 0, query = false) => { setBusy(true); setError(''); try {
    const filters = query ? { q, location, ...(dateFiltered ? { start, end } : {}) } : applied.current
    const data = await fetchRows(targetPage, false, filters)
    applied.current = filters
    setRows(listPayload(data)); setCount(data.count ?? listPayload(data).length); setPage(targetPage)
  } catch (e) { setError(e.message) } finally { setBusy(false) } }
  useEffect(() => {
    load()
    let live = true
    const names = serverPaged ? ['location'] : ['material', 'location', 'uom']
    Promise.all(names.map(async r => [r, Object.fromEntries(listPayload(await api(`/${r}/`, { token: session.token })).map(item => [item.id, item]))]))
      .then(entries => { if (live) setLookups(Object.fromEntries(entries)) })
      .catch(e => { if (live) setError(e.message) })
    return () => { live = false }
  }, [resource, session.token])
  const columns = report ? [['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '库位'], ['uom', '单位'], ['batch_number', '批号'], ['opening', '期初'], ['receipt', '收入'], ['issue', '发出'], ['adjustment', '盘点调整'], ['closing', '期末']]
    : detailKind === 'material-inventory' ? [['material_code', '物料编码'], ['material_name', '物料名称'], ['specification', '规格'], ['location_code', '库位'], ['location_name', '库位名称'], ['site', '站点'], ['batch_number', '批号'], ['uom_name', '单位'], ['quantity', '现存量'], ['reserved_quantity', '预留量'], ['available_quantity', '可用量'], ['updated_at', '更新时间']]
    : detailKind === 'material-movement' ? [['effective_date', '业务日期'], ['movement_type', '业务类型'], ['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '库位'], ['site', '站点'], ['batch_number', '批号'], ['uom_name', '单位'], ['quantity', '数量'], ['balance_after', '结存'], ['source_model', '来源类型'], ['source_id', '来源单号'], ['source_line_id', '来源行号'], ['actor', '操作人']]
    : detailKind === 'transfer' ? [['document_date', '单据日期'], ['number', '转仓单号'], ['status', '状态'], ['line_number', '行号'], ['material_code', '物料编码'], ['material_name', '物料名称'], ['from_location_code', '调出库位'], ['to_location_code', '调入库位'], ['site', '站点'], ['batch_number', '批号'], ['quantity', '数量'], ['transfer_class', '转仓类别'], ['source_key', '来源键']]
    : detailKind === 'count' ? [['document_date', '盘点日期'], ['number', '盘点单号'], ['status', '状态'], ['line_number', '行号'], ['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '盘点库位'], ['site', '站点'], ['batch_number', '批号'], ['system_quantity', '账面数量'], ['counted_quantity', '实盘数量'], ['variance_quantity', '差异数量'], ['checker_name', '盘点人'], ['count_basis', '取数口径']]
    : detailReport ? [['document_date', '单据日期'], ['number', '单据号'], ['status', '状态'], ['line_number', '行号'], ['material_code', '物料编码'], ['material_name', '物料名称'], ['from_location_code', '出库库位'], ['to_location_code', '入库库位'], ['site', '站点'], ['batch_number', '批号'], ['quantity', '数量'], ['category_code', '业务类别'], ['reference_number', '来源单号'], ['reference_line', '来源行号'], ['source_key', '来源键']]
    : history ? [['source_table', '来源表'], ['source_key', '来源键'], ['material_code', '物料编码'], ['location_code', '库位'], ['effective_date', '业务日期'], ['legacy_type', '类型'], ['quantity', '原始数量'], ['reference', '来源单号'], ['reference_line', '来源行号']]
    : [['material_code', '物料编码'], ['material_name', '物料名称'], ['location_code', '库位'], ['uom_name', '单位'], ['batch_number', '批号'], ['quantity', '数量'], ...(resource === 'stock-balance' ? [['reserved_quantity', '预留量']] : [['movement_type', '业务类型'], ['balance_after', '结存'], ['effective_date', '业务日期'], ['source_model', '来源类型'], ['source_id', '来源单据ID'], ['source_line_id', '来源行ID'], ['posted_at', '过账时间']])]
  const formatted = rows.map((r) => { const p = r.payload || {}; return { ...r, material_code: r.material_code || lookups.material?.[r.material]?.code || p.tr_part || p.ld_part || p.movd_part || '', material_name: r.material_name || lookups.material?.[r.material]?.name || '', location_code: r.location_code || lookups.location?.[r.location]?.code || p.tr_loc || p.ld_loc || p.movd_loc || '', uom_name: r.uom_name || lookups.uom?.[r.uom]?.name || '', legacy_type: p.tr_type || p.mov_type || p.adj_type || '', quantity: history ? p.tr_qty_loc ?? p.ld_qty_oh ?? p.movd_qty ?? p.adjd_qty_diff ?? '' : r.quantity, reference: p.tr_ref || p.movd_mov || p.adjd_adj || '', reference_line: p.tr_ref_line || p.movd_line || p.adjd_line || '' } })
  const filtered = serverPaged ? formatted : formatted.filter((r) => (!history || r.source_table === table) && (!location || report || [r.location, r.location_id, r.from_location_id, r.to_location_id].some((id) => Number(id) === Number(location))) && JSON.stringify(r).toLowerCase().includes(q.toLowerCase()))
  const exportCsv = async () => { setBusy(true); setError(''); try { const exportData = serverPaged ? listPayload(await fetchRows(0, true)) : filtered; const escape = (v) => `"${String(v ?? '').replace(/^[=+@-]/, "'$&").replaceAll('"', '""')}"`; const value = [columns.map(([, name]) => name), ...exportData.map((r) => columns.map(([key]) => r[key]))].map((r) => r.map(escape).join(',')).join('\r\n'); const url = URL.createObjectURL(new Blob(['\ufeff' + value], { type: 'text/csv;charset=utf-8' })); const link = document.createElement('a'); link.href = url; link.download = `${title}.csv`; link.click(); URL.revokeObjectURL(url) } catch (e) { setError(e.message) } finally { setBusy(false) } }
  return <section className="wh-workspace"><div className="wh-tabs"><h1>{title}</h1></div><div className="wh-filter" style={{ flexWrap: 'wrap' }}><Search size={16}/><input aria-label="搜索库存" placeholder="物料、批号；回车查询" onKeyDown={(e) => { if (e.key === 'Enter') load(0, true) }} value={q} onChange={(e) => { setQ(e.target.value); if (!serverPaged) setPage(0) }}/>
    <SearchableLookup label="筛选库位" value={location} options={Object.values(lookups.location || {})} onChange={(v) => { setLocation(v || ''); if (!serverPaged) setPage(0) }} portal hideLabel clearOnFocus allowClear className="wh-lookup" optionCode={(r) => `${r.code} ${r.name}`} />
    {dateFiltered && <><input aria-label="开始日期" type="date" value={start} onChange={(e) => setStart(e.target.value)}/><input aria-label="结束日期" type="date" value={end} onChange={(e) => setEnd(e.target.value)}/></>}
    {history && <SearchableLookup label="来源表" value={table} options={['tr_hist', 'tr_hist_rec', 'ld_det', 'mov_mstr', 'movd_det', 'adj_mstr', 'adjd_det'].map((t) => ({ id: t, code: t }))} onChange={(v) => { setTable(v); if (!serverPaged) setPage(0) }} portal hideLabel clearOnFocus className="wh-lookup" />}
    <button disabled={busy} onClick={() => load(0, true)} title="查询/刷新"><RefreshCw size={16}/></button><button disabled={busy} onClick={exportCsv} title="导出查询结果"><Download size={16}/></button></div>{error && <div role="alert" className="wh-error">{error}</div>}{history && <div className="wh-notice">dgyzx1 并行试运样本 · 来源记录只读 · 不计入新系统收发存</div>}<div className="wh-grid"><table><thead><tr>{columns.map(([key, name]) => <th key={key}>{name}</th>)}</tr></thead><tbody>{(serverPaged ? filtered : filtered.slice(page * 100, (page + 1) * 100)).map((r, i) => <tr key={r.id || i}>{columns.map(([key]) => <td key={key} title={String(r[key] ?? '')}>{String(r[key] ?? '')}</td>)}</tr>)}</tbody></table>{!filtered.length && <p className="wh-empty">{busy ? '加载中' : '暂无记录'}</p>}</div><footer className="wh-footer"><span>记录数 {serverPaged ? count : filtered.length}</span><button disabled={busy || page === 0} onClick={() => serverPaged ? load(page - 1) : setPage(page - 1)}>上一页</button><span>{page + 1} / {Math.max(1, Math.ceil((serverPaged ? count : filtered.length) / 100))}</span><button disabled={busy || (page + 1) * 100 >= (serverPaged ? count : filtered.length)} onClick={() => serverPaged ? load(page + 1) : setPage(page + 1)}>下一页</button></footer></section>
}
