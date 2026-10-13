import { useEffect, useRef, useState } from 'react'
import { Search, Plus, Save, Undo2, Trash2, Check, CheckCheck, X, ChevronFirst, ChevronLast, ChevronLeft, ChevronRight, Printer, Download, RefreshCw, Minus, RotateCcw } from 'lucide-react'
import { api, listPayload } from '../../api/client'
import { can } from '../../auth/session'
import { SearchableLookup } from '../../components/Field'
import './warehouse.css'

const titles = { draft: '草稿', confirmed: '已确认', posted: '已审核', reversed: '已冲销' }
const today = () => new Date().toLocaleDateString('en-CA')
const blank = (kind) => ({ kind, document_date: today(), count_basis: '2', transfer_class: kind === 'transfer' ? '1' : '', lines: [], notes: '', category_code: '' })
const transferClasses = [{ id: '1', code: '1', name: '内部转仓' }, { id: '2', code: '2', name: '外协领料转仓' }, { id: '3', code: '3', name: '外协退料转仓' }]
const countBases = [{ id: '1', code: '1', name: '盘点日期实时库存（待核验）', disabled: true }, { id: '2', code: '2', name: '即时库存' }, { id: '3', code: '3', name: '盘点日期单据库存（待核验）', disabled: true }]
const dateTime = (value) => value ? String(value).replace('T', ' ').slice(0, 19) : ''
const text = (value) => value ?? ''
const fmt = (value) => value == null ? '' : String(value).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '')
const sum = (lines, field) => {
  const value = lines.reduce((acc, line) => { const s = String(line[field] || '0'); if (!/^-?\d*(\.\d*)?$/.test(s)) return acc; const [whole, fraction = ''] = s.replace('-', '').split('.'); return acc + (s.startsWith('-') ? -1n : 1n) * (BigInt(whole || 0) * 100000000n + BigInt(fraction.padEnd(8, '0').slice(0, 8))) }, 0n)
  const abs = value < 0 ? -value : value
  return `${value < 0 ? '-' : ''}${abs / 100000000n}.${String(abs % 100000000n).padStart(8, '0')}`
}

