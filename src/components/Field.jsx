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
    return (
      <SearchableLookup
        label={item.label}
        required={item.required}
        customerMaterial={item.lookup === 'customerMaterials'}
        value={value}
        options={options}
        onChange={onChange}
      />
    )
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

export function ReadonlyField({ label, value }) {
  return (
    <label>
      <span>{label}</span>
      <input value={value ?? ''} readOnly />
    </label>
  )
}

export function SearchableLookup({
  label,
  value,
  options = [],
  onChange,
  required = false,
  disabled = false,
  customerMaterial = false,
  className = '',
  clearOnFocus = false,
  optionCode = (option) =>
    customerMaterial
      ? option.customer_code || option.code || option.material_code
      : option.code || option.number || option.username || option.name || option.material_code,
  optionText = (option) =>
    [
      optionCode(option),
      option.name,
      option.customer_name,
      option.material_name,
      option.specification,
      option.material_specification
    ]
      .filter(Boolean)
      .join(' ')
}) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find((option) => option.id === Number(value))
  const selectedLabel = selected ? optionCode(selected) : ''
  const visible = options
    .filter((option) => optionText(option).toLowerCase().includes(query.trim().toLowerCase()))
    .slice(0, 30)
  const display = clearOnFocus ? (open ? query : selectedLabel) : query || selectedLabel
  return (
    <label className={`lookup-field ${className} ${customerMaterial ? 'customer-material-lookup' : ''}`}>
      <span>
        {label}
        {required ? <em>*</em> : null}
      </span>
      <input
        required={required}
        disabled={disabled}
        value={display}
        placeholder="输入代码或名称检索"
        onFocus={() => {
          setOpen(true)
          if (clearOnFocus) setQuery('')
        }}
        onChange={(event) => {
          setOpen(true)
          setQuery(event.target.value)
        }}
        onBlur={() =>
          setTimeout(() => {
            setOpen(false)
            setQuery('')
          }, 150)
        }
      />
      {open && !disabled ? (
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
              <span>
                {option.name || option.customer_name || option.material_name}
                {className === 'line-lookup' && option.material_code ? ` · ${option.material_code}` : ''}
              </span>
            </button>
          ))}
          {visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}
        </div>
      ) : null}
    </label>
  )
}
