import { ReadonlyField, SearchableLookup } from '../../components/Field'
import { useMemo, useState } from 'react'
import { Check, Plus, Trash2, X } from 'lucide-react'
import { statusLabels, today } from '../../shared/presentation'
import { AsyncForm } from '../../components/PendingControls'

const numeric = (value) => Number(value || 0)
const fixed = (value) => (Number.isFinite(value) ? value.toFixed(8) : '')
const timestamp = (value) => (value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '')

function BusinessGroupPicker({ value, groups, disabled, onChange }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedId, setSelectedId] = useState(value ? Number(value) : null)
  const selected = groups.find((group) => group.id === Number(value))
  const visible = groups.filter((group) =>
    `${group.code} ${group.name}`.toLowerCase().includes(query.trim().toLowerCase())
  )

  const close = () => {
    setSelectedId(value ? Number(value) : null)
    setQuery('')
    setOpen(false)
  }
  const confirm = () => {
    if (selectedId) onChange(selectedId)
    setQuery('')
    setOpen(false)
  }

  return (
    <>
      <label className="business-group-field">
        <span>
          业务类型<em>*</em>
        </span>
        <button
          type="button"
          className="quote-picker-input"
          disabled={disabled}
          onClick={() => {
            setSelectedId(value ? Number(value) : null)
            setOpen(true)
          }}
        >
          {selected?.code || '选择业务组'}
        </button>
      </label>
      {open ? (
        <div className="modal-backdrop business-group-backdrop">
          <div className="modal business-group-modal" role="dialog" aria-modal="true" aria-label="选择业务组">
            <div className="modal-head">
              <div>
                <h2>选择业务组</h2>
                <p>按业务组代码或名称检索后选择一条记录</p>
              </div>
              <button type="button" aria-label="关闭" onClick={close}>
                <X size={19} />
              </button>
            </div>
            <div className="business-group-content">
              <label>
                <span>检索</span>
                <input
                  autoFocus
                  value={query}
                  placeholder="输入代码或名称"
                  onChange={(event) => setQuery(event.target.value)}
                />
              </label>
              <div className="business-group-table-wrap">
                <table className="business-group-table">
                  <thead>
                    <tr>
                      <th>序号</th>
                      <th>业务模式</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((group) => (
                      <tr
                        key={group.id}
                        className={selectedId === group.id ? 'selected' : ''}
                        onClick={() => setSelectedId(group.id)}
                      >
                        <td>{group.code}</td>
                        <td>{group.name}</td>
                      </tr>
                    ))}
                    {visible.length === 0 ? (
                      <tr>
                        <td colSpan="2" className="business-group-empty">
                          无匹配业务组
                        </td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="modal-foot">
              <button type="button" className="secondary" onClick={close}>
                取消
              </button>
              <button type="button" className="primary" disabled={!selectedId} onClick={confirm}>
                确定
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}

export function SupplierQuoteModal({ lookups, record, readOnly = false, onClose, onSave }) {
  const [values, setValues] = useState({
    supplier: record?.supplier || '',
    material: record?.material || '',
    business_group: record?.business_group || '',
    quote_type: record?.quote_type || 'purchase',
    effective_date: record?.effective_date || today(),
    expiry_date: record?.expiry_date || '',
    material_unit_price: record?.material_unit_price || '',
    processing_unit_price: record?.processing_unit_price || '',
    min_purchase_qty: record?.min_purchase_qty || '',
    min_pack_qty: record?.min_pack_qty || '',
    delivery_days: record?.delivery_days || '',
    operation: record?.operation || '',
    notes: record?.notes || ''
  })
  const [tiers, setTiers] = useState(record?.lines || [])
  const supplier = (lookups.suppliers || []).find((row) => row.id === Number(values.supplier))
  const material = (lookups.materials || []).find((row) => row.id === Number(values.material))
  const businessGroup = (lookups.businessGroups || []).find((row) => row.id === Number(values.business_group))
  const currency = (lookups.currencies || []).find((row) => row.id === supplier?.currency)
  const uom = (lookups.uoms || []).find((row) => row.id === material?.uom)
  const operations = useMemo(() => lookups.routingOperations || [], [lookups.routingOperations])
  const taxRate = numeric(supplier?.tax_rate ?? record?.tax_rate)
  const taxIncluded = supplier?.quote_tax_included ?? record?.tax_included ?? true
  const isOutsource = values.quote_type === 'outsource'
  const priceKey = isOutsource ? 'processing_unit_price' : 'material_unit_price'
  const priceLabel = isOutsource ? '加工单价' : '材料单价'
  const unitPrice = numeric(values[priceKey])
  const untaxed = fixed(taxIncluded ? unitPrice / (1 + taxRate / 100) : unitPrice)

  const update = (key, value) =>
    setValues((current) => {
      if (key === 'quote_type')
        return {
          ...current,
          quote_type: value,
          material_unit_price: value === 'purchase' ? current.material_unit_price : '',
          processing_unit_price: value === 'outsource' ? current.processing_unit_price : '',
          operation: value === 'outsource' ? current.operation : ''
        }
      if (key === 'material') return { ...current, material: value, operation: '' }
      return { ...current, [key]: value }
    })
  const updateTier = (index, key, value) =>
    setTiers((current) => current.map((tier, tierIndex) => (tierIndex === index ? { ...tier, [key]: value } : tier)))
  const tierPrice = (tier) => numeric(tier[priceKey])
  const save = (event) => {
    event.preventDefault()
    if (!values.business_group) {
      window.alert('请选择业务组')
      return
    }
    return onSave({
      supplier: values.supplier,
      material: values.material,
      business_group: values.business_group,
      quote_type: values.quote_type,
      effective_date: values.effective_date,
      expiry_date: values.expiry_date || null,
      material_unit_price: isOutsource ? '0' : values.material_unit_price,
      processing_unit_price: isOutsource ? values.processing_unit_price : '0',
      min_purchase_qty: values.min_purchase_qty || '0',
      min_pack_qty: values.min_pack_qty || '0',
      delivery_days: values.delivery_days || '0',
      operation: isOutsource ? values.operation : null,
      notes: values.notes,
      lines: tiers.map((tier, index) => ({
        line_number: tier.line_number || index + 1,
        min_qty: tier.min_qty,
        material_unit_price: isOutsource ? null : tier.material_unit_price,
        processing_unit_price: isOutsource ? tier.processing_unit_price : null,
        notes: tier.notes || ''
      }))
    })
  }

  return (
    <div className="modal-backdrop">
      <AsyncForm className="modal sales-quote-modal" onSubmit={save}>
        <div className="modal-head">
          <div>
            <h2>{readOnly ? '供应商报价详情' : record ? '编辑供应商报价' : '新增供应商报价'}</h2>
            <p>
              {record?.number || '报价单号保存后按月份自动生成'}
              {record?.status
                ? ` · ${statusLabels[record.status] || record.status}${record.is_ratified ? ' · 已核准' : ''}`
                : ''}
            </p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <section className="quote-section">
          <h3>供应商与有效期</h3>
          <div className="quote-grid">
            <ReadonlyField label="报价单号" value={record?.number || '自动生成'} />
            <SearchableLookup
              clearOnFocus
              className="quote-lookup-field"
              label="供应商代码"
              value={values.supplier}
              options={lookups.suppliers || []}
              required
              disabled={readOnly}
              onChange={(value) => update('supplier', value)}
            />
            <ReadonlyField label="供应商名称" value={supplier?.name || record?.supplier_name} />
            <BusinessGroupPicker
              value={values.business_group}
              groups={(lookups.businessGroups || []).filter(
                (group) => group.active || group.id === Number(values.business_group)
              )}
              disabled={readOnly}
              onChange={(value) => update('business_group', value)}
            />
            <ReadonlyField label="业务组名称" value={businessGroup?.name || record?.business_group_name} />
            <ReadonlyField label="币种" value={currency?.code || record?.currency_code} />
            <ReadonlyField label="报价含税" value={taxIncluded ? '是' : '否'} />
            <ReadonlyField label="税率(%)" value={fixed(taxRate)} />
            <label>
              <span>
                生效日期<em>*</em>
              </span>
              <input
                type="date"
                required
                disabled={readOnly}
                value={values.effective_date}
                onChange={(event) => update('effective_date', event.target.value)}
              />
            </label>
            <label>
              <span>失效日期</span>
              <input
                type="date"
                disabled={readOnly}
                value={values.expiry_date}
                onChange={(event) => update('expiry_date', event.target.value)}
              />
            </label>
          </div>
        </section>
        <section className="quote-section">
          <h3>物料与报价</h3>
          <div className="quote-grid">
            <SearchableLookup
              clearOnFocus
              className="quote-lookup-field"
              label="物料编码"
              value={values.material}
              options={lookups.materials || []}
              required
              disabled={readOnly}
              onChange={(value) => update('material', value)}
            />
            <ReadonlyField label="物料名称" value={material?.name || record?.material_name} />
            <ReadonlyField label="物料规格" value={material?.specification || record?.material_specification} />
            <ReadonlyField label="税务编码" value={material?.tax_code || record?.tax_code} />
            <ReadonlyField label="税务名称" value={material?.tax_name || record?.tax_name} />
            <ReadonlyField label="开票名称" value={material?.invoice_name || record?.invoice_name} />
            <ReadonlyField label="采购单位" value={uom?.code || record?.purchase_uom_code} />
            <div className="quote-type">
              <span>
                报价类型<em>*</em>
              </span>
              <div role="group" aria-label="报价类型">
                <button
                  type="button"
                  className={isOutsource ? '' : 'active'}
                  disabled={readOnly}
                  onClick={() => update('quote_type', 'purchase')}
                >
                  采购报价
                </button>
                <button
                  type="button"
                  className={isOutsource ? 'active' : ''}
                  disabled={readOnly}
                  onClick={() => update('quote_type', 'outsource')}
                >
                  外协报价
                </button>
              </div>
            </div>
            {isOutsource ? (
              <label>
                <span>
                  外协工序<em>*</em>
                </span>
                <select
                  required
                  disabled={readOnly}
                  value={values.operation}
                  onChange={(event) => update('operation', event.target.value)}
                >
                  <option value="">请选择</option>
                  {operations.map((operation) => (
                    <option key={operation.id} value={operation.id}>
                      {operation.sequence || ''} {operation.name || ''}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <ReadonlyField label="外协工序" value="不适用" />
            )}
            <label>
              <span>
                {priceLabel}
                <em>*</em>
              </span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                required
                disabled={readOnly}
                value={values[priceKey]}
                onChange={(event) => update(priceKey, event.target.value)}
              />
            </label>
            <ReadonlyField label="含税单价" value={fixed(unitPrice)} />
            <ReadonlyField label="未税单价" value={untaxed} />
            <label>
              <span>最小采购数量</span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                disabled={readOnly}
                value={values.min_purchase_qty}
                placeholder={`默认 ${record?.effective_min_purchase_qty ?? material?.min_purchase_qty ?? 0}`}
                onChange={(event) => update('min_purchase_qty', event.target.value)}
              />
            </label>
            <label>
              <span>最小包装数量</span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                disabled={readOnly}
                value={values.min_pack_qty}
                placeholder={`默认 ${record?.effective_min_pack_qty ?? material?.min_pack_qty ?? 0}`}
                onChange={(event) => update('min_pack_qty', event.target.value)}
              />
            </label>
            <label>
              <span>交货天数</span>
              <input
                type="number"
                min="0"
                step="1"
                disabled={readOnly}
                value={values.delivery_days}
                onChange={(event) => update('delivery_days', event.target.value)}
              />
            </label>
          </div>
        </section>
        <section className="quote-section">
          <div className="quote-section-head">
            <h3>数量阶梯价</h3>
            {!readOnly ? (
              <button
                type="button"
                className="secondary"
                onClick={() =>
                  setTiers((current) => [
                    ...current,
                    { min_qty: '', material_unit_price: '', processing_unit_price: '', notes: '' }
                  ])
                }
              >
                <Plus size={15} />
                新增阶梯
              </button>
            ) : null}
          </div>
          <div className="quote-tier-wrap">
            <table className="quote-tier-table supplier-tier-table">
              <thead>
                <tr>
                  <th>数量大于等于</th>
                  <th>{priceLabel}</th>
                  <th>含税单价</th>
                  <th>未税单价</th>
                  <th>价格注释</th>
                  {!readOnly ? <th>操作</th> : null}
                </tr>
              </thead>
              <tbody>
                {tiers.map((tier, index) => {
                  const price = tierPrice(tier)
                  return (
                    <tr key={tier.id || index}>
                      <td>
                        <input
                          type="number"
                          min="0"
                          step="0.00000001"
                          required
                          disabled={readOnly}
                          value={tier.min_qty}
                          onChange={(event) => updateTier(index, 'min_qty', event.target.value)}
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          min="0"
                          step="0.00000001"
                          required
                          disabled={readOnly}
                          value={tier[priceKey] ?? ''}
                          onChange={(event) => updateTier(index, priceKey, event.target.value)}
                        />
                      </td>
                      <td>
                        <input readOnly value={fixed(price)} />
                      </td>
                      <td>
                        <input readOnly value={fixed(taxIncluded ? price / (1 + taxRate / 100) : price)} />
                      </td>
                      <td>
                        <input
                          disabled={readOnly}
                          value={tier.notes || ''}
                          onChange={(event) => updateTier(index, 'notes', event.target.value)}
                        />
                      </td>
                      {!readOnly ? (
                        <td>
                          <button
                            type="button"
                            title="删除阶梯"
                            aria-label="删除阶梯"
                            onClick={() => setTiers((current) => current.filter((_, tierIndex) => tierIndex !== index))}
                          >
                            <Trash2 size={15} />
                          </button>
                        </td>
                      ) : null}
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {tiers.length === 0 ? <div className="quote-tier-empty">未设置阶梯时，采购订单使用主报价单价</div> : null}
          </div>
        </section>
        <section className="quote-section">
          <h3>其他资料与审计</h3>
          <div className="quote-grid">
            <label className="quote-wide">
              <span>价格注释</span>
              <textarea
                disabled={readOnly}
                value={values.notes}
                onChange={(event) => update('notes', event.target.value)}
              />
            </label>
            <ReadonlyField label="录入人" value={record?.created_by} />
            <ReadonlyField label="录入时间" value={timestamp(record?.created_at)} />
            <ReadonlyField label="采购确认人" value={record?.confirmed_by} />
            <ReadonlyField label="采购确认时间" value={timestamp(record?.confirmed_at)} />
            <ReadonlyField label="审核人" value={record?.approved_by} />
            <ReadonlyField label="审核时间" value={timestamp(record?.approved_at)} />
            <ReadonlyField label="核准人" value={record?.ratified_by} />
            <ReadonlyField label="核准时间" value={timestamp(record?.ratified_at)} />
            <ReadonlyField label="销售确认人" value={record?.sales_confirmed_by} />
            <ReadonlyField label="销售确认时间" value={timestamp(record?.sales_confirmed_at)} />
          </div>
        </section>
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            {readOnly ? '关闭' : '取消'}
          </button>
          {!readOnly ? (
            <button className="primary">
              <Check size={16} />
              保存草稿
            </button>
          ) : null}
        </div>
      </AsyncForm>
    </div>
  )
}