export function WarehouseWorkspace({ kind, title, session, initialCount = false }) {
  const newDocument = () => ({ ...blank(kind), ...(initialCount ? { category_code: '001' } : {}) })
  const [doc, setDoc] = useState(newDocument)
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [tab, setTab] = useState('edit')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [dirty, setDirty] = useState(false)
  const [selected, setSelected] = useState(null)
  const [query, setQuery] = useState('')
  const [reason, setReason] = useState(null)
  const [deletePrompt, setDeletePrompt] = useState(false)
  const materialSearch = useRef(0)
  const materialTimer = useRef(null)
  const editable = !doc.status || doc.status === 'draft'
  const canWrite = can(session, 'inventory_document', doc.id ? 'change' : 'create')
  const locked = !editable || busy || !canWrite || Boolean(doc.source_key)
  const isCount = kind === 'count'
  const hasFrom = !['receipt', 'opening'].includes(kind)
  const hasTo = ['receipt', 'transfer', 'scrap'].includes(kind)
  const hasConfirm = ['transfer', 'count'].includes(kind)
  const countEditing = isCount && doc.status === 'confirmed' && !busy && can(session, 'inventory_document', 'approve')
  const request = (path, options = {}) => api(path, { token: session.token, ...options })
  const searchMaterials = (q = '', lines = doc.lines) => {
    const sequence = ++materialSearch.current
    clearTimeout(materialTimer.current)
    materialTimer.current = setTimeout(async () => {
      try {
        const params = new URLSearchParams({ lookup: 'warehouse', q, ids: lines.map(l => l.material).filter(Boolean).join(',') })
        const materials = listPayload(await request(`/material/?${params}`))
        if (sequence === materialSearch.current) setLookups(old => ({ ...old, material: materials }))
      } catch (e) { if (sequence === materialSearch.current) setError(e.message) }
    }, 200)
  }
  const run = async (fn) => { setBusy(true); setError(''); setNotice(''); try { await fn() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const reload = async () => setRows(listPayload(await request(`/inventory-document/?kind=${kind}&summary=1${initialCount ? '&category=001' : ''}`)))
  useEffect(() => {
    let live = true
    setBusy(true)
    Promise.all([reload(), Promise.all(['location', 'material', 'uom', 'department', 'partner', 'employee', 'inventory-dictionary'].map(async (resource) => [resource, listPayload(await request(`/${resource}/${resource === 'material' ? '?lookup=warehouse' : ''}`))]))])
      .then(([, entries]) => { if (live) setLookups(Object.fromEntries(entries)) })
      .catch((e) => { if (live) setError(e.message) }).finally(() => { if (live) setBusy(false) })
    return () => { live = false; materialSearch.current++; clearTimeout(materialTimer.current) }
  }, [kind, session.token])
  const set = (key, value) => {
    setDoc((prev) => ({ ...prev, [key]: value,
      ...(['from_location', 'to_location'].includes(key) ? { lines: prev.lines.map((line) => !line[key] || line[key] === prev[key] ? { ...line, [key]: value } : line) } : {}) }))
    setDirty(true)
  }
  const lineSet = (index, key, value) => {
    setDoc((prev) => ({ ...prev, lines: prev.lines.map((line, i) => {
      if (i !== index) return line
      if (key === 'material') {
        const material = (lookups.material || []).find((m) => m.id === Number(value))
        return { ...line, material: value, uom: material?.uom, material_code: material?.code, material_name: material?.name, specification: material?.specification, english_name: material?.english_name, batch_number: '' }
      }
      return { ...line, [key]: value }
    }) })); setDirty(true)
  }
  const load = (row) => { setDoc(row); setDirty(false); setSelected(null); setTab('edit'); setError(''); searchMaterials('', row.lines) }
  const selectDoc = (row) => { if (!dirty || window.confirm('放弃未保存的修改？')) {
    if (row.id) run(async () => load(await request(`/inventory-document/${row.id}/`)))
    else load(row)
  } }
  const save = () => run(async () => {
    if (countEditing) {
      const results = Object.fromEntries(doc.lines.map((line) => [String(line.id), line.counted_quantity]))
      load(await request(`/inventory-document/${doc.id}/transition/`, { method: 'POST', body: { action: 'count-results', results } }))
    } else {
      const headFields = ['kind', 'document_date', 'from_location', 'to_location', 'from_department', 'to_department', 'category_code', 'transfer_class', 'supplier', 'count_basis', 'checker', 'printer', 'notes']
      const body = Object.fromEntries(headFields.map((key) => [key, doc[key] || (key.endsWith('location') || key.endsWith('department') || key === 'supplier' ? null : '')]))
      body.lines = doc.lines.map((line) => ({ ...(line.id ? { id: line.id } : {}), ...Object.fromEntries(['line_number', 'material', 'uom', 'quantity', 'from_location', 'to_location', 'batch_number', 'grade', 'notes', 'reference_number', 'reference_line', 'reference_cost', 'counted_quantity'].map((key) => [key,
        line[key] === '' || line[key] == null ? (['from_location', 'to_location', 'reference_line', 'reference_cost', 'counted_quantity'].includes(key) ? null : key === 'quantity' ? '0' : '') : line[key]]))
      }))
      load(await request(doc.id ? `/inventory-document/${doc.id}/` : '/inventory-document/', { method: doc.id ? 'PATCH' : 'POST', body }))
    }
    await reload(); setNotice('已保存')
  })
  const transition = (action, extra = {}) => run(async () => {
    load(await request(`/inventory-document/${doc.id}/transition/`, { method: 'POST', body: { action, ...extra } })); await reload(); setReason(null); setNotice('操作完成')
  })
  const add = () => { const number = Math.max(0, ...doc.lines.map((line) => line.line_number)) + 10; set('lines', [...doc.lines, { line_number: number, quantity: '', batch_number: '', from_location: doc.from_location || null, to_location: doc.to_location || null }]); setSelected(doc.lines.length) }
  const label = (resource, id) => { const row = (lookups[resource] || []).find((item) => item.id === Number(id)); return row ? `${row.code} ${row.name || row.description || ''}` : '' }
  const lookup = (name, value, change, entries, codeOnly = false, clear = true, onSearch) => {
    const selected = entries.find((r) => String(r.id) === String(value))
    const disabled = locked || (name === '外协供应商' && (!doc.transfer_class || doc.transfer_class === '1'))
    const input = <SearchableLookup label={name} value={value} options={entries} onChange={change} onSearch={onSearch} disabled={disabled} portal hideLabel clearOnFocus allowClear={clear} className="wh-lookup" optionCode={(r) => r.code} />
    return codeOnly ? input : <div className={`wh-code-name${disabled ? ' disabled' : ''}`}>{input}<output aria-label={`${name}名称`} title={selected?.name || selected?.description || ''}>{selected?.name || selected?.description || ''}</output></div>
  }
  const options = (resource, value, change, name, codeOnly = false) => lookup(name, value, change, (lookups[resource] || []).filter((row) => String(row.id) === String(value) || (resource === 'partner' ? ['supplier', 'both'].includes(row.kind) : resource === 'material' ? row.active && !row.no_stock_movement : resource === 'location' ? !row.disabled_for_inventory : !row.disabled)), codeOnly, true, resource === 'material' ? searchMaterials : undefined)
  const relatedName = (resource, id) => (lookups[resource] || []).find((r) => r.id === Number(id))?.name || ''
  const lineLocation = (line, i, key, name) => kind === 'transfer'
    ? <input aria-label={`${name}${line.line_number}`} readOnly value={(lookups.location || []).find((r) => r.id === Number(line[key]))?.code || ''} />
    : options('location', line[key], (v) => lineSet(i, key, v), `${name}${line.line_number}`, true)
  const head = (label, key, input) => <div className="wh-field"><span>{label}</span>{input || <input aria-label={label} value={text(doc[key])} disabled={locked} onChange={(e) => set(key, e.target.value)} />}</div>
  const Tool = ({ icon: Icon, children, onClick, disabled = false }) => <button type="button" title={children} disabled={disabled || busy} onClick={onClick}><Icon size={17} /><span>{children}</span></button>
  const exportCsv = () => {
    const columns = ['行号', '物料编码', '物料名称', '数量', '出库位', '入库位', '库存单位', '批号', '账面数量', '实盘数量', '差异数量', '备注']
    const values = doc.lines.map((l) => [l.line_number, l.material_code, l.material_name, l.quantity, label('location', l.from_location), label('location', l.to_location), label('uom', l.uom), l.batch_number, l.system_quantity, l.counted_quantity, l.variance_quantity, l.notes])
    const escape = (v) => `"${String(v ?? '').replace(/^[=+@-]/, "'$&").replaceAll('"', '""')}"`
    const url = URL.createObjectURL(new Blob(['\ufeff' + [columns, ...values].map((r) => r.map(escape).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a'); link.href = url; link.download = `${doc.number || title}.csv`; link.click(); URL.revokeObjectURL(url)
  }
  const index = rows.findIndex((r) => r.id === doc.id)
  const filtered = rows.filter((r) => `${r.number} ${r.notes} ${r.document_date}`.toLowerCase().includes(query.toLowerCase()))
  return <section className="wh-workspace" aria-label={title}>
    <div className="wh-toolbar">
      <Tool icon={Search} onClick={() => setTab('list')}>查询</Tool>
      <Tool icon={Plus} disabled={!can(session, 'inventory_document', 'create')} onClick={() => selectDoc(newDocument())}>新增</Tool>
      <Tool icon={Save} disabled={(!editable || !canWrite) && !countEditing || !dirty} onClick={save}>保存</Tool>
      <Tool icon={Undo2} disabled={!dirty} onClick={() => selectDoc(rows.find((r) => r.id === doc.id) || newDocument())}>取消</Tool>
      <Tool icon={Trash2} disabled={!doc.id || locked || !can(session, 'inventory_document', 'delete')} onClick={() => setDeletePrompt(true)}>删除</Tool>
      <Tool icon={Plus} disabled={locked} onClick={add}>增行</Tool>
      <Tool icon={Minus} disabled={locked || selected == null} onClick={() => { set('lines', doc.lines.filter((_, i) => i !== selected)); setSelected(null) }}>删行</Tool>
      {hasConfirm && <Tool icon={Check} disabled={!doc.id || dirty || doc.status !== 'draft' || !can(session, 'inventory_document', 'approve')} onClick={() => transition('confirm')}>确认</Tool>}
      {hasConfirm && <Tool icon={X} disabled={!doc.id || dirty || doc.status !== 'confirmed' || !can(session, 'inventory_document', 'approve')} onClick={() => transition('unconfirm')}>反确认</Tool>}
      <Tool icon={CheckCheck} disabled={!doc.id || dirty || doc.status !== (hasConfirm ? 'confirmed' : 'draft') || !can(session, 'inventory_document', 'approve')} onClick={() => transition('approve')}>审核</Tool>
      <Tool icon={RotateCcw} disabled={doc.status !== 'posted' || !can(session, 'inventory_document', 'approve')} onClick={() => setReason('')}>冲销</Tool>
      <span className="wh-divider" />
      <Tool icon={ChevronFirst} disabled={!rows.length} onClick={() => selectDoc(rows[0])}>第一笔</Tool>
      <Tool icon={ChevronLeft} disabled={index <= 0} onClick={() => selectDoc(rows[index - 1])}>上一笔</Tool>
      <Tool icon={ChevronRight} disabled={index < 0 || index >= rows.length - 1} onClick={() => selectDoc(rows[index + 1])}>下一笔</Tool>
      <Tool icon={ChevronLast} disabled={!rows.length} onClick={() => selectDoc(rows.at(-1))}>末一笔</Tool>
      <Tool icon={Printer} disabled={!doc.id} onClick={() => window.print()}>预览/打印</Tool>
      <Tool icon={Download} disabled={!doc.lines.length} onClick={exportCsv}>导出</Tool>
      <Tool icon={RefreshCw} onClick={() => run(reload)}>刷新</Tool>
    </div>
    <div className="wh-tabs"><button className={tab === 'edit' ? 'active' : ''} onClick={() => setTab('edit')}>资料维护</button><button className={tab === 'list' ? 'active' : ''} onClick={() => setTab('list')}>资料浏览</button><h1>{title}</h1></div>
    {error && <div className="wh-error" role="alert">{error}</div>}{notice && <div className="wh-notice" role="status">{notice}</div>}
    {tab === 'list' ? <><div className="wh-filter"><Search size={16}/><input aria-label="查询单据" placeholder="单号、日期、备注" value={query} onChange={(e) => setQuery(e.target.value)} /></div><div className="wh-grid"><table><thead><tr>{['单号', '日期', '状态', '出库/盘点库位', '入库库位', '备注'].map((s) => <th key={s}>{s}</th>)}</tr></thead><tbody>{filtered.map((row) => <tr key={row.id} onDoubleClick={() => selectDoc(row)}><td><button className="wh-link" onClick={() => selectDoc(row)}>{row.number}</button></td><td>{row.document_date}</td><td>{titles[row.status]}</td><td>{label('location', row.from_location)}</td><td>{label('location', row.to_location)}</td><td>{row.notes}</td></tr>)}</tbody></table>{!filtered.length && <p className="wh-empty">暂无单据</p>}</div></> : <>
      <div className="wh-head">
        <div className="wh-fields">
          {head('单号', 'number', <input value={doc.number || ''} readOnly placeholder="保存后生成" />)}
          {head('日期', 'document_date', <input type="date" value={doc.document_date} disabled={locked} onChange={(e) => set('document_date', e.target.value)} />)}
          {hasFrom && head(isCount ? '盘点库位' : '出库库位', 'from_location', options('location', doc.from_location, (v) => set('from_location', v), isCount ? '盘点库位' : '出库库位'))}
          {hasTo && head('入库库位', 'to_location', options('location', doc.to_location, (v) => set('to_location', v), '入库库位'))}
          {!isCount && head('类型', 'category_code', initialCount ? <input value="001 初盘导入" readOnly/> : lookup('类型', doc.category_code, (v) => set('category_code', v || ''), (lookups['inventory-dictionary'] || []).filter((r) => r.dictionary === 'MOV_CAT' && !r.disabled).map((r) => ({ ...r, id: r.code }))))}
          {!isCount && hasFrom && head(kind === 'scrap' ? '报废部门' : '出库部门', 'from_department', options('department', doc.from_department, (v) => set('from_department', v), kind === 'scrap' ? '报废部门' : '出库部门'))}
          {!isCount && hasTo && kind !== 'scrap' && head('入库部门', 'to_department', options('department', doc.to_department, (v) => set('to_department', v), '入库部门'))}
          {kind === 'transfer' && head('转仓类别', 'transfer_class', lookup('转仓类别', doc.transfer_class || '1', (v) => set('transfer_class', v), transferClasses, false, false))}
          {kind === 'transfer' && head('外协供应商', 'supplier', options('partner', doc.supplier, (v) => set('supplier', v), '外协供应商'))}
          {isCount && head('账面数量类型', 'count_basis', lookup('账面数量类型', doc.count_basis, (v) => set('count_basis', v), countBases, false, false))}
          {isCount && head('盘点人', 'checker', lookup('盘点人', doc.checker, (v) => set('checker', v), (lookups.employee || []).filter((row) => String(row.id) === String(doc.checker) || (!row.is_locked && !row.is_left))))}
          {['receipt', 'issue'].includes(kind) && head('默认打印人', 'printer')}
          {head('备注', 'notes')}
        </div>
        <div className="wh-audit"><strong className={`wh-state ${doc.status || 'draft'}`}>{titles[doc.status] || '草稿'}</strong>{[['录入人', doc.created_by], ['录入时间', doc.created_at], ['确认人', doc.confirmed_by], ['审核人', doc.posted_by], ['审核时间', doc.posted_at], ['冲销原因', doc.reversal_reason]].map(([name, value]) => <div key={name}><span>{name}</span><output>{value ? String(value).replace('T', ' ').slice(0, name.includes('时间') ? 19 : 240) : ''}</output></div>)}</div>
      </div>
      <div className="wh-grid"><table className="wh-lines"><thead><tr>{['行号', '物料编码', '物料名称', '英文名称', '规格', ...(isCount ? ['账面数量', '实盘数量', '差异数量'] : ['数量']), ...(hasFrom ? [isCount ? '盘点库位' : '出库库位', '出库库位名称'] : []), ...(hasTo ? ['入库库位', '入库库位名称'] : []), '库存单位', '批号', '等级', '备注', ...(['receipt', 'scrap'].includes(kind) ? ['参考成本'] : []), ...(kind === 'issue' ? ['原出库单号', '原行号'] : []), '录入人', '录入时间', '修改次数', '最后修改人', '最后修改时间'].map((name) => <th key={name}>{name}</th>)}</tr></thead><tbody>
        {doc.lines.map((line, i) => <tr key={line.id || line.line_number} className={selected === i ? 'selected' : ''} onClick={() => setSelected(i)}><td className="wh-derived">{line.line_number}</td><td>{options('material', line.material, (v) => lineSet(i, 'material', v), `物料编码${line.line_number}`, true)}</td><td className="wh-derived" title={line.material_name}>{line.material_name}</td><td className="wh-derived">{line.english_name}</td><td className="wh-derived" title={line.specification}>{line.specification}</td>
          {isCount ? <><td className="numeric">{fmt(line.system_quantity)}</td><td><input aria-label={`实盘数量${line.line_number}`} type="number" min="0" step="0.00000001" disabled={!countEditing} value={text(line.counted_quantity)} onChange={(e) => lineSet(i, 'counted_quantity', e.target.value)} /></td><td className="numeric">{fmt(line.variance_quantity)}</td></> : <td><input aria-label={`数量${line.line_number}`} type="number" min="0.00000001" step="0.00000001" disabled={locked} value={text(line.quantity)} onChange={(e) => lineSet(i, 'quantity', e.target.value)} /></td>}
          {hasFrom && <><td className={kind === 'transfer' ? 'wh-derived' : ''}>{lineLocation(line, i, 'from_location', '出库库位')}</td><td className="wh-derived">{relatedName('location', line.from_location)}</td></>}{hasTo && <><td className={kind === 'transfer' ? 'wh-derived' : ''}>{lineLocation(line, i, 'to_location', '入库库位')}</td><td className="wh-derived">{relatedName('location', line.to_location)}</td></>}
          <td className="wh-derived">{relatedName('uom', line.uom)}</td>{['batch_number', 'grade', 'notes'].map((key) => <td key={key}><input aria-label={`${key}-${line.line_number}`} maxLength={key === 'batch_number' ? 18 : key === 'grade' ? 2 : 255} disabled={locked} value={text(line[key])} onChange={(e) => lineSet(i, key, e.target.value)} /></td>)}
          {['receipt', 'scrap'].includes(kind) && <td><input aria-label={`参考成本${line.line_number}`} type="number" step="0.00000001" disabled={locked} value={text(line.reference_cost)} onChange={(e) => lineSet(i, 'reference_cost', e.target.value)} /></td>}
          {kind === 'issue' && ['reference_number', 'reference_line'].map((key) => <td key={key}><input aria-label={`${key}-${line.line_number}`} disabled={locked} value={text(line[key])} onChange={(e) => lineSet(i, key, e.target.value)} /></td>)}
          {[line.created_by, dateTime(line.created_at), line.id ? line.modification_count : '', line.modified_by, dateTime(line.modified_at)].map((value, index) => <td className="wh-derived" key={index}>{value}</td>)}
        </tr>)}
      </tbody></table>{!doc.lines.length && <div className="wh-empty">暂无明细{!locked && <button onClick={add}><Plus size={15}/>新增明细</button>}</div>}</div>
    </>}
    <footer className="wh-footer"><span>记录数 {tab === 'list' ? filtered.length : doc.lines.length}</span><span>{busy ? '处理中' : dirty ? '未保存' : titles[doc.status] || '草稿'}</span>{tab === 'edit' && [...new Set(doc.lines.map((l) => l.uom).filter(Boolean))].map((uom) => <span key={uom}>{label('uom', uom)} 合计 {fmt(sum(doc.lines.filter((l) => l.uom === uom), isCount ? 'counted_quantity' : 'quantity'))}</span>)}<span>{doc.number}</span></footer>
    {(reason !== null || deletePrompt) && <div className="modal-backdrop"><div className="wh-dialog" role="dialog" aria-modal="true" aria-label={deletePrompt ? '删除草稿' : '冲销单据'}><h2>{deletePrompt ? '删除这张草稿？' : '冲销单据'}</h2>{!deletePrompt && <textarea aria-label="冲销原因" maxLength={240} value={reason} onChange={(e) => setReason(e.target.value)} /> }<div><button onClick={() => { setReason(null); setDeletePrompt(false) }}>取消</button><button disabled={busy || (!deletePrompt && !reason.trim())} onClick={() => deletePrompt ? run(async () => { await request(`/inventory-document/${doc.id}/`, { method: 'DELETE' }); load(newDocument()); setDeletePrompt(false); await reload() }) : transition('reverse', { reason })}>确定</button></div></div></div>}
  </section>
}
