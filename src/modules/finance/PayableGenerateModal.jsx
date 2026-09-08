import { useEffect, useState } from 'react'
import { Coins, X } from 'lucide-react'
import { api, listPayload } from '../../api/client'
import { today } from '../../shared/presentation'
import { AsyncForm } from '../../components/PendingControls'

export function PayableGenerateModal({ session, onClose, onSave }) {
  const [sources, setSources] = useState([])
  const [selected, setSelected] = useState(new Set())
  const [voucherDate, setVoucherDate] = useState(today())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    Promise.all([
      api('/goods-receipt-line/', { token: session.token }),
      api('/goods-receipt/', { token: session.token }),
      api('/purchase-return-line/', { token: session.token }),
      api('/purchase-return/', { token: session.token }),
      api('/payable-voucher-line/', { token: session.token }),
    ])
      .then(([receiptLines, receipts, returnLines, returns, usedLines]) => {
        const approvedReceipts = new Set(
          listPayload(receipts)
            .filter((row) => row.status === 'approved')
            .map((row) => row.id)
        )
        const approvedReturns = new Set(
          listPayload(returns)
            .filter((row) => row.status === 'approved')
            .map((row) => row.id)
        )
        const usedReceipts = new Set(
          listPayload(usedLines)
            .map((row) => row.source_receipt_line)
            .filter(Boolean)
        )
        const usedReturns = new Set(
          listPayload(usedLines)
            .map((row) => row.source_purchase_return_line)
            .filter(Boolean)
        )
        setSources([
          ...listPayload(receiptLines)
            .filter((row) => approvedReceipts.has(row.receipt) && !usedReceipts.has(row.id))
            .map((row) => ({
              key: `receipt-${row.id}`,
              type: '收货',
              id: row.id,
              material: row.material,
              quantity: row.quantity,
            })),
          ...listPayload(returnLines)
            .filter((row) => approvedReturns.has(row.purchase_return) && !usedReturns.has(row.id))
            .map((row) => ({
              key: `return-${row.id}`,
              type: '退货',
              id: row.id,
              material: row.material,
              quantity: row.quantity,
            })),
        ])
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [session])
  const toggle = (key) =>
    setSelected((current) => {
      const next = new Set(current)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  const submit = (event) => {
    event.preventDefault()
    const chosen = sources.filter((source) => selected.has(source.key))
    return onSave({
      voucher_date: voucherDate,
      receipt_line_ids: chosen.filter((source) => source.type === '收货').map((source) => source.id),
      purchase_return_line_ids: chosen.filter((source) => source.type === '退货').map((source) => source.id),
    })
  }
  return (
    <div className="modal-backdrop">
      <AsyncForm className="modal payable-modal" onSubmit={submit}>
        <div className="modal-head">
          <div>
            <h2>自动生成应付凭单</h2>
            <p>按供应商、币种、支付方式和税率自动拆分</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <label>
          <span>
            凭单日期<em>*</em>
          </span>
          <input required type="date" value={voucherDate} onChange={(event) => setVoucherDate(event.target.value)} />
        </label>
        <div className="source-list">
          {loading ? (
            <div className="empty">正在加载</div>
          ) : error ? (
            <div className="error-banner">{error}</div>
          ) : sources.length ? (
            sources.map((source) => (
              <label className="source-row" key={source.key}>
                <input type="checkbox" checked={selected.has(source.key)} onChange={() => toggle(source.key)} />
                <strong>{source.type}</strong>
                <span>来源行 #{source.id}</span>
                <span>物料 #{source.material}</span>
                <span>{source.quantity}</span>
              </label>
            ))
          ) : (
            <div className="empty">没有待生成的已审核来源</div>
          )}
        </div>
        <div className="modal-foot">
          <span>已选择 {selected.size} 条</span>
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary" disabled={!selected.size}>
            <Coins size={16} />
            生成凭单
          </button>
        </div>
      </AsyncForm>
    </div>
  )
}
