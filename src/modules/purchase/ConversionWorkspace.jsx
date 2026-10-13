import { useState } from 'react'
import { Search, Check, CheckSquare, Square, X, ArrowRight } from 'lucide-react'
import { api } from '../../api/client'
import { can } from '../../auth/session'
import { Lookup, LookupField, Tool, PurchaseGrid, format, sum, today, amounts, converted } from './PurchaseControls'
import './purchase-workspace.css'

const columns = [['selected','选择'],['supplier_code','供应商代码'],['supplier_name','供应商简称'],['currency_code','币种'],['tax_rate','增值税率%'],['requester','请购人'],['number','请购单号'],['line_number','请购行号'],['material_code','物料编码'],['material_name','物料名称'],['english_name','英文名称'],['specification','规格'],['customer_material','客户物料'],['supplier_material','供应商物料编码'],['request_date','请购日期'],['needed_date','需求日期'],['requested_qty','请购数量'],['uom_name','库存单位'],['original_price','采购单价'],['amount','采购金额'],['purchase_uom_name','采购单位'],['min_purchase_qty','最小采购数量'],['min_pack_qty','最小包装数量'],['converted_qty','已采购数量'],['remaining','剩余数量'],['quantity','本次分配数量'],['unit_price','本次单价'],['department_name','采购部门'],['payment_method','支付方式'],['reason','不可转原因']]
const previewColumns = [['supplier_code','供应商'],['supplier_name','简称'],['material_code','物料编码'],['material_name','物料名称'],['currency_code','币种'],['tax_rate','税率%'],['source_quantity','采购数量'],['quantity','合计采购数量'],['extra_quantity','额外采购数量'],['original_price','原单价'],['unit_price','新单价'],['amount','采购金额'],['source','请购来源']]

