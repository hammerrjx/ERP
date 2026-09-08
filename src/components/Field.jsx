import { useState } from 'react'
import { formatDateTime, labelFor } from '../shared/presentation'

export function Field({ field: item, value, options, onChange }) {
  if (item.kind === 'checkbox')
    return (
      <label className="check-field">
        <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} />
        <span>{item.label}</span>
      </label>
    )
  if (item.kind === 'readonly') {
    const related = item.lookup ? options.find((option) => option.id === Number(value) || option.code === value) : null
    const display = item.key.endsWith('_at') ? formatDateTime(value) : related ? labelFor(related) : value || ''
    return (
      <label className="readonly-field">
        <span>{item.label}</span>
        <input value={display} readOnly />
      </label>
    )
  }
  if (item.kind === 'permissions')
    return (
      <label className="field-wide">
        <span>
          {item.label}
          {item.required ? <em>*</em> : null}
        </span>
        <textarea
          required={item.required}
          value={Array.isArray(value) ? value.join(', ') : value}
          onChange={(event) =>
            onChange(
              event.target.value
                .split(',')
                .map((entry) => entry.trim())
                .filter(Boolean)
            )
          }
          placeholder="例如 purchase_order.view, purchase_order.create"
        />
      </label>
    )
  if (item.lookup || item.key === 'address_code')
    return <SearchableLookup field={item} value={value} options={options} onChange={onChange} />
  if (item.kind === 'select') {
    const selectOptions = item.lookup
      ? options.map((option) => ({ value: option.id, label: labelFor(option) }))
      : options.map(([optionValue, label]) => ({ value: optionValue, label }))
    return (
      <label>
        <span>
          {item.label}
          {item.required ? <em>*</em> : null}
        </span>
        <select
          required={item.required}
          value={value}
          onChange={(event) =>
            onChange(event.target.value === '' ? '' : item.lookup ? Number(event.target.value) : event.target.value)
          }
        >
          <option value="">请选择</option>
          {selectOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    )
  }
  return (
    <label>
      <span>
        {item.label}
        {item.required ? <em>*</em> : null}
      </span>
      <input
        required={item.required}
        type={item.kind || 'text'}
        step={item.kind === 'number' ? 'any' : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  )
}

function SearchableLookup({ field: item, value, options, onChange }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find((option) => option.id === Number(value))
  const customerMaterial = item.lookup === 'customerMaterials'
  const optionCode = (option) =>
    customerMaterial
      ? option.customer_code || option.code || option.material_code
      : option.code || option.number || option.username || option.name || option.material_code
  const optionText = (option) =>
    [
      optionCode(option),
      option.name,
      option.customer_name,
      option.material_name,
      option.specification,
      option.material_specification,
    ]
      .filter(Boolean)
      .join(' ')
  const selectedLabel = selected ? optionCode(selected) : ''
  const visible = options
    .filter((option) => optionText(option).toLowerCase().includes(query.trim().toLowerCase()))
    .slice(0, 30)
  return (
    <label className={`lookup-field ${customerMaterial ? 'customer-material-lookup' : ''}`}>
      <span>
        {item.label}
        {item.required ? <em>*</em> : null}
      </span>
      <input
        required={item.required}
        value={query || (selected ? selectedLabel : '')}
        placeholder="输入代码或名称检索"
        onFocus={() => setOpen(true)}
        onChange={(event) => {
          setOpen(true)
          setQuery(event.target.value)
        }}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
      />
      {open ? (
        <div className="lookup-menu">
          {visible.map((option) => (
            <button
              type="button"
              key={option.id}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => {
                onChange(option.id)
                setQuery('')
                setOpen(false)
              }}
            >
              <strong>{optionCode(option)}</strong>
              {option.name || option.customer_name || option.material_name ? (
                <span>{option.name || option.customer_name || option.material_name}</span>
              ) : null}
            </button>
          ))}
          {visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}
        </div>
      ) : null}
    </label>
  )
}
