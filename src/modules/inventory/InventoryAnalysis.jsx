import { useEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, Download, Filter, Search, X } from 'lucide-react'
import { api, download } from '../../api/client'
import './warehouse.css'
import './inventory-analysis.css'

const groups = [['inb_part', '物料编码'], ['loc_cost_type', '库位成本分类'], ['pt_prod_line', '产品类'], ['pt_part_type', '零件类型'], ['pt_group', '产品组'], ['loc_type', '库位类型'], ['inb_loc', '库位'], ['inb_lot', '批号']]
const tabs = [['stock', '库存明细'], ['demand', '需求明细'], ['order', '订购或生产中明细'], ['requisition', '请购中明细'], ['allocation', '已分配明细']]
const initial = (monthly) => ({ source: monthly ? 'dgyzx1' : 'local', site: '1000', groups: 'inb_part,loc_cost_type', period: new Date().toLocaleDateString('en-CA').slice(0, 7), direction: 'asc', sort: monthly ? 'inb_part' : 'tmp_part' })
function format(value, key, monthly) {
  if (value == null || value === '') return ''
  const precision = monthly && !key.includes('amt') && !key.startsWith('inb_cost_') && !key.match(/^inb_(beg|end)_/) && key !== 'diff_rate' ? 4 : 2
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: precision, maximumFractionDigits: precision })
}

