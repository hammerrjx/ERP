import { useEffect, useState } from 'react'
import { Search, Plus, Save, Undo2, Trash2, Minus, Check, ChevronFirst, ChevronLeft, ChevronRight, ChevronLast, Printer, Download, X, HelpCircle } from 'lucide-react'
import { api, download } from '../../api/client'
import { can } from '../../auth/session'
import columns from '../../../shared/purchase-columns.json'
import { Lookup, LookupField, Tool, PurchaseGrid, format, sum, today, statusNames, amounts, dateTime, converted } from './PurchaseControls'
import './purchase-workspace.css'

const blank = () => ({ order_date: today(), promised_date: today(), tax_rate: '0', exchange_rate: '1', document_type: 'standard', lines: [], status: 'draft', version: 1, terms: '' })
const numeric = new Set(['quantity','spare_quantity','over_receipt_quantity','extra_quantity','copper_price','unit_price','amount','untaxed_price','untaxed_amount','received_quantity','accepted_quantity','accepted_inventory_quantity','received_spare_quantity','accepted_spare_quantity','accepted_spare_inventory_quantity','returned_quantity','returned_spare_quantity','uom_rate_m','uom_rate_d','minimum_price'])
const editableFields = new Set(['quantity','spare_quantity','over_receipt_quantity','extra_quantity','copper_price','unit_price','needed_date','due_date','promised_date','notes'])

