import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { api, listPayload } from '../api/client'
import { today } from '../shared/presentation'

export function OrderWorkflowModal({ workflow, row, session, onClose, onSave }) {
  const isMrp = workflow === 'mrp'
  const isReceipt = workflow === 'receipt'
  const [departments, setDepartments] = useState([])
  const [sourceLines, setSourceLines] = useState([])
  const [locations, setLocations] = useState([])
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [values, setValues] = useState(() =>
    isMrp
      ? {
          department: '',
          needed_date: row.promised_date || today(),
          notes: '',
        }
      : isReceipt
        ? {
            receipt_date: today(),
            supplier_delivery_number: '',
            notes: '',
          }
        : {
            delivery_date: today(),
            delivery_address: row.delivery_address || '',
            srm_number: row.srm_number || '',
            customer_po: row.customer_po || '',
            delivery_mode: row.delivery_mode || 'direct',
            notes: '',
          }
  )
  useEffect(() => {
    const requests = isMrp
      ? [api('/department/', { token: session.token })]
      : [
          api(isReceipt ? '/purchase-order-line/' : '/sales-order-line/', { token: session.token }),
          api('/location/', { token: session.token }),
          api('/material/', { token: session.token }),
        ]
    Promise.all(requests)
      .then((result) => {
        if (isMrp) {
          setDepartments(listPayload(result[0]))
          return
        }
        const candidates = listPayload(result[0]).filter((line) => {
          if (isReceipt) return line.order === row.id && Number(line.quantity) > Number(line.received_quantity)
          return (
            line.order === row.id &&
            (Number(line.quantity) > Number(line.delivered_quantity) ||
              Number(line.spare_quantity) > Number(line.delivered_spare_quantity))
          )
        })
        const locs = listPayload(result[1])
        const mats = listPayload(result[2])
        setLocations(locs)
        setMaterials(mats)
        setSourceLines(
          candidates.map((line) => ({
            ...line,
            selected: true,
            quantity: isReceipt ? String(Number(line.quantity) - Number(line.received_quantity)) : undefined,
            actual_quantity: isReceipt ? undefined : String(Number(line.quantity) - Number(line.delivered_quantity)),
            actual_spare_quantity: isReceipt
              ? '0'
              : String(Math.max(Number(line.spare_quantity) - Number(line.delivered_spare_quantity), 0)),
            location: isReceipt ? undefined : line.material_default_location,
            source_location: isReceipt ? undefined : line.material_default_location,
            batch_number: '',
          }))
        )
      })
      .catch((requestError) => setLoadError(requestError.message))
      .finally(() => setLoading(false))
  }, [isMrp, isReceipt, row.id, session.token])
  const update = (key, value) => setValues((current) => ({ ...current, [key]: value }))
  const updateLine = (id, key, value) =>
    setSourceLines((current) => current.map((line) => (line.id === id ? { ...line, [key]: value } : line)))
  const submit = (event) => {
    event.preventDefault()
    const selected = sourceLines.filter((line) => line.selected)
    onSave(
      isMrp
        ? values
        : {
            ...values,
            lines: selected.map((line) =>
              isReceipt
                ? {
                    purchase_order_line: line.id,
                    quantity: line.quantity,
                    location: line.location,
                    batch_number: line.batch_number,
                  }
                : {
                    sales_order_line: line.id,
                    actual_quantity: line.actual_quantity,
                    actual_spare_quantity: line.actual_spare_quantity,
                    source_location: line.source_location,
                    batch_number: line.batch_number,
                  }
            ),
          }
    )
  }
  const title = isMrp ? 'MRP 请购分析' : isReceipt ? '按采购单生成收货草稿' : '按订单生成送货草稿'
  const source = isReceipt ? '采购单' : '销售订单'
  const materialName = (id) => materials.find((item) => item.id === id)?.name || `物料 #${id}`
  const lineEditor = !isMrp ? (
    <div className="source-list">
      {sourceLines.length ? (
        sourceLines.map((line) => (
          <div className="source-row workflow-source" key={line.id}>
            <input
              type="checkbox"
              checked={line.selected}
              onChange={(event) => updateLine(line.id, 'selected', event.target.checked)}
            />
            <strong>{materialName(line.material)}</strong>
            <span>订单行 {line.line_number}</span>
            <label>
              <span>{isReceipt ? '本次收货' : '本次正式送货'}</span>
              <input
                required={line.selected}
                disabled={!line.selected}
                type="number"
                min={isReceipt ? '0.000001' : '0'}
                step="any"
                value={isReceipt ? line.quantity : line.actual_quantity}
                onChange={(event) =>
                  updateLine(line.id, isReceipt ? 'quantity' : 'actual_quantity', event.target.value)
                }
              />
            </label>
            {!isReceipt ? (
              <label>
                <span>送备品数</span>
                <input
                  disabled={!line.selected}
                  type="number"
                  min="0"
                  step="any"
                  value={line.actual_spare_quantity}
                  onChange={(event) => updateLine(line.id, 'actual_spare_quantity', event.target.value)}
                />
              </label>
            ) : null}
            <label>
              <span>{isReceipt ? '入库库位' : '出库库位'}</span>
              <select
                required={line.selected}
                disabled={!line.selected}
                value={isReceipt ? line.location || '' : line.source_location || ''}
                onChange={(event) =>
                  updateLine(line.id, isReceipt ? 'location' : 'source_location', Number(event.target.value))
                }
              >
                <option value="">请选择</option>
                {locations.map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.code} {location.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>批号</span>
              <input
                disabled={!line.selected}
                value={line.batch_number}
                onChange={(event) => updateLine(line.id, 'batch_number', event.target.value)}
              />
            </label>
          </div>
        ))
      ) : (
        <div className="empty">没有可生成的待处理来源行</div>
      )}
    </div>
  ) : null
  return (
    <div className="modal-backdrop">
      <form className="modal workflow-modal" onSubmit={submit}>
        <div className="modal-head">
          <div>
            <h2>{title}</h2>
            <p>{row.number || `${source} #${row.id}`}，勾选来源行并确认数量、库位后生成草稿</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        {loadError ? (
          <div className="error-banner">{loadError}</div>
        ) : (
          <>
            <div className="form-grid">
              {isMrp ? (
                <>
                  <label>
                    <span>
                      请购部门<em>*</em>
                    </span>
                    <select
                      required
                      value={values.department}
                      onChange={(event) =>
                        update('department', event.target.value === '' ? '' : Number(event.target.value))
                      }
                      disabled={loading}
                    >
                      <option value="">请选择</option>
                      {departments.map((department) => (
                        <option key={department.id} value={department.id}>
                          {department.code} {department.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>
                      需求日期<em>*</em>
                    </span>
                    <input
                      required
                      type="date"
                      value={values.needed_date}
                      onChange={(event) => update('needed_date', event.target.value)}
                    />
                  </label>
                  <label className="field-wide">
                    <span>分析备注</span>
                    <textarea value={values.notes} onChange={(event) => update('notes', event.target.value)} />
                  </label>
                </>
              ) : isReceipt ? (
                <>
                  <label>
                    <span>
                      收货日期<em>*</em>
                    </span>
                    <input
                      required
                      type="date"
                      value={values.receipt_date}
                      onChange={(event) => update('receipt_date', event.target.value)}
                    />
                  </label>
                  <label>
                    <span>
                      供应商送货单号<em>*</em>
                    </span>
                    <input
                      required
                      value={values.supplier_delivery_number}
                      onChange={(event) => update('supplier_delivery_number', event.target.value)}
                    />
                  </label>
                  <label className="field-wide">
                    <span>单头备注</span>
                    <textarea value={values.notes} onChange={(event) => update('notes', event.target.value)} />
                  </label>
                </>
              ) : (
                <>
                  <label>
                    <span>
                      送货日期<em>*</em>
                    </span>
                    <input
                      required
                      type="date"
                      value={values.delivery_date}
                      onChange={(event) => update('delivery_date', event.target.value)}
                    />
                  </label>
                  <label>
                    <span>
                      送货模式<em>*</em>
                    </span>
                    <select
                      required
                      value={values.delivery_mode}
                      onChange={(event) => update('delivery_mode', event.target.value)}
                    >
                      <option value="direct">直送</option>
                      <option value="supplier">供应商代送</option>
                    </select>
                  </label>
                  <label>
                    <span>
                      送货地址<em>*</em>
                    </span>
                    <input
                      required
                      value={values.delivery_address}
                      onChange={(event) => update('delivery_address', event.target.value)}
                    />
                  </label>
                  <label>
                    <span>
                      SRM 系统单号<em>*</em>
                    </span>
                    <input
                      required
                      value={values.srm_number}
                      onChange={(event) => update('srm_number', event.target.value)}
                    />
                  </label>
                  <label>
                    <span>
                      客户 PO<em>*</em>
                    </span>
                    <input
                      required
                      value={values.customer_po}
                      onChange={(event) => update('customer_po', event.target.value)}
                    />
                  </label>
                  <label className="field-wide">
                    <span>单头备注</span>
                    <textarea value={values.notes} onChange={(event) => update('notes', event.target.value)} />
                  </label>
                </>
              )}
            </div>
            {lineEditor}
          </>
        )}
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button
            className="primary"
            disabled={loading || Boolean(loadError) || (!isMrp && !sourceLines.some((line) => line.selected))}
          >
            {isMrp ? '生成请购草稿' : isReceipt ? '生成收货草稿' : '生成送货草稿'}
          </button>
        </div>
      </form>
    </div>
  )
}