export function ConversionWorkspace({ session, onOpenOrder, onClose }) {
  const request = (path, options) => api(path, { token: session.token, ...options })
  const [filters, setFilters] = useState({}), [applied, setApplied] = useState({}), [page, setPage] = useState(1)
  const [result, setResult] = useState({ count: 0, results: [] }), [selected, setSelected] = useState({})
  const [options, setOptions] = useState({ grouping: '3', document_type: 'standard', auto_number: true, consider_pack: true, line_limit: '0', order_date: today() })
  const [defaults, setDefaults] = useState({}), [lookup, setLookup] = useState(null), [preview, setPreview] = useState(null)
  const [generation, setGeneration] = useState(null), [orders, setOrders] = useState([]), [askOpen, setAskOpen] = useState(false)
  const [previewPrices, setPreviewPrices] = useState({})
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [queried, setQueried] = useState(false)
  const run = async fn => { setBusy(true); setError(''); try { await fn() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const load = async (values = applied, p = page) => { setResult(await request(`/purchase-requisition/purchase-candidates/?${new URLSearchParams({ ...values, page: p })}`)); setPage(p); setQueried(true) }
  const chooseRows = rows => run(async () => {
    let choices = rows
    if (defaults.supplier && rows.length) {
      const data = await request(`/purchase-requisition/purchase-candidates/?${new URLSearchParams({ ids: rows.map(r => r.id).join(','), supplier: defaults.supplier, order_date: options.order_date })}`)
      choices = data.results
    }
    setSelected(old => ({ ...old, ...Object.fromEntries(choices.map(r => [r.id, old[r.id] || { ...defaults, ...r, department: defaults.department || r.department, department_name: defaults.department_name || r.department_name }])) }))
  })
  const choose = (row, checked) => checked ? chooseRows([row]) : setSelected(old => { const next = { ...old }; delete next[row.id]; return next })
  const edit = (id, values) => { setSelected(old => ({ ...old, [id]: { ...old[id], ...values } })); setPreview(null) }
  const query = () => run(async () => { setApplied({ ...filters }); setSelected({}); await load(filters, 1) })
  const submit = () => run(async () => {
    const body = { ...options, lines: Object.values(selected).map(r => ({ line_id: r.id, quantity: r.quantity, unit_price: r.unit_price, supplier: r.supplier, department: r.department, currency: r.currency, tax_rate: r.tax_rate, payment_method: r.payment_method, needed_date: r.needed_date })) }
    const data = await request('/purchase-requisition/purchase-preview/', { method: 'POST', body })
    setPreviewPrices({}); setPreview(data); setGeneration({ ...body, fingerprint: data.fingerprint, idempotency_key: crypto.randomUUID() })
  })
  const generate = () => run(async () => {
    if (Object.keys(previewPrices).length) {
      const body = { ...generation, lines: generation.lines.map(r => ({ ...r, unit_price: previewPrices[r.line_id] ?? r.unit_price })) }
      const updated = await request('/purchase-requisition/purchase-preview/', { method: 'POST', body })
      setPreview(updated); setPreviewPrices({}); setGeneration({ ...body, fingerprint: updated.fingerprint, idempotency_key: crypto.randomUUID() })
      return
    }
    const data = await request('/purchase-requisition/purchase-generate/', { method: 'POST', body: generation })
    setOrders(data.orders); setPreview(null); setAskOpen(true); setSelected({}); await load()
  })
  const pick = row => run(async () => {
    const values = lookup.kind === 'supplier' ? { supplier: row.id, supplier_code: row.code, supplier_name: row.name, currency: row.currency, currency_code: row.currency_code, tax_rate: row.tax_rate, payment_method: row.payment_method, unit_price: '' }
      : { department: row.id, department_name: row.name }
    const ids = lookup.id ? [lookup.id] : Object.keys(selected)
    const refreshed = {}
    if (lookup.kind === 'supplier') {
      for (let i = 0; i < ids.length; i += 50) {
        const data = await request(`/purchase-requisition/purchase-candidates/?${new URLSearchParams({ ids: ids.slice(i, i + 50).join(','), supplier: row.id, order_date: options.order_date })}`)
        data.results.forEach(r => { refreshed[r.id] = r })
      }
    }
    setSelected(old => Object.fromEntries(Object.entries(old).map(([id, r]) => [id, ids.map(String).includes(id) ? { ...r, ...values, ...(refreshed[id] || {}), quantity: r.quantity, department: lookup.kind === 'department' ? row.id : r.department, department_name: lookup.kind === 'department' ? row.name : r.department_name } : r])))
    if (!lookup.id) setDefaults(old => ({ ...old, ...values }))
    setPreview(null)
    setLookup(null)
  })
  const cell = (raw, key, label) => {
    const row = selected[raw.id] || raw, chosen = !!selected[raw.id]
    if (key === 'selected') return <input type="checkbox" aria-label={`选择${row.number}行${row.line_number}`} checked={chosen} disabled={busy || !!row.reason} onChange={e => choose(raw, e.target.checked)} />
    if (key === 'supplier_code' || key === 'supplier_name' || key === 'department_name') return <button className="pu-link" disabled={!chosen || busy} onClick={() => setLookup({ kind: key === 'department_name' ? 'department' : 'supplier', id: row.id })}>{row[key] || '选择'}</button>
    if (['quantity','unit_price','tax_rate'].includes(key)) return <input aria-label={`${label}${row.number}行${row.line_number}`} type="number" min="0" step="any" disabled={!chosen || busy} value={row[key] ?? ''} placeholder={key === 'unit_price' ? '自动取价' : ''} onChange={e => edit(row.id, { [key]: e.target.value })} />
    if (key === 'payment_method') return <input aria-label={`支付方式${row.line_number}`} disabled={!chosen || busy} value={row[key] || ''} onChange={e => edit(row.id, { [key]: e.target.value })} />
    if (key === 'amount') return format(amounts(converted(row.quantity, row.uom_rate_d, row.uom_rate_m), row.unit_price === '' ? row.original_price : row.unit_price, row.tax_rate).amount)
    if (key === 'material_code' || key === 'number') return <span className="pu-source-code">{row[key]}</span>
    return String(row[key] ?? '')
  }
  const ranges = [['part','物料编码'],['category','产品类'],['number','请购单号'],['request_date','请购日期'],['needed_date','需求日期']]
  const selectedAmounts = Object.values(selected).reduce((groups, r) => {
    const currency = r.currency_code || '未设币种'
    const value = amounts(converted(r.quantity, r.uom_rate_d, r.uom_rate_m), r.unit_price === '' ? r.original_price : r.unit_price, r.tax_rate).amount
    groups[currency] = sum([groups[currency] || '0', value]); return groups
  }, {})
  return <section className="pu-workspace">
    <h1>请购单转采购单</h1>
    <div className="pu-toolbar"><Tool icon={Search} disabled={busy} onClick={query}>查询</Tool><Tool icon={CheckSquare} disabled={busy} onClick={() => chooseRows(result.results.filter(r => !r.reason))}>全选本页</Tool><Tool icon={Square} disabled={busy} onClick={() => setSelected({})}>全不选</Tool><Tool icon={Check} disabled={busy || !Object.keys(selected).length || !can(session, 'purchase_order', 'create')} onClick={submit}>提交</Tool><Tool icon={X} onClick={onClose}>关闭</Tool></div>
    {error && <p className="pu-error" role="alert">{error}</p>}
    <div className="pu-conversion-header"><div className="pu-ranges">{ranges.map(([key, label]) => <div key={key}><label>{label}<input aria-label={`${label}起`} type={key.includes('date') ? 'date' : 'text'} value={filters[key + '_from'] || ''} onChange={e => setFilters({ ...filters, [key + '_from']: e.target.value })} /></label><span>→</span><input aria-label={`${label}止`} type={key.includes('date') ? 'date' : 'text'} value={filters[key + '_to'] || ''} onChange={e => setFilters({ ...filters, [key + '_to']: e.target.value })} /></div>)}<div><label>采购员<input aria-label="采购员" value={filters.buyer || ''} onChange={e => setFilters({ ...filters, buyer: e.target.value })} /></label><span /><label>类型<select aria-label="类型" value="P" readOnly><option value="P">P.采购</option></select></label></div></div>
    <div className="pu-options"><label>采购单类型<select value={options.document_type} onChange={e => setOptions({ ...options, document_type: e.target.value })}><option value="standard">标准采购单</option></select></label><label>采购单行数<input type="number" min="0" aria-label="采购单行数" title="0表示不限制；大于0时按此行数拆单" value={options.line_limit} onChange={e => setOptions({ ...options, line_limit: e.target.value })} /></label><label className="pu-checkbox"><input type="checkbox" checked={options.auto_number} onChange={e => setOptions({ ...options, auto_number: e.target.checked })} />自动生成采购单号</label>{!options.auto_number && <label>采购单号<input value={options.number || ''} onChange={e => setOptions({ ...options, number: e.target.value })} /></label>}<label>生成汇总方式<select aria-label="生成汇总方式" value={options.grouping} onChange={e => setOptions({ ...options, grouping: e.target.value })}><option value="1">1.不汇总</option><option value="2">2.按物料汇总</option><option value="3">3.按物料＋需求日期汇总</option></select></label><label className="pu-checkbox"><input type="checkbox" checked={options.consider_pack} onChange={e => setOptions({ ...options, consider_pack: e.target.checked })} />考虑物料最小采购及包装数量</label></div>
    <div className="pu-options"><LookupField label="统一供应商" value={defaults.supplier_name} disabled={busy} onClick={() => setLookup({ kind: 'supplier' })} /><LookupField label="统一采购部门" value={defaults.department_name} disabled={busy} onClick={() => setLookup({ kind: 'department' })} /><label>下单日期<input type="date" value={options.order_date} onChange={e => setOptions({ ...options, order_date: e.target.value })} /></label><small>统一设置应用于当前选中行及后续选择；不同条件自动拆单。</small></div></div>
    <PurchaseGrid label="可转采购请购明细" columns={columns} rows={result.results} cell={cell} totals={{ quantity: sum(Object.values(selected).map(r => r.quantity)) }} empty={queried ? '没有符合条件的可转请购明细' : '输入请购单号或筛选范围，然后点击查询'} className="pu-grow" />
    <div className="pu-pagination"><span>共 {result.count} 条 · 已选 {Object.keys(selected).length} 条（跨页保留）{Object.entries(selectedAmounts).map(([currency, amount]) => ` · ${currency} ${format(amount)}`).join('')}</span><button disabled={busy || page <= 1} onClick={() => run(() => load(applied, page - 1))}>上一页</button><span>{page} / {Math.max(1, Math.ceil(result.count / 50))}</span><button disabled={busy || page * 50 >= result.count} onClick={() => run(() => load(applied, page + 1))}>下一页</button></div>
    <div className="pu-section-title">生成结果</div><div className="pu-generation-result" role="status">{!orders.length ? '尚未生成采购单' : orders.map(o => <button className="pu-link" key={o.id} onClick={() => onOpenOrder(o.id)}>{o.number} · {o.supplier_name} · {o.currency_code} · 查看</button>)}</div>
    {lookup && <Lookup kind={lookup.kind} request={request} onClose={() => setLookup(null)} onPick={pick} />}
    {preview && <div className="pu-backdrop"><section className="pu-dialog pu-preview" role="dialog" aria-modal="true" aria-label="继续生成采购单"><header><strong>确认供应商、数量与新单价 · 共 {preview.groups.length} 张采购单</strong></header><div className="pu-toolbar"><Tool icon={ArrowRight} disabled={busy} onClick={generate}>{Object.keys(previewPrices).length ? '重新核价' : '继续生成'}</Tool><Tool icon={X} disabled={busy} onClick={() => setPreview(null)}>取消生成</Tool></div>{error && <p className="pu-error" role="alert">{error}</p>}<PurchaseGrid label="生成预览" cell={(r, key, label, i) => key === 'unit_price' ? <input type="number" min="0" step="0.000001" aria-label={`预览新单价第${i + 1}行`} disabled={busy} value={previewPrices[r.allocations[0].requisition_line] ?? r.unit_price} onChange={e => setPreviewPrices(old => ({ ...old, ...Object.fromEntries(r.allocations.filter(a => a.kind === '1').map(a => [a.requisition_line, e.target.value])) }))} /> : String(r[key] ?? '')} columns={previewColumns} rows={preview.groups.flatMap((g, gi) => g.lines.map((r, i) => ({ ...g, ...r.snapshot, ...r, id: `${gi}-${i}-${r.material}`, source_quantity: sum(r.allocations.filter(a => a.kind === '1').map(a => a.quantity)), source: r.allocations.filter(a => a.kind === '1').map(a => `${a.snapshot.requisition_number}/${a.snapshot.requisition_line_number}`).join('、') })))} empty="" /><p>额外采购已包含在合计采购数量中；修改新单价后，先重新核价再继续生成。取消生成不占用请购数量。</p></section></div>}
    {askOpen && <div className="pu-backdrop"><section className="pu-dialog" role="dialog" aria-modal="true" aria-label="查看采购单"><header><strong>生成成功</strong></header><p>是否要查看生成的采购单？</p><p>共生成 {orders.length} 张，选择“否”仍保留采购单。</p><footer><button autoFocus onClick={() => { setAskOpen(false); onOpenOrder(orders[0].id) }}>是</button><button onClick={() => setAskOpen(false)}>否</button></footer></section></div>}
  </section>
}
