import { useEffect, useMemo, useState } from 'react'
import { Check, History, Plus, Trash2, X } from 'lucide-react'
import { ReadonlyField, SearchableLookup } from '../../components/Field'
import { api } from '../../api/client'
import { statusLabels, today } from '../../shared/presentation'
import { AsyncForm } from '../../components/PendingControls'

const numeric = (value) => Number(value || 0)
const fixed = (value) => (Number.isFinite(value) ? value.toFixed(8) : '')
const optionCode = (row) => row?.customer_code || row?.code || row?.material_code || row?.number || `#${row?.id}`
const optionSearchText = (row) =>
  [optionCode(row), row?.name, row?.customer_name, row?.material_name, row?.customer_code, row?.material_code]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
const timestamp = (value) => (value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '')

export function SalesQuoteModal({ token, lookups, record, readOnly = false, onClose, onSave }) {
  const sourceLine = record?.lines?.[0] || {}
  const [values, setValues] = useState({
    customer: record?.customer || '',
    currency: record?.currency || '',
    address_code: record?.address_code || '',
    address: record?.address_snapshot || record?.address || '',
    tax_included: record?.tax_included ?? '',
    tax_rate: record?.tax_rate ?? '',
    discount_rate: record?.discount_rate ?? '',
    effective_date: record?.effective_date || today(),
    expiry_date: record?.expiry_date || '',
    usage: record?.usage || '',
    notes: record?.notes || '',
    material: sourceLine.material || '',
    customer_material: sourceLine.customer_material || '',
    quantity: sourceLine.quantity || '1',
    unit_price: sourceLine.unit_price || '',
    price_type: sourceLine.price_type || '1',
    promised_date: sourceLine.promised_date || '',
    line_notes: sourceLine.notes || ''
  })
  const [tiers, setTiers] = useState(sourceLine.tiers || [])
  const [previous, setPrevious] = useState(null)
  const [previousError, setPreviousError] = useState('')
  const [previousLoading, setPreviousLoading] = useState(false)
  const [retry, setRetry] = useState(0)
  const customer = (lookups.customers || []).find((row) => row.id === Number(values.customer))
  const material = (lookups.materials || []).find((row) => row.id === Number(values.material))
  const customerMaterial = (lookups.customerMaterials || []).find((row) => row.id === Number(values.customer_material))
  const currency = (lookups.currencies || []).find((row) => row.id === Number(values.currency))
  const uom = (lookups.uoms || []).find((row) => row.id === (customerMaterial?.customer_uom || material?.uom))
  const customerMaterials = useMemo(
    () =>
      (lookups.customerMaterials || []).filter(
        (row) =>
          row.enabled === true &&
          Number(row.customer) === Number(values.customer) &&
          (!values.material || Number(row.material) === Number(values.material))
      ),
    [lookups.customerMaterials, values.customer, values.material]
  )
  const customerAddresses = useMemo(
    () =>
      (lookups.customerAddresses || []).filter(
        (row) => row.enabled !== false && Number(row.customer) === Number(values.customer)
      ),
    [lookups.customerAddresses, values.customer]
  )
  const taxRate = numeric(values.tax_rate === '' ? (customer?.tax_rate ?? record?.tax_rate) : values.tax_rate)
  const discountRate = numeric(
    values.discount_rate === '' ? (customer?.discount_rate ?? record?.discount_rate ?? 100) : values.discount_rate
  )
  const taxIncluded =
    values.tax_included === ''
      ? (customer?.quote_tax_included ?? record?.tax_included ?? true)
      : Boolean(values.tax_included)
  const discounted = fixed((numeric(values.unit_price) * discountRate) / 100)
  const untaxed = fixed(taxIncluded ? numeric(values.unit_price) / (1 + taxRate / 100) : numeric(values.unit_price))

  useEffect(() => {
    setPrevious(null)
    setPreviousError('')
    if (!values.customer || !values.material) {
      setPreviousLoading(false)
      return
    }
    setPreviousLoading(true)
    let active = true
    const query = new URLSearchParams({
      customer: values.customer,
      material: values.material,
      customer_material: values.customer_material,
      currency: values.currency || customer?.currency || '',
      date: values.effective_date || today()
    })
    api(`/sales-quote/previous/?${query}`, { token })
      .then((data) => {
        if (active) setPrevious(data)
      })
      .catch((error) => {
        if (active) setPreviousError(error.message)
      })
      .finally(() => { if (active) setPreviousLoading(false) })
    return () => {
      active = false
    }
  }, [token, values.customer, values.material, values.customer_material, values.currency,
    values.effective_date, customer?.currency, retry])

  const update = (key, value) =>
    setValues((current) => {
      if (key === 'customer') {
        const selected = (lookups.customers || []).find((row) => row.id === Number(value))
        return {
          ...current,
          customer: value,
          customer_material: '',
          address_code: '',
          address: '',
          currency: selected?.currency || '',
          tax_included: selected?.quote_tax_included ?? true,
          tax_rate: selected?.tax_rate ?? 0,
          discount_rate: selected?.discount_rate ?? 100
        }
      }
      if (key === 'material') {
        const selected = (lookups.customerMaterials || []).find((row) => row.id === Number(current.customer_material))
        return {
          ...current,
          material: value,
          customer_material: Number(selected?.material) === Number(value) ? current.customer_material : ''
        }
      }
      if (key === 'customer_material') {
        const selected = (lookups.customerMaterials || []).find((row) => row.id === Number(value))
        return { ...current, customer_material: value, material: selected?.material || current.material }
      }
      if (key === 'address_code') {
        const selected = (lookups.customerAddresses || []).find((row) => row.id === Number(value))
        return { ...current, address_code: value, address: selected?.address || current.address }
      }
      return { ...current, [key]: value }
    })
  const tierPrice = (price) => ({
    discounted: fixed((numeric(price) * discountRate) / 100),
    untaxed: fixed(taxIncluded ? numeric(price) / (1 + taxRate / 100) : numeric(price))
  })
  const save = (event) => {
    event.preventDefault()
    return onSave({
      customer: values.customer,
      effective_date: values.effective_date,
      address_code: values.address_code || null,
      address: values.address,
      currency: values.currency || customer?.currency,
      tax_included: taxIncluded,
      tax_rate: values.tax_rate === '' ? customer?.tax_rate : values.tax_rate,
      discount_rate: values.discount_rate === '' ? customer?.discount_rate : values.discount_rate,
      expiry_date: values.expiry_date || null,
      usage: values.usage,
      notes: values.notes,
      lines: [
        {
          material: values.material,
          customer_material: values.customer_material,
          quantity: values.quantity,
          unit_price: values.unit_price,
          price_type: values.price_type,
          promised_date: values.promised_date || null,
          notes: values.line_notes,
          tiers: tiers.map((tier, index) => ({
            line_number: tier.line_number || (index + 1) * 10,
            min_quantity: tier.min_quantity,
            unit_price: tier.unit_price,
            backup_ratio: tier.backup_ratio || '0',
            notes: tier.notes || ''
          }))
        }
      ]
    })
  }

  return (
    <div className="modal-backdrop">
      <AsyncForm className="modal sales-quote-modal" onSubmit={save}>
        <div className="modal-head">
          <div>
            <h2>{readOnly ? '销售报价详情' : record ? '编辑销售报价' : '新增销售报价'}</h2>
            <p>
              {record?.number || '报价单号保存后自动生成'}
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
          <h3>客户与有效期</h3>
          <div className="quote-grid">
            <ReadonlyField label="报价单号" value={record?.number || '自动生成'} />
            <SearchableLookup
              optionCode={optionCode}
              optionText={optionSearchText}
              label="客户代码"
              value={values.customer}
              options={lookups.customers || []}
              required
              disabled={readOnly}
              onChange={(value) => update('customer', value)}
            />
            <ReadonlyField label="客户名称" value={customer?.name || record?.customer_name} />
            <SearchableLookup
              optionCode={optionCode}
              optionText={optionSearchText}
              label="币种"
              value={values.currency || customer?.currency}
              options={lookups.currencies || []}
              required
              disabled={readOnly}
              onChange={(value) => update('currency', value)}
            />
            <SearchableLookup
              optionCode={optionCode}
              optionText={optionSearchText}
              label="地址代码"
              value={values.address_code}
              options={customerAddresses}
              disabled={readOnly}
              onChange={(value) => update('address_code', value)}
            />
            <label>
              <span>送货地址（可填临时地址）</span>
              <input
                disabled={readOnly}
                value={values.address || ''}
                onChange={(event) => update('address', event.target.value)}
              />
            </label>
            <label className="check-field">
              <input
                type="checkbox"
                disabled={readOnly}
                checked={taxIncluded}
                onChange={(event) => update('tax_included', event.target.checked)}
              />
              <span>含税</span>
            </label>
            <label>
              <span>增值税率(%)</span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                disabled={readOnly}
                value={values.tax_rate === '' ? taxRate : values.tax_rate}
                onChange={(event) => update('tax_rate', event.target.value)}
              />
            </label>
            <label>
              <span>折扣率(%)</span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                disabled={readOnly}
                value={
                  values.discount_rate === ''
                    ? (customer?.discount_rate ?? record?.discount_rate ?? 100)
                    : values.discount_rate
                }
                onChange={(event) => update('discount_rate', event.target.value)}
              />
            </label>
            <ReadonlyField label="备品率(%)" value={customer?.backup_ratio ?? record?.backup_ratio} />
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
            <ReadonlyField label="付款条件" value={customer?.payment_terms || record?.payment_terms} />
          </div>
        </section>
        <section className="quote-section">
          <h3>物料与价格</h3>
          <div className="quote-grid">
            <SearchableLookup
              optionCode={optionCode}
              optionText={optionSearchText}
              label="物料编码"
              value={values.material}
              options={lookups.materials || []}
              required
              disabled={readOnly}
              onChange={(value) => update('material', value)}
            />
            <ReadonlyField label="物料名称" value={material?.name || sourceLine.material_name} />
            <ReadonlyField label="规格型号" value={material?.specification || sourceLine.material_specification} />
            <SearchableLookup
              optionCode={optionCode}
              optionText={optionSearchText}
              label="客户物料编码"
              value={values.customer_material}
              options={customerMaterials}
              disabled={readOnly}
              onChange={(value) => update('customer_material', value)}
            />
            <ReadonlyField
              label="客户物料名称"
              value={customerMaterial?.customer_name || sourceLine.customer_material_name}
            />
            <ReadonlyField
              label="终端客户料号"
              value={customerMaterial?.terminal_customer_code || sourceLine.terminal_customer_code}
            />
            <ReadonlyField
              label="终端客户物料名称"
              value={customerMaterial?.terminal_customer_name || sourceLine.terminal_customer_name}
            />
            <ReadonlyField label="销售单位" value={uom?.code || sourceLine.uom_code} />
            <ReadonlyField
              label="单位换算分子"
              value={customerMaterial?.customer_uom_rate_m || sourceLine.uom_rate_m}
            />
            <ReadonlyField
              label="单位换算分母"
              value={customerMaterial?.customer_uom_rate_d || sourceLine.uom_rate_d}
            />
            <label>
              <span>
                数量<em>*</em>
              </span>
              <input
                type="number"
                min="0.00000001"
                step="0.00000001"
                required
                disabled={readOnly}
                value={values.quantity}
                onChange={(event) => update('quantity', event.target.value)}
              />
            </label>
            <label>
              <span>
                单价类型<em>*</em>
              </span>
              <select
                required
                disabled={readOnly}
                value={values.price_type}
                onChange={(event) => update('price_type', event.target.value)}
              >
                <option value="1">期货价</option>
                <option value="2">期目价</option>
                <option value="3">即日价</option>
                <option value="4">议价</option>
              </select>
            </label>
            <label>
              <span>
                单价<em>*</em>
              </span>
              <input
                type="number"
                min="0"
                step="0.00000001"
                required
                disabled={readOnly}
                value={values.unit_price}
                onChange={(event) => update('unit_price', event.target.value)}
              />
            </label>
            <ReadonlyField label="折后单价" value={discounted} />
            <ReadonlyField label="未税单价" value={untaxed} />
            <label>
              <span>承诺日期</span>
              <input
                type="date"
                disabled={readOnly}
                value={values.promised_date}
                onChange={(event) => update('promised_date', event.target.value)}
              />
            </label>
            <label>
              <span>用途</span>
              <input
                disabled={readOnly}
                value={values.usage}
                onChange={(event) => update('usage', event.target.value)}
              />
            </label>
            <label className="quote-wide">
              <span>物料行备注</span>
              <input
                disabled={readOnly}
                value={values.line_notes}
                onChange={(event) => update('line_notes', event.target.value)}
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
                    { min_quantity: '', unit_price: '', backup_ratio: customer?.backup_ratio || '0', notes: '' }
                  ])
                }
              >
                <Plus size={15} />
                新增阶梯
              </button>
            ) : null}
          </div>
          <div className="quote-tier-wrap">
            <table className="quote-tier-table">
              <thead>
                <tr>
                  <th>起订数量</th>
                  <th>单价</th>
                  <th>折后单价</th>
                  <th>未税单价</th>
                  <th>备品率(%)</th>
                  <th>备注</th>
                  {!readOnly ? <th>操作</th> : null}
                </tr>
              </thead>
              <tbody>
                {tiers.map((tier, index) => {
                  const calculated = tierPrice(tier.unit_price)
                  return (
                    <tr key={tier.id || index}>
                      <td>
                        <input
                          type="number"
                          min="0"
                          step="0.00000001"
                          required
                          disabled={readOnly}
                          value={tier.min_quantity}
                          onChange={(event) =>
                            setTiers((current) =>
                              current.map((row, rowIndex) =>
                                rowIndex === index ? { ...row, min_quantity: event.target.value } : row
                              )
                            )
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          min="0"
                          step="0.00000001"
                          required
                          disabled={readOnly}
                          value={tier.unit_price}
                          onChange={(event) =>
                            setTiers((current) =>
                              current.map((row, rowIndex) =>
                                rowIndex === index ? { ...row, unit_price: event.target.value } : row
                              )
                            )
                          }
                        />
                      </td>
                      <td>
                        <input value={calculated.discounted} readOnly />
                      </td>
                      <td>
                        <input value={calculated.untaxed} readOnly />
                      </td>
                      <td>
                        <input
                          type="number"
                          min="0"
                          step="0.00000001"
                          disabled={readOnly}
                          value={tier.backup_ratio ?? ''}
                          onChange={(event) =>
                            setTiers((current) =>
                              current.map((row, rowIndex) =>
                                rowIndex === index ? { ...row, backup_ratio: event.target.value } : row
                              )
                            )
                          }
                        />
                      </td>
                      <td>
                        <input
                          disabled={readOnly}
                          value={tier.notes || ''}
                          onChange={(event) =>
                            setTiers((current) =>
                              current.map((row, rowIndex) =>
                                rowIndex === index ? { ...row, notes: event.target.value } : row
                              )
                            )
                          }
                        />
                      </td>
                      {!readOnly ? (
                        <td>
                          <button
                            type="button"
                            title="删除阶梯"
                            aria-label="删除阶梯"
                            onClick={() => setTiers((current) => current.filter((_, rowIndex) => rowIndex !== index))}
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
            {tiers.length === 0 ? <div className="quote-tier-empty">暂无阶梯价格</div> : null}
          </div>
        </section>
        <section className="quote-section quote-history">
          <div className="quote-section-head">
            <h3>
              <History size={16} />
              上次报价
            </h3>
          </div>
          {previousLoading ? <div role="status">正在查询上次报价…</div> : previousError ? (
            <div className="error-banner" role="alert">
              上次报价查询失败：{previousError}
              <button type="button" onClick={() => setRetry((value) => value + 1)}>重试</button>
            </div>
          ) : previous?.quote_number ? (
            <div className="quote-history-grid">
              <ReadonlyField label="报价单号" value={previous.quote_number} />
              <ReadonlyField label="生效日期" value={previous.effective_date} />
              <ReadonlyField label="单价" value={previous.unit_price} />
              <ReadonlyField label="币种" value={previous.currency} />
              <ReadonlyField label="税率(%)" value={previous.tax_rate} />
            </div>
          ) : (
            <div className="quote-tier-empty">暂无已核准的相同客户物料报价</div>
          )}
        </section>
        <section className="quote-section">
          <h3>其他资料与审计</h3>
          <div className="quote-grid">
            <label className="quote-wide">
              <span>其他资料</span>
              <textarea
                disabled={readOnly}
                value={values.notes}
                onChange={(event) => update('notes', event.target.value)}
              />
            </label>
            <ReadonlyField label="录入人" value={record?.created_by} />
            <ReadonlyField label="录入时间" value={timestamp(record?.created_at)} />
            <ReadonlyField label="修改人" value={record?.updated_by} />
            <ReadonlyField label="修改时间" value={timestamp(record?.updated_at)} />
            <ReadonlyField label="确认人" value={record?.confirmed_by} />
            <ReadonlyField label="确认时间" value={timestamp(record?.confirmed_at)} />
            <ReadonlyField label="审核人" value={record?.approved_by} />
            <ReadonlyField label="审核时间" value={timestamp(record?.approved_at)} />
            <ReadonlyField label="核准人" value={record?.ratified_by} />
            <ReadonlyField label="核准时间" value={timestamp(record?.ratified_at)} />
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