export function InventoryAnalysis({ monthly = false, session, title }) {
  const resource = monthly ? 'material-monthly-inventory' : 'material-inventory-batch'
  const [filters, setFilters] = useState(() => initial(monthly))
  const [applied, setApplied] = useState(() => initial(monthly))
  const [data, setData] = useState({ columns: [], numeric_columns: [], results: [], totals: {}, count: 0 })
  const [options, setOptions] = useState({ periods: [], cost_types: {}, location_types: {} })
  const [page, setPage] = useState(1), [busy, setBusy] = useState(false), [error, setError] = useState('')
  const [selected, setSelected] = useState(''), [tab, setTab] = useState('stock'), [details, setDetails] = useState({ results: [] })
  const [includeWip, setIncludeWip] = useState(false), [condition, setCondition] = useState(null), [exporting, setExporting] = useState(false)
  const [detailBusy, setDetailBusy] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [fullTotals, setFullTotals] = useState(null), [totalsBusy, setTotalsBusy] = useState(false)
  const sequence = useRef(0)
  useEffect(() => { if (!monthly) return; let live = true; api(`/${resource}/choices/?site=${encodeURIComponent(applied.site)}`, { token: session.token }).then(r => { if (live) setOptions(r) }).catch(e => { if (live) setError(e.message) }); return () => { live = false } }, [resource, applied.site, session.token, monthly])
  useEffect(() => {
    const id = ++sequence.current
    const controller = new AbortController()
    setBusy(true); setError(''); setSelected(''); setDetails({ results: [] }); setFullTotals(null)
    api(`/${resource}/?${new URLSearchParams({ ...applied, page, ...(!monthly ? { page_mode: '1', page_size: 100 } : {}) })}`, { token: session.token, signal: controller.signal })
      .then(r => { if (id === sequence.current) setData(r) })
      .catch(e => { if (id === sequence.current) { setError(e.message); setData(old => ({ ...old, results: [], count: 0, totals: {} })) } })
      .finally(() => { if (id === sequence.current) setBusy(false) })
    return () => { sequence.current++; controller.abort() }
  }, [resource, applied, page, session.token])
  useEffect(() => {
    let live = true
    const controller = new AbortController()
    setDetails({ results: [] }); setDetailError(''); setDetailBusy(Boolean(selected && !monthly))
    if (selected && !monthly) api(`/${resource}/details/?${new URLSearchParams({ source: applied.source, site: applied.site, part: selected, tab, include_wip: includeWip ? '1' : '0' })}`, { token: session.token, signal: controller.signal })
      .then(r => { if (live) setDetails(r) }).catch(e => { if (live && e.name !== 'AbortError') setDetailError(e.message) }).finally(() => { if (live) setDetailBusy(false) })
    return () => { live = false; controller.abort() }
  }, [selected, tab, includeWip, resource, applied.site, applied.source, session.token, monthly])
  const change = (key, value) => setFilters(old => ({ ...old, [key]: value }))
  const execute = (values = filters) => { setPage(1); setApplied({ ...values }) }
  const sort = (key) => { const next = { ...applied, sort: key, direction: applied.sort === key && applied.direction === 'asc' ? 'desc' : 'asc' }; setFilters(old => ({ ...old, sort: next.sort, direction: next.direction })); execute(next) }
  const range = (key, label) => <label className="ia-range"><span>{label}</span><input aria-label={`${label}起始`} value={filters[key+'_from'] || ''} onChange={e => change(key+'_from', e.target.value)}/><span>至</span><input aria-label={`${label}结束`} value={filters[key+'_to'] || ''} onChange={e => change(key+'_to', e.target.value)}/></label>
  const numericFilters = JSON.parse(applied.numeric_filters || '{}')
  const applyCondition = (remove = false) => { const next = { ...numericFilters }; if (remove) delete next[condition.key]; else next[condition.key] = { op: condition.op, value: condition.value, high: condition.high }; const values = { ...applied, numeric_filters: JSON.stringify(next) }; setFilters(old => ({ ...old, numeric_filters: values.numeric_filters })); execute(values); setCondition(null) }
  const exportRows = async () => { setExporting(true); try { const result = await download(`/${resource}/export/`, { token: session.token, body: { filters: applied } }); const url = URL.createObjectURL(result.blob); const link = document.createElement('a'); link.href = url; link.download = result.filename; link.click(); URL.revokeObjectURL(url) } catch (e) { setError(e.message) } finally { setExporting(false) } }
  const totalsKey = JSON.stringify(applied)
  const shownTotals = fullTotals?.key === totalsKey ? fullTotals.values : data.totals
  const totalsLabel = fullTotals?.key === totalsKey || data.totals_scope !== 'page' ? '合计' : '本页合计'
  const calculateTotals = async () => {
    const requestId = sequence.current
    setTotalsBusy(true); setError('')
    try {
      const result = await api(`/${resource}/?${new URLSearchParams({ ...applied, page: 1, page_size: 1 })}`, { token: session.token })
      if (requestId === sequence.current) setFullTotals({ key: totalsKey, values: result.totals })
    } catch (e) { setError(e.message) } finally { setTotalsBusy(false) }
  }
  return <section className="wh-workspace ia-workspace" aria-label={title}>
    <div className="wh-tabs"><h1>{title}</h1></div>
    <form className="ia-filters" onSubmit={e => { e.preventDefault(); execute() }}>
      <div className="ia-fields"><label>站点<input aria-label="站点" value={filters.site} onChange={e => change('site', e.target.value)} required/></label>
        {monthly && <label>期间<input type="month" aria-label="期间" value={filters.period} onChange={e => change('period', e.target.value)} required list="ia-periods"/><datalist id="ia-periods">{options.periods.map(p => <option key={p} value={p}/>)}</datalist></label>}
        {range('material', '物料编码')}<label>名称或规格<input aria-label="名称或规格" value={filters.q || ''} onChange={e => change('q', e.target.value)}/></label>
        {monthly && <>{range('category', '产品类')}{range('part_type', '零件类型')}{range('group', '产品组')}{range('location', '库位')}<label>多个库位<input aria-label="多个库位" value={filters.locations || ''} onChange={e => change('locations', e.target.value)}/></label><label>成本差异率 ≥<input type="number" step="any" aria-label="成本差异率" value={filters.diff_rate || ''} onChange={e => change('diff_rate', e.target.value)}/>%</label></>}
      </div>
      {monthly && <div className="ia-options"><fieldset><legend>汇总维度</legend>{groups.map(([key, label]) => <label key={key}><input type="checkbox" checked={filters.groups.split(',').includes(key)} onChange={e => change('groups', e.target.checked ? [...filters.groups.split(',').filter(Boolean), key].join(',') : filters.groups.split(',').filter(k => k !== key).join(','))}/>{label}</label>)}</fieldset>
        {[['cost_types', '库位成本分类'], ['location_types', '库位类型']].map(([key, label]) => <fieldset key={key}><legend>{label}</legend><select multiple size={3} aria-label={label} value={filters[key] ? filters[key].split(',') : Object.keys(options[key])} onChange={e => change(key, [...e.target.selectedOptions].map(o => o.value).join(',') || '__none__')}>{Object.entries(options[key]).map(([code, name]) => <option key={code} value={code}>{code} {name}</option>)}</select><button type="button" onClick={() => change(key, '')}>全选</button><button type="button" onClick={() => change(key, '__none__')}>全不选</button></fieldset>)}</div>}
      <div className="ia-actions">{!monthly && <label>数据口径<select value={filters.source} onChange={e => change('source', e.target.value)}><option value="local">本地业务账</option><option value="dgyzx1">dgyzx1 历史快照</option></select></label>}<button type="submit" disabled={busy}><Search size={16}/>查询</button><button type="button" disabled={busy || exporting || !data.snapshot} onClick={exportRows}><Download size={16}/>导出</button>{!monthly && <label><input type="checkbox" checked={includeWip} onChange={e => setIncludeWip(e.target.checked)}/>库存明细显示生产线在制</label>}
      {!monthly && data.totals_scope === 'page' && <button type="button" disabled={busy || totalsBusy || !data.snapshot} onClick={calculateTotals}>{totalsBusy ? '计算合计中…' : '计算全部合计'}</button>}
      {Object.keys(numericFilters).length > 0 && <button type="button" onClick={() => { const values = { ...applied, numeric_filters: '{}' }; setFilters(old => ({ ...old, numeric_filters: '{}' })); execute(values) }}><X size={14}/>清除数量筛选</button>}</div>
    </form>
    {error && <div role="alert" className="wh-error">{error}</div>}
    <div className="ia-grid" aria-busy={busy}><table><thead><tr>{data.columns.map(([key, label]) => <th key={key} aria-sort={applied.sort === key ? applied.direction === 'asc' ? 'ascending' : 'descending' : 'none'}><div><button type="button" onClick={() => sort(key)}>{label}{applied.sort === key && (applied.direction === 'asc' ? <ArrowUp size={12}/> : <ArrowDown size={12}/>)}</button>{data.numeric_columns.includes(key) && <button type="button" className={numericFilters[key] ? 'ia-filter-active' : ''} title={`筛选${label}`} aria-label={`筛选${label}`} onClick={() => setCondition({ key, label, op: 'eq', value: '', high: '', ...numericFilters[key] })}><Filter size={13}/></button>}</div></th>)}</tr></thead>
      <tbody>{!busy && data.results.map((row, index) => <tr key={index} className={selected === row.tmp_part ? 'selected' : ''} onClick={() => setSelected(row.tmp_part || '')}>{data.columns.map(([key]) => <td key={key} className={`${data.numeric_columns.includes(key) ? 'ia-number' : ''} ${key === 'tmp_qty_remain' && Number(row[key]) < 0 ? 'ia-negative' : ''}`} title={String(row[key] ?? '')}>{data.numeric_columns.includes(key) ? format(row[key], key, monthly) : key === 'tmp_part' ? <button className="wh-link" onClick={() => setSelected(row.tmp_part)}>{row[key]}</button> : row[key]}</td>)}</tr>)}</tbody>
      <tfoot><tr>{data.columns.map(([key], i) => <td className="ia-number" key={key}>{i === 0 ? totalsLabel : shownTotals[key] != null ? format(shownTotals[key], key, monthly) : ''}</td>)}</tr></tfoot></table>
      {(busy || !data.results.length) && <p className="wh-empty">{busy ? '加载中' : data.snapshot ? '无匹配数据' : '该期间尚未同步报表数据'}</p>}
    </div>
    <footer className="wh-footer"><span>共 {data.count.toLocaleString()} 条</span><button title="上一页" aria-label="上一页" disabled={busy || page === 1} onClick={() => setPage(page-1)}><ChevronLeft size={16}/></button><span>{page} / {Math.max(1, Math.ceil(data.count/100))}</span><button title="下一页" aria-label="下一页" disabled={busy || page*100 >= data.count} onClick={() => setPage(page+1)}><ChevronRight size={16}/></button>{data.snapshot && <span>{data.snapshot.source === 'local' ? '本地库存及销售实时 · 其他需求基准 ' : 'dgyzx1 · '}{new Date(data.snapshot.captured_at).toLocaleString('zh-CN')}</span>}</footer>
    {!monthly && <div className="ia-details"><div role="tablist" className="wh-tabs">{tabs.map(([key, label]) => <button role="tab" aria-selected={tab === key} className={tab === key ? 'active' : ''} key={key} onClick={() => setTab(key)}>{label}</button>)}<span>{selected}</span></div><div className="ia-detail-grid"><table><thead><tr>{['来源类型', '单号/库位', '行号', '库位', '库位名称', '参与计算', '批号', '储位', '数量'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{details.results.map((row, i) => <tr key={i}>{['kind', 'document', 'line', 'location', 'location_name', 'eligible_for_balance', 'lot', 'position', 'quantity'].map(k => <td key={k}>{k === 'quantity' ? format(row[k], k, false) : k === 'eligible_for_balance' ? row[k] === false ? '否' : '是' : row[k]}</td>)}</tr>)}</tbody><tfoot><tr><td colSpan={8}>合计</td><td>{format(details.total, 'quantity', false)}</td></tr></tfoot></table>{!details.results.length && <p className="wh-empty">{detailBusy ? '正在加载明细…' : detailError ? `加载失败：${detailError}` : selected ? '无明细数据' : '未选择物料'}</p>}</div></div>}
    {condition && <QuantityCondition condition={condition} setCondition={setCondition} apply={applyCondition}/>}
  </section>
}

function QuantityCondition({ condition, setCondition, apply }) {
  const ref = useRef(null)
  useEffect(() => { ref.current.showModal() }, [])
  return <dialog ref={ref} className="ir-dialog ia-condition" onCancel={e => { e.preventDefault(); setCondition(null) }}><form onSubmit={e => { e.preventDefault(); apply() }}><header><h2>{condition.label}</h2><button type="button" title="关闭" aria-label="关闭筛选" onClick={() => setCondition(null)}><X size={18}/></button></header><label>比较方式<select aria-label="比较方式" value={condition.op} onChange={e => setCondition({ ...condition, op: e.target.value })}>{[['eq', '等于'], ['ne', '不等于'], ['gt', '大于'], ['ge', '大于等于'], ['lt', '小于'], ['le', '小于等于'], ['between', '范围']].map(([v, label]) => <option key={v} value={v}>{label}</option>)}</select></label><label>数值<input autoFocus type="number" step="any" required aria-label="数值" value={condition.value} onChange={e => setCondition({ ...condition, value: e.target.value })}/></label>{condition.op === 'between' && <label>上限<input type="number" step="any" required aria-label="上限" value={condition.high} onChange={e => setCondition({ ...condition, high: e.target.value })}/></label>}<footer><button type="button" onClick={() => apply(true)}>清除此列</button><button type="submit">确定</button></footer></form></dialog>
}