export function PurchaseOrderWorkspace({ session, initialId, onClose }) {
  const request = (path, options) => api(path, { token: session.token, ...options })
  const [doc, setDoc] = useState(blank), [saved, setSaved] = useState(null), [browse, setBrowse] = useState(!initialId)
  const [tab, setTab] = useState('order'), [selected, setSelected] = useState(0), [dirty, setDirty] = useState(false)
  const [list, setList] = useState({ count: 0, results: [] }), [page, setPage] = useState(1), [q, setQ] = useState(''), [applied, setApplied] = useState('')
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState(''), [lookup, setLookup] = useState(null)
  const [printPreview, setPrintPreview] = useState(false), [help, setHelp] = useState(false), [sourceDoc, setSourceDoc] = useState(null)
  const run = async fn => { setBusy(true); setError(''); setNotice(''); try { await fn() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const adopt = value => { setDoc(value); setSaved(value); setDirty(false); setSelected(0); setBrowse(false) }
  const loadList = async (query = applied, p = page) => { setList(await request(`/purchase-order/?${new URLSearchParams({ workspace: '1', q: query, page: p })}`)); setPage(p) }
  const load = id => run(async () => adopt(await request(`/purchase-order/${id}/`)))
  useEffect(() => { run(async () => { await loadList('', 1); if (initialId) adopt(await request(`/purchase-order/${initialId}/`)) }) }, [initialId])
  const change = (key, value) => { setDoc(old => ({ ...old, [key]: value })); setDirty(true) }
  const setLine = (index, key, value) => { setDoc(old => ({ ...old, lines: old.lines.map((r, i) => i === index ? { ...r, [key]: value } : r) })); setDirty(true) }
  const displayLines = doc.lines.map(r => ({ ...r, ...amounts(r.quantity, r.unit_price, doc.tax_rate) }))
  const currentLine = doc.lines[selected]
  const line = currentLine && { ...currentLine, allocations: (currentLine.allocations || []).map(a => ({ ...a, inventory_quantity: converted(a.quantity, currentLine.uom_rate_m, currentLine.uom_rate_d) })) }
  const locked = busy || !['draft', 'rejected'].includes(doc.status) || doc.is_confirmed || !!doc.delivery_approved_at || !can(session, 'purchase_order', doc.id ? 'change' : 'create')
  const confirmLeave = () => !dirty || window.confirm('放弃未保存的采购单修改？')
  const save = () => run(async () => {
    const body = Object.fromEntries(['supplier','currency','department','order_date','promised_date','tax_rate','buyer','payment_method','notes','shipping_address','billing_address','revision_label','terms','document_type','version'].map(k => [k, doc[k] ?? '']))
    body.lines = doc.lines.map(r => ({ id: r.id, material: r.material, line_number: r.line_number, ...Object.fromEntries([...editableFields].map(k => [k, r[k] ?? (numeric.has(k) ? '0' : '')])), allocations: (r.allocations || []).map(a => ({ id: a.id, quantity: a.quantity })) }))
    adopt(await request(`/purchase-order/${doc.id ? doc.id + '/' : ''}`, { method: doc.id ? 'PUT' : 'POST', body })); await loadList(); setNotice('已保存')
  })
  const transition = verb => run(async () => { adopt(await request(`/purchase-order/${doc.id}/${verb}/`, { method: 'POST' })); await loadList(); setNotice('操作完成') })
  const pick = row => {
    if (lookup === 'material') {
      const next = Math.max(0, ...doc.lines.map(l => l.line_number), ...(saved?.lines || []).map(l => l.line_number)) + 10
      change('lines', [...doc.lines, { ...row, id: undefined, material: row.id, line_number: next, quantity: '1', unit_price: '0', extra_quantity: '0', spare_quantity: '0', over_receipt_quantity: '0', copper_price: '0', needed_date: doc.order_date, due_date: doc.promised_date, promised_date: doc.promised_date, allocations: [], notes: '' }]); setSelected(doc.lines.length)
    } else if (lookup === 'supplier') {
      setDoc(old => ({ ...old, supplier: row.id, supplier_name: row.name, supplier_code: row.code, currency: row.currency, currency_code: row.currency_code, tax_rate: row.tax_rate, payment_method: row.payment_method })); setDirty(true)
      setNotice('供应商已更换，请重新核对采购单价、币种、税率及支付方式。')
    } else if (lookup === 'currency') { change('currency', row.id); setDoc(old => ({ ...old, currency_code: row.code })); setNotice('币种已更换，请确认各行单价；保存时更新汇率。') }
    else if (lookup === 'department') { change('department', row.id); setDoc(old => ({ ...old, department_name: row.name })) }
    else change('buyer', row.code)
    setLookup(null)
  }
  const field = (key, label, type = 'text', readOnly = false) => <label>{label}<input aria-label={label} type={type} value={key.endsWith('_at') ? dateTime(doc[key]) : doc[key] || ''} readOnly={readOnly} disabled={!readOnly && locked} onChange={e => change(key, e.target.value)} /></label>
  const orderCell = (row, key, label, i) => {
    if (['source_requisition_number','material_code'].includes(key)) return <button className="pu-link" onClick={() => setSelected(i)}>{row[key] || '—'}</button>
    if (editableFields.has(key)) return <input aria-label={`${label}第${row.line_number}行`} disabled={locked} type={numeric.has(key) ? 'number' : key.includes('date') ? 'date' : 'text'} step="any" min="0" value={row[key] ?? ''} onChange={e => setLine(i, key, e.target.value)} />
    if (key === 'line_status') return row[key] === 'C' ? 'C.关闭' : '.正常'
    if (key === 'return_replacement') return row[key] ? '是' : '否'
    if (numeric.has(key)) return format(row[key], key === 'untaxed_price' ? 4 : 2)
    return key.endsWith('_at') ? dateTime(row[key]) : String(row[key] ?? '')
  }
  const sourceCell = (a, key, label, i) => {
    if (key === 'requisition_number' && a.requisition_line) return <button className="pu-link" onClick={() => run(async () => {
      const found = await request(`/purchase-requisition/?workspace=1&q=${encodeURIComponent(a.requisition_number)}&requisition_type=P`)
      const target = found.results.find(r => r.number === a.requisition_number)
      if (!target) throw new Error('未找到来源请购单')
      setSourceDoc(await request(`/purchase-requisition/${target.id}/`))
    })}>{a[key]}</button>
    if (key === 'quantity' && a.id) return <input aria-label={`来源采购数量第${a.sequence}行`} type="number" min="0" step="any" disabled={locked} value={a.quantity} onChange={e => setLine(selected, 'allocations', line.allocations.map((v, j) => j === i ? { ...v, quantity: e.target.value } : v))} />
    return key === 'quantity' || key === 'inventory_quantity' ? format(a[key]) : key.endsWith('_at') ? dateTime(a[key]) : String(a[key] ?? '')
  }
  const exportFile = () => run(async () => { const result = await download(`/purchase-order/${doc.id}/export/`, { token: session.token }); const url = URL.createObjectURL(result.blob); const a = document.createElement('a'); a.href = url; a.download = result.filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000) })
  const navigate = direction => run(async () => {
    if (!confirmLeave()) return
    let rows = list.results, p = page, index = rows.findIndex(r => r.id === doc.id)
    if (direction === 'first') { p = 1; index = 0 }
    else if (direction === 'last') { p = Math.max(1, Math.ceil(list.count / 50)); index = -1 }
    else { index += direction === 'previous' ? -1 : 1; if (index < 0 && p > 1) { p--; index = -1 } else if (index >= rows.length && p * 50 < list.count) { p++; index = 0 } }
    if (p !== page || direction === 'first' || direction === 'last') { const data = await request(`/purchase-order/?${new URLSearchParams({ workspace: '1', q: applied, page: p })}`); setList(data); setPage(p); rows = data.results }
    const target = rows[index < 0 ? rows.length - 1 : Math.min(index, rows.length - 1)]
    if (target) adopt(await request(`/purchase-order/${target.id}/`))
  })
  const totals = { ...doc.totals, amount: sum(displayLines.map(r => r.amount)), untaxed_amount: sum(displayLines.map(r => r.untaxed_amount)), quantity: sum(doc.lines.map(r => r.quantity)), spare_quantity: sum(doc.lines.map(r => r.spare_quantity)), extra_quantity: sum(doc.lines.map(r => r.extra_quantity)), over_receipt_quantity: sum(doc.lines.map(r => r.over_receipt_quantity)) }
  return <section className={`pu-workspace ${printPreview ? 'pu-print-preview' : ''}`}>
    <h1>采购单 <span>{doc.number || '〈自动编号〉'}</span></h1>
    <div className="pu-toolbar">
      <Tool icon={Search} onClick={() => { if (confirmLeave()) { setBrowse(true); run(() => loadList()) } }}>查询</Tool><Tool icon={Plus} disabled={busy || !can(session, 'purchase_order', 'create')} onClick={() => { if (confirmLeave()) { setDoc(blank()); setSaved(null); setDirty(false); setBrowse(false) } }}>新增</Tool>
      <Tool icon={Save} disabled={locked || !dirty} onClick={save}>保存</Tool><Tool icon={Undo2} disabled={busy || !dirty} onClick={() => { if (saved) adopt(saved); else { setDoc(blank()); setDirty(false) } }}>取消</Tool>
      <Tool icon={Trash2} disabled={locked || !doc.id || !can(session, 'purchase_order', 'delete')} onClick={() => { if (window.confirm(`删除采购单 ${doc.number}？`)) run(async () => { await request(`/purchase-order/${doc.id}/`, { method: 'DELETE' }); setDoc(blank()); setSaved(null); setBrowse(true); await loadList() }) }}>删除</Tool>
      <Tool icon={Minus} disabled={locked || !line} onClick={() => { change('lines', doc.lines.filter((_, i) => i !== selected)); setSelected(0) }}>删行</Tool>
      <Tool icon={Check} disabled={busy || dirty || !doc.id || doc.is_confirmed || !can(session, 'purchase_order', 'approve')} onClick={() => transition('confirm')}>总监确认</Tool><Tool icon={Undo2} disabled={busy || dirty || !doc.is_confirmed || !can(session, 'purchase_order', 'approve')} onClick={() => transition('unconfirm')}>反总监确认</Tool>
      <Tool icon={Check} disabled={busy || dirty || !doc.id || doc.status === 'approved' || !can(session, 'purchase_order', 'approve')} onClick={() => transition('approve')}>审核</Tool><Tool icon={Undo2} disabled={busy || dirty || doc.status !== 'approved' || !can(session, 'purchase_order', 'approve')} onClick={() => transition('unapprove')}>反审核</Tool>
      <Tool icon={Check} disabled={busy || dirty || doc.status !== 'approved' || !!doc.delivery_approved_at || !can(session, 'purchase_order', 'approve')} onClick={() => transition('delivery-approve')}>交期审核</Tool><Tool icon={Undo2} disabled={busy || dirty || !doc.delivery_approved_at || !can(session, 'purchase_order', 'approve')} onClick={() => transition('delivery-unapprove')}>交期反审核</Tool>
      {[[ChevronFirst,'第一笔','first'],[ChevronLeft,'上一笔','previous'],[ChevronRight,'下一笔','next'],[ChevronLast,'末笔','last']].map(([icon, label, action]) => <Tool key={action} icon={icon} disabled={busy || !list.count} onClick={() => navigate(action)}>{label}</Tool>)}
      <Tool icon={Search} disabled={!doc.id} onClick={() => { setBrowse(false); setPrintPreview(!printPreview) }}>{printPreview ? '关闭预览' : '预览'}</Tool><Tool icon={Printer} disabled={!doc.id || dirty} onClick={() => window.print()}>打印</Tool><Tool icon={Printer} disabled={!doc.id || dirty} onClick={() => window.print()}>页面设置</Tool><Tool icon={Download} disabled={!doc.id || dirty || busy} onClick={exportFile}>导出</Tool><Tool icon={HelpCircle} onClick={() => setHelp(true)}>帮助</Tool><Tool icon={X} onClick={() => { if (confirmLeave()) onClose() }}>关闭</Tool>
    </div>{error && <p className="pu-error" role="alert">{error}</p>}{notice && <p className="pu-notice" role="status">{notice}</p>}
    <nav className="pu-tabs"><button aria-selected={!browse} onClick={() => setBrowse(false)}>资料维护</button><button aria-selected={browse} onClick={() => { if (confirmLeave()) setBrowse(true) }}>资料浏览</button></nav>
    {browse ? <><form className="pu-query" onSubmit={e => { e.preventDefault(); setApplied(q); run(() => loadList(q, 1)) }}><input aria-label="采购单查询" placeholder="采购单号、供应商编码或名称" value={q} onChange={e => setQ(e.target.value)} /><button disabled={busy}>查询</button></form><PurchaseGrid label="采购单资料浏览" className="pu-grow" columns={[["number","采购单号"],["supplier_name","供应商"],["currency_code","币种"],["department_name","部门"],["order_date","下单日期"],["status","状态"]]} rows={list.results} cell={(row, key) => key === 'number' ? <button className="pu-link" onClick={() => load(row.id)}>{row.number}</button> : key === 'status' ? statusNames[row.status] : row[key]} empty="暂无采购单。可新增，或从请购单转采购单生成。" /><footer className="pu-pagination">共 {list.count} 张<button disabled={page <= 1 || busy} onClick={() => run(() => loadList(applied, page - 1))}>上一页</button>{page}<button disabled={page * 50 >= list.count || busy} onClick={() => run(() => loadList(applied, page + 1))}>下一页</button></footer></>
      : <><nav className="pu-tabs"><button aria-selected={tab === 'order'} onClick={() => setTab('order')}>采购单</button><button aria-selected={tab === 'terms'} onClick={() => setTab('terms')}>条款</button></nav>
      {tab === 'terms' ? <label className="pu-terms">采购条款<textarea disabled={locked} value={doc.terms || ''} onChange={e => change('terms', e.target.value)} /></label> : <div className="pu-order-header"><div className="pu-header-fields">
        {field('number','采购单号','text',true)}<LookupField label="供应商" value={[doc.supplier_code,doc.supplier_name].filter(Boolean).join(' ')} disabled={locked} onClick={() => setLookup('supplier')} /><label>单别<select aria-label="单别" disabled={locked} value={doc.document_type} onChange={e => change('document_type', e.target.value)}><option value="standard">标准采购单</option></select></label>
        {field('order_date','下单日期','date')}{field('shipping_address','送货地址')}{field('created_at','录入时间','text',true)}
        <LookupField label="采购员" value={doc.buyer} disabled={locked} onClick={() => setLookup('employee')} />{field('payment_method','支付方式')}{field('created_by','录入人','text',true)}
        <LookupField label="币种" value={doc.currency_code} disabled={locked} onClick={() => setLookup('currency')} />{field('exchange_rate','兑换率','text',true)}{field('tax_rate','增值税率%','number')}
        {field('revision_label','版本号')}{field('billing_address','票据开往地址')}{field('approved_by','审核人','text',true)}
        {field('notes','备注')}<LookupField label="部门" value={doc.department_name} disabled={locked} onClick={() => setLookup('department')} />{field('approved_at','审核时间','text',true)}
        {field('high_price_permission','高价审核权限','text',true)}{field('confirmed_by','确认人','text',true)}{field('confirmed_at','确认时间','text',true)}
        {field('delivery_approved_by','交期审核人','text',true)}{field('delivery_approved_at','交期审核时间','text',true)}<label>确认<output>{doc.is_confirmed ? '已确认' : '未确认'}</output></label>
      </div><div className={`pu-stamp ${doc.status === 'approved' ? 'approved' : ''}`}>{statusNames[doc.status]}</div></div>}
      <div className="pu-line-actions"><button disabled={locked} onClick={() => setLookup('material')}><Plus size={13} />增行</button><span>{doc.lines.length} 条采购明细{dirty ? ' · 未保存' : ''}</span></div>
      <div className="pu-upper"><PurchaseGrid label="采购明细" columns={columns.order} rows={displayLines} totals={totals} selected={selected} onSelect={setSelected} cell={orderCell} empty="点击增行，或从请购单生成采购明细" /></div>
      <div className="pu-section-title">关联请购明细：<strong>{line?.material_code}　{line?.material_name}</strong><span>订购数量变更时，请同步调整下方来源分配。</span></div>
      <PurchaseGrid label="关联请购明细" className="pu-lower" columns={columns.allocation} rows={line?.allocations || []} totals={{ quantity: sum((line?.allocations || []).map(a => a.quantity)), inventory_quantity: sum((line?.allocations || []).map(a => a.inventory_quantity)) }} cell={sourceCell} empty="当前采购行没有请购来源分配" />
      <footer className="pu-status">记录数 {list.count} · {statusNames[doc.status]} · {dirty ? '未保存' : '已保存'} · {doc.currency_code || ''}</footer></>}
    <article className="pu-print-sheet"><h2>采购单</h2><dl><dd>单号：{doc.number}</dd><dd>日期：{doc.order_date}</dd><dd>供应商：{doc.supplier_name}</dd><dd>币种：{doc.currency_code}</dd><dd>税率：{doc.tax_rate}%</dd><dd>支付方式：{doc.payment_method}</dd><dd>部门：{doc.department_name}</dd><dd>采购员：{doc.buyer}</dd><dd>送货地址：{doc.shipping_address}</dd></dl><table><thead><tr>{['行号','物料编码','物料名称 / 规格','数量','单位','含税单价','含税金额','交货日期'].map(t => <th key={t}>{t}</th>)}</tr></thead><tbody>{displayLines.map(r => <tr key={r.line_number}><td>{r.line_number}</td><td>{r.material_code}</td><td>{r.material_name}<br />{r.specification}</td><td>{format(r.quantity)}</td><td>{r.uom_name}</td><td>{format(r.unit_price)}</td><td>{format(r.amount)}</td><td>{r.due_date}</td></tr>)}</tbody><tfoot><tr><td colSpan="6">合计（{doc.currency_code}）</td><td>{format(totals.amount)}</td><td /></tr></tfoot></table><p>备注：{doc.notes}</p><p>条款：{doc.terms}</p><footer>录入：{doc.created_by}　审核：{doc.approved_by}　{dateTime(doc.approved_at)}</footer></article>
    {lookup && <Lookup kind={lookup} request={request} onPick={pick} onClose={() => setLookup(null)} />}
    {help && <div className="pu-backdrop"><section className="pu-dialog" role="dialog" aria-modal="true" aria-label="采购单帮助"><header>采购单操作帮助<button onClick={() => setHelp(false)}>关闭</button></header><p>点击蓝色请购单号或物料编码，下方显示当前采购行的来源分配。调整订购数量时，同时修改来源分配数量；额外采购单独分配。</p><p>审核前核对币种、部门、支付方式、税率、数量及单价。已有收货或退货引用的采购单不能删除或反审核。</p><p>总监确认和交期审核分别记录；未审核采购单不会直接增加库存。打印对话框提供纸张、方向和页边距设置。</p></section></div>}
    {sourceDoc && <div className="pu-backdrop"><section className="pu-dialog pu-preview" role="dialog" aria-modal="true" aria-label="来源请购单"><header><strong>请购单 {sourceDoc.number}</strong><button onClick={() => setSourceDoc(null)}>关闭</button></header><PurchaseGrid label="来源请购单明细" columns={[["line_number","行号"],["material_code","物料编码"],["material_name","物料名称"],["requested_qty","请购数量"],["converted_qty","已采购数量"],["needed_date","需求日期"]]} rows={sourceDoc.lines.map(l => ({ ...l, material_code: l.material_snapshot.pt_part, material_name: l.material_snapshot.pt_desc1 }))} /></section></div>}
  </section>
}
