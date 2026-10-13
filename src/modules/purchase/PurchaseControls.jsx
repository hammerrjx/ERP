import { useEffect, useState } from 'react'
import { Search, X } from 'lucide-react'

export const today = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
export const statusNames = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
export const format = (v, digits = 2) => v === '' || v == null ? '' : Number(v).toLocaleString('zh-CN', { minimumFractionDigits: digits, maximumFractionDigits: digits })
const SCALE = 100000000n
const scaled = v => {
  const match = String(v || 0).match(/^([+-]?)(\d*)(?:\.(\d*))?(?:e([+-]?\d+))?$/i)
  if (!match) return 0n
  const [, sign, whole, fraction = '', exponent = '0'] = match
  const shift = 8 + Number(exponent) - fraction.length
  if (Math.abs(shift) > 100) return 0n
  const digits = BigInt((whole + fraction) || '0')
  return (sign === '-' ? -1n : 1n) * (shift >= 0 ? digits * 10n ** BigInt(shift) : digits / 10n ** BigInt(-shift))
}
const decimal = n => `${n < 0n ? '-' : ''}${(n < 0n ? -n : n) / SCALE}.${String((n < 0n ? -n : n) % SCALE).padStart(8, '0')}`
export const sum = values => decimal(values.reduce((n, v) => n + scaled(v), 0n))
export const converted = (quantity, numerator, denominator) => scaled(denominator) > 0n ? decimal(scaled(quantity) * scaled(numerator) / scaled(denominator)) : ''
const round = (n, d) => (n + d / 2n) / d
export const amounts = (quantity, price, tax) => {
  const q = scaled(quantity), p = scaled(price), divisor = 100n * SCALE + scaled(tax)
  const net = divisor > 0n ? round(p * 100n * SCALE, divisor * 10000n) * 10000n : 0n
  return { amount: decimal(round(q * p, SCALE * 1000000n) * 1000000n), untaxed_price: decimal(net), untaxed_amount: decimal(round(q * net, SCALE * 1000000n) * 1000000n) }
}
export const dateTime = value => value ? new Date(value).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }) : ''

export function Lookup({ kind, request, onPick, onClose }) {
  const titles = { supplier: '供应商', department: '部门', currency: '币种', material: '物料', employee: '员工', uom: '单位' }
  const [q, setQ] = useState(''), [rows, setRows] = useState([]), [error, setError] = useState('')
  useEffect(() => {
    let active = true
    const timer = setTimeout(() => request(`/purchase-order/lookups/?${new URLSearchParams({ kind, q })}`).then(data => { if (active) { setRows(data); setError('') } }).catch(e => { if (active) setError(e.message) }), 180)
    return () => { active = false; clearTimeout(timer) }
  }, [kind, q])
  return <div className="pu-backdrop"><section className="pu-dialog pu-lookup" role="dialog" aria-modal="true" aria-label={`${titles[kind]}检索`} onKeyDown={e => { if (e.key === 'Escape') onClose() }}>
    <header><strong>{titles[kind]}检索</strong><button onClick={onClose} aria-label="关闭检索"><X size={16} /></button></header>
    <input autoFocus aria-label="编码或名称" placeholder="输入编码或名称" value={q} onChange={e => setQ(e.target.value)} />
    <small>最多显示50项，可输入条件缩小范围。</small>{error && <p role="alert">{error}</p>}
    <div className="pu-lookup-list">{rows.map(row => <button key={row.id} onClick={() => onPick(row)}>{row.code}　{row.name}</button>)}{!rows.length && <p>没有匹配资料</p>}</div>
  </section></div>
}

export function LookupField({ label, value, disabled, onClick }) {
  return <label>{label}<span className="pu-search-field"><input aria-label={label} readOnly value={value || ''} disabled={disabled} onClick={disabled ? undefined : onClick} /><button disabled={disabled} onClick={onClick} aria-label={`检索${label}`}><Search size={13} /></button></span></label>
}

export function Tool({ icon: Icon, children, ...props }) {
  return <button type="button" {...props}>{Icon && <Icon size={16} />}<span>{children}</span></button>
}

export function PurchaseGrid({ label, columns, rows, totals = {}, selected, onSelect, cell, empty = '暂无明细', className = '' }) {
  const widths = columns.map(([key]) => key === 'line_number' ? 40 : /line_number|sequence/.test(key) ? 48 : /material_name|parent_name/.test(key) ? 176 : /requisition_number|source_order/.test(key) ? 124 : /notes/.test(key) ? 150 : /_at/.test(key) ? 145 : /date/.test(key) ? 95 : /material_code|specification/.test(key) ? 95 : /uom_name/.test(key) ? 55 : /price|amount/.test(key) ? 80 : 70)
  return <div className={`pu-grid ${className}`} role="region" aria-label={label} tabIndex={0}><table style={{ width: widths.reduce((a, b) => a + b, 0) }}>
    <colgroup>{columns.map(([key], i) => <col key={key} style={{ width: widths[i] }} />)}</colgroup>
    <thead><tr>{columns.map(([key, text]) => <th key={key} scope="col" title={text}>{text}</th>)}</tr></thead>
    <tbody>{rows.map((row, i) => <tr key={row.id || row.line_number || i} className={selected === i ? 'selected' : ''} onClick={() => onSelect?.(i)}>{columns.map(([key, title]) => <td key={key}>{cell ? cell(row, key, title, i) : String(row[key] ?? '')}</td>)}</tr>)}{!rows.length && <tr><td className="pu-empty" colSpan={columns.length}>{empty}</td></tr>}</tbody>
    <tbody className="pu-grid-space" aria-hidden="true"><tr><td colSpan={columns.length} /></tr></tbody>
    <tfoot><tr>{columns.map(([key], i) => <td key={key}>{key in totals ? format(totals[key]) : i === 0 ? '合计' : ''}</td>)}</tr></tfoot>
  </table></div>
}
