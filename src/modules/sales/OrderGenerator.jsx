import { useEffect, useRef, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, Search, X } from 'lucide-react'
import { api } from '../../api/client'
import { formatQuantity } from '../../shared/presentation'

const FILTERS = [
  ['customer_po', '客户 PO'],
  ['material_code', '内部物料编码'],
  ['customer_material_code', '客户物料编码'],
  ['terminal_material_code', '客户终端物料编码'],
  ['order_number', '客户订单']
]
export function OrderGenerator({ token, customer, delivery, documentType, existing, onClose, onGenerate }) {
  const [filters, setFilters] = useState({ match: 'contains' })
  const [result, setResult] = useState({ results: [], count: 0, page: 1 })
  const [selected, setSelected] = useState({})
  const [direction, setDirection] = useState(documentType === 'normal' ? 'ship' : 'return')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const requestId = useRef(0)
  const existingIds = new Set(existing.map((row) => Number(row.sales_order_line)))
  const query = async (page = 1) => {
    const id = ++requestId.current
    setBusy(true)
    setError('')
    const params = new URLSearchParams({ ...filters, customer, page, ...(delivery ? { delivery } : {}) })
    try {
      const response = await api('/delivery-order/order-candidates/?' + params, { token })
      if (id === requestId.current) setResult(response)
    } catch (e) {
      if (id === requestId.current) setError(e.message)
    } finally {
      if (id === requestId.current) setBusy(false)
    }
  }
  useEffect(() => {
    query()
    return () => {
      requestId.current++
    }
  }, [])
  const toggle = (row, checked) =>
    setSelected((current) => {
      const next = { ...current }
      if (checked) {
        next[row.sales_order_line] = {
          ...row,
          actual_quantity: direction === 'return' ? String(-Number(row.returnable_quantity)) : row.available_quantity,
          actual_spare_quantity:
            direction === 'return' ? String(-Number(row.returnable_spare_quantity)) : row.available_spare_quantity,
          batch_number: '',
          notes: ''
        }
      } else delete next[row.sales_order_line]
      return next
    })
  const generate = () => {
    const rows = Object.values(selected)
    if (!rows.length) return setError('请勾选订单明细')
    for (const row of rows) {
      const amount = Number(row.actual_quantity),
        spare = Number(row.actual_spare_quantity)
      if (!Number.isFinite(amount) || !Number.isFinite(spare) || (!amount && !spare))
        return setError('送货数量与备品数不能同时为0')
      const limit = amount < 0 ? row.returnable_quantity : row.available_quantity
      const spareLimit = spare < 0 ? row.returnable_spare_quantity : row.available_spare_quantity
      if (Math.abs(amount) > Number(limit) || Math.abs(spare) > Number(spareLimit))
        return setError(row.order_number + ' / ' + row.order_line_number + '：数量超过当前可用额度')
    }
    onGenerate(rows)
  }
  const update = (id, key, value) => setSelected((current) => ({ ...current, [id]: { ...current[id], [key]: value } }))
  return (
    <div className="modal-backdrop delivery-overlay">
      <div role="dialog" aria-modal="true" aria-label="根据客户订单生成明细" className="modal delivery-generator">
        <div className="modal-head">
          <h2>根据客户订单生成明细</h2>
          <button type="button" aria-label="关闭生成窗口" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <form
          className="delivery-query"
          onSubmit={(event) => {
            event.preventDefault()
            query()
          }}
        >
          <label>
            <span>查询方式</span>
            <select
              value={filters.match}
              onChange={(event) => setFilters((current) => ({ ...current, match: event.target.value }))}
            >
              <option value="contains">包含</option>
              <option value="exact">精确</option>
              <option value="range">区间</option>
            </select>
          </label>
          {FILTERS.map(([key, label]) => (
            <label key={key}>
              <span>{label}</span>
              <div className="delivery-range">
                <input
                  aria-label={label}
                  value={filters[key] || ''}
                  onChange={(event) => setFilters((current) => ({ ...current, [key]: event.target.value }))}
                />
                {filters.match === 'range' && (
                  <input
                    aria-label={label + '结束'}
                    value={filters[key + '_to'] || ''}
                    onChange={(event) => setFilters((current) => ({ ...current, [key + '_to']: event.target.value }))}
                  />
                )}
              </div>
            </label>
          ))}
          {[
            ['order_date', '下单日期'],
            ['promised_date', '预计交货日期']
          ].map(([key, label]) => (
            <label key={key}>
              <span>{label}</span>
              <div className="delivery-range">
                <input
                  type="date"
                  aria-label={label + '开始'}
                  value={filters[key + '_from'] || ''}
                  onChange={(event) => setFilters((current) => ({ ...current, [key + '_from']: event.target.value }))}
                />
                <input
                  type="date"
                  aria-label={label + '结束'}
                  value={filters[key + '_to'] || ''}
                  onChange={(event) => setFilters((current) => ({ ...current, [key + '_to']: event.target.value }))}
                />
              </div>
            </label>
          ))}
          <button className="primary" disabled={busy}>
            <Search size={15} />
            查询
          </button>
        </form>
        <div className="delivery-selection-bar">
          <label>
            数量方向{' '}
            <select
              value={direction}
              onChange={(event) => {
                setDirection(event.target.value)
                setSelected({})
              }}
            >
              <option value="ship">送出（正数）</option>
              <option value="return">退回（负数）</option>
            </select>
          </label>
          <button
            type="button"
            onClick={() =>
              result.results.filter((row) => !existingIds.has(row.sales_order_line)).forEach((row) => toggle(row, true))
            }
            disabled={busy}
          >
            选中本页
          </button>
          <button type="button" onClick={() => setSelected({})}>
            全不选
          </button>
          <span>已选 {Object.keys(selected).length} 行</span>
        </div>
        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}
        <div className="delivery-candidates-wrap">
          <table className="delivery-candidates">
            <thead>
              <tr>
                {[
                  '选择',
                  '客户订单',
                  '订单行号',
                  '内部物料编码',
                  '客户物料编码',
                  '终端物料编码',
                  '客户 PO',
                  '物料名称',
                  '订购数量',
                  '净已送数量',
                  '未审核送货',
                  '可送上限',
                  '可退数量',
                  '本次送货数量',
                  '本次备品数',
                  '可送备品',
                  '可退备品',
                  '库存参考'
                ].map((label) => (
                  <th key={label}>{label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.results.map((row) => {
                const picked = selected[row.sales_order_line]
                return (
                  <tr key={row.sales_order_line} className={picked ? 'is-selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        aria-label={'选择' + row.order_number + '行' + row.order_line_number}
                        checked={Boolean(picked)}
                        disabled={existingIds.has(row.sales_order_line) || busy}
                        onChange={(event) => toggle(row, event.target.checked)}
                      />
                    </td>
                    <td>{row.order_number}</td>
                    <td>{row.order_line_number}</td>
                    <td>{row.material_code}</td>
                    <td>{row.customer_material_code}</td>
                    <td>{row.terminal_material_code}</td>
                    <td>{row.customer_po}</td>
                    <td>{row.material_name}</td>
                    {[
                      row.ordered_quantity,
                      row.delivered_quantity,
                      row.pending_quantity,
                      row.available_quantity,
                      row.returnable_quantity
                    ].map((value, index) => (
                      <td className="numeric" key={index}>
                        {formatQuantity(value)}
                      </td>
                    ))}
                    <td>
                      <input
                        type="number"
                        step="0.00000001"
                        aria-label="本次送货数量"
                        value={picked?.actual_quantity ?? ''}
                        disabled={!picked || busy}
                        onChange={(event) => update(row.sales_order_line, 'actual_quantity', event.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.00000001"
                        aria-label="本次备品数"
                        value={picked?.actual_spare_quantity ?? ''}
                        disabled={!picked || busy}
                        onChange={(event) => update(row.sales_order_line, 'actual_spare_quantity', event.target.value)}
                      />
                    </td>
                    <td className="numeric">{formatQuantity(row.available_spare_quantity)}</td>
                    <td className="numeric">{formatQuantity(row.returnable_spare_quantity)}</td>
                    <td>未同步</td>
                  </tr>
                )
              })}
              {!result.results.length && (
                <tr>
                  <td colSpan={18} className="delivery-empty">
                    {busy ? '查询中…' : '无符合条件的订单明细'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="modal-foot">
          <span>
            共 {result.count} 行 · 第 {result.page} 页
          </span>
          <button
            type="button"
            title="上一页"
            disabled={busy || result.page <= 1}
            onClick={() => query(result.page - 1)}
          >
            <ChevronLeft size={16} />
          </button>
          <button
            type="button"
            title="下一页"
            disabled={busy || result.page * 30 >= result.count}
            onClick={() => query(result.page + 1)}
          >
            <ChevronRight size={16} />
          </button>
          <button type="button" className="secondary" onClick={onClose}>
            关闭
          </button>
          <button type="button" className="primary" disabled={busy || !Object.keys(selected).length} onClick={generate}>
            <Check size={16} />
            生成
          </button>
        </div>
      </div>
    </div>
  )
}
