import { useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Search, X } from 'lucide-react'
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
  onSearch,
  label,
  value,
  options = [],
  onChange,
  required = false,
  disabled = false,
  customerMaterial = false,
  className = '',
  clearOnFocus = false,
  portal = false,
  hideLabel = false,
  allowClear = false,
  selectedText,
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
  const [active, setActive] = useState(0)
  const [position, setPosition] = useState({})
  const inputRef = useRef(null)
  const menuRef = useRef(null)
  const menuId = useId()
  const selected = options.find((option) => String(option.id) === String(value))
  const selectedLabel = selected ? (selectedText || optionCode)(selected) : ''
  const visible = options
    .filter((option) => optionText(option).toLowerCase().includes(query.trim().toLowerCase()))
    .sort((a, b) => Number(String(b.code || '').toLowerCase() === query.trim().toLowerCase()) - Number(String(a.code || '').toLowerCase() === query.trim().toLowerCase()))
    .slice(0, 100)
  useLayoutEffect(() => {
    if (!open || !portal) return
    const place = () => {
      const rect = inputRef.current.getBoundingClientRect()
      const below = window.innerHeight - rect.bottom - 8
      const above = below < 180 && rect.top > below
      const width = Math.min(Math.max(rect.width, 360), window.innerWidth - 16)
      setPosition({ position: 'fixed', width, left: Math.max(8, Math.min(rect.left, window.innerWidth - width - 8)),
        top: above ? undefined : rect.bottom + 3, bottom: above ? window.innerHeight - rect.top + 3 : undefined,
        maxHeight: Math.min(300, Math.max(80, above ? rect.top - 8 : below)), zIndex: 1100 })
    }
    place()
    window.addEventListener('resize', place)
    window.addEventListener('scroll', place, true)
    return () => { window.removeEventListener('resize', place); window.removeEventListener('scroll', place, true) }
  }, [open, portal])
  useLayoutEffect(() => { menuRef.current?.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: 'nearest' }) }, [active])
  const choose = (option) => {
    if (!option || option.disabled) return
    onChange(option.id)
    setQuery('')
    setOpen(false)
  }
  const menu = open && !disabled ? <div ref={menuRef} id={menuId} role="listbox" aria-label={`${label}检索结果`} className={`lookup-menu ${portal ? 'wh-lookup-menu' : ''}`} style={portal ? position : undefined}>
    {visible.map((option, index) => <button type="button" role="option" id={`${menuId}-${index}`} aria-selected={active === index} aria-disabled={Boolean(option.disabled)} disabled={option.disabled} key={option.id}
      onMouseDown={(event) => event.preventDefault()} onClick={() => choose(option)}>
      <strong>{optionCode(option)}</strong><span>{option.name || option.customer_name || option.material_name}{option.specification ? ` · ${option.specification}` : ''}</span>
    </button>)}
    {visible.length === 0 && <div className="lookup-empty">无匹配项</div>}
  </div> : null
  const display = clearOnFocus ? (open ? query : selectedLabel) : query || selectedLabel
  return (
    <label className={`lookup-field ${className} ${customerMaterial ? 'customer-material-lookup' : ''}`}>
      <span hidden={hideLabel}>
        {label}
        {required ? <em>*</em> : null}
      </span>
      <input
        ref={inputRef}
        aria-label={label}
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open && !disabled}
        aria-controls={open ? menuId : undefined}
        aria-activedescendant={open && visible[active] ? `${menuId}-${active}` : undefined}
        autoComplete="off"
        required={required}
        disabled={disabled}
        value={display}
        title={selectedLabel || display}
        placeholder="输入代码或名称检索"
        onFocus={() => {
          setOpen(true)
          setActive(0)
          if (clearOnFocus) setQuery('')
          onSearch?.('')
        }}
        onChange={(event) => {
          setOpen(true)
          setActive(0)
          setQuery(event.target.value)
          onSearch?.(event.target.value)
        }}
        onKeyDown={(event) => {
          if (event.key === 'Escape') { setOpen(false); setQuery(''); event.preventDefault() }
          if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault()
            setOpen(true)
            setActive((index) => Math.max(0, Math.min(visible.length - 1, index + (event.key === 'ArrowDown' ? 1 : -1))))
          }
          if (event.key === 'Enter' && open) { event.preventDefault(); choose(visible[active]) }
        }}
        onBlur={() =>
          setTimeout(() => {
            setOpen(false)
            setQuery('')
          }, 150)
        }
      />
      {portal && <button className="wh-lookup-search" type="button" title={`检索${label}`} aria-label={`检索${label}`} disabled={disabled} onMouseDown={(e) => e.preventDefault()} onClick={() => { inputRef.current.focus(); setQuery(''); setOpen(true); setActive(0) }}><Search size={13}/></button>}
      {allowClear && value != null && value !== '' && !disabled && <button className="wh-lookup-clear" type="button" title={`清空${label}`} aria-label={`清空${label}`} onMouseDown={(e) => e.preventDefault()} onClick={() => { onChange(null); setQuery(''); setOpen(false) }}><X size={12}/></button>}
      {portal ? createPortal(menu, document.body) : menu}
    </label>
  )
}
