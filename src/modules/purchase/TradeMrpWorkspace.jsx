import { useState } from 'react'
import { Search, Check, CheckSquare, Square, Copy, History, HelpCircle, Ban, X } from 'lucide-react'
import { api } from '../../api/client'
import { sum, today, dateTime } from './PurchaseControls'
import '../inventory/warehouse.css'
import './trade-mrp.css'

const tabs = [['detail', '需求明细'], ['document', '按单据汇总'], ['material', '按物料汇总'], ['date', '按物料＋需求日期汇总']]
const quantity = value => sum([value ?? '0']).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '')
const positive = value => Number(value) > 0
const validQty = value => /^\d{1,11}(?:\.\d{1,8})?$/.test(String(value))
const initialFilters = { site: '1000', mode: 'net', date_from: '', date_to: '', order: '', material: '', customer: '', customer_po: '', customer_material_id: null, last_pr: true }
const states = { preview: '未确认', confirmed: '已生成', cancelled: '已取消' }

export function TradeMrpWorkspace({ session, onOpenRequisition, onClose }) {
  const [filters, setFilters] = useState(initialFilters)
  const [run, setRun] = useState(null)
  const [tab, setTab] = useState('detail')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [quantities, setQuantities] = useState({})
  const [selected, setSelected] = useState(new Set())
  const [reason, setReason] = useState('')
  const [confirmation, setConfirmation] = useState(null)
  const [header, setHeader] = useState({ requester: session.username || '', request_date: today(), notes: '' })
  const [display, setDisplay] = useState({ short: false, positive: false })
  const [sort, setSort] = useState('date')
  const [history, setHistory] = useState(null)
  const [drill, setDrill] = useState(null)
  const [lookup, setLookup] = useState({ q: '', rows: [], chosen: null })
  const [help, setHelp] = useState(false)
  const [batch, setBatch] = useState(null)
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const perform = async action => {
    setBusy(true); setError('')
    try { await action() } catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const results = run?.results || []
  const editable = run?.status === 'preview'
  const actual = source => quantities[source.sales_order_line_id] ?? quantity(source.suggested_qty)
  const chosenQty = (row, sources = row.source_snapshot) => sum(sources.filter(s => selected.has(s.sales_order_line_id)).map(actual))
  const visibleResults = results.filter(r => !display.short || positive(r.shortage_qty))
  const sourcesFor = row => row.source_snapshot.filter(s => !display.positive || positive(actual(s)))
  const detail = visibleResults.flatMap(row => sourcesFor(row).map(source => ({ row, source })))
  detail.sort((a,b) => {
    const key = entry => sort === 'material' ? entry.row.material_code : sort === 'order' ? entry.source.sales_order : entry.source.promised_date
    return String(key(a)).localeCompare(String(key(b))) || a.source.line-b.source.line
  })
  const selectedEntries = results.flatMap(row => row.source_snapshot.filter(s => selected.has(s.sales_order_line_id)).map(source => ({ row, source })))
  const invalid = selectedEntries.some(({ source }) => !validQty(actual(source)))
  const canPreview = editable && !invalid && selectedEntries.some(({ source }) => positive(actual(source))) && !selectedEntries.some(({ row }) => row.calculation_snapshot.issues?.length)
  const adopt = next => {
    setRun(next); setBatch(null); setQuantities({}); setReason(''); setConfirmation(null); setDrill(null)
    const plan = next.confirmation_snapshot?.plan
    if (plan) {
      setHeader({ requester: next.confirmed_by || session.username || '', request_date: today(), notes: '', ...plan.header })
      setSelected(new Set(plan.lines.map(x => x.source_id)))
      setQuantities(Object.fromEntries(plan.lines.map(x => [x.source_id, x.quantity])))
    } else setSelected(new Set(next.results.filter(r => !r.calculation_snapshot.issues?.length).flatMap(r => r.source_snapshot.filter(s => positive(s.suggested_qty)).map(s => s.sales_order_line_id))))
  }
  const calculate = () => perform(async () => {
    setNotice(''); setConfirmation(null); setRun(null)
    const body = Object.fromEntries(Object.entries(filters).map(([key, value]) => [key, (key.includes('date_') || key.startsWith('line_')) && value === '' ? null : value]))
    adopt(await request('/trade-mrp/preview/', { method: 'POST', body }))
  })
  const changeFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value })); setRun(null); setBatch(null); setConfirmation(null); setDrill(null)
  }
  const payload = () => ({ selected_sources: [...selected], source_quantities: Object.fromEntries(selectedEntries.map(({ source }) => [source.sales_order_line_id, actual(source)])), adjustment_reason: reason, header })
  const preview = () => perform(async () => {
    const body = payload()
    const plan = await request(`/trade-mrp/${run.id}/generation-preview/`, { method: 'POST', body })
    setConfirmation({ plan, body })
  })
  const confirm = () => perform(async () => {
    const req = await request(`/trade-mrp/${run.id}/confirm/`, { method: 'POST', body: confirmation.body })
    setNotice(`已生成标准P型请购草稿 ${req.number}，需另行提交审核。`)
    adopt(await request(`/trade-mrp/${run.id}/`))
  })
  const loadHistory = (page = 1) => perform(async () => {
    setHistory(await request(`/trade-mrp/?${new URLSearchParams({ site: filters.site, page })}`))
  })
  const cancelRun = () => perform(async () => adopt(await request(`/trade-mrp/${run.id}/cancel/`, { method: 'POST', body: {} })))
  const toggle = (ids, checked) => setSelected(prev => {
    const next = new Set(prev); ids.forEach(id => checked ? next.add(id) : next.delete(id)); return next
  })
  const checkbox = (row, source) => {
    const ids = source ? [source.sales_order_line_id] : sourcesFor(row).map(s => s.sales_order_line_id)
    return <input type="checkbox" aria-label={`选择 ${source ? `${source.sales_order}/${source.line}` : row.material_code}`} checked={ids.length > 0 && ids.every(id => selected.has(id))} disabled={busy || !editable || !!row.calculation_snapshot.issues?.length} onChange={e => toggle(ids, e.target.checked)} />
  }
  const showSources = (row, kind) => setDrill({ row, kind, rows: kind === 'demand' ? row.calculation_snapshot.global_demand : row.calculation_snapshot.supply.filter(x => kind === 'all' || x.kind === kind || (x.kind === 'requisition' && (kind === 'approved_requisition' ? x.status === 'approved' : kind === 'pending_requisition' && x.status !== 'approved'))) })
  const metric = (row, value, kind) => <button className="mrp-link" onClick={() => showSources(row, kind)}>{quantity(value)}</button>
  const groups = new Map()
  detail.forEach(({ row, source }) => {
    const key = tab === 'document' ? `${source.sales_order}:${row.uom}` : `${row.material}:${source.promised_date}`
    if (!groups.has(key)) groups.set(key, { key, label: tab === 'document' ? source.sales_order : row.material_code, date: source.promised_date, uom: row.uom_name, entries: [] })
    groups.get(key).entries.push({ row, source })
  })
  const totals = new Map()
  detail.forEach(({ row, source }) => {
    if (!totals.has(row.uom)) totals.set(row.uom, { unit: row.uom_name, demand: [], selected: [] })
    totals.get(row.uom).demand.push(source.quantity)
    if (selected.has(source.sales_order_line_id)) totals.get(row.uom).selected.push(actual(source))
  })
  const sourceQtyInput = (row, source) => <input className="mrp-quantity" inputMode="decimal" aria-label={`本次请购 ${source.sales_order}/${source.line}`} value={actual(source)} disabled={busy || !editable || !selected.has(source.sales_order_line_id) || !!row.calculation_snapshot.issues?.length} onChange={e => setQuantities(prev => ({ ...prev, [source.sales_order_line_id]: e.target.value }))} />
  const range = (key, label, type = 'text') => <div className="mrp-range" key={key}><span>{label}</span><input aria-label={`${label}起`} type={type} min={type==='number'?0:undefined} value={filters[`${key}_from`] ?? ''} disabled={busy} onChange={e=>changeFilter(`${key}_from`,e.target.value)} /><span>→</span><input aria-label={`${label}止`} type={type} min={type==='number'?0:undefined} value={filters[`${key}_to`] ?? ''} disabled={busy} onChange={e=>changeFilter(`${key}_to`,e.target.value)} /></div>
  const info = row => row.calculation_snapshot.material_info || {}
  const descriptionColumns = [['主件编码',r=>info(r).code || r.material_code],['主件名称',r=>info(r).name || r.material_name],['主件英文名称',r=>info(r).english_name],['主件规格',r=>info(r).specification]]
  const detailColumns = [
    ['选择',(r,s)=>checkbox(r,s)],['类型',()=> '采购'],['订单编号',(r,s)=>s.sales_order],['行号/标志',(r,s)=>s.line],['客户订单号',(r,s)=>s.customer_po],
    ...descriptionColumns,['序号',(r,s)=>s.analysis_sequence],
    ['子件编码',r=>info(r).code || r.material_code],['子件名称',r=>info(r).name || r.material_name],['子件英文名称',r=>info(r).english_name],['子件规格',r=>info(r).specification],
    ['需求数量',(r,s)=>quantity(s.quantity),'numeric'],['库存余量',r=>quantity(r.calculation_snapshot.balance_qty),'numeric'],['短缺数量',r=>quantity(r.shortage_qty),'numeric'],['请购数量',(r,s)=>sourceQtyInput(r,s),'numeric'],
    ['MRP总需求数',r=>metric(r,r.demand_qty,'demand'),'numeric'],['可用库存数',r=>metric(r,r.available_qty,'stock'),'numeric'],['不可用库存',r=>quantity(r.calculation_snapshot.unavailable_qty),'numeric'],
    ['订购数（已审核）',r=>metric(r,r.on_order_qty,'purchase'),'numeric'],['请购中数量（已审核）',r=>metric(r,r.approved_requisition_qty,'approved_requisition'),'numeric'],['待审核覆盖',r=>metric(r,r.pending_requisition_qty,'pending_requisition'),'numeric'],
    ['库存单位',r=>r.uom_name],['需求日期',(r,s)=>s.promised_date],['建议到货日',(r,s)=>s.arrival_date],['逾期',(r,s)=>s.overdue?'是':'否'],['订单备注',(r,s)=>s.order_notes],
    ['安全存量',r=>quantity(r.safety_stock_qty),'numeric'],['产品类',r=>info(r).category],['产品类名称',r=>info(r).category_name],['产品组',r=>info(r).product_group],['产品组名称',r=>info(r).product_group_name],['零件类型',r=>info(r).part_type],['零件类型名称',r=>info(r).part_type_name],
    ['最小采购数量',r=>quantity(r.calculation_snapshot.min_purchase_qty),'numeric'],['最小包装数量',r=>quantity(r.calculation_snapshot.min_pack_qty),'numeric'],['单别',(r,s)=>s.order_type],
    ['原始分配',(r,s)=>quantity(s.allocated_qty),'numeric'],['其中补足',(r,s)=>quantity(s.supplement_qty),'numeric'],['包装差量',(r,s)=>quantity(s.packaging_delta),'numeric'],['建议请购',(r,s)=>quantity(s.suggested_qty),'numeric'],
    ['客户',(r,s)=>s.customer],['客户料号',(r,s)=>s.customer_material_code],['终端料号',(r,s)=>s.terminal_material_code]
  ]
  const resultTabs = <nav className="wh-tabs mrp-tabs" aria-label="结果视图">{tabs.map(([key,name]) => <button key={key} className={tab===key?'active':''} aria-pressed={tab===key} onClick={() => setTab(key)}>{name}</button>)}</nav>
  return <section className="wh-workspace trade-mrp" aria-label="贸易端MRP">
    <div className="wh-toolbar mrp-toolbar">
      <button onClick={calculate} disabled={busy} title="按当前条件重新计算"><Search size={18} />{busy ? '处理中…' : '查询'}</button>
      <button disabled={busy || !editable} onClick={() => toggle(detail.filter(({row})=>!row.calculation_snapshot.issues?.length).map(({source})=>source.sales_order_line_id),true)} title="选中当前显示的可用来源"><CheckSquare size={18}/>全选中</button>
      <button disabled={busy || !editable} onClick={() => setSelected(new Set())}><Square size={18}/>全不选</button>
      <button disabled={busy || !editable || !selectedEntries.length} onClick={()=>setBatch('')} title="为已选来源填写相同请购数量"><Copy size={18}/>相同值</button>
      <button onClick={preview} disabled={busy || !canPreview} title="预览后确认生成标准 P 请购"><Check size={18} />生成预览</button>
      <span className="wh-divider"/>
      <button onClick={() => loadHistory()} disabled={busy}><History size={18}/>历史运算</button>
      <button onClick={cancelRun} disabled={busy || !editable}><Ban size={18}/>取消本批次</button>
      <button onClick={()=>setHelp(!help)} aria-expanded={help}><HelpCircle size={18}/>帮助</button>
      <button onClick={onClose} disabled={busy}><X size={18}/>关闭</button>
      <h1>物料请购需求分析 <small>贸易端 MRP</small></h1>
    </div>
    <div className="mrp-query-panel">
      <fieldset className="mrp-query"><legend>订单来源</legend>
        <label className="mrp-field">站点<input value={filters.site} onChange={e=>changeFilter('site',e.target.value)} disabled={busy}/></label>
        {range('order','客户订单')}{range('line','行号/标志','number')}{range('order_date','订单日期','date')}{range('date','订单行交期','date')}{range('material','物料编码')}{range('category','产品类')}
        <div className="mrp-pair">{[['planner','计划员'],['buyer','采购员']].map(([key,label])=><label className="mrp-field" key={key}>{label}<input value={filters[key] || ''} disabled={busy} onChange={e=>changeFilter(key,e.target.value)}/></label>)}</div>
      </fieldset>
      <fieldset className="mrp-options"><legend>运算与生成</legend>
        <label className="mrp-field">请购单汇总方式<output>不汇总（每条来源独立一行）</output></label>
        <label className="mrp-field">请购单程序类型<output>P · 标准请购单</output></label>
        <label className="mrp-field">请购数量规则<output>净需求 · 共享库存</output></label>
        <label className="mrp-field">排序方式<select value={sort} onChange={e=>setSort(e.target.value)}><option value="date">需求日期</option><option value="order">订单编号</option><option value="material">物料编码</option></select></label>
        <label className="mrp-check"><input type="checkbox" checked={display.short} onChange={e => setDisplay({ ...display,short:e.target.checked })} />只列出有短缺物料</label>
        <label className="mrp-check"><input type="checkbox" checked={filters.last_pr} onChange={e => changeFilter('last_pr',e.target.checked)} disabled={busy} />最后一笔补足物料剩余短缺</label>
        <label className="mrp-check"><input type="checkbox" checked={display.positive} onChange={e => setDisplay({ ...display,positive:e.target.checked })} />只显示请购量大于0</label>
        <p className="mrp-note">显示筛选保留已选项；排序不改变运算分配。</p>
      </fieldset>
      <fieldset className="mrp-generation"><legend>生成结果</legend>
        <div className="mrp-result-log" aria-label="生成结果" aria-live="polite">
          {!run && !busy && <p>设置订单来源后，点击“查询”。</p>}{busy && <p>正在处理，请稍候…</p>}
          {run && <><p>批次 #{run.id} · {states[run.status]}</p><p>{results.length} 种物料 · 已选 {selected.size} 条来源</p><p>{dateTime(run.created_at)} · {run.created_by}</p></>}
          {run && <p>{run.generation_readiness?.message || (run.generation_enabled ? '当前账套已启用生成。' : '当前账套未启用生成。')}</p>}
          {run?.generation_readiness?.local_test && <p><strong>本机测试账套</strong><br/>冻结基准：{dateTime(run.generation_readiness.baseline_at)}</p>}
          {error && <p className="mrp-error" role="alert">{error}</p>}{notice && <p className="mrp-success" role="status">{notice}</p>}
          {results.filter(r=>r.calculation_snapshot.issues?.length).map(r=><p key={r.id} className="mrp-error" role="alert">{r.material_code}：{r.calculation_snapshot.issues.join('；')}。</p>)}
          {run?.confirmation_snapshot?.requisition_number && <p>原生成单号：{run.confirmation_snapshot.requisition_number}</p>}
        </div>
        <button disabled={!run?.confirmation_snapshot?.requisition_id || busy} onClick={()=>onOpenRequisition?.(run.confirmation_snapshot.requisition_id)}>查询请购单</button>
      </fieldset>
    </div>
    {run?.generation_readiness?.excluded_materials?.length > 0 && <details className="mrp-more"><summary>已排除 {run.generation_readiness.excluded_materials.length} 个单位冲突物料（保留原数据）</summary><p>{run.generation_readiness.excluded_materials.map(x=>`${x.source_code}：${x.local_unit} / 源 ${x.source_unit}`).join('；')}</p><p>这些物料不进入可生成范围；缺少源订单的物料也列在此处，不以结果行数判断完整性。</p></details>}
    <details className="mrp-more"><summary>更多查询条件 · 客户 / 料号映射</summary>
    <div className="mrp-filters">
      {[['customer','客户编码或名称'],['customer_po','客户PO'],['order','订单号包含'],['material','物料编码或名称']].map(([key,title]) => <label className="mrp-field" key={key}>{title}<input value={filters[key]} onChange={e => changeFilter(key,e.target.value)} disabled={busy} /></label>)}
    </div>
    <details className="mrp-lookup"><summary>通过终端料号／客户料号定位</summary>
      <div className="mrp-actions"><input aria-label="客户物料检索" placeholder="终端料号、客户料号或内部料号" value={lookup.q} onChange={e => setLookup({ ...lookup, q:e.target.value })} /><button disabled={busy || !lookup.q.trim()} onClick={() => perform(async () => setLookup({ ...lookup, rows:await request(`/trade-mrp/customer-materials/?q=${encodeURIComponent(lookup.q)}`) }))}>查找映射</button><button disabled={busy || !filters.customer_material_id} onClick={() => { changeFilter('customer_material_id',null); setLookup({ ...lookup,chosen:null }) }}>清除映射限制</button></div>
      <p>最多列出50项。相同料号命中多个客户或内部物料时，请选择准确的一条关系。</p>
      {lookup.rows.map(r => <button className="mrp-mapping" key={r.id} disabled={busy} onClick={() => { changeFilter('customer_material_id',r.id);setLookup({ ...lookup,chosen:r }) }}>{r.customer} · {r.customer_name} / {r.material} · {r.material_name} / 客户料号 {r.customer_code} / 终端料号 {r.terminal_code || '—'}</button>)}
    </details>
    {filters.customer_material_id && <p className="mrp-note">已限定客户物料关系 #{filters.customer_material_id} {lookup.chosen?.customer} / {lookup.chosen?.material} / {lookup.chosen?.customer_code}</p>}
    </details>
    {help && <section className="mrp-help" aria-label="使用帮助"><strong>本期范围：客户订单 → 贸易净需求 → 标准 P 请购</strong><p>库存按同站点、同物料共用，物料总需求包含来源筛选外的有效订单。已审核供应与本网页 MRP 待审核覆盖分列，其他未审核请购不抵扣。需检物料、非普通库存采购及非 1:1 换算阻止生成。</p><p>贸易模式不展开 BOM，主件与子件为同一采购物料。生产线、开工日、领退料、生产净需求、制造分配、余料仓、单位用量、领料单位、生产及完成数量不适用；产品组与零件类型名称使用库存模块的源字典，未导入或未匹配时留空。空白历史字段用“—”表示未记录。</p><p>物料级库存与短缺在来源行重复展示以便对照，不累加；底部仅按库存单位合计当前显示来源。全选中仅选择当前显示的可用来源，全不选清除全部选择；相同值应用到所有已选来源，修改数量必须填写原因。生成结果保留原快照，请购页显示当前数量。</p></section>}
    {batch !== null && <section className="mrp-batch" aria-label="相同值设置"><label>已选 {selectedEntries.length} 条来源的请购数量<input autoFocus aria-label="相同请购数量" inputMode="decimal" value={batch} onChange={e=>setBatch(e.target.value)}/></label><button disabled={!validQty(batch)||busy||!editable} onClick={()=>{setQuantities(prev=>({...prev,...Object.fromEntries(selectedEntries.map(({source})=>[source.sales_order_line_id,batch]))}));setBatch(null)}}>应用到已选来源</button><button onClick={()=>setBatch(null)}>取消相同值</button><span>包含显示筛选外的已选来源；调整后需填写原因。</span></section>}
    {invalid && <p className="mrp-error" role="alert">本次请购量必须为非负数，最多11位整数、8位小数。</p>}
    {history && <section className="mrp-history" aria-label="历史运算"><div className="mrp-actions"><strong>历史运算 · 共 {history.count} 批</strong><button onClick={() => setHistory(null)}>关闭历史</button></div>
      <div className="mrp-table"><table><thead><tr>{['批次','站点','运算时间','操作人','状态','生成单号','查看'].map(x => <th key={x}>{x}</th>)}</tr></thead><tbody>{history.results.map(r => <tr key={r.id}><td>#{r.id}</td><td>{r.site}</td><td>{dateTime(r.created_at)}</td><td>{r.created_by}</td><td>{states[r.status] || r.status}</td><td>{r.confirmation_snapshot?.requisition_number}</td><td><button disabled={busy} onClick={() => perform(async () => { const next=await request(`/trade-mrp/${r.id}/`);setFilters({...initialFilters,...next.filters,site:next.site});setLookup(prev=>({...prev,chosen:null}));adopt(next);setHistory(null) })}>查看批次 {r.id}</button></td></tr>)}</tbody></table></div>
      <div className="mrp-actions"><button disabled={busy || history.page<=1} onClick={() => loadHistory(history.page-1)}>上一页</button><span>第 {history.page} 页</span><button disabled={busy || history.page*20>=history.count} onClick={() => loadHistory(history.page+1)}>下一页</button></div>
    </section>}
    {!run ? <>{resultTabs}<div className="mrp-table mrp-results"><table><thead><tr>{detailColumns.map(([label])=><th key={label}>{label}</th>)}</tr></thead></table><p className="mrp-empty">设置条件后点击“查询”，查看订单需求与请购建议。</p></div></> : <>
      <div className="mrp-entry-header">
        {[['requester','请购人','text'],['request_date','请购日期','date'],['notes','请购备注','text']].map(([key,title,type])=><label className="mrp-field" key={key}>{title}<input type={type} value={header[key]} maxLength={key==='notes'?240:64} disabled={busy||!editable} onChange={e=>setHeader({...header,[key]:e.target.value})}/></label>)}
        <label className="mrp-field mrp-reason">调整原因<input aria-label="人工调整原因（修改本次请购量时必填）" placeholder="修改请购量时必填" value={reason} onChange={e=>setReason(e.target.value)} maxLength={1000} disabled={busy||!editable}/></label>
      </div>
      {resultTabs}
      <div className="mrp-table mrp-results" role="region" aria-label={tabs.find(([key])=>key===tab)[1]} tabIndex={0}>
        {tab==='detail' && <table><thead><tr>{detailColumns.map(([label])=><th key={label}>{label}</th>)}</tr></thead><tbody>{detail.map(({row,source})=><tr className={selected.has(source.sales_order_line_id)?'selected':''} key={source.sales_order_line_id}>{detailColumns.map(([label,render,style])=><td className={style} key={label}>{render(row,source) ?? '—'}</td>)}</tr>)}</tbody></table>}
        {tab==='material' && <table><thead><tr>{['选择','物料','名称','库存单位','全物料需求','可用库存','不可用库存','已审核采购中','已审核请购中','待审核覆盖','安全存量','库存余量','短缺','建议请购','本次请购合计','供需明细'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{visibleResults.filter(r=>!display.positive || sourcesFor(r).length).map(r=><tr key={r.id}><td>{checkbox(r)}</td><td>{r.material_code}</td><td>{r.material_name}</td><td>{r.uom_name}</td><td>{metric(r,r.demand_qty,'demand')}</td><td>{metric(r,r.available_qty,'stock')}</td><td>{quantity(r.calculation_snapshot.unavailable_qty)}</td><td>{metric(r,r.on_order_qty,'purchase')}</td><td>{metric(r,r.approved_requisition_qty,'approved_requisition')}</td><td>{metric(r,r.pending_requisition_qty,'pending_requisition')}</td>{[r.safety_stock_qty,r.calculation_snapshot.balance_qty,r.shortage_qty,r.suggested_qty].map((v,i)=><td key={i}>{quantity(v)}</td>)}<td aria-label={`本次请购合计 ${r.material_code}`}>{quantity(chosenQty(r))}</td><td><button onClick={()=>showSources(r,'all')}>查看构成</button></td></tr>)}</tbody></table>}
        {(tab==='document'||tab==='date') && <table><thead><tr><th>{tab==='document'?'订单编号':'物料编码'}</th>{tab==='date'&&<th>原需求日期</th>}<th>库存单位</th><th>来源行数</th><th>来源需求</th><th>建议请购</th><th>本次请购合计</th></tr></thead><tbody>{[...groups.values()].map(g=><tr key={g.key}><td>{g.label}</td>{tab==='date'&&<td>{g.date}</td>}<td>{g.uom}</td><td>{g.entries.length}</td><td>{quantity(sum(g.entries.map(({source})=>source.quantity)))}</td><td>{quantity(sum(g.entries.map(({source})=>source.suggested_qty)))}</td><td>{quantity(sum(g.entries.filter(({source})=>selected.has(source.sales_order_line_id)).map(({source})=>actual(source))))}</td></tr>)}</tbody></table>}
        {!detail.length && <p className="mrp-empty">没有符合显示条件的来源。</p>}
      </div>
      <div className="wh-footer mrp-totals"><span>当前显示 {detail.length} 条 · 全批次已选 {selected.size} 条</span><span>筛选来源合计：{[...totals.values()].map(t=>`${t.unit}：需求 ${quantity(sum(t.demand))}，已选本次 ${quantity(sum(t.selected))}`).join('；') || '0'}。物料级库存及在途不累加。</span></div>
      {drill && <section className="mrp-drill" aria-label="供需构成"><div className="mrp-actions"><strong>{drill.row.material_code} · {drill.kind==='demand'?'全物料需求':'供应构成'}</strong><button onClick={()=>setDrill(null)}>关闭构成</button></div><div className="mrp-table"><table><thead><tr>{['类型','单号／库位','行／批号','数量','预留','状态／参与','日期','换算分子','换算分母'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{drill.rows.map((s,i)=><tr key={i}><td>{s.kind || '销售订单'}</td><td>{s.number || s.order || s.location}</td><td>{s.line || s.batch || '—'}</td><td>{quantity(s.quantity)}</td><td>{s.reserved || '—'}</td><td>{s.status || (s.usable===false?'不可用／不参与':'参与')}</td><td>{s.date || '—'}</td><td>{s.rate_m || '1'}</td><td>{s.rate_d || '1'}</td></tr>)}</tbody></table></div><p className="mrp-note">库位不可用、停用、不参与MRP或不良库存不计入可用；未审核采购、非P请购、委外与制造供需不进入本贸易池。</p></section>}
    </>}
    {confirmation && <div className="mrp-backdrop"><section className="mrp-dialog" role="dialog" aria-modal="true" aria-label="确认生成标准请购" onKeyDown={e=>{
      if(e.key==='Escape'&&!busy)setConfirmation(null)
      if(e.key==='Tab'){const buttons=[...e.currentTarget.querySelectorAll('button:not(:disabled)')];const target=e.shiftKey&&e.target===buttons[0]?buttons.at(-1):!e.shiftKey&&e.target===buttons.at(-1)?buttons[0]:null;if(target){e.preventDefault();target.focus()}}
    }}><header><h2>确认生成标准请购</h2><button autoFocus aria-label="关闭生成预览" onClick={()=>setConfirmation(null)} disabled={busy}><X size={18}/></button></header>
      {error && <p className="mrp-error" role="alert">{error}</p>}
      <p>站点 {run.site} · 不汇总 · 一张 P 请购草稿，{confirmation.plan.lines.length} 条来源各保留一行。四种显示视图不会改变生成方式。</p>
      <p>请购人：{header.requester} · 日期：{header.request_date} · {header.notes}</p>
      <div className="mrp-table"><table><thead><tr>{['物料','来源','库存单位','建议量','本次数量','人工差量','补足量','包装差量','原需求日期','建议到货日'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{confirmation.plan.lines.map(s=><tr key={s.source_id}><td>{s.material_code}</td><td>{s.source_number}/{s.source_line}</td><td>{s.uom}</td>{[s.suggested_qty,s.quantity,s.adjustment_delta,s.supplement_qty,s.packaging_delta].map((v,i)=><td key={i}>{quantity(v)}</td>)}<td>{s.original_date}</td><td>{s.needed_date}</td></tr>)}</tbody></table></div>
      <p>确认时再次核验供需。生成后须另行审核；重复提交会返回同一单据。</p>{!run.generation_enabled&&<p className="mrp-note">当前账套尚未启用生成。</p>}<div className="mrp-actions"><button onClick={()=>setConfirmation(null)} disabled={busy}>返回调整</button><button className="mrp-primary" onClick={confirm} disabled={busy||!run.generation_enabled}>确认生成 P 型请购</button></div>
    </section></div>}
  </section>
}
