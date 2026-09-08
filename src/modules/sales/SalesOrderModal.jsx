import { useState } from 'react'
import {
  CalendarCheck,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  CircleHelp,
  Download,
  Eye,
  FileCheck,
  Plus,
  Printer,
  RotateCcw,
  Save,
  Search,
  Settings,
  Trash2,
  Wrench,
  X,
} from 'lucide-react'
import { api } from '../../api/client'
import { labelFor, today } from '../../shared/presentation'
import { Field } from '../../components/Field'
import { SalesOrderDetailModal } from './SalesOrderDetailModal'
import { orderLineColumns, orderFieldByKey, orderGroups } from './salesOrderFields'

export function SalesOrderModal({ token, lookups, record, onClose, onSave, onDelete, onAction, readOnly = false }) {
  if (readOnly) return <SalesOrderDetailModal lookups={lookups} record={record} onClose={onClose} />
  return (
    <SalesOrderEditor
      token={token}
      lookups={lookups}
      record={record}
      onClose={onClose}
      onSave={onSave}
      onDelete={onDelete}
      onAction={onAction}
    />
  )
}

function SalesOrderEditor({ token, lookups, record, onClose, onSave, onDelete, onAction }) {
  const [quoteError, setQuoteError] = useState('')
  const [values, setValues] = useState({
    order_type: '1',
    tax_included: true,
    order_date: today(),
    delivery_mode: 'direct',
    exchange_rate: '1',
    version: 'A',
    ...(record || {}),
  })
  const [lines, setLines] = useState(
    record?.lines || [
      {
        material: '',
        customer_material: '',
        quantity: '',
        spare_quantity: 0,
        promised_date: values.promised_date || today(),
        copper_origin: '',
        copper_currency: '',
        copper_price: 0,
      },
    ]
  )
  const customers = lookups.customers || []
  const materials = lookups.materials || []
  const customerMaterials = lookups.customerMaterials || []
  const addressOptions = customerAddressesFor(values.customer, lookups.customerAddresses)
  const priceTypes = [
    ['1', '期货价'],
    ['2', '期目价'],
    ['3', '即日价'],
    ['4', '议价'],
  ]
  const update = (key, value) => {
    setQuoteError('')
    if (key === 'customer') {
      const selected = customers.find((item) => item.id === Number(value))
      const paymentMethod =
        (lookups.paymentMethods || []).find((item) => item.id === Number(selected?.payment_method_master)) ||
        (lookups.paymentMethods || []).find((item) => item.code === selected?.payment_method)
      setValues((current) => ({
        ...current,
        customer: value,
        customer_name: selected?.name || '',
        currency: selected?.currency || '',
        payment_method: paymentMethod?.id || '',
        tax_rate: selected?.tax_rate ?? 0,
        exchange_rate: selected?.exchange_rate || '1',
        address_code: '',
        delivery_address: '',
      }))
      setLines((current) =>
        current.map((line) => ({
          ...line,
          customer_material: '',
          source_quote_line: '',
          quote_number: '',
          unit_price: '',
          discounted_unit_price: '',
          untaxed_unit_price: '',
        }))
      )
      return
    }
    if (key === 'address_code') {
      const address = addressOptions.find((item) => item.id === Number(value))
      setValues((current) => ({ ...current, address_code: value, delivery_address: address?.address || '' }))
      return
    }
    setValues((current) => ({ ...current, [key]: value }))
  }
  const fetchQuote = async (index, line) => {
    if (!values.customer || !line.material) return
    setQuoteError('')
    const params = new URLSearchParams({
      customer: values.customer,
      material: line.material,
      customer_material: line.customer_material || '',
      currency: values.currency || '',
      date: values.order_date || today(),
    })
    try {
      const quote = await api(`/sales-quote/previous/?${params}`, { token })
      if (!quote.quote_line_id) {
        setQuoteError('未找到与当前客户、物料、客户料号、币种及订单日期匹配的有效报价')
        return
      }
      setLines((current) =>
        current.map((row, rowIndex) =>
          rowIndex === index && row.material === line.material && row.customer_material === line.customer_material
            ? {
                ...row,
                source_quote_line: quote.quote_line_id || '',
                quote_number: quote.quote_number || '',
                price_type: quote.price_type || '',
                unit_price: quote.unit_price ?? '',
                discount_rate: quote.discount_rate ?? 100,
                discounted_unit_price: quote.discounted_unit_price ?? '',
                untaxed_unit_price: quote.untaxed_unit_price ?? '',
                requested_date: quote.effective_date || row.requested_date,
                expected_delivery_date: quote.promised_date || row.expected_delivery_date,
              }
            : row
        )
      )
    } catch (error) {
      setQuoteError(`采用报价失败：${error.message}`)
    }
  }
  const updateLine = (index, key, value) => {
    setQuoteError('')
    const current = lines[index] || {}
    let next = { ...current, [key]: value }
    if (key === 'material') {
      const matches = customerMaterials.filter(
        (item) => item.customer === Number(values.customer) && item.material === Number(value) && item.enabled
      )
      next = {
        ...next,
        customer_material: matches.length === 1 ? matches[0].id : '',
        source_quote_line: '',
        quote_number: '',
        unit_price: '',
        price_type: '',
        discount_rate: 100,
        discounted_unit_price: '',
        untaxed_unit_price: '',
        material_name: materials.find((item) => item.id === Number(value))?.name || '',
        material_specification: materials.find((item) => item.id === Number(value))?.specification || '',
      }
    }
    if (key === 'customer_material') {
      const selected = customerMaterials.find((item) => item.id === Number(value))
      next = {
        ...next,
        material: selected?.material || current.material,
        source_quote_line: '',
        quote_number: '',
        unit_price: '',
        price_type: '',
        discount_rate: 100,
        discounted_unit_price: '',
        untaxed_unit_price: '',
      }
    }
    setLines((currentLines) => currentLines.map((line, lineIndex) => (lineIndex === index ? next : line)))
  }
  const lineValue = (line, key) => {
    if (key === 'line_number') return line.line_number || ''
    if (key === 'material_code') return materials.find((item) => item.id === Number(line.material))?.code || ''
    if (key === 'customer_material_code')
      return customerMaterials.find((item) => item.id === Number(line.customer_material))?.customer_code || ''
    if (key === 'material_name')
      return line.material_name || materials.find((item) => item.id === Number(line.material))?.name || ''
    if (key === 'material_specification')
      return (
        line.material_specification || materials.find((item) => item.id === Number(line.material))?.specification || ''
      )
    if (key === 'customer_material_name')
      return customerMaterials.find((item) => item.id === Number(line.customer_material))?.customer_name || ''
    if (key === 'customer_material_specification')
      return customerMaterials.find((item) => item.id === Number(line.customer_material))?.customer_specification || ''
    if (key === 'terminal_customer_code' || key === 'terminal_customer_name')
      return customerMaterials.find((item) => item.id === Number(line.customer_material))?.[key] || ''
    if (key === 'sales_uom') {
      const customerMaterial = customerMaterials.find((item) => item.id === Number(line.customer_material))
      return (
        (lookups.uoms || []).find((item) => item.id === Number(line.uom || customerMaterial?.customer_uom))?.code || ''
      )
    }
    if (key === 'inventory_uom')
      return (
        (lookups.uoms || []).find((item) => item.id === Number(line.inventory_uom))?.code ||
        materials.find((item) => item.id === Number(line.material))?.uom_code ||
        ''
      )
    if (key === 'tax_code' || key === 'tax_name' || key === 'invoice_name')
      return line[key] || materials.find((item) => item.id === Number(line.material))?.[key] || ''
    if (key === 'discounted_unit_price') return (Number(line.unit_price || 0) * Number(line.discount_rate ?? 100)) / 100
    if (key === 'untaxed_unit_price') return line.untaxed_unit_price || ''
    if (key === 'tax_included_amount')
      return (
        ((Number(line.quantity) || 0) * Number(line.unit_price || 0) * Number(line.discount_rate ?? 100)) /
        100
      ).toFixed(2)
    if (key === 'untaxed_amount')
      return ((Number(line.quantity) || 0) * (Number(line.untaxed_unit_price) || 0)).toFixed(2)
    if (key === 'spare_ratio')
      return Number(line.quantity)
        ? ((Number(line.spare_quantity || 0) / Number(line.quantity)) * 100).toFixed(2)
        : '不适用'
    if (key.startsWith('execution_')) return line.execution_summary?.[key.slice(10)] ?? ''
    if (key === 'cartons')
      return (
        Number(line.products_per_carton) ? Number(line.quantity || 0) / Number(line.products_per_carton) : 0
      ).toFixed(2)
    return line[key] ?? ''
  }
  const save = (event) => {
    event.preventDefault()
    onSave({
      ...values,
      lines: lines
        .filter((line) => line.material)
        .map((line, index) => ({
          ...line,
          unit_price: line.unit_price === '' || line.unit_price == null ? '0' : line.unit_price,
          price_type: line.price_type || '1',
          line_number: line.line_number || (index + 1) * 10,
          promised_date: line.promised_date || values.promised_date,
        })),
    })
  }
  const deleteLine = () =>
    setLines((current) =>
      current.length > 1
        ? current.slice(0, -1)
        : [
            {
              material: '',
              customer_material: '',
              quantity: '',
              spare_quantity: 0,
              promised_date: values.promised_date || today(),
              copper_origin: '',
              copper_currency: '',
              copper_price: 0,
            },
          ]
    )
  const renderOrderField = (key) => {
    const item = orderFieldByKey[key]
    if (!item) return null
    const options = item.key === 'address_code' ? addressOptions : lookups[item.lookup] || item.options || []
    return (
      <Field
        key={item.key}
        field={item}
        value={values[item.key] ?? ''}
        options={options}
        onChange={(value) => update(item.key, value)}
      />
    )
  }
  const columns = [...orderLineColumns]
  const total = lines.reduce((sum, line) => sum + Number(lineValue(line, 'tax_included_amount') || 0), 0)
  columns.splice(
    columns.findIndex(([key]) => key === 'unit_price'),
    0,
    ['quote_choice', '报价取价', 'readonly']
  )
  columns.splice(
    columns.findIndex(([key]) => key === 'spare_quantity') + 1,
    0,
    ['execution_formal_net', '正式净累计', 'readonly'],
    ['execution_spare_net', '备品净累计', 'readonly'],
    ['execution_formal_remaining', '正式剩余', 'readonly'],
    ['execution_spare_remaining', '备品剩余', 'readonly']
  )
  const renderCell = (line, index, [key, label]) => {
    if (key === 'quote_choice')
      return (
        <td key={key}>
          <button
            type="button"
            title="采用有效报价"
            aria-label="采用有效报价"
            disabled={!line.material || !values.customer}
            onClick={() => fetchQuote(index, line)}
          >
            <Search size={15} />
          </button>
          {line.quote_number || ''}
        </td>
      )
    if (key === 'material_code')
      return (
        <td key={key}>
          <LineLookup
            label={label}
            value={line.material}
            options={materials}
            onChange={(value) => updateLine(index, 'material', value)}
          />
        </td>
      )
    if (key === 'customer_material_code') {
      const options = customerMaterials.filter(
        (item) =>
          item.enabled !== false &&
          item.customer === Number(values.customer) &&
          (!line.material || item.material === Number(line.material))
      )
      return (
        <td key={key}>
          <LineLookup
            label={label}
            value={line.customer_material}
            options={options}
            customerMaterial
            onChange={(value) => updateLine(index, 'customer_material', value)}
          />
        </td>
      )
    }
    if (key === 'quantity' || key === 'spare_quantity' || key === 'unit_price')
      return (
        <td key={key}>
          <input
            type="number"
            min="0"
            step={key === 'unit_price' ? '0.000001' : '0.00000001'}
            required={key === 'quantity'}
            value={line[key] ?? ''}
            onChange={(event) => updateLine(index, key, event.target.value)}
          />
        </td>
      )
    if (key === 'copper_origin' || key === 'copper_currency' || key === 'copper_price')
      return (
        <td key={key}>
          <input
            type={key === 'copper_price' ? 'number' : 'text'}
            min="0"
            step="any"
            value={line[key] ?? ''}
            onChange={(event) => updateLine(index, key, event.target.value)}
          />
        </td>
      )
    if (key === 'promised_date')
      return (
        <td key={key}>
          <input
            type="date"
            required
            value={line[key] || values.promised_date || today()}
            onChange={(event) => updateLine(index, key, event.target.value)}
          />
        </td>
      )
    if (key === 'price_type')
      return (
        <td key={key}>
          <input
            className="line-readonly"
            readOnly
            value={priceTypes.find(([value]) => value === String(line[key]))?.[1] || ''}
          />
        </td>
      )
    return (
      <td key={key}>
        <input
          className="line-readonly"
          readOnly
          value={lineValue(line, key) || (key === 'line_number' ? (index + 1) * 10 : '')}
        />
      </td>
    )
  }
  return (
    <div className="modal-backdrop">
      <form className="modal sales-order-modal" onSubmit={save}>
        <div className="modal-head order-modal-head">
          <div>
            <div className="order-kicker">销售管理 / 客户订单</div>
            <h2>{record ? '编辑客户订单' : '新增客户订单'}</h2>
          </div>
          <div className="order-head-meta">
            <span className={`status ${record?.status === 'approved' ? 'green' : 'orange'}`}>
              <i />
              {record?.status === 'approved' ? '已审核' : '草稿'}
            </span>
            <button type="button" aria-label="关闭" onClick={onClose}>
              <X size={19} />
            </button>
          </div>
        </div>
        <div>
          <OrderToolbar
            record={record}
            onAction={onAction}
            onDelete={onDelete}
            onDeleteLine={deleteLine}
            onClose={onClose}
          />
          {quoteError ? (
            <div className="error-banner" role="alert">
              {quoteError}
            </div>
          ) : null}
        </div>
        <div className="order-summary">
          <div>
            <span>客户</span>
            <strong>
              {values.customer
                ? labelFor(customers.find((item) => item.id === Number(values.customer)) || {})
                : '待选择'}
            </strong>
          </div>
          <div>
            <span>明细行</span>
            <strong>{lines.filter((line) => line.material).length} 行</strong>
          </div>
          <div>
            <span>订单含税金额</span>
            <strong>¥ {total.toFixed(2)}</strong>
          </div>
          <div>
            <span>数据状态</span>
            <strong className="summary-ok">可保存</strong>
          </div>
        </div>
        <section className="order-section order-header-section">
          <div className="section-title">
            <h3>订单表头</h3>
            <span>按客户端 ERP 分组显示客户、结算、审核和变更信息</span>
          </div>
          <div className="order-header-groups">
            {orderGroups.map((group) => (
              <div className="order-field-group" key={group.label}>
                <h4>{group.label}</h4>
                <div className="form-grid order-form-grid">{group.keys.map(renderOrderField)}</div>
              </div>
            ))}
          </div>
        </section>
        <section className="order-section order-lines-section">
          <div className="order-section-head">
            <div className="section-title">
              <h3>订单明细</h3>
              <span>选定物料后可向右拖动滚动条查看其余明细字段，承诺交期由业务员填写</span>
            </div>
            <button
              type="button"
              className="secondary"
              onClick={() =>
                setLines((current) => [
                  ...current,
                  {
                    material: '',
                    customer_material: '',
                    quantity: '',
                    spare_quantity: 0,
                    promised_date: values.promised_date || today(),
                    copper_origin: '',
                    copper_currency: '',
                    copper_price: 0,
                  },
                ])
              }
            >
              <span>＋</span>新增明细
            </button>
          </div>
          <div className="order-lines-wrap">
            <table className="order-lines">
              <thead>
                <tr>
                  {columns.map(([key, label]) => (
                    <th key={key}>{label}</th>
                  ))}
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {lines.map((line, index) => (
                  <tr key={index}>
                    {columns.map((column) => renderCell(line, index, column))}
                    <td>
                      <button
                        type="button"
                        title="删除明细"
                        aria-label="删除明细"
                        onClick={() =>
                          setLines((current) =>
                            current.length > 1 ? current.filter((_, lineIndex) => lineIndex !== index) : current
                          )
                        }
                      >
                        <X size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        <div className="modal-foot">
          <span className="order-foot-note">保存后可从列表提交审核</span>
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary">
            <Check size={16} />
            保存草稿
          </button>
        </div>
      </form>
    </div>
  )
}

function customerAddressesFor(customer, addresses = []) {
  return (addresses || []).filter((item) => item.customer === Number(customer))
}

function OrderToolbar({ record, onAction, onDelete, onDeleteLine, onClose }) {
  const run = (action) => {
    if (record?.id && onAction) onAction(action)
  }
  const command = (label, icon, action, disabled = false) => (
    <button
      type="button"
      className="order-command"
      title={label}
      disabled={disabled || !record?.id}
      onClick={() => run(action)}
    >
      {icon}
      <span>{label}</span>
    </button>
  )
  return (
    <div className="order-command-bar">
      {command('查询', <Search size={14} />, 'query', true)}
      <button type="button" className="order-command" title="新增" onClick={() => onAction?.('new')}>
        <Plus size={14} />
        <span>新增</span>
      </button>
      <button type="submit" className="order-command">
        <Save size={14} />
        <span>保存</span>
      </button>
      <button type="button" className="order-command" onClick={onClose}>
        <RotateCcw size={14} />
        <span>取消</span>
      </button>
      <button type="button" className="order-command" title="删除" disabled={!record?.id} onClick={onDelete}>
        <Trash2 size={14} />
        <span>删除</span>
      </button>
      <button type="button" className="order-command" title="删行" onClick={onDeleteLine}>
        <Trash2 size={14} />
        <span>删行</span>
      </button>
      {command('审核', <FileCheck size={14} />, 'approve')}
      {command('反审核', <RotateCcw size={14} />, 'unapprove')}
      {command('交期审核', <CalendarCheck size={14} />, 'delivery-approve')}
      {command('交期反审核', <RotateCcw size={14} />, 'delivery-unapprove')}
      {command('PO变更确认', <CheckCircle2 size={14} />, 'po-change-confirm')}
      {command('PO变更反确认', <RotateCcw size={14} />, 'po-change-unconfirm')}
      {command('第一笔', <ChevronsLeft size={14} />, 'first', true)}
      {command('上一笔', <ChevronLeft size={14} />, 'previous', true)}
      {command('下一笔', <ChevronRight size={14} />, 'next', true)}
      {command('末一笔', <ChevronsRight size={14} />, 'last', true)}
      <button type="button" className="order-command" title="预览" onClick={() => window.print()}>
        <Eye size={14} />
        <span>预览</span>
      </button>
      <button
        type="button"
        className="order-command"
        title="打印"
        onClick={() => {
          window.print()
          run('print')
        }}
      >
        <Printer size={14} />
        <span>打印</span>
      </button>
      {command('页面设置', <Settings size={14} />, 'page-settings', true)}
      {command('导出', <Download size={14} />, 'export', true)}
      {command('工具', <Wrench size={14} />, 'tools', true)}
      {command('帮助', <CircleHelp size={14} />, 'help', true)}
      <button type="button" className="order-command" title="关闭" onClick={onClose}>
        <X size={14} />
        <span>关闭</span>
      </button>
    </div>
  )
}

function LineLookup({ label, value, options, customerMaterial = false, onChange }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find((option) => option.id === Number(value))
  const code = (option) =>
    customerMaterial ? option.customer_code || option.code || option.material_code : option.code || option.material_code
  const text = (option) =>
    [
      code(option),
      option.name,
      option.customer_name,
      option.material_name,
      option.specification,
      option.material_specification,
    ]
      .filter(Boolean)
      .join(' ')
  const visible = options
    .filter((option) => text(option).toLowerCase().includes(query.trim().toLowerCase()))
    .slice(0, 30)
  return (
    <label className={`lookup-field line-lookup ${customerMaterial ? 'customer-material-lookup' : ''}`}>
      <span>{label}</span>
      <input
        value={query || (selected ? code(selected) : '')}
        placeholder="输入代码或名称检索"
        onFocus={() => setOpen(true)}
        onChange={(event) => {
          setQuery(event.target.value)
          setOpen(true)
        }}
        onBlur={() =>
          setTimeout(() => {
            setQuery('')
            setOpen(false)
          }, 150)
        }
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
              <strong>{code(option)}</strong>
              <span>
                {[option.name || option.customer_name || option.material_name, option.material_code]
                  .filter(Boolean)
                  .join(' · ')}
              </span>
            </button>
          ))}
          {visible.length === 0 ? <div className="lookup-empty">无匹配项</div> : null}
        </div>
      ) : null}
    </label>
  )
}
