import { useEffect, useState } from 'react'
import { ArrowUpRight, Check, X } from 'lucide-react'
import { api, listPayload } from '../api/client'
import { formatDateTime, labelFor, relatedLabel } from '../shared/presentation'
import { field } from '../app/config'
import { Field } from './Field'
import { AsyncForm } from './PendingControls'

const auditFields = [
  field('created_by', '录入人'),
  field('created_at', '录入时间'),
  field('updated_by', '修改人'),
  field('updated_at', '修改时间'),
]

export function DetailModal({ config: cfg, row, lookups, onClose }) {
  const configuredFields =
    cfg.resource === 'material' ? [field('code', '物料编码', { kind: 'readonly' }), ...cfg.fields] : cfg.fields
  const detailFields = [
    ...new Map(
      (cfg.audited ? [...configuredFields, ...auditFields] : configuredFields).map((item) => [item.key, item])
    ).values(),
  ]
  return (
    <div className="modal-backdrop">
      <div className="modal detail-modal">
        <div className="modal-head">
          <div>
            <h2>{cfg.title}详情</h2>
            <p>{labelFor(row)}</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <div className="detail-grid">
          {detailFields
            .filter((item) => item.kind !== 'hidden')
            .map((item) => (
              <div key={item.key}>
                <span>{item.label}</span>
                <strong>
                  {item.key.endsWith('_at')
                    ? formatDateTime(row[item.key])
                    : relatedLabel(row[item.key], item, lookups)}
                </strong>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}

export function RecordModal({ config: cfg, lookups, record, onClose, onSave }) {
  const defaults = Object.fromEntries(
    cfg.fields.filter((item) => item.defaultValue !== undefined).map((item) => [item.key, item.defaultValue])
  )
  const [values, setValues] = useState({ ...defaults, ...(record || {}) })
  const [contacts, setContacts] = useState(() =>
    Array.from({ length: 4 }, (_, index) => ({
      name: '',
      position: '',
      phone: '',
      fax: '',
      email: '',
      is_primary: index === 0,
      ...(record?.contacts?.[index] || {}),
    }))
  )
  const [tab, setTab] = useState(cfg.formTabs?.[0]?.id || '')
  const activeTab = cfg.formTabs?.find((item) => item.id === tab)
  const visibleFields = cfg.formTabs
    ? cfg.fields.filter((item) => activeTab?.keys.has(item.key))
    : cfg.fields.filter((item) => item.kind !== 'hidden')
  const save = (event) => {
    event.preventDefault()
    return onSave(
      activeTab?.id === 'contacts' || cfg.formTabs?.some((item) => item.id === 'contacts')
        ? { ...values, contacts: contacts.filter((contact) => contact.name.trim()) }
        : values
    )
  }
  return (
    <div className="modal-backdrop">
      <AsyncForm className={`modal ${cfg.formTabs ? 'partner-modal' : ''}`} onSubmit={save}>
        <div className="modal-head">
          <div>
            <h2>
              {record ? '编辑' : '新增'}
              {cfg.title}
            </h2>
            <p>{cfg.audited ? '先保存草稿，再从列表提交审核' : '保存后立即写入业务明细'}</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        {cfg.formTabs ? (
          <div className="material-tabs partner-tabs" role="tablist" aria-label={`${cfg.title}属性`}>
            {cfg.formTabs.map((item) => (
              <button
                key={item.id}
                type="button"
                role="tab"
                aria-selected={tab === item.id}
                className={tab === item.id ? 'active' : ''}
                onClick={() => setTab(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
        ) : null}
        {activeTab?.id === 'contacts' ? (
          <ContactFields
            contacts={contacts}
            onChange={(index, key, value) =>
              setContacts((current) =>
                current.map((contact, contactIndex) =>
                  contactIndex === index ? { ...contact, [key]: value } : contact
                )
              )
            }
          />
        ) : (
          <div className="form-grid">
            {visibleFields.map((item) => {
              const options =
                item.key === 'address_code'
                  ? (lookups.customerAddresses || []).filter((address) => address.customer === Number(values.customer))
                  : item.lookup
                    ? lookups[item.lookup] || []
                    : item.options || []
              return (
                <Field
                  key={item.key}
                  field={item}
                  value={values[item.key] ?? ''}
                  options={options}
                  onChange={(value) =>
                    setValues((current) => {
                      const address =
                        item.key === 'address_code' ? options.find((option) => option.id === Number(value)) : null
                      return {
                        ...current,
                        [item.key]: value,
                        ...(address ? { delivery_address: address.address } : {}),
                      }
                    })
                  }
                />
              )
            })}
          </div>
        )}
        {cfg.fields
          .filter((item) => item.kind === 'hidden')
          .map((item) => (
            <input key={item.key} type="hidden" value={values[item.key] ?? ''} readOnly />
          ))}
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary">
            <Check size={16} />
            保存
          </button>
        </div>
      </AsyncForm>
    </div>
  )
}

function ContactFields({ contacts, onChange }) {
  return (
    <div className="contact-list">
      {contacts.map((contact, index) => (
        <section className="contact-card" key={index}>
          <strong>联系人 {index + 1}</strong>
          <div className="form-grid">
            <label>
              <span>姓名</span>
              <input value={contact.name} onChange={(event) => onChange(index, 'name', event.target.value)} />
            </label>
            <label>
              <span>职位</span>
              <input value={contact.position} onChange={(event) => onChange(index, 'position', event.target.value)} />
            </label>
            <label>
              <span>联系电话</span>
              <input value={contact.phone} onChange={(event) => onChange(index, 'phone', event.target.value)} />
            </label>
            <label>
              <span>传真</span>
              <input value={contact.fax} onChange={(event) => onChange(index, 'fax', event.target.value)} />
            </label>
            <label className="field-wide">
              <span>电子邮箱</span>
              <input
                type="email"
                value={contact.email}
                onChange={(event) => onChange(index, 'email', event.target.value)}
              />
            </label>
          </div>
        </section>
      ))}
    </div>
  )
}

export function ConversionModal({ kind, row, session, onClose, onSave }) {
  const salesFields = [
    field('customer_po', '客户 PO', { required: true }),
    field('delivery_address', '送货地址', { required: true }),
    field('promised_date', '承诺交期', { kind: 'date', required: true }),
    field('delivery_mode', '送货模式', {
      kind: 'select',
      defaultValue: 'direct',
      options: [
        ['direct', '直送'],
        ['supplier', '供应商代送'],
      ],
    }),
    field('srm_number', 'SRM 单号'),
    field('notes', '备注'),
  ]
  const defaults = Object.fromEntries(
    salesFields.filter((item) => item.defaultValue !== undefined).map((item) => [item.key, item.defaultValue])
  )
  const [values, setValues] = useState(defaults)
  const [choices, setChoices] = useState([])
  const [selected, setSelected] = useState(new Set())
  const [loading, setLoading] = useState(kind === 'purchase')
  const [loadError, setLoadError] = useState('')
  useEffect(() => {
    if (kind !== 'purchase') return
    Promise.all([
      api('/supplier-inquiry/', { token: session.token }),
      api('/rfq-line/', { token: session.token }),
      api('/rfq/', { token: session.token }),
    ])
      .then(([inquiries, rfqLines, rfqs]) => {
        const rfqIds = new Set(
          listPayload(rfqs)
            .filter((rfq) => rfq.requisition === row.id)
            .map((rfq) => rfq.id)
        )
        const lineIds = new Set(
          listPayload(rfqLines)
            .filter((line) => rfqIds.has(line.rfq))
            .map((line) => line.id)
        )
        setChoices(listPayload(inquiries).filter((item) => item.selected && lineIds.has(item.rfq_line)))
      })
      .catch((requestError) => setLoadError(requestError.message))
      .finally(() => setLoading(false))
  }, [kind, row.id, session])
  const toggle = (id) =>
    setSelected((current) => {
      const next = new Set(current)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  const submit = (event) => {
    event.preventDefault()
    return onSave(kind === 'sales' ? values : { supplier_inquiry_ids: [...selected] })
  }
  const title = kind === 'sales' ? '转销售订单' : '转采购单'
  return (
    <div className="modal-backdrop">
      <AsyncForm className="modal" onSubmit={submit}>
        <div className="modal-head">
          <div>
            <h2>{title}</h2>
            <p>来源 {row.number || `#${row.id}`}，生成后保留来源关系</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        {kind === 'sales' ? (
          <div className="form-grid">
            {salesFields.map((item) => (
              <Field
                key={item.key}
                field={item}
                value={values[item.key] ?? ''}
                options={item.options || []}
                onChange={(value) => setValues((current) => ({ ...current, [item.key]: value }))}
              />
            ))}
          </div>
        ) : (
          <div className="source-list">
            {loading ? (
              <div className="empty">正在加载</div>
            ) : loadError ? (
              <div className="error-banner">{loadError}</div>
            ) : choices.length ? (
              choices.map((choice) => (
                <label className="source-row" key={choice.id}>
                  <input type="checkbox" checked={selected.has(choice.id)} onChange={() => toggle(choice.id)} />
                  <strong>响应</strong>
                  <span>询价行 #{choice.rfq_line}</span>
                  <span>供应商 #{choice.supplier}</span>
                  <span>{choice.unit_price}</span>
                </label>
              ))
            ) : (
              <div className="empty">没有可转换的已选中供应商响应</div>
            )}
          </div>
        )}
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary" disabled={kind === 'purchase' && !selected.size}>
            <ArrowUpRight size={16} />
            {title}
          </button>
        </div>
      </AsyncForm>
    </div>
  )
}

export function DocumentEvidenceModal({ row, evidenceType, onClose, onSave }) {
  const [file, setFile] = useState(null)
  const [notes, setNotes] = useState('')
  return (
    <div className="modal-backdrop">
      <AsyncForm
        className="modal"
        onSubmit={(event) => {
          event.preventDefault()
          return onSave({ file, notes })
        }}
      >
        <div className="modal-head">
          <div>
            <h2>上传签收凭证并确认</h2>
            <p>{row.number || `单据 #${row.id}`}，确认后保留凭证和确认人记录</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <div className="form-grid">
          <label className="field-wide">
            <span>
              签收/退货凭证<em>*</em>
            </span>
            <input
              required
              type="file"
              accept=".pdf,image/*"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>
          <label className="field-wide">
            <span>备注</span>
            <textarea value={notes} onChange={(event) => setNotes(event.target.value)} />
          </label>
        </div>
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary" disabled={!file}>
            <Check size={16} />
            上传并确认
          </button>
        </div>
      </AsyncForm>
    </div>
  )
}
